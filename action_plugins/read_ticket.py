#!/usr/bin/env python

# Copyright: (c) 2020, MSS ACE <mssace@us.ibm.com>
# IBM internal usage

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import platform
import base64
import requests
import os

from ansible.module_utils.six import iteritems, string_types
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.plugins.action import ActionBase
from ansible.utils.vars import isidentifier

import ansible.constants as C

class ActionModule(ActionBase):

    TRANSFERS_FILES = False

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp  # tmp no longer has any effect

        params = dict()

        cacheable = boolean(self._task.args.pop('cacheable', False))

        if self._task.args:
            for (k, v) in iteritems(self._task.args):
                k = self._templar.template(k)

                if not isidentifier(k):
                    result['failed'] = True
                    result['msg'] = ("The variable name '%s' is not valid. Variables must start with a letter or underscore character, and contain only "
                                     "letters, numbers and underscores." % k)
                    return result

                if not C.DEFAULT_JINJA2_NATIVE and isinstance(v, string_types) and v.lower() in ('true', 'false', 'yes', 'no'):
                    v = boolean(v, strict=False)
                params[k] = v


        result = self.read_opstt(params=params)

        result['changed'] = False
        return result

    def read_opstt(self, params):

        if 'id' not in params.keys():
            result['failed'] = True
            result['msg'] = "Missing required parameter: 'id'"
            return result

        populationLevel = "NORMAL"
        if 'populationLevel' in params:
            populationLevel = params['populationLevel']

        populationLevels = ["ID_ONLY","LIGHT","NORMAL","HEAVY"]
        if populationLevel not in populationLevels:
            result['failed'] = True
            result['msg'] = "Failed to read OPSTT. Disallowed value for field 'populationLevel': {}. Allowed values are: {}".format(params['populationLevel'],str(populationLevels))
            return result

        result = {}
        try:
            response = self.remedyUpdateUsingJson(method="GET", service="Ticket", params=params)
        except Exception as exception:
            result['failed'] = True
            result['msg'] = "Failed to read OPS:Trouble Ticket. {}".format(exception)
            result['id'] = None
            return result

        result['totalCount'] = response['totalCount']
        result['limit'] = response['limit']
        result['start'] = response['start']
        
        try:
            responseItems = response['items'][0]
        except Exception as exception:
            result['failed'] = True
            result['msg'] = "Failed to read OPS:Trouble Ticket. No ticket found with id: {}".format(params['id'])
            result['id'] = None
            return result

        for item in responseItems:
            result[item] = responseItems[item]

        result['failed'] = False
        result['msg'] = "Successfully read OPS:Trouble Ticket {}.".format(params['id'])

        return result

    def getToken(self, token="/opt/ace/tokens/"):
        # input tokens must be unecoded if not using default MSS ACE token.
        if token != "/opt/ace/tokens/":
            return base64.b64encode("MSSToken:"+token)
        else:
            with open('/opt/ace/tokens/token') as f:
                unencToken = f.read().strip()
                return base64.b64encode("MSSToken:"+unencToken)
            return


    def getEnvironment(self):
        environment = os.environ.get('ENVIRONMENT')
        if not environment:
            environment = platform.node()

        if 'prd' in environment:
            return 'prd'
        if 'stg' in environment:
            return 'stg'
        return 'dev'


    def getServicesUrl(self):
        environment = self.getEnvironment()
        if 'prd' in environment:
            return 'services.mss.iss.net'
        return 'stg-services.mss.iss.net'

    def remedyUpdateUsingJson(self, url=None, jsonData={}, method="POST",params={},service="Ticket"):
        auth = "Basic " + self.getToken()
        header = {'Content-Type': "application/json", 'Authorization': auth}

        if 'format' not in params:
            params["format"] = "json"
        params["optimize"] = "false"

        if not url:
            url = "https://{}/rest/{}".format(self.getServicesUrl(),service)

        try:
            restcall = requests.request(method, url, data=jsonData, headers=header, params=params)
            restcall.raise_for_status()
        except Exception as restError:
            response = "Failed to interact with MSS Services (status_code={}).".format(restcall.status_code)
            if restcall.status_code == 500:
                response = "{} Invalid field name or field value provided. Please see https://services.mss.iss.net/rest/{}Schema for valid field names and values.".format(response,service)
            elif restcall.status_code == 401:
                response = "{}  Unauthorized. The ACE MSS Services token is invalid for this request. Please contact the MSS ACE team (#mss-ace) for support.".format(response)
            else:

                try:
                    msg = json.loads(restcall.content)['msg']
                except:
                    msg = str(restcall.content)

                response = "{}  Reason returned by MSS Services: {}. Error: {}".format(response,str(msg),restError)
            raise Exception(response)

        try:
            response = restcall.json()
        except Exception as parseError:
            raise Exception("Failed to retrieve valid JSON from MSS Services: {}".format(parseError))

        return response
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
                    result['msg'] = "The variable name '%s' is not valid. Variables must start with a letter or underscore character, and contain only "\
                                     "letters, numbers and underscores." % k
                    return result

                if not C.DEFAULT_JINJA2_NATIVE and isinstance(v, string_types) and v.lower() in ('true', 'false', 'yes', 'no'):
                    v = boolean(v, strict=False)
                params[k] = v


        result = self.create_opstt(params=params)

        result['changed'] = False
        return result

    
    def create_opstt(self, params):
        result = {}

        required_fields = ['customerId','issueDescription','description','type','priority']
        allowed_fields = ["description","issue","ticketPendingUpon","severity","queue","partnerTicketId"]
        allowed_fields.extend(required_fields)

        not_allowed = ','.join(map(str,[i for i in params if i not in allowed_fields]))

        if len(not_allowed) > 0:
            allowed_fields_str = ', '.join(map(str,allowed_fields))
            result['failed'] = True
            result['msg'] = "Failed to create OPS:Trouble Ticket. Disallowed fields were requested: {}. Allowed fields are: {}".format(not_allowed,allowed_fields_str)
            result['id'] = None
            return result

        missing_required_fields = []
        for field in required_fields:
            if field not in params.keys():
                missing_required_fields.append(field)

        if len(missing_required_fields) > 0:
            result['failed'] = True
            result['msg'] = "create_ticket: Missing required fields: {}".format(', '.join(missing_required_fields))
            return result
        
        if 'priority' in params:
            allowed_priorities = ["HIGH","MEDIUM","LOW"]
            if params['priority'] not in allowed_priorities:
                result['failed'] = True
                result['msg'] = "Failed to create OPS:Trouble Ticket. Disallowed value for field 'priority': {}. Allowed values are: {}".format(params['priority'],', '.join(map(str,allowed_priorities)))
                result['id'] = None
                return result

        jsonData = json.dumps(params)
        
        try:
            response = self.remedyUpdateUsingJson(jsonData=jsonData, method="POST", service="Ticket")
        except Exception as exception:
            result['failed'] = True
            result['msg'] = "Failed to create OPS:Trouble Ticket. {}".format(exception)
            result['id'] = None
            return result

        if "id" in response and len(response['id'])>0:
            result['failed'] = False
            result['msg'] = "Successfully created OPS:Trouble Ticket with id '{}'".format(response['id'])
            result['id'] = response['id']
        else:
            result['failed'] = True
            result['msg'] = "Failed to create OPS:Trouble Ticket. {}".format(str(response))
            result['id'] = None

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
                response = "{}  Unauthorized. The ACE MSS Services token is invalid for this request. Please contact the MSS ACE team (#mss-ace) for support. Header: {}".format(response,header)
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

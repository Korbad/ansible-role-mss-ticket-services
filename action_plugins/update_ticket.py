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
import xml.etree.cElementTree as et

from ansible.module_utils.six import iteritems, string_types
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.plugins.action import ActionBase
from ansible.utils.vars import isidentifier

import ansible.constants as C

#from ansible.plugins.read_ticket import ActionModule as read_ticket

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


        result = self.update_opstt(params=params)
        result['changed'] = False
        return result

    def update_opstt(self, params):
        result = {}
        result['msg'] = ""
        
        required_user_inputs = ['id']
        allowed_user_inputs = ["description","issueDescription","ticketPendingUpon","status","queue","privateWorklog","publicWorklog","partnerTicketId"]
        allowed_user_inputs.extend(required_user_inputs)

        ticket_service_to_remedy_entry_field_names = {}
        ticket_service_to_remedy_entry_field_names["id"] = "1"
        ticket_service_to_remedy_entry_field_names["description"] = "536870945"
        ticket_service_to_remedy_entry_field_names["issueDescription"] = "536870950"
        ticket_service_to_remedy_entry_field_names["customerId"] = "600000000"
        ticket_service_to_remedy_entry_field_names["ticketPendingUpon"] = "536874514"
        ticket_service_to_remedy_entry_field_names["status"] = "7"
        ticket_service_to_remedy_entry_field_names["queue"] = "536871428"
        ticket_service_to_remedy_entry_field_names["partnerTicketId"] = "536871100"
        ticket_service_to_remedy_entry_field_names["privateWorklog"] = "536871102"
        ticket_service_to_remedy_entry_field_names["publicWorklog"] = "536870923"

        ticket_service_to_remedy_entry_field_value_mapping = {}
        ticket_service_to_remedy_entry_field_value_mapping['status'] = { "NEW":0, "ASSIGNED":1, "WORK_IN_PROGRESS":2, "PENDING":3, "RESOLVED_PENDING_CLOSURE":4}

        allowed_field_values_remedy_entry = {}
        allowed_field_values_remedy_entry['ticketPendingUpon'] = ["Customer","Vendor","Partner","Engineering","Maintenance Window","Prep Schedule","Device Prep","Upgrade Window","Escalation","Customer (Hold Open)","Shift Delayed Follow Up","Callback","Service Deviation Request"]

        for _field_name in allowed_field_values_remedy_entry.keys():
            if _field_name in params:
                if params[_field_name] not in allowed_field_values_remedy_entry[_field_name]:
                    result['failed'] = True
                    result['msg'] = "Failed to update OPS:Trouble Ticket. Disallowed value for field '{}': {}. Allowed values are: {}".format(_field_name,params[_field_name],', '.join(map(str,allowed_field_values_remedy_entry[_field_name])))
                    result['id'] = None
                    return result

        missing_required_fields = []
        for field in required_user_inputs:
            if field not in params.keys():
                missing_required_fields.append(field)

        if len(missing_required_fields) > 0:
            result['failed'] = True
            result['msg'] += "update_ticket: Missing required fields: {}".format(', '.join(missing_required_fields))
            return result
        
        not_allowed = ', '.join(map(str,[i for i in params if i not in allowed_user_inputs]))

        if len(not_allowed) > 0:
            allowed_inputs_str = ', '.join(map(str,allowed_user_inputs))
            result['failed'] = True
            result['msg'] += "Failed to update OPS:Trouble Ticket. Disallowed fields were requested: {}. Allowed fields are: {}".format(not_allowed,allowed_inputs_str)
            return result

        data_elements = []
        request_data = {}

        for field in allowed_user_inputs:
            if field in params:
                remedy_entry_field_name = ticket_service_to_remedy_entry_field_names[field]
                if field in ticket_service_to_remedy_entry_field_value_mapping:
                    # print("field:{}".format(field))
                    if params[field] in ticket_service_to_remedy_entry_field_value_mapping[field]:
                        params[field] = ticket_service_to_remedy_entry_field_value_mapping[field][params[field]]
                if field == "privateWorklog" or field == "publicWorklog":
                    params[field] = "Submitted by: MSS Dynamic Automation\n{}".format(params[field])
                data_element = {"key": remedy_entry_field_name, "value": params[field]}
                data_elements.append(data_element)

        request_data['data'] = data_elements
        request_data["schema"] = "OPS:Trouble Ticket"
        request_data["id"] = params['id']
        # print(request_data)
        jsonData = json.dumps(request_data)

        try:
            response = self.remedyUpdateUsingJson(jsonData=jsonData, method="POST", service="RemedyEntry")
        except Exception as exception:
            result['failed'] = True
            result['msg'] += "Failed to update OPS:Trouble Ticket. {}".format(exception)
            result['id'] = None
            return result

        if response == "ok":
            result['failed'] = False
            result['msg'] += "Successfully updated OPS:Trouble Ticket {} using RemedyEntry Service.".format(params['id'])
        elif "id" in response and len(response['id'])>0:
            result['failed'] = False
            result['msg'] += "Successfully updated OPS:Trouble Ticket {}.".format(response['id'])
            result['id'] = response['id']
        else:
            result['failed'] = True
            result['msg'] += "Failed to update OPS:Trouble Ticket. No 'id' parameter was returned by MSS Services. {}".format(str(response))
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
        # if 'optimize' not in params:
        #     params["optimize"] = "false"

        if not url:
            url = "https://{}/rest/{}".format(self.getServicesUrl(),service)

        try:
            restcall = requests.request(method, url, data=jsonData, headers=header, params=params)
            restcall.raise_for_status()
        except Exception as restError:
            response = "Failed to interact with MSS Services (status_code={}).".format(restcall.status_code)
            if restcall.status_code == 500:
                response = "{} Invalid field name or field value provided. Please see https://{}/rest/{}Schema for valid field names and values.".format(response,self.getServicesUrl(),service)
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

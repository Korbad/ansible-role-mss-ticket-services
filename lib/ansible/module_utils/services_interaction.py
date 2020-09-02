#!/usr/bin/env python

# Copyright: (c) 2020, MSS ACE <mssace@us.ibm.com>
# IBM internal usage

    
def getToken(self, token="/opt/ace/tokens/"):
    # input tokens must be unecoded if not using default MSS ACE token.
    if token != "/opt/ace/tokens/":
        return base64.b64encode("MSSToken:"+token)
    else:
        with open('/opt/ace/tokens/token') as f:
            unencToken = f.read()
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

    # url = "{}?&format=json&id={}".format(url,params['id'])
    if method=="POST" and False:
        url = "{}/{}?&format=json".format(url,params['id'])
    else:
        url = "{}?&format=json&id={}".format(url,params['id'])

    try:
        print("method {}".format(method))
        print("url {}".format(url))
        print("jsonData {}".format(jsonData))
        print("header {}".format(header))
        print("params {}".format(params))
        restcall = requests.request(method, url, data=jsonData, headers=header)
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
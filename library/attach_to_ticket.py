#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, MSS ACE <mssace@us.ibm.com>
# IBM internal usage

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: attach_to_ticket
author:
    - MSS ACE Team (mssace@us.ibm.com)
    - Josh Perry (perryjo@us.ibm.com)
short_description: Performs file attachment to OPS:Trouble Ticket
description:
    - Attaches files to OPS:Trouble Tickets in the MSS ticket system.
    - File attachment does not take files from disk, only files read into memory.
    - Interaction with the MSS ticket system is via MSS Ticket Services.
options:
    ticketId:
        description:
        - The OPS:Trouble Ticket id on which to attach the file
        required: true
    base64Bytes:
        description:
        - The base64 encoded contents of the file to be attached
        - One can use jinja2 templating to perform the base64 encoding on the file contents
        required: true
    fileName:
        description:
        - The fileName of the file to be attached
        - The fileName must contain the customerId or Customer Name associated with the OPS:TT
        - The fileName will be prepended with the customerId if the above are not satisfied
        required: true
'''

EXAMPLES = r'''
  - name: Creating new OPS Trouble Ticket for the DNR
    update_ticket:
        id: SOCY00701743778
        status: Assigned
        severity: SEV3
        publicWorklog: "This is a public worklog update"
        privateWorklog: "This is a private worklog update"
    register: create_ticket_result
'''

RETURN = r'''
msg:
  description: result of the file attachment
  returned: success
  type: str
  sample: Successfully attached file 'P000002820-SSDA Test Customer-file.txt' to OPS:Trouble Ticket SOCY00701799006.
msg:
  description: result of the file attachment
  returned: failed
  type: str
  sample: Failed to attach file to OPS:Trouble Ticket
'''

#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, MSS ACE <mssace@us.ibm.com>
# IBM internal usage

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: read_ticket
author:
    - MSS ACE Team (mssace@us.ibm.com)
    - Josh Perry (perryjo@us.ibm.com)
short_description: Get OPS:Trouble Ticket information
description:
    - Fetches ticket information from an OPS:Touble Ticket.
    - Interaction with the MSS ticket system is via MSS Ticket Services.
options:
    id:
        description:
        - Remedy OPS:Trouble Ticket Id
        required: true
    populationLevel:
        description:
        - MSS Services Population level value. Specifys the amount of data to retreive from the ticket.
        - Values must be specified in all Caps.
        choice: ["LOW", "NORMAL", "HEAVY"]
        default: NORMAL
'''

EXAMPLES = r'''
  - name: Lookup ticket information
    read_ticket:
      id: SOCJ00703222626
'''

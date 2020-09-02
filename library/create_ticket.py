#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, MSS ACE <mssace@us.ibm.com>
# IBM internal usage

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: create_ticket
author:
    - MSS ACE Team (mssace@us.ibm.com)
    - Josh Perry (perryjo@us.ibm.com)
short_description: Create OPS:Trouble Ticket module
description:
    - Creates new OPS:Trouble Ticket in the MSS ticket system.
    - Interaction with the MSS ticket system is via MSS Ticket Services.
options:
    customerId:
        descrition:
        - Remedy Customer Id.
        - Creates ticket under this customer Id.
        required: true
    # customerName:
    #     description:
    #     - Remedy Customer Name. Must match Remedy exactly.
    #     - Creates ticket under this customer name.
    description:
        description:
        - OPS:Trouble Ticket 'Issue Description Reason For Escalation' field.
        required: true
    issueDescription:
        description:
        - OPS:Trouble Ticket 'Issue' value.
        - Sets the ticket issue to the specified value.
        - Must match a valid issue from Remedy OPS:Troule Ticket.
        required: true
    type:
        description:
        - Services ticketType code.
        - See https://services.mss.iss.net/rest/TicketSchema for valid ticketType values.
        - Sets the ticket type to the specified value.
    # partnerId:
    #     description:
    #     - Remedy Partner Id.
    # partnerName:
    #     descrioption:
    #     - Remedy Partner Name. Must match Remedy exactly.
    prority:
        description:
        - OPS:Trouble Ticket 'Priority' value.
        - Set the ticket priority to the specified value.
        choice: ["LOW", "MEDIUM", "HIGH"]
        required: true
    ticketPendingUpon:
        description:
        - OPS:Trouble Ticket 'Pending Upon' value.
        - Sets ticket pending upon field to the specified value.
        choices: ["Customer", "Vendor", "Partner", "Engineering", "Maintenance Window", "Prep Schedule", "Device Prep",
            "Upgrade Window", "Escalation", "Customer (Hold Open)", "Shift Delayed Follow up", "Callback", "Service Devaition Request"]
    severity:
        description:
        - OPS:Trouble Ticket 'Severity Code' value.
        - Sets the ticket severity code to the specified value.
        choice: ["SEV1", "SEV2", "SEV3", "SEV4"]
        required: true
    queue:
        description:
        - OPS:Trouble Ticket 'Queue Name' value.
        - Sets the ticket queue to the specified value.
        - Must match a valid queue from Remedy OPS:Trouble Ticket.
        required: true
'''

EXAMPLES = r'''
  - name: Creating new OPS Trouble Ticket for the DNR
    create_ticket:
      issueDescription: INC - Device Logging Incident
      type: MANAGED_SIEM
      severity: SEV3
      customerId: P000002820
      description: >
        "Dear Customer,
        ...
        Managed Security Services
        IBM Security"
      queue: MSIEM ADMIN PCRs/OCRs/Inbound
      group: MSIEM
    register: create_ticket_result
'''

RETURN = r'''
id:
  description: Remedy OPS:Trouble Ticket Id of newly created ticket.
  returned: success
  type: str
  sample: SOCJ00703222626
'''

#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, MSS ACE <mssace@us.ibm.com>
# IBM internal usage

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: update_ticket
author:
    - MSS ACE Team (mssace@us.ibm.com)
    - Josh Perry (perryjo@us.ibm.com)
short_description: Performs updates to OPS:Trouble Ticket
description:
    - Updates ticket data for the given OPS:Trouble Ticket in the MSS ticket system.
    - Interaction with the MSS ticket system is via MSS Ticket Services.
options:
    description:
        description:
        - OPS:Trouble Ticket 'Issue Description / Reason For Escalation' field.
        - Set the ticket descrition to the specified value.
    id:
        description:
        - OPS:Trouble Ticket Id.
        required: true
    issue:
        description:
        - Services ticketIssue code.
        - See https://services.mss.iss.net/rest/TicketSchema for valid ticketIssue values.
    issueDescription:
        description:
        - OPS:Trouble Ticket 'Issue' value.
        - Sets the ticket issue to the specified value.
        - Must match a valid issue from Remedy OPS:Troule Ticket.
    type:
        description:
        - Services ticketType code.
        - See https://services.mss.iss.net/rest/TicketSchema for valid ticketType values.
        - Sets the ticket type to the specified value.
    prority:
        description:
        - OPS:Trouble Ticket 'Priority' value.
        - Set the ticket priority to the specified value.
        choice: ["LOW", "MEDIUM", "HIGH"]
    ticketPendingUpon:
        description:
        - OPS:Trouble Ticket 'Pending Upon' value.
        - Sets ticket pending upon field to the specified value.
        choices: ["Customer", "Vendor", "Partner", "Engineering", "Maintenance Window", "Prep Schedule", "Device Prep",
            "Upgrade Window", "Escalation", "Customer (Hold Open)", "Shift Delayed Follow up", "Callback", "Service Devaition Request"]
    status:
        description:
        - OPS:Trouble Ticket 'Status' value.
        - Updates the ticket status to the speificed value.
        choice: ["New", "Assigned", "Work In Progress", "Pending", "Resolved, Pending Closure", "Closed"]
    severity:
        description:
        - OPS:Trouble Ticket 'Severity Code' value.
        - Sets the ticket severity code to the specified value.
        choice: ["SEV1", "SEV2", "SEV3", "SEV4"]
    queue:
        description:
        - OPS:Trouble Ticket 'Queue Name' value.
        - Sets the ticket queue to the specified value.
        - Must match a valid queue from Remedy OPS:Trouble Ticket.
    privateWorkLog:
        description:
        - Writes the provided input to the OPS:Trouble Ticket Private worklog.
    publicWorkLog:
        description:
        - Writes the provided input to the OPS:Trouble Ticket Public worklog.
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
  description: result of the ticket update
  returned: success
  type: str
  sample: Successfully updated OPSTT with SOCJ00703222626
msg:
  description: result of the ticket update
  returned: failed
  type: str
  sample: Failed to update OPSTT using MSS Services plugin
'''

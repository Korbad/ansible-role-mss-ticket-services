ansible-mss-ticket-services
=========

This role contains the MSS Ticket Services plugin which allows you to Create, Update, and Read tickets through MSS Services.

Requirements
------------

This role requires the following Python modules to be installed: future, requests
This role requires that an MSS Service token is present here: /opt/ace/tokens/token

Role Variables
--------------

None

Dependencies
------------

None

Example Playbook
----------------

``` yaml
---
- name: Test role usage
  hosts: localhost
  roles:
    - mss_ticket_services
  tasks:
    - create_ticket:
        customerId: P000002820
        issueDescription: INC - Device Logging Incident
        description: test ticket
        type: INTERNAL
        priority: LOW
      register: create_ticket_response

    - name: Reading OPS TT
      read_ticket:
        id: "{{ create_ticket_response.id }}"
      register: ticket_result

    - name: Updating new OPS TT
      update_ticket:
        id: "{{ create_ticket_response.id }}"
        description: |
          Dear Testing 
          for testing, 
          newline tested
      register: update_ticket_result

    - attach_to_ticket:
        ticketId: "{{ create_ticket_response.id }}"
        fileName: file.txt
        base64Bytes: "{{ ticket_result.issueType | b64encode }}"

    - attach_to_ticket:
        ticketId: "{{ create_ticket_response.id }}"
        fileName: MSS SSDA Test Customer-file.txt
        base64Bytes: VGhpcyBpcyBhbiBlbmNvZGVkIHRlc3QgZmlsZQ==
```

License
-------

IBM Internal

Author Information
------------------

MSS ACE Team (mssace@us.ibm.com)
Joshua Perry (perryjo@us.ibm.com)

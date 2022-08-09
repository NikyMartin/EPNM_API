This example can be used to retrieve Audit Log messages from EPN-M

It provides applications and category filters

It can be used as query option as opposed to the EPN-M syslog function where same audit messages are available, without any filter

Available Application Options:

   - NCS
   - Prime Infrastructure
   - EPNM
   - Evolved Programmable Network Manager
   - Service Provisioning
   - Discovery

Available Category Options:

   - ADMIN
   - User Management			   
   - PROVISIONING
   - Device Management
   - Grouping
   - MONITOR CONFIGURATION
   - Job Management
   - Software-Update			
   - SYSTEM
   - CONFIG
   - Service Discovery
   - Device Console	
   - Configuration Archive
   - Virtual Domain
   - Software Image Management
   - Report				 
   - RESTCONF

**NOTE**: Available categories will depend on the selected application. 
During script execution, category list selection menu will also show applicable application

Syntax to be used:
```python
python get_audits.py <EPNM IP>
```

Example Output Message:
```json
    {
        "audit-log.appname": "NCS",
        "audit-log.category": "ADMIN",
        "audit-log.client-ip": "10.209.193.3",
        "audit-log.description": "Login successful for user root from 10.209.193.3",
        "audit-log.timestamp": 1659966146785,
        "audit-log.timestamp-iso8601": "2022-08-08T13:42:26.785+00:00",
        "audit-log.username": "root"
    }
```
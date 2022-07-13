### Intro

This content is based on a real customer project where EPNM API has been used to deliver ODU2E 
services on an hybrid network made of NCS 2000 and NCS 4000
More details are available in the included Powerpoint deck: Provision_ODU2E.pptx

### Setup:

- Import the ExportedTemplates.zip template file in EPNM
    In EPNM main navigation menu:
    Configuration -> Features & Technologies. Then "Import" button

- Update dbapassword file with the output from EPNM script:
	/opt/CSCOlumos/bin/getDatabaseParams.sh
	Oracle password changes upon server restart. The automated environment using this solution
	should implement a periodic check on this dbapassword. An error message will advice if
	password is wrong while executing the create ODU2E scripts:
	"ORA-01017: invalid username/password; logon denied" 

- Open Oracle listener port on EPNM firewall with:
	sudo iptables -I INPUT 1 -p tcp --dport 1522 -j ACCEPT

- Create a device ID list executing getDeviceID_progress.py
    this script need to be executed when a new device is added in EPNM

### Create an ODU2E Service:

- Create a JSON service file
    Examples are available under service_file_examples folder (remember 
    service_ID must be unique for each file)

- Validate the JSON service file using  validate_input_file.py

- Create a protected or unprotected ODU2E servioce using createODU2E_Prot.py or createODU2E_unprot.py 
    scripts, passing EPNM IP and JSON service file as input parameters
    EX: python createODU2E_unprot.py 10.58.234.32 2K-2K_unprot.json

- Validate template execution using jobHistory.py. 
    Complete syntax will be provided at the end of the create script
    EX: python jobHistory.py 10.58.234.32 Create_JobList2022-07-12_16:46_CEST.json 

- Verify service discovery state in EPNM GUI

### Delete an ODU2E service:

- deleteODU2E_Prot.py and deleteODU2E_unprot.py can be used to delete a service. 
    Syntax is same as the the create ODU2E scripts
    EX: python deleteODU2E_unprot.py 10.58.234.32 2K-2K_unprot.json

### Best practices:

- JSON service file should be not edited if a service was created (even if partial or failed) and kept as is until the server is deleted
- If a change in the JSON service file is required, then first make sure the associated service (or part of it) is deleted.

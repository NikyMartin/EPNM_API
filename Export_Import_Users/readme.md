# Export and Import EPN Manager users

### Intro
When users upgrades EPN Manager (either minor or major upgrades) the provided upgrade process preserves, 
among other data, all user accounts. Many times users prefer a fresh install rather then following 
the whole upgrade process. Sometimes users are in the need of reinstalling same release from scratch 
(previous server got broken for example).

In both cases, one of the most valuable information lost would be the user accounts

Those two scripts help importing all user accounts from one system to the other

### Workflow
The **Export** process consists of two steps:

- Export all EPN-M Users using REST API and same content to a JSON file. This file will contain 
assigned user groups and domains 
- Make an SQL select to the USERS Oracle table to extract passwords and other user data like 
firstname, lastname and email address. Output will be saved on a second JSON file

The **Import** process same way consists of:

- Importing all EPN-M Users using REST API using first JSON file. Users will be added with an 
hardcoded password
- Update USERS Oracle table using second JSON file to set proper passwords (as long with firstname, 
lastname and email address). 

***NOTE***: In current version, email address are imported but for unknown 
reasons not properly shown on EPNM GUI

### Setup:

- take note of the Oracle WCSDBA user password running following EPNM script:
	/opt/CSCOlumos/bin/getDatabaseParams.sh
	
	This will be provided as of of the scripts user inputs

- Open Oracle listener port on EPNM firewall with:

	sudo iptables -I INPUT 1 -p tcp --dport 1522 -j ACCEPT

Syntax to be used:
```python
python export_users.py <EPNM Server IP> <WCSDBA Password>

python import_users.py <EPNM Server IP> <WCSDBA Password>
```

The **export_users.py** script will generate two JSON files:

export_epnm_users.json

export_oracle_users.json

And a log file also, export.log

The JSON filenames are hardcoded and automatically used by the import script

The **import_users.py** will generate a log file, import.log
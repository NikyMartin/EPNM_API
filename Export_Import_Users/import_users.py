#!/usr/bin/python

"""
    Created by:
    Nicola Martino, nmartino@cisco.com

    Feb 8th, 2020
    Original version

"""

#############################################################
# This script does two things:
#    - Adds EPNM users via API using first json file
#    - Updates Oracle user table to impport user passwords 
#         and other user data stored a second json file
#############################################################

import cx_Oracle
import os 
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import socket
import requests
import sys
import getpass
import platform
import logging.handlers as handlers
import logging

logger = logging.getLogger('nicola')
logger.setLevel(logging.INFO)

LOG_FILE="import.log"
open(LOG_FILE, 'w').close()
logHandler = handlers.RotatingFileHandler(LOG_FILE, maxBytes=10000, backupCount=2, mode='w')
logHandler.setLevel(logging.INFO)
logger.addHandler(logHandler)
logger.info("\nAdd something here\n")

version=platform.python_version_tuple()
if version[0] != '3':
    print("This script requires Python3")
    exit(1)

logger.info("Python version is "+platform.python_version())

# Static username and password
# Remember to comment getusername and password down in the script

# epnm_username = 'martino'
# epnm_password = 'Public123'

### Check if IP address and port have been passed as input parameters
if len(sys.argv)!=3:
    print('\nMust pass server IP address and Oracle wcsdba password as script arguments')
    print('Example: python import_users.py3 10.58.345.67 RpeQo8DJ9p8chFBJ\n')
    exit(1)
scripts, server_ip, dbapassword = sys.argv

###### Uncomment next two linesto use static server IP and dba password
# server_ip="10.58.124.33"
# dbapassword='RpeQo8DJ9p8chFBJ'
import_oracle_filename='export_oracle_users.json'
import_epnm_filename='export_epnm_users.json'

listener_port=1522
sid='wcs'
dbauser='wcsdba'
sid = cx_Oracle.makedsn(server_ip, listener_port, service_name=sid)

def isOpen(server_ip,port):
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   try:
      s.connect((server_ip, int(port)))
      s.shutdown(2)
      return True
   except:
      return False

def isEPNM(server_ip):
    response = requests.get('https://'+server_ip+'/webacs/welcomeAction.do', verify=False)
    if response.status_code == 200:
       return True
    else:
       return False

def isAccountValid(server_ip,user,pwd):
    response = requests.get('https://'+server_ip+'/webacs/api/v4/data/Devices?.maxResults=1', verify=False, auth=(user, pwd))
    if response.status_code == 401: # Error code 401 = Unauthorized
       return False
    else:
       return True

def EPNMuserslenght(server_ip,user,pwd):
    headers = {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }
    response = requests.get('https://'+server_ip+'/webacs/api/v4/op/userManagement/users', headers=headers, verify=False, auth=(user, pwd))
    if response.status_code != 200:
       return (False,response.status_code)
    else:
       epnm_users = json.loads(response.text)['mgmtResponse']['usersDTO']
       how_many = len(epnm_users)
       logger.info("Found "+str(how_many)+" users")
       return (True,how_many)

# Function to add a user via EPNM API
# Password will be initiallly hardcoded then changed later
# To the correct one

def add_user(epnm_user):

    headers = {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

    logger.info("Adding user "+epnm_user['name'])
    payload = json.dumps({
      "createUserDTO": {
        "name": epnm_user['name'],
        "password": "Public123",
        "userGroups": epnm_user['userGroups'],
        "virtualDomains": epnm_user['virtualDomains'],
        "wirelessUser": False
      }
    })    

    if epnm_user['name'] != 'root':
        response = requests.post('https://'+server_ip+'/webacs/api/v4/op/userManagement/users',  headers=headers, data=payload, verify=False, auth=(epnm_username, epnm_password))
        if response.status_code != 200:
           print("Error while adding user ",epnm_user['name'])
           print("HTTP ERROR "+str(response.status_code))

##################
### Basic controls
##################

logger.info("Checking HTTPS Port 443")

# Check if https server is up and port 443 is reachable

if not isOpen(server_ip,443):
   print("\nERROR: "+server_ip+" is not reachable, either the server is down or port 443 is filtered\n")
   exit()

logger.info("HTTPS Port 443 is Open")

# Check if https server is EPNM

logger.info("Checking if this is an EPNM Server")

if not isEPNM(server_ip):
   print("\nERROR: "+server_ip+" is not an EPN-M Server\n")
   exit()

logger.info("Control on EPNM Server passed")

# Check if Oracle Listner port is reachable and iptables disabled

logger.info("Checking Oracle listener port")

if not isOpen(server_ip,listener_port):
   print("\nERROR: Either Oracle is down or port ",listener_port," is filtered")
   print("Make sure you have disabled iptables on EPNM Server with: sudo service iptables stop\n")
   exit()

logger.info("Listener port is open")

# Check if account is correct

logger.info("Checking User Credentials")

###### Comment those two lines to use hardcoded credentials
epnm_username = input("Enter Username: ")
epnm_password = getpass.getpass()

if not isAccountValid(server_ip,epnm_username,epnm_password):
    print("\nERROR: Check if username and password are correct\n")
    exit()

logger.info("EPNM credentials are connect")

# Check if EPNM server has userso

logger.info("Checking if EPNM has existing users")

status, resp = EPNMuserslenght(server_ip,epnm_username,epnm_password)

if not status:
    print("ERROR: It was not possible to execute GET EPNM users")
    print("Server returned :",resp)
else:
    if resp != 1:
       print("ERROR: This server has existing users")
       print("To add additional users, edit code and comment this section")
       exit(1)

logger.info("Only root found")

##############################
### Adding EPNM Users via API
##############################

logger.info("Adding EPNM users via API")
logger.info("Importing EPNM JSON file")

try:
   f = open(import_epnm_filename,'r')
except Exception as e:
    print ('Failed loading EPNM json file')
    print (str(e))
    exit (1)
epnm_users=json.load(f)
f.close ()

logger.info("EPNM JSON file imported")
logger.info("Calling Function to add EPNM users via API")

for user in epnm_users:
    add_user(user)

print("EPNM Users Added")
logger.info("Added EPNM users")

###############################
### Updating Oracle users table
###############################

logger.info("Updating Oracle users table")
logger.info("Importing Oracle JSON file")

try:
   f = open(import_oracle_filename,'r')
except Exception as e:
    print ('Failed loading EPNM json file')
    print (str(e))
    exit (1)
epnm_users=json.load(f)
f.close ()

logger.info("Oracle JSON file imported")
logger.info("Connecting to Oracle listener")

try:
    connection = cx_Oracle.connect(dbauser, dbapassword, sid)
#     connection = cx_Oracle.connect(dbauser, dbapassword, sid, encoding="UTF-8")
except Exception as e:
    print ('Failed to connect Database')
    print (str(e))
    exit (1)

logger.info("Oracle listener connected")

cursor = connection.cursor()

SQL = 'update USERS set PASSWORD = :password, SALT = :salt, FIRSTNAME = :firstname, LASTNAME = :lastname, EMAIL = :email where USERNAME = :username'

logger.info("Performing SQL Update")

for user in epnm_users:
    logger.info("Updating User "+user['username'])
    username=user['username']
    password=user['password']
    salt=user['salt']
    firstname=user['firstname']
    lastname=user['lastname']
    email=user['email']
    try:
        cursor.execute(SQL, password=password,salt=salt,firstname=firstname,lastname=lastname,email=email,username=username)
    except Exception as e:
        print ('Failed to perform update for user ',username)
        print (str(e))

cursor.close ()
connection.commit ()
connection.close ()

print("Oracle users tale updated")
logger.info("Oracle users table updated")

exit (0)

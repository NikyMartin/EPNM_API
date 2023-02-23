#!/usr/bin/python

"""
    Created by:
    Nicola Martino, nmartino@cisco.com

    Feb 8th, 2020
    Original version

    Feb 23rd, 2023
    Rev1: Moved form cx_Oracle to oracledb
    To solve arm64 compatibility problems

    TODO: add export Domains + exported filename including server IP

"""

#############################################################
# This script does two things:
#    - exports all EPNM users via API to a first json file
#    - exports user passwords and other data directly 
#              from Oracle users table to a second json file
#############################################################

import oracledb
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

LOG_FILE="export.log"
open(LOG_FILE, 'w').close()
logHandler = handlers.RotatingFileHandler(LOG_FILE, maxBytes=1000, backupCount=2, mode='w')
logHandler.setLevel(logging.INFO)
logger.addHandler(logHandler)
logger.info("\nAdd something here\n")

version=platform.python_version_tuple()
if version[0] != '3':
    print("This script requires Python3")
    exit(1)

logger.info("Python version is "+platform.python_version())

# lib_dir = os.path.join(os.environ.get("HOME"), "bin", "instantclient_19_8")
# cx_Oracle.init_oracle_client(lib_dir=lib_dir)

### Check if IP address and port have been passed as input parameters
if len(sys.argv)!=3:
    print('\nMust pass server IP address and Oracle wcsdba password as script arguments')
    print('Example: python export_users.py3 10.58.345.67 NzyiE5sRosS5R7lj\n')
    exit(1)
scripts, server_ip, dbapassword = sys.argv

export_oracle_filename='export_oracle_users.json'
export_epnm_filename='export_epnm_users.json'

listener_port='1522'
sid='wcs'
dbauser='wcsdba'
# old command to genereta the connection string. Still working
# conn_string = cx_Oracle.makedsn(server_ip, listener_port, service_name=sid)

# This one would work as well
conn_string = "".join([server_ip,':',listener_port,'/',sid])

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

def getEPNMusers(server_ip,user,pwd):
    headers = {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }
    response = requests.get('https://'+server_ip+'/webacs/api/v4/op/userManagement/users', headers=headers, verify=False, auth=(user, pwd))
    if response.status_code != 200:
       return (False,response.status_code)
    else:
       return (True,response.text)

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

#############################
### Export EPNM users via API
#############################

logger.info("Exporting EPNM Users via API")

status, resp = getEPNMusers(server_ip,epnm_username,epnm_password)

if not status:
    print("ERROR: It was not possible to execute GET EPNM users")
    print("Server returned :",resp)
else:
    epnm_users = json.loads(resp)['mgmtResponse']['usersDTO']

f = open(export_epnm_filename,'w')
json.dump(epnm_users,f)
f.close()

print("EPNM Users Exported")
logger.info("Users exported\n")

###############################
### Export Oracle users table
###############################

logger.info("Exporting Oracle users table")
logger.info("Connecting to Oracle listener")

try:
#    connection = cx_Oracle.connect(dbauser, dbapassword, sid)
# This is the onld one working with cx_Oracle before moving to oracledb
#    connection = cx_Oracle.connect(dbauser, dbapassword, sid, encoding="UTF-8")
#     connection = cx_Oracle.connect(user=dbauser, password=dbapassword, dsn=sid, encoding="UTF-8")
     print(conn_string)
     connection = oracledb.connect(user=dbauser, password=dbapassword, dsn=conn_string, encoding="UTF-8")
except Exception as e:
  print ('Failed to connect Database')
  print (str(e))
  exit (1)

logger.info("Oracle listener connected")

cursor = connection.cursor()

SQL = 'select USERNAME, PASSWORD, SALT, FIRSTNAME, LASTNAME, EMAIL from users'

logger.info("Performing SQL Select")

try:
   cursor.execute(SQL)
except Exception as e:
  print ('Failed to perform select')
  print (str(e))
  exit (1)

# lets convert select output in a json array

logger.info("Converting select output in a JSON array\n")

users=[]
for row in cursor:
    if row[0] != 'root':
        user = ({
            "username": row[0],
            "password": row[1],
            "salt": row[2],
            "firstname": row[3],
            "lastname": row[4],
            "email": row[5]
        })
        users.append(user)
        logger.info("Converting User "+row[0])

logger.info("\nDumping JSON array to file\n")
f = open(export_oracle_filename,'w')
json.dump(users,f)
f.close()

cursor.close ()
connection.close ()

print("Oracle Users table exported")

exit (0)

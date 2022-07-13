#!/usr/bin/python

# python 3 is required

"""
    Created by:
    Nicola Martino, nmartino@cisco.com

    March 4th, 2022
    Original version

    March 22nd, 2022
    Added 4K-4K use case

"""

# #####################################################################################
# This is the main script who creates protected 10G ODU services. Following imports use
# other python files present in same directory
# #####################################################################################

# Main does following:
#   - executes basic controls (443 port open, verify credentials and other)
#   - validates input JSON file
#   - verifies the file containing EPNM device IDs list ("deviceIDlist.json") exists
#       The EPNM internal device ID is required as input when executing EPNM templates
#       from NBI
#   - if A end is 4K, executes "CREATE_PROT_ODU2E_4kendpoint_A" EPNM template
#   - if A end is 2K, executes "CREATE_PROT_ODU2E_2kendpoint_A" EPNM template
#   - for any device found in the working or protecetd path, execute either
#       "CREATE_ODU2E_2kmidpoint" or "CREATE_ODU2E_4kmidpoint" depending on if
#       midnode is 2K or 4K
#
# This script generates an output file (in JSON) made of all EPNM job IDs created by EPNM
# templates in a list format

from executeTemplate import executeTemplate
# "executeTemplate" Can execute any type of EPNM template
from getCreatePayload_4K_End import createPayload_4K_End
from getCreatePayload_2K_End import createPayload2Kend
from getCreatePayloadMid import createPayloadMid
# "createPayloadMid" Creates the required payload to execute
# "CREATE_ODU2E_2kmidpoint" or "CREATE_ODU2E_4kmidpoint" depending
# on if midnode is 2K or 4K
from get4K_NodeID import get4K_nodeID
# "get4K_nodeID" "creates" a TL1 like node ID (4K do not have)
from getTL1details import get_TL1_NodeID
# "get_TL1_NodeID" connects to EPNM Oracle DB and exctact
# TL1 node ID for a given node name
from validate_input_file import runValidate
from checkUseCase import getFileProtection

import sys
import getpass
from os.path import exists
import json
import datetime
from pytz import reference
import requests
import platform
import socket
import logging.handlers as handlers
import logging


logger = logging.getLogger('nicola')
logger.setLevel(logging.INFO)

now = datetime.datetime.now()
localtime = reference.LocalTimezone()
localtime.tzname(now)
ora = now.strftime("%Y-%m-%d_%H:%M_") + localtime.tzname(now)

output_file = "Create_JobList" + ora + ".json"
LOG_FILE = "CreateTampletes.log"
open(LOG_FILE, 'w').close()
logHandler = handlers.RotatingFileHandler(LOG_FILE, maxBytes=100000, backupCount=2, mode='w')
logHandler.setLevel(logging.INFO)
logger.addHandler(logHandler)

# EPNM Template names
templateName4Kend_A = "CREATE_PROT_ODU2E_4kendpoint_A"
templateName4Kend_Z = "CREATE_PROT_ODU2E_4kendpoint_Z"
templateName2Kend_A = "CREATE_PROT_ODU2E_2kendpoint_A"
templateName2Kend_Z = "CREATE_PROT_ODU2E_2kendpoint_Z"
templateName2Kmid = "CREATE_ODU2E_2kmidpoint"
templateName4Kmid = "CREATE_ODU2E_4kmidpoint"

# Device ID list file name
device_id_list = "deviceIDlist.json"

# Check if using python 3. If not 3, terminates execution
version=platform.python_version_tuple()
if version[0] != '3':
    print("This script requires Python3")
    exit(1)

logger.info("Python version is "+platform.python_version())

# Check if EPNM HTTPS port 443 (or other ports) is open
def isOpen(server_ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((server_ip, int(port)))
        s.shutdown(2)
        return True
    except:
        return False

# Check is HTTPS server is indeed an EPNM server
# This URL exists only for EPNM
# Get would return 404 (not found) if webeserver is not EPNM
def isEPNM(server_ip):
    url = 'https://' + server_ip + '/webacs/welcomeAction.do'
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        return True
    else:
        return False

# Check if provided EPNM username and pwd are valid
def isAccountValid(server_ip, user, pwd):
    url = 'https://' + server_ip + '/webacs/api/v4/data/Devices?.maxResults=1'
    response = requests.get(url, verify=False, auth=(user, pwd))
    if response.status_code == 401:  # Error code 401 = Unauthorized
        return False
    else:
        return True

# generates a list with all device names for midnodes on working and protected
# it returns empty = True if no node is found on working or protected midpoints list
def getMidNodeNameList(json_object, isWorking):
    empty = False
    nodeNameList = []
    if isWorking:
        node_list = json_object["service_instance"]["service_termination_points"]["midpoints_working"]
    else:
        node_list = json_object["service_instance"]["service_termination_points"]["midpoints_protected"]
    if len(node_list) == 0:
        empty = True
    else:
        for node in node_list:
            nodeName = node["node_name"]
            nodeNameList.append(nodeName)
    return empty, nodeNameList

# This function returns the the internal EPN-M node ID for a given node name in input
def getNodeID(nodeName,id_list):
    found = False
    for node in id_list:
        if found:
            break
        name = node["device_name"]
        if name == nodeName:
            found = True
            id = node["device_id"]
            logger.info("Found device ID for "+name+":"+str(id))
    return id

# This function gets service name and service ID from the input file
def get_service_name_plus_id(json_object):
    service_name = json_object["service_instance"]["service_details"]["service_name"]
    service_id = json_object["service_instance"]["service_details"]["service_id"]
    return service_name, service_id


#############################
###     MAIN
############################

if len(sys.argv)!=3:
  print('\nMust pass EPNM IP Address and service file name as script argument\n')
  exit()
scripts, epnm_ip, input_file = sys.argv

if not exists(input_file):
    print("\nFile",input_file,"not found\n")
    exit(1)

epnm_username = input("Enter Username: ")
epnm_password = getpass.getpass()

#############################
###     Basic controls
#############################

logger.info("Checking HTTPS Port 443")

# Check if https server is up and port 443 is reachable
if not isOpen(epnm_ip, 443):
    print("\nERROR: " + epnm_ip + " is not reachable, either the server is down or port 443 is filtered\n")
    exit()

logger.info("HTTPS Port 443 is Open")

# Check if https server is EPNM
logger.info("Checking if this is an EPNM Server")

if not isEPNM(epnm_ip):
    print("\nERROR: " + epnm_ip + " is not an EPN-M Server\n")
    exit()

logger.info("Control on EPNM Server passed")

# Check if account is valid
logger.info("Checking User Credentials")

if not isAccountValid(epnm_ip, epnm_username, epnm_password):
    print("\nERROR: Check if username and password are correct\n")
    exit()

logger.info("EPNM credentials are connect")

#############################
###    INPUT VALIDATION
#############################

try:
   f = open(input_file,'r')
except Exception as e:
    print ('\nFailed loading JSON input file')
    print (str(e))
    exit(1)
content_file = f.read()
f.close()
json_file = json.loads(content_file)
# json_file now contains a dict made of input file content

# Before using the JSON file content, we call runValidate() to make sure JSON content
# is valid and could be used
print("\nValidating input file")

# Checking if payload protection is "protected"

protection = getFileProtection(json_file)
if protection != "protected":
    print("\nERROR: Found unprotected service. Expected protected")
    print("Terminating execution\n")
    exit(1)

# runValidate() returns a boolean, master_control
# if validation passes, it will be True
master_control = runValidate(epnm_ip, epnm_username, epnm_password, json_file, protection)
if master_control:
   print("\nAll good. Validation passed")
else:
   print("\nPlease fix ERRORS and retry\n")
   print("Terminating script execution\n")
   exit(1)

# deviceIDlist.json file is a must have
# it contains the full list (in JSON) of device name and device node_ID
# If not present, exit
logger.info("Importing device ID list JSON file")

if not exists(device_id_list):
    print("\nFile",device_id_list,"not found")
    print('Please execute getDeviceID.py\n')
    exit(1)

# If file cannot be open, exit
try:
   f = open(device_id_list,'r')
except Exception as e:
    print ('\nFailed loading device ID list JSON file')
    print (str(e))
    print('\nPlease execute getDeviceID.py')
    exit(1)
device_ids=json.load(f)
f.close ()
# device_ids  now contains a dict made of device name and device ID

logger.info("Device ID list JSON file imported")

#############################
#           CORE
#############################

# Getting service name and service ID
service_name, service_id = get_service_name_plus_id(json_file)  # input file can be changed to json_file

# following should be easy to understand
a_end_node = json_file["service_instance"]["service_termination_points"]["A_endpoint"]
z_end_node = json_file["service_instance"]["service_termination_points"]["Z_endpoint"]
a_end_node_type = a_end_node["node_type"]
z_end_node_type = z_end_node["node_type"]
a_end_node_name = a_end_node["node_name"]
z_end_node_name = z_end_node["node_name"]
deviceID_a_end = getNodeID(a_end_node_name, device_ids)
deviceID_z_end = getNodeID(z_end_node_name, device_ids)

# This script generates an output file (in JSON) made of all EPNM jobs created by EPNM
# templates in a list format
# Initializing the list
outputList = []

print("\nTemplates deployment starts")
## using input_file for functions on other python files and json_file for internal functions
## This helps on testing. Can be changed to json_file at the end

# This is the core where templates get executed
# Different templates and different sets of parameters are required depending on following use cases:
#   the device is an A end
#   the device is a Z end
#   the device is part of working or protected paths
#   the device is 2K or 4K

# In following lines:
# Source ID is key component of each templates. It identifies the TL1 ID for the source node
#   for 2K, that's retrieved by get_TL1_NodeID()
#   for 4K, being not a TL1 device, a dedicated function is used to generate one. get4K_nodeID()
#
# Each template requires a paramList. For each use case (described before) a different createPayload function
# is used.
# createPayload functions will use
#       input_file (could use json_file to reduce # file access)
#       service name
#       service id
#       source id
#
# executeTemplate() uses following (regardless of the use case)
#       EPNM server ip and credentials
#       Node name
#       Node ID (EPNM internal)
#       template name (one from EPNM Template names list at the beginning)
#       template paramList
# executeTemplate() returns a job details and execution status
# job details will be part of the output file

#### A-End

if a_end_node_type == "4K":
    print("\nDeploy template on A endpoint", a_end_node_name)
    sourceNodeID = get4K_nodeID(a_end_node_name, epnm_ip, epnm_username, epnm_password)
    paramListAend = createPayload_4K_End(input_file, service_name, service_id, sourceNodeID, "A-End", "protected")
    status, jobDetails = executeTemplate(epnm_ip, epnm_username, epnm_password, a_end_node_name, deviceID_a_end,
                                         templateName4Kend_A, paramListAend)
    if not status:
        print("ERROR: cannot deploy template ", templateName4Kend_A, "on device", a_end_node_name)
        print("Terminating script execution")
        print("Check logs for more")
        exit(1)

    outputList.append(jobDetails)

if a_end_node_type == "2K":
    print("\nDeploy template on A endpoint", a_end_node_name)
    sourceNodeID = get_TL1_NodeID(a_end_node_name, epnm_ip)
    paramListAend = createPayload2Kend(input_file, service_name, service_id, sourceNodeID, "A-End", "protected",
                                       epnm_ip, epnm_username, epnm_password)
    status, jobDetails = executeTemplate(epnm_ip, epnm_username, epnm_password, a_end_node_name, deviceID_a_end,
                                         templateName2Kend_A, paramListAend)
    if not status:
        print("ERROR: cannot deploy template ", templateName2Kend_A, "on device", a_end_node_name)
        print("Terminating script execution")
        print("Check logs for more")
        exit(1)

    outputList.append(jobDetails)

#### Z-End

if z_end_node_type == "2K":
    print("\nDeploy template on Z endpoint", z_end_node_name)
    paramListZend = createPayload2Kend(input_file, service_name, service_id, sourceNodeID, "Z-End", "protected",
                                         epnm_ip, epnm_username, epnm_password)  # Keep input_file for now

    status, jobDetails = executeTemplate(epnm_ip, epnm_username, epnm_password, z_end_node_name, deviceID_z_end,
                                         templateName2Kend_Z, paramListZend)
    if not status:
        print("ERROR: cannot deploy template ", templateName2Kend_Z, "on device", z_end_node_name)
        print("Terminating script execution")
        print("Check logs for more")
        exit(1)
    outputList.append(jobDetails)

if z_end_node_type == "4K":
    print("\nDeploy template on Z endpoint", z_end_node_name)
    paramListZend = createPayload_4K_End(input_file, service_name, service_id, sourceNodeID,"Z-End", "protected")

    status, jobDetails = executeTemplate(epnm_ip, epnm_username, epnm_password, z_end_node_name, deviceID_z_end,
                                         templateName4Kend_Z, paramListZend)
    if not status:
        print("ERROR: cannot deploy template ", templateName4Kend_Z, "on device", z_end_node_name)
        print("Terminating script execution")
        print("Check logs for more")
        exit(1)
    outputList.append(jobDetails)


#### Working and Protected Path

# For Working and Protected paths, building blocks are the same as before
# executeTemplate function works same as before
# what changes here is what createPayload() generates and how is used
# In this case, function generates a paramList that is a bi-dimensional list.
#       First hierarchical level contains one list for each midnode.
#       Second level contains the param list for any given midnode
# createPayload() also creates a list containing node types only
# We will also be using an additional list containing device names. When executing
# the "for node" loop, for each node all lists (nodename, nodetype and paramList)
# will be be pointing to same device

for isWorking in (True, False):  # This way I can define one loop for both paths

    missing_string = "working"  # this is used only for the print below. Nothing else
    if not isWorking:
        missing_string = "protected"
    print("\nDeploy template on", missing_string, "route")

    # if no midnode is found in working or protected path, getMidNodeNameList will return empty = True
    # if not empty, getMidNodeNameList will return a list of node names
    empty, nodenames = getMidNodeNameList(json_file, isWorking)

    if not empty:
        numnodes = len(nodenames)
        print("\nFound", numnodes, "nodes on", missing_string, "path")

        nodeTypeList, paramslist = createPayloadMid(input_file, service_name, service_id, sourceNodeID, isWorking)

        for node in range(0, numnodes):
            deviceNameMid = nodenames[node]
            nodeType = nodeTypeList[node]
            paramListMid = paramslist[node]
            deviceIDmid = getNodeID(deviceNameMid, device_ids)
            print("Deploy template on node", str(node+1) + ":", deviceNameMid)

            if nodeType == "2K":
                status, jobDetails = executeTemplate(epnm_ip, epnm_username, epnm_password, deviceNameMid, deviceIDmid,
                                                     templateName2Kmid, paramListMid)
                if not status:
                    print("ERROR: cannot deploy template ", templateName2Kmid, "on device", deviceNameMid)
                    print("Terminating script execution")
                    print("Check logs for more")
                    exit(1)

            if nodeType == "4K":
                status, jobDetails = executeTemplate(epnm_ip, epnm_username, epnm_password, deviceNameMid, deviceIDmid,
                                                     templateName4Kmid, paramListMid)
                if not status:
                    print("ERROR: cannot deploy template ", templateName4Kmid, "on device", deviceNameMid)
                    print("Terminating script execution")
                    print("Check logs for more")
                    exit(1)

            outputList.append(jobDetails)

        logger.info("\nDumping JSON array to output file\n")
        f = open(output_file, 'w')
        json.dump(outputList, f)
        f.close()
    else:
        print("\nWarning: No mid nodes found on", missing_string, "route !!!!!")

print("\nOutput File:", output_file)
print("Please execute - python jobHistory.py", epnm_ip, output_file, "- to check results\n")

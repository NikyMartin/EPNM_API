#!/usr/bin/python3

"""

    This script uses REST to extract following inventory details from EPN-M
      - Module Name
      - Module Description
      - Module Type
      - Serial Number
      - Product ID

    Created by:
    Nicola Martino, nmartino@cisco.com

    March 8th, 2020
      - First release

"""

import os
import requests
import sys
import getpass
import urllib3
import json
import signal
from os.path import exists
from tabulate import tabulate

from commonControls import isOpen, isEPNM, isAccountValid, isNodeValid, getHeaders, getNodeID, getNodeFamily

signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

device_id_list = "deviceIDlist.json"

############
#   Main
############

if __name__ == '__main__':

### Check if I EPN-M IP address has been passed as input parameters

    if len(sys.argv)!=3:
       print('\nMust pass EPN-M IP address and device name as script arguments\n')
       exit()
    scripts, server_ip, node_name = sys.argv

### Basic controls

# Check if https server is up and port 443 is reachable

    if not isOpen(server_ip, 443):
        print("\nERROR: " + server_ip + " is not reachable, either the server is down or port 443 is filtered\n")
        exit()

# Check if https server is EPNM

    if not isEPNM(server_ip):
        print("\nERROR: " + server_ip + " is not an EPN-M Server\n")
        exit()

# Check if account is correct

    username = input("Enter Username: ")
    password = getpass.getpass()

    if not isAccountValid(server_ip, username, password):
        print("\nERROR: Check if username and password are correct\n")
        exit()

    if not isNodeValid(server_ip, username, password, node_name):
        print("\nERROR: node", node_name, "not found\n")
        exit()

    if not exists(device_id_list):
        print("\nFile", device_id_list, "not found")
        print('Please execute getDeviceID.py\n')
        exit(1)

    # If file cannot be open, exit
    try:
        f = open(device_id_list, 'r')
    except Exception as e:
        print('\nFailed loading device ID list JSON file')
        print(str(e))
        print('\nPlease execute getDeviceID.py')
        exit(1)
    device_ids = json.load(f)
    f.close()

# Execution

    os.system('clear')
    deviceID = getNodeID(node_name, device_ids)
    url = 'https://'+server_ip+'/webacs/api/v4/data/InventoryDetails/'+str(deviceID)
    response = requests.get(url,  headers=getHeaders(), verify=False, auth=(username, password))
    if response.status_code != 200:
       print ("HTTP ERROR "+str(response.status_code))
       exit()

    unformatted = response.text
    parsed = json.loads(unformatted)
    module_list = parsed["queryResponse"]["entity"][0]["inventoryDetailsDTO"]["modules"]["module"]

    module_list_output=[]
    for module in module_list:
        try:
            module_name = module["productName"]
        except:
            module_name= ""
        try:
            module_description = module["description"]
        except:
            module_description = ""
        try:
            module_type = module["equipmentType"]
        except:
            module_type = ""
        try:
            module_productId = module["productId"]
        except:
            module_productId = ""
        try:
            module_serialNr = module["serialNr"]
        except:
            module_serialNr = ""

        entry = (module_name, module_description, module_type,
                 module_serialNr,module_productId)
        module_list_output.append(entry)

    print(tabulate(module_list_output, headers=(['Name', 'Description', 'Module Type',
                                                         'Serial NB', 'Product ID'])))


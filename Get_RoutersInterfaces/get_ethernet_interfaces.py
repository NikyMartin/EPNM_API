#!/usr/bin/python3

"""

    This script uses REST to extract following details from ethernet interfaces
      - Interface Name
      - Interface Description
      - Admin State
      - Operational State

    This script only runs for devices in the "Routers" product family

    Created by:
    Nicola Martino, nmartino@cisco.com

    October 5th, 2022
      - Initial release

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

    nodeFamily = getNodeFamily(server_ip, username, password, node_name)
    if nodeFamily != "Routers":
        print("\nERROR: node", node_name, "belongs to", nodeFamily, "product family")
        print("It must be a router\n")
        exit(1)

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
    try:
        interface_list = parsed["queryResponse"]["entity"][0]["inventoryDetailsDTO"]["ethernetInterfaces"]["ethernetInterface"]
    except:
        print("ERROR: Could not locate ethernetInterface")
        exit(1)

    interface_list_output = []
    for interface in interface_list:
        try:
            interface_name = interface["name"]
        except:
            interface_name= ""
        try:
            interface_description = interface["description"]
        except:
            interface_description = ""
        try:
            interface_adminStatus = interface["adminStatus"]
        except:
            interface_adminStatus = ""
        try:
            interface_operationalStatus = interface["operationalStatus"]
        except:
            interface_operationalStatus = ""

        entry = (interface_name, interface_description, interface_adminStatus, interface_operationalStatus)
        interface_list_output.append(entry)

    print(tabulate(sorted(interface_list_output), headers=(['Name', 'Description', 'Admin Status', 'Op Status'])))
# output is ordered on "Name" column. Remove sorted() for unordered output


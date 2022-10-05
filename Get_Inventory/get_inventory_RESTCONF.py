#!/usr/bin/python3

"""
    This script uses REST to extract following inventory details from EPN-M
      - Interface Name
      - Interface Description
      - Module Type
      - Part Number
      - Serial Number
      - Product ID

    Created by:
    Nicola Martino, nmartino@cisco.com

    September 22nd, 2020
      - First release

    October 03, 2022
      - Converted from using ET to JSON

    October 05, 2022
      - Moved Common controls on a different file
      - Added more controls

"""

import requests
import sys
import getpass
import json
from tabulate import tabulate
import urllib3

from commonControls import isOpen, isEPNM, isAccountValid, sendGET, isNodeValid, getHeaders

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def getNode(server_ip, user, pwd, node_name):
    nd_fdn = 'MD=CISCO_EPNM!ND=' + node_name
    url = 'https://' + server_ip + '/restconf/data/v1/cisco-resource-physical:node?fdn=' + nd_fdn
    status, resp = sendGET(url, user, pwd)
    if not status:
        print("ERROR: It was not possible to run execute GET node")
        print("Server returned :",resp.status_code)
        exit(1)
    else:
        return resp


############
#   Main
############

if __name__ == '__main__':

### Check if IP address and port have been passed as input parameters
    if len(sys.argv)!=3:
       print('\nMust pass device IP address and device name as script arguments\n')
       exit()
    scripts, server_ip, node_name = sys.argv

# Check if https server is up and port 443 is reachable

    if not isOpen(server_ip, 443):
        print("\nERROR: " + server_ip + " is not reachable, either the server is down or port 443 is filtered\n")
        exit()

# Check if https server is EPNM

    if not isEPNM(server_ip):
        print("\nERROR: " + server_ip + " is not an EPN-M Server\n")
        exit()

    username = input("Enter Device Username: ")
    password = getpass.getpass()

    if not isAccountValid(server_ip, username, password):
        print("\nERROR: Check if username and password are correct\n")
        exit()

    if not isNodeValid(server_ip, username, password, node_name):
        print("\nERROR: node", node_name, "not found\n")
        exit()

    node = json.loads(getNode(server_ip, username, password, node_name))

    try:
        equipment_list = node['com.response-message']['com.data']['nd.node'][0]['nd.equipment-list']['eq.equipment']
    except:
        print("Could not find equipment-list")
        exit(1)

    list = []
    for equipment in equipment_list:

        try:
            part_number = equipment['eq.part-number']
        except:
            part_number = ""

        try:
            product_id = equipment['eq.product-id']
        except:
            product_id = ""

        try:
            serial_number = equipment['eq.serial-number']
        except:
            serial_number = ""

        entry = (equipment['fdtn.name'], equipment['fdtn.description'], equipment['eq.equipment-type'],
                 part_number, serial_number, product_id)
        list.append(entry)

    print(tabulate(list, headers=(['Name', 'Description', 'Type', 'PartNumber', 'SerialNumber', 'ProductID'])))
# output table might get ordered with
#   print(tabulate(ordered(list), headers=(['Name', 'Description', 'Type', 'PartNumber', 'SerialNumber', 'ProductID'])))

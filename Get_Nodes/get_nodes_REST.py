#!/usr/bin/python3

"""

    This script uses REST to extract following node details from EPNM
          - Device ID
          - Device IP Address
          - Device Name
          - Device Type
          - Device Collection Status

    March 8th, 2020
    Created by:
    Nicola Martino, nmartino@cisco.com

    September 7th, 2021
    Rev2: Added print in tabular format

    January 31st, 2022
    Rev3: Added control on device count = 0

    July 28th, 2022
    Rev4:
        converted output in a list before printing
        introduced tabulate to create a tabular output
        added a progress counter

"""

import os
import socket
import requests
import sys
import getpass
import urllib3
import json
import signal
from tabulate import tabulate


signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

### Check if I EPN-M IP address and device name been passed as input parameters
if len(sys.argv)!=2:
   print('\nMust pass EPN-M IP address as script argument\n')
   exit()
scripts, server_ip = sys.argv

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

def extract_node_data(payload):
    base = payload["queryResponse"]["entity"][0]["devicesDTO"]
    if base["adminStatus"] == 'UNMANAGED':
        node_data = [base["@id"], base["ipAddress"], '', '', base["collectionStatus"]]
    else:
        node_data = [base["@id"], base["ipAddress"], base["deviceName"], base["deviceType"], base["collectionStatus"]]
    return node_data

############
#   Main
############

if __name__ == '__main__':

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

# Execution

    os.system('clear')
    print ("\nPlease wait. It can take a while.\n")

    headers = {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

    url = 'https://'+server_ip+'/webacs/api/v4/data/Devices'
    response = requests.get(url,  headers=headers, verify=False, auth=(username, password))
    # print response.status_code
    if response.status_code != 200:
       print ("HTTP ERROR "+str(response.status_code))
       exit()

    unformatted = response.text

    parsed = json.loads(unformatted)

    nodes_lenght = parsed["queryResponse"]["@count"]
    if nodes_lenght == 0:
       print("No device found\n")
       exit()

    print('Found',nodes_lenght,'nodes\n')

    nodes_link_list=parsed["queryResponse"]["entityId"]

    node_list = []
    counter = 0
    for index1 in nodes_link_list:
        counter = counter +1
        print(' Node', counter, end = "\r")
        node_details_link = index1["@url"]
        node_details = requests.get(node_details_link,  headers=headers, verify=False, auth=(username, password))
        node_details_unformatted = node_details.text
        node_details_parsed = json.loads(node_details_unformatted)
        node_data = extract_node_data(node_details_parsed)
        node_list.append(node_data)

    print(tabulate(node_list, headers=(['Device ID', 'Device IP Address', 'Device Name', 'Device Type', 'Device Collection Status'])))

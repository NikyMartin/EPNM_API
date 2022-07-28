#!/usr/bin/python3

"""

    This script uses REST to extract following node details from EPNM
          - Device IP Address
          - Device Name
          - Device Type
          - Device Collection Status

    September 22nd, 2020
    Created by:
    Nicola Martino, nmartino@cisco.com

    October 14th, 2020
    Rev2: Added control when device list is > 100

    September 7th, 2021
    Rev3: Added control in case device is unreachable and has no name ("nd.name")
          Added platform type and print in tabular format

    July 28th, 2022
    Rev4: Converted output in a list before printing
          introduced tabulate to create a tabular output

"""

import os
import requests
import socket
import sys
import getpass
import urllib3
import signal
from tabulate import tabulate

signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import json

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


############
#   Main
############

if __name__ == '__main__':

### Check if I EPN-M IP address has been passed as input parameters

    if len(sys.argv)!=2:
       print('\nMust pass EPN-M IP address as script argument\n')
       exit()
    scripts, server_ip = sys.argv

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

# execution

    os.system('clear')
    print("\nPlease wait. It can take a while.\n")

    headers = {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

    last_index = 0
    page = 0
    node_list = []

    while (page - last_index < 2 ):
          url = 'https://'+server_ip+'/restconf/data/v1/cisco-resource-physical:node?.depth=1&.startIndex='+str(page)
          response = requests.get(url, headers=headers, verify=False, auth=(username, password))
          page = page +100
          unformatted = response.text
          parsed = json.loads(unformatted)
          last_index = parsed["com.response-message"]["com.header"]["com.lastIndex"]
          nodes = parsed["com.response-message"]["com.data"]["nd.node"]
          for index1 in nodes:
              if "nd.name" in index1:
                  node_name = index1["nd.name"]
              else:
                  node_name = ''
              node_list.append([index1["nd.management-address"], index1["nd.name"], index1["nd.product-type"],
                                index1["nd.lifecycle-state"]])

          print("\nLast Index: "+str(last_index))

          if (page - last_index < 2):
             print("Please Wait. More coming.\n")
          else:
             print("Process Complete\n")

          print(tabulate(node_list, headers=(['Device IP Address', 'Device Name', 'Device Type', 'Collection Status',
                                              'Lifecycle State'])))


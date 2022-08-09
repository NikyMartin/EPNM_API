#!/usr/bin/python3

"""
    October 5th, 2020
    Created by:
    Nicola Martino, nmartino@cisco.com

    Aug 9th, 2022
    Rev1: Changed output parsing
    from:
        node = parsed["com.response-message"]["com.data"][0]["nd.node"][0]
    to:
        node = parsed["com.response-message"]["com.data"]["nd.node"][0]

"""

import requests
import sys
import getpass
import urllib3
import socket
import json
import re
import signal

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))

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

### Check if I EPN-M IP address and device name been passed as input parameters

    if len(sys.argv)!=3:
       print('\nMust pass EPN-M IP address and device name as script arguments\n')
       exit()
    scripts, server_ip, device_name = sys.argv

### Basic controls

# Check if https server is up and port 443 is reachable

    if not isOpen(server_ip,443):
       print('\nERROR: "+server_ip+" is not reachable, either the server is down or port 443 is filtered\n')
       exit()

# Check if https server is EPNM

    if not isEPNM(server_ip):
       print('\nERROR: "+server_ip+" is not an EPN-M Server\n')
       exit()

# Check if account is correct

    username = input("Enter Username: ")
    password = getpass.getpass()

    if not isAccountValid(server_ip,username,password):
        print('\nERROR: Check if username and password are correct\n')
        exit()

### Execution

    headers = {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

    params = (
        ('fdn', 'MD=CISCO_EPNM!ND='+device_name),
    )

    response = requests.get('https://'+server_ip+'/restconf/data/v1/cisco-resource-physical:node',  headers=headers, params=params, verify=False, auth=(username, password))
    if response.status_code != 200:
       print('HTTP ERROR '+str(response.status_code))
       exit()

    unformatted = response.text
    parsed = json.loads(unformatted)

    if parsed["com.response-message"]["com.header"]["com.lastIndex"] == -1:
       print('\nEmpty reply (Got -1 as lastIndex)\n')
       exit()

    try:
        # Next is the previous code. Supposed to be originally working
        #  node = parsed["com.response-message"]["com.data"][0]["nd.node"][0]
        node = parsed["com.response-message"]["com.data"]["nd.node"][0]
    except:
        print('ERROR: Cannot parse output and find this')
        print('["com.response-message"]["com.data"]["nd.node"][0]\n')
        print(json.dumps(parsed, indent=4))
        exit(1)

    print('\nNode '+device_name+' belongs to following groups:\n')

    list = node["nd.group"]
    for index in list:
       group = re.search(r'GR=(?P<group>.*)',index)
       if group:
          print(group.group('group'))

#!/usr/bin/python2

"""
    March 5th, 2021
    Created by:
    Nicola Martino, nmartino@cisco.com

    Aug 9th, 2022
    Rev4: Minor changes

"""

import os
import requests
import sys
import socket
import getpass
import urllib3
import signal
import json

signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def print_app_options():
    os.system('clear')

    print("""
    
    Application List

   1 - NCS
   2 - Prime Infrastructure
   3 - EPNM
   4 - Evolved Programmable Network Manager
   5 - Service Provisioning
   6 - Discovery
   0 - Exit

    """)

def print_cat_options():
    os.system('clear')

    print("""
    
    Category List                       Associated Applications

   0 -  All
   1 -  ADMIN				NCS, Prime Infrastructure, Evolved Programmable Network Manager
   2 -  User Management			Evolved Programmable Network Manager
   3 -  PROVISIONING			Service Provisioning
   4 -  Device Management		NCS, Prime Infrastructure, Evolved Programmable Network Manager
   5 -  Grouping			Prime Infrastructure
   6 -  MONITOR CONFIGURATION		NCS
   7 -  Job Management			NCS
   8 -  Software-Update			
   9 -  SYSTEM				Evolved Programmable Network Manager
   10 - CONFIG				NCS
   11 - Service Discovery		Discovery
   12 - Device Console			EPNM	
   13 - Configuration Archive		Evolved Programmable Network Manager
   14 - Virtual Domain
   15 - Software Image Management       (No app found)
   16 - Report				Prime Infrastructure
   17 - RESTCONF			Evolved Programmable Network Manager

    """)

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

def run_query(url):

   headers = {
     'Accept': 'application/json',
     'Cache-Control': 'no-cache',
     'Content-Type': 'application/json',
   }

   os.system('clear')
   print('\nPlease wait. It can take a while.\n')

   last_index = 0
   page = 0

   while (page - last_index < 2 ):
      newurl = url+'&.startIndex='+str(page)
#      print(newurl)
      response = requests.get(newurl, headers=headers, verify=False, auth=(username, password))
      if response.status_code != 200:
        print('HTTP ERROR ')+str(response.status_code)
        exit()
      page = page +100
      unformatted = response.text
      parsed = json.loads(unformatted)
      last_index = parsed["com.response-message"]["com.header"]["com.lastIndex"]
      output = parsed["com.response-message"]["com.data"]["audit-log.audit-log"]
#      print(json.dumps(parsed, indent=4))
      print(json.dumps(output, indent=4))
      print('\nLast Index: '+str(last_index))
      if (page - last_index < 2):
         print('Please Wait. More coming.\n')
      else:
         print('Output Complete\n')

############
#   Main
############

if __name__ == '__main__':

### Basic controls

### Check if IP address and port have been passed as input parameters

    if len(sys.argv)!=2:
      print('\nMust pass EPN-M IP address as script argument\n')
      exit()
    scripts, server_ip = sys.argv

# Check if https server is up and port 443 is reachable

    if not isOpen(server_ip,443):
       print('\nERROR: '+server_ip+' is not reachable, either the server is down or port 443 is filtered\n')
       exit()

# Check if https server is EPNM

    if not isEPNM(server_ip):
       print('\nERROR: '+server_ip+' is not an EPN-M Server\n')
       exit()

# Check if account is correct

    username = input("Enter Username: ")
    password = getpass.getpass()

    if not isAccountValid(server_ip,username,password):
        print
        '\nERROR: Check if username and password are correct\n'
        exit()

### Execution

    app_names=["","NCS","Prime Infrastructure","EPNM","Evolved Programmable Network Manager","Service Provisioning",
               "Discovery"]
    category_names=["All","ADMIN","User Management","PROVISIONING","Device Management","Grouping","MONITOR CONFIGURATION",
                    "Job Management","Software-Update","SYSTEM","CONFIG","Service Discovery","Device Console",
                    "Configuration Archive","Virtual Domain","Software Image Management","Report","RESTCONF"]

    scelta_app = -1
    while scelta_app != 0:
          print_app_options()
          scelta_app = int(input("Select application - 0 or ^C to exit > "))

          if scelta_app in range(7):
            if scelta_app == 0:
               exit()
            else:
               app_name=app_names[scelta_app]
               scelta_category = -1
               while not (scelta_category in range(17)):
                  print_cat_options()
                  scelta_category  = int(input("Select category - 0 for All, ^C to exit > "))
                  if scelta_category in range(18):
                     if scelta_category == 0:
                        url='https://'+server_ip+'/restconf/data/v1/cisco-audit:audit-log?appname='+app_name
                     else:
                        category_name=category_names[scelta_category]
                        url='https://'+server_ip+'/restconf/data/v1/cisco-audit:audit-log?appname='+app_name+'&category='+category_name
#                     print(url)
                     run_query(url)
                  else:
                     print ("\n" + "Invalid option")
                     print ("\n" + "Press ENTER")
                     input()
               exit()


          else:
            print ("\n" + "Invalid option")

          print ("\n" + "Press ENTER")
          input()

#!/usr/bin/python

import sys
import getpass
import json
import datetime
from pytz import reference
import requests
import socket
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import logging

logger = logging.getLogger('nicola')
logger.setLevel(logging.INFO)

now = datetime.datetime.now()
localtime = reference.LocalTimezone()
localtime.tzname(now)
ora = now.strftime("%Y-%m-%d_%H:%M_") + localtime.tzname(now)

output_file = "deviceIDlist.json"

def isOpen(server_ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((server_ip, int(port)))
        s.shutdown(2)
        return True
    except:
        return False


def isEPNM(server_ip):
    url = 'https://' + server_ip + '/webacs/welcomeAction.do'
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        return True
    else:
        return False


def isAccountValid(server_ip, user, pwd):
    url = 'https://' + server_ip + '/webacs/api/v4/data/Devices?.maxResults=1'
    response = requests.get(url, verify=False, auth=(user, pwd))
    if response.status_code == 401:  # Error code 401 = Unauthorized
        return False
    else:
        return True

def getHeaders():
    headers = {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }
    return headers

def sendGET(url,user,pwd):
    logger.info("Sending GET "+url)
    response = requests.get(url, headers=getHeaders(), verify=False, auth=(user, pwd))
    if response.status_code != 200:
        error_message = json.loads(response._content.decode())["errorDocument"]["message"]
        logger.info(json.dumps(error_message, indent =4))
        return (False,response.status_code)
    else:
       return (True,response.text)

def getDeviceID(server_ip,user,pwd):
    print("\nDumping device name and ID to a list\n")

    deviceIDlist = []

    last_index = 0
    page = 0

    while page - last_index < 2:
        if page == 0:
            url = 'https://' + server_ip + '/webacs/api/v4/data/Devices'
        else:
            url = 'https://' + server_ip + '/webacs/api/v4/data/Devices.firstResult=' + str(page)

        status, resp = sendGET(url,user,pwd)
        last_index = json.loads(resp)["queryResponse"]["@last"]
        print('Total device count is:', last_index+1)

        if not status:
            print("ERROR: It was not possible to run execute GET node")
            print("Server returned :",resp.status_code)
            exit(1)
        else:
            if json.loads(resp)["queryResponse"]["@count"] == 0:
                print("ERROR: Strange .... GET devices is an empty list")
                exit(1)
            nodes_list = json.loads(resp)["queryResponse"]["entityId"]
            for node in nodes_list:
                node_details_link = node["@url"]
                status, resp = sendGET(node_details_link,user,pwd)
                if not status:
                    print("ERROR: It was not possible to run execute GET node details")
                    print("Server returned Error",resp.status_code)
                    exit(1)
                else:
                    node_details = json.loads(resp)["queryResponse"]["entity"][0]["devicesDTO"]
                    id = node_details["@id"]
                    name = node_details["deviceName"]
                    logger.info(str(id)+" "+name)
                    node = ({
                            "device_name": name,
                            "device_id": id
                        })
                    deviceIDlist.append(node)

        page = page + 100

        print('\nOutput File Entries:', len(deviceIDlist))

    return deviceIDlist


#############################
### MAIN
#############################

if __name__ == '__main__':

    if len(sys.argv)!=2:
      print('\nMust pass EPNM IP as script argument\n')
      exit()
    scripts, epnm_ip = sys.argv

    epnm_username = input("Enter Username: ")
    epnm_password = getpass.getpass()

##################
### Basic controls
##################

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

    # Check if account is correct

    logger.info("Checking User Credentials")

    if not isAccountValid(epnm_ip, epnm_username, epnm_password):
        print("\nERROR: Check if username and password are correct\n")
        exit()

    logger.info("EPNM credentials are connect")

    outputlist = getDeviceID(epnm_ip,epnm_username,epnm_password)

    f = open(output_file, 'w')
    json.dump(outputlist, f)
    f.close()

    print("\nGenerated output file:", output_file)
#!/usr/bin/python3

"""
    This script uses REST to retrieve device name and device ID from EPN-M
    and store them on a json file "deviceIDlist.json"

    Created by:
    Nicola Martino, nmartino@cisco.com

    March 08th, 2022
    Original version

    October 05th, 2022
        - Moved Common Controls on a dedicated file
        - Fixed paging
        - Added inline progress counter

"""
import sys
import getpass
import json
import datetime
from pytz import reference
import urllib3
import logging
import signal

from commonControls import isOpen, isEPNM, isAccountValid, sendGET

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))

logger = logging.getLogger('nicola')
logger.setLevel(logging.INFO)

now = datetime.datetime.now()
localtime = reference.LocalTimezone()
localtime.tzname(now)
ora = now.strftime("%Y-%m-%d_%H:%M_") + localtime.tzname(now)

output_file = "deviceIDlist.json"

def getDeviceID(server_ip,user,pwd):
    print("\nDumping device name and ID to a list\n")

    deviceIDlist = []

    last_index = 0
    page = 0

    while page - last_index < 2:

        url = 'https://' + server_ip + '/webacs/api/v4/data/Devices?.firstResult=' + str(page)

        status, resp = sendGET(url,user,pwd)

        # If status = False, resp is the error code. If true is the actual reply

        if not status:
            print("ERROR: It was not possible to run execute GET node")
            print("Server returned :",resp)
            exit(1)
        else:
            tot_device_count = json.loads(resp)["queryResponse"]["@last"]
            print('Total device count is:', tot_device_count + 1)
            if json.loads(resp)["queryResponse"]["@count"] == 0:
                print("ERROR: Strange .... GET devices is an empty list")
                exit(1)
            nodes_list = json.loads(resp)["queryResponse"]["entityId"]
            counter = 0
            for node in nodes_list:
                counter +=1
                print(' Node', counter, end="\r")
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

        page += 100

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
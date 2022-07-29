#!/usr/bin/python

"""

    This script uses RESTCONF API to retrieve all TP from a given node

    Created by:
    Nicola Martino, nmartino@cisco.com

    May 6th, 2022
    Initial version

"""

import json
import requests
import urllib3
import socket
import sys
import getpass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def isOpen(server_ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#    socket.setdefaulttimeout(5)      # cant make it working
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

def getLastIndex(payload):
    try:
       lastIndex=json.loads(payload)['com.response-message']['com.header']['com.lastIndex']
    except Exception as e:
        exit(1)
    return lastIndex

def isNodeValid(server_ip,user,pwd,node_name):
    nd_fdn = 'MD=CISCO_EPNM!ND='+node_name
    url = 'https://'+server_ip+'/restconf/data/v1/cisco-resource-physical:node?fdn='+nd_fdn
    status, resp = sendGET(url,user,pwd)
    if not status:
        print("ERROR: It was not possible to run execute GET node")
        print("Server returned :",resp.status_code)
        exit(1)
    else:
        if getLastIndex(resp) == 0:
            return True
        else:
            return False

def getHeaders():
    headers = {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }
    return headers

def sendGET(url, user, pwd):
    response = requests.get(url, headers=getHeaders(), verify=False, auth=(user, pwd))
    if response.status_code != 200:
        error_message = json.loads(response._content.decode())["errorDocument"]["message"]
        print(json.dumps(error_message, indent=4))
        return (False, response.status_code)
    else:
        return (True, response.text)

def get_all_tp(urlpassed,user,pwd):
    last_index = 0
    page = 0

    while (page - last_index < 2):
        if page != 0:
            url = urlpassed+'&.startIndex='+str(page)
        else:
            url = urlpassed

        status, resp = sendGET(url, user, pwd)
        if not status:
            print("ERROR: It was not possible to run execute GET operation")
            print("Server returned Error", resp)
            exit(1)
        else:
            message = json.loads(resp)
            tp_list = message["com.response-message"]["com.data"]["tp.termination-point"]
            for tp in tp_list:
                print(tp["tp.fdn"])

        page = page + 100
        last_index = message["com.response-message"]["com.header"]["com.lastIndex"]
        print("\nLast Index: " + str(last_index))
        if (page - last_index < 2):
            print("Please Wait. More coming.\n")
        else:
            print("Output Complete\n")

############
#   Main
############

if __name__ == '__main__':

    if len(sys.argv)!=2:
       print('\nMust pass EPN-M IP address as script argument\n')
       exit()
    scripts, server_ip, = sys.argv

    if not isOpen(server_ip, 443):
        print("\nERROR: " + server_ip + " is not reachable, either the server is down or port 443 is filtered\n")
        exit()

    if not isEPNM(server_ip):
        print("\nERROR: " + server_ip + " is not an EPN-M Server\n")
        exit()

    username = input("\nEnter Username: ")
    password = getpass.getpass()
    nodeName = input("\nEnter Node Name: ")

    if not isAccountValid(server_ip, username, password):
        print("\nERROR: Check if username and password are correct\n")
        exit()

    if not isNodeValid(server_ip, username, password, nodeName):
        print('\nERROR: ' + nodeName, 'is not found in EPN-M inventory\n')
        exit()

    url = 'https://'+server_ip+'/restconf/data/v1/cisco-resource-ems:termination-point?ndFdn=MD=CISCO_EPNM!ND='+nodeName
    get_all_tp(url, username, password)

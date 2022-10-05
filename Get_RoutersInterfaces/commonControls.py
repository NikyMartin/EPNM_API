#!/usr/bin/python3

"""

    Set of EPN-M Common Functions:
          - Check if HTTPS server port is open
          - Check if HTTPS server is EPN-M
          - Check if user account is correct
          - Check if device exists in EPN-M
          - Return lastIndex
          - Return headers
          - Return nodeID
          - Return node family
          - Execute GET

    Created by:
    Nicola Martino, nmartino@cisco.com

    March 08th, 2022
    Original version

    October 05th, 2022
        - Added "Return node family"
        - Improved "Return nodeID"

"""

import socket
import requests
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

def getLastIndex(payload):
    try:
       lastIndex=json.loads(payload)['com.response-message']['com.header']['com.lastIndex']
    except Exception as e:
        exit(1)
    return lastIndex

def getHeaders():
    headers = {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }
    return headers

def sendGET(url,user,pwd):
    response = requests.get(url, headers=getHeaders(), verify=False, auth=(user, pwd))
    if response.status_code != 200:
        error_message = json.loads(response._content.decode())["errorDocument"]["message"]
        return False, response.status_code
    else:
        return True, response.text

def isNodeValid(server_ip, user, pwd, node_name):
    nd_fdn = 'MD=CISCO_EPNM!ND='+node_name
    url = 'https://'+server_ip+'/restconf/data/v1/cisco-resource-physical:node?.depth=1&fdn='+nd_fdn
    status, resp = sendGET(url,user,pwd)
    if not status:
        print("ERROR: It was not possible to run execute GET node")
        print("Server returned :",resp)
        exit(1)
    else:
        if getLastIndex(resp) == 0:
            return True
        else:
            return False

def getNodeFamily(server_ip, user, pwd, node_name):
    nd_fdn = 'MD=CISCO_EPNM!ND='+node_name
    url = 'https://'+server_ip+'/restconf/data/v1/cisco-resource-physical:node?.depth=1&fdn='+nd_fdn
    status, resp = sendGET(url,user,pwd)
    if not status:
        print("ERROR: It was not possible to run execute GET node")
        print("Server returned :",resp)
        exit(1)
    else:
        try:
            node_family = json.loads(resp)["com.response-message"]["com.data"]["nd.node"][0]["nd.product-family"]
            return node_family
        except:
            print("ERROR: It was not possible to retrieve product family")
            exit(1)

def getNodeID(nodeName,id_list):
    found = False
    for node in id_list:
        if found:
            break
        name = node["device_name"]
        if name == nodeName:
            found = True
            id = node["device_id"]
    if not found:
        print("ERROR: It was not possible to retrieve", nodeName, "in the deviceID file")
        print('Please execute getDeviceID.py again\n')
        exit(1)
    return id
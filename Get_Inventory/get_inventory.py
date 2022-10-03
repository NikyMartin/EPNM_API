#!/usr/bin/python3

"""
    September 22nd, 2020
    Created by:
    Nicola Martino, nmartino@cisco.com

    October 03, 2022
    Converted from using ET to JSON

"""

username = 'nmartino'
password = 'Public!23'

import requests
import re
import sys
# import xml.etree.ElementTree as ET
import json
from tabulate import tabulate
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
        print("Server returned :",resp.status_code)
        exit(1)
    else:
        if getLastIndex(resp) == 0:
            return True
        else:
            return False


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
    scripts, server_ip, device_name = sys.argv

# username = input("Enter Device Username: ")
# password = getpass.getpass()

    if isNodeValid(server_ip, username, password, device_name):
        node = json.loads(getNode(server_ip, username, password, device_name))

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
    else:
        print("\nNode", device_name, "not found\n")

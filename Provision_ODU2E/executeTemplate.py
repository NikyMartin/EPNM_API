#!/usr/bin/python

"""
    Created by:
    Nicola Martino, nmartino@cisco.com

    Feb 15th, 2020
    Original version

"""

##################################################################
# This script can execute any EPNM Template with any set of
# paramList for any device type
##################################################################

# executeTemplate() foes following
# gets device name, device id, template name, template param list
# generates templay payload using provided input
# execute a POST on deploy template EPNM API URL
# returns status and EPNM job ID

import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
import logging.handlers as handlers
import logging

logger = logging.getLogger('nicola')
logger.setLevel(logging.INFO)

LOG_FILE = "execute_tamplete.log"
open(LOG_FILE, 'w').close()
logHandler = handlers.RotatingFileHandler(LOG_FILE, maxBytes=100000, backupCount=2, mode='w')
logHandler.setLevel(logging.INFO)
logger.addHandler(logHandler)
logger.info("\nDeploy Template script started !!!\n")

def getLastIndex(payload):  # TODO can be removed or is imported by other?
    try:
        lastIndex = json.loads(payload)['com.response-message']['com.header']['com.lastIndex']
    except Exception as e:
        print('Problem with lastIndex')
        logger.info('Problem with lastIndex')
        exit(1)
    return lastIndex


def getHeaders():  # Fixed set of headers to be used by EPNM API GET or SET operations
    headers = {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }
    return headers

# generic function to perform EPNM API GET operation
# The url passed as input already contains server IP
# function returns False if o call if status_code is not 200
# function returns also response.text
def sendGET(url, user, pwd):  # It was used in previous version. Now is used by other scripts TODO check imports on other files
    logger.info("Sending GET " + url)
    response = requests.get(url, headers=getHeaders(), verify=False, auth=(user, pwd))
    if response.status_code != 200:
        error_message = json.loads(response._content.decode())["errorDocument"]["message"]
        logger.info(json.dumps(error_message, indent=4))
        return (False, response.status_code)
    else:
        return (True, response.text)


# generic function to perform EPNM API SET operation
# The url passed as input already contains server IP
# function returns False if o call if status_code is not 200
# function returns also response.text
def sendPUT(url, data, user, pwd):
    logger.info("Sending PUT " + url)
    response = requests.put(url, headers=getHeaders(), data=data, verify=False, auth=(user, pwd))
    if response.status_code != 200:
        error_message = json.loads(response._content.decode())["errorDocument"]["message"]
        logger.info(json.dumps(error_message, indent=4))
        return (False, response.status_code)
    else:
        return (True, response.text)

# Template payload can be JSON or XML. I prefer JSON
# Template payload is made of, devicename, internal EPNM device ID and paramList
def createTemplatePayload(template, deviceID, params):
    payload = {
        "cliTemplateCommand": {
            "targetDevices": {
                "targetDevice": [{
                    "targetDeviceID": deviceID,
                    "variableValues": {
                        "variableValue": params
                    }
                }]
            },
            "templateName": template
        }
    }
    logger.info("Following payload has been used")
    logger.info(json.dumps(payload, indent=4))
    return json.dumps(payload)

# This is core part
# what it does is explained at the beginning
def executeTemplate(server_ip, user, pwd, device, deviceid, template, params):
    jobDetails = ""  # function returns empty string in case cannot execute its job
    logger.info("Now executing template " + template + " on device " + device)
    templatePayload = createTemplatePayload(template, deviceid, params)
    url = 'https://' + server_ip + '/webacs/api/v4/op/cliTemplateConfiguration/deployTemplateThroughJob'
    status, resp = sendPUT(url, templatePayload, user, pwd)
    if not status:
        print("ERROR: It was not possible to run execute PUT template")
        print("Server returned Error", resp)
        exit(1)
    else:
        logger.info("Job Created for device " + device)
        output_message = json.loads(resp)
        jobID = output_message["mgmtResponse"]["cliTemplateCommandJobResult"][0]["jobName"]
        logger.info("Job ID: " + jobID)
        jobDetails = ({
            "nodeName": device,
            "jobID": jobID
        })
    return status, jobDetails

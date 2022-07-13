#!/usr/bin/python

"""
    Created by:
    Nicola Martino, nmartino@cisco.com

    Feb 16th, 2020
    Original version

"""

##################################################################
# This script implements following:
##################################################################

import os 
import re
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import socket
import requests
import sys
import getpass
import platform
import logging.handlers as handlers
import logging

logger = logging.getLogger('nicola')
logger.setLevel(logging.INFO)

LOG_FILE="jobHistory.log"
open(LOG_FILE, 'w').close()
logHandler = handlers.RotatingFileHandler(LOG_FILE, maxBytes=100000, backupCount=2, mode='w')
logHandler.setLevel(logging.INFO)
logger.addHandler(logHandler)
logger.info("\nGet Jobs Summary script started !!!\n")

version=platform.python_version_tuple()
if version[0] != '3':
    print("This script requires Python3")
    exit(1)

logger.info("Python version is "+platform.python_version())

# Static username and password
# Remember to comment getusername and password down in the script

### Check if IP address and port have been passed as input parameters
if len(sys.argv)!=3:
    print('\nMust pass job list json file')
    exit(1)
scripts, epnm_ip, jobListFile = sys.argv

def isOpen(server_ip,port):
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   try:
      s.connect((server_ip, int(port)))
      s.shutdown(2)
      return True
   except:
      return False

def isEPNM(server_ip):
    url = 'https://'+server_ip+'/webacs/welcomeAction.do'
    response = requests.get(url, verify=False)
    if response.status_code == 200:
       return True
    else:
       return False

def isAccountValid(server_ip,user,pwd):
    url = 'https://'+server_ip+'/webacs/api/v4/data/Devices?.maxResults=1'
    response = requests.get(url, verify=False, auth=(user, pwd))
    if response.status_code == 401: # Error code 401 = Unauthorized
       return False
    else:
       return True

def getLastIndex(payload):
    try:
       lastIndex=json.loads(payload)['com.response-message']['com.header']['com.lastIndex']
    except Exception as e:
        print ('Problem with lastIndex')
        logger.info('Problem with lastIndex')
        logger.info(tp_list[1])
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
    logger.info("Sending GET "+url)
    response = requests.get(url, headers=getHeaders(), verify=False, auth=(user, pwd))
    if response.status_code != 200:
        error_message = json.loads(response._content.decode())["errorDocument"]["message"]
        logger.info(json.dumps(error_message, indent =4))
        return (False,response.status_code)
    else:
       return (True,response.text)
       
def is_job_valid(payload):
    valid = True
    try:
        job = json.loads(payload)["mgmtResponse"]["job"][0]
    except Exception as e:
        valid = False
    return valid
       
def getJobsSummary(server_ip,user,pwd,jobList):
    logger.info("Retriving jobsummary one by one")
    for job in jobList:
        url = 'https://'+server_ip+'/webacs/api/v4/op/jobService/runhistory?jobName='+job["jobID"]
        status, resp = sendGET(url,user,pwd)
        if not status:
            print("ERROR: It was not possible to run execute GET node")
            print("Server returned :",response.status_code)
            exit(1)
        else:
            logger.info('Cheking if job ID is valid')
            if is_job_valid(resp):
                logger.info('Job ID is valid')
                job_rsp = json.loads(resp)
                jobName = job_rsp["mgmtResponse"]["job"][0]["jobName"]
                jobStatus = job_rsp["mgmtResponse"]["job"][0]["jobStatus"]
                print('\n##### Device',job["nodeName"],'#####')
                print('Job Name:',jobName)
                print('Job Status:',jobStatus)
                logger.info('Cheking if job is COMPLETE')
                if jobStatus == "COMPLETED":
                    logger.info('Job is COMPLETE')
                    jobResultResult = job_rsp["mgmtResponse"]["job"][0]["runInstances"]["runInstance"][0]["resultStatus"]
                    print('Job Result:',jobResultResult)
                    result = job_rsp["mgmtResponse"]["job"][0]["runInstances"]["runInstance"][0]["results"]["result"]
                    if len(result) == 0:
                        print('EPNM Failed to execute job')
                    else:
                        logger.info('Checking if device failed to execute')
                        for index1 in result:
                            isMessage = re.search(r'message(?P<isMessage>.*)', index1["property"])
                            if isMessage:
                                deviceMessage = index1["value"]
                            isDeployStatus = re.search(r'deployStatus(?P<isDeployStatus>.*)', index1["property"])
                            if isDeployStatus:
                                deviceStatus = index1["value"]
                        if deviceStatus != "true":
                            print("Device failed execution")
                        print(deviceMessage)
                
            else:
                print('\n####Device',job["nodeName"],'#####')
                print('ERROR: Job',job["jobID"],'is not valid')


#############################
### MAIN
#############################

logger.info("Importing Job List JSON file")

try:
   f = open(jobListFile,'r')
except Exception as e:
    print ('Failed loading Job List json file')
    print (str(e))
    exit (1)
jobList=json.load(f)
f.close ()

# jobList = [{
#        "nodeName": "MESH-1-128",
#        "jobID": "CREATE_PROT_ODU2E_2kmidpoint_07_04_53_590_PM_02_22_2022_6"
#    }]


if __name__ == '__main__':

    if len(sys.argv)!=3:
      print('\nMust pass EPNM IP address and job_list file name as script arguments\n')
      print('EX: jobHistory.py 10.58.111.222 Create_JobList2022-07-07_11:18_CEST.json\n')
      exit()
    scripts, epnm_ip, input_file = sys.argv

    epnm_username = input("Enter Username: ")
    epnm_password = getpass.getpass()

    getJobsSummary(epnm_ip,epnm_username,epnm_password,jobList)

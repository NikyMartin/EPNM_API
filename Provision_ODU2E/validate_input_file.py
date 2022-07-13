from checkUseCase import isValidUseCase
from validate4K import validate_4K
from validate2k import validate_2K

import json
import getpass
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
import sys
import socket
from os.path import exists
import logging.handlers as handlers
import logging

logger = logging.getLogger('nicola')
logger.setLevel(logging.INFO)

LOG_FILE="validate_input.log"
open(LOG_FILE, 'w').close()
logHandler = handlers.RotatingFileHandler(LOG_FILE, maxBytes=100000, backupCount=2, mode='w')
logHandler.setLevel(logging.INFO)
logger.addHandler(logHandler)


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

def runBasicControls(server_ip,epnm_username, epnm_password):
    logger.info("\n***** Running Basic Controls ******\n")
    logger.info("Checking HTTPS Port 443")

    # Check if https server is up and port 443 is reachable

    if not isOpen(server_ip, 443):
        print("\nERROR: " + server_ip + " is not reachable, either the server is down or port 443 is filtered\n")
        exit()

    logger.info("HTTPS Port 443 is Open")

    # Check if https server is EPNM

    logger.info("Checking if this is an EPNM Server")

    if not isEPNM(server_ip):
        print("\nERROR: " + server_ip + " is not an EPN-M Server\n")
        exit()

    logger.info("Control on EPNM Server passed")

    # Check if account is correct

    logger.info("Checking User Credentials")

    if not isAccountValid(server_ip, epnm_username, epnm_password):
        print("\nERROR: Check if username and password are correct\n")
        exit()

    logger.info("EPNM credentials are connect")

##########################
#### A End control
##########################

def validate_Aend(json_file,use_case,protection,epnm_ip, epnm_username, epnm_password):
    print("Validating A End section")
    logger.info("\n****** Validating A End section ******\n")
    control = True

    if use_case in ["4K-2K","4K-4K"]:
        logger.info("Enter if use case [4K-2K 4K-4K]")
        node = json_file["service_instance"]["service_termination_points"]["A_endpoint"]  # presence already validated in isValidUseCase
        midnode = False
        logger.info("Running validate_4K() with payload "+str(node))
        control = validate_4K(node, midnode, protection, epnm_ip, epnm_username, epnm_password)
        return control

    if use_case == "2K-2K":
        logger.info("Enter if use case [2K-2K]")
        node = json_file["service_instance"]["service_termination_points"]["A_endpoint"]
        midnode = False
        endnode = True
        logger.info("Running validate_2K() with payload " + str(node))
        control = validate_2K(node, midnode, endnode, protection,epnm_ip, epnm_username, epnm_password)
        return control

##########################
#### Z End control
##########################

def validate_Zend(json_object,use_case,protection,epnm_ip, epnm_username, epnm_password):

    print("Validating Z endpoint section")
    logger.info("\n****** Validating Z End section ********\n")
    control = True
    if use_case in ["4K-2K","2K-2K"]:
        logger.info("Enter if use case [4K-2K or 2K-2K] ")
        node = json_object["service_instance"]["service_termination_points"]["Z_endpoint"]
        midnode = False
        endnode = False
        logger.info("Running validate_2K() with payload " + str(node))
        control = validate_2K(node, midnode, endnode, protection, epnm_ip, epnm_username, epnm_password)
        return control

    if use_case == "4K-4K":
        logger.info("Enter if use case [4K-4K]")
        node = json_object["service_instance"]["service_termination_points"]["Z_endpoint"]
        midnode = False
        logger.info("Running validate_4K() with payload "+str(node))
        control = validate_4K(node, midnode, protection, epnm_ip, epnm_username, epnm_password)
        return control

##########################
#### working and
#### protected path
#### control
##########################

# This function can validate both working and protected paths depending on "path"
def validate_midpoints(json_file,epnm_ip, epnm_username, epnm_password,route,protection):
    control = True
    list = True
    control_node = True

    if route == "Working":
        print("Validating working path")
        logger.info("\n****** Validating Working Path ********\n")

        try:
            node_list = json_file["service_instance"]["service_termination_points"]["midpoints_working"]
        except:
            print("\nERROR: Cannot find working path list")
            print("Will skip this control\n")
            list = False

    else:
        print("Validating protected path")
        logger.info("\n****** Validating Protected Path ********\n")

        try:
            node_list = json_file["service_instance"]["service_termination_points"]["midpoints_protected"]
        except:
            print("\nERROR: Cannot find protected path list")
            print("Will skip this control\n")
            list = False

    if list:
        lung = len(node_list)
        if lung == 0:
            print("Warning: "+route,"path list is empty\n")
            logger.info(route+" path list is empty !!!")
            list = False
        else:
            print(route,"path has",lung,"nodes")
            logger.info(route + " path has "+str(lung)+" nodes")
            index = 1
            for node in node_list:
                print("Checking node",index)
                midnode = True
                if node["node_type"] == "2K":
                    endnode = False
                    logger.info("Running validate_2K() with payload " + str(node))
                    control_node = validate_2K(node, midnode, endnode, protection, epnm_ip, epnm_username, epnm_password)
                    if not control_node:
                        control = False
                if node["node_type"] == "4K":
                    logger.info("Running validate_4K() with payload " + str(node))
                    control_node = validate_4K(node, midnode, protection, epnm_ip, epnm_username, epnm_password)
                    if not control_node:
                        control = False
                index += 1

    return control,list

def runValidate(epnm_ip, epnm_username, epnm_password, json_file, protection):
    master_control = True
    print('\nPlease wait. It can take a while')
    logger.info("\n****** Validate Input JSON File Starts Here ******\n")
    logger.info("Checking if use case is valid")
    logger.info("Running isValidUseCase()")
    status, use_case = isValidUseCase(json_file)
    if not status:
        print("\nUse case not valid")
        print("Supported use cases are: 4K-2K, 2K-2K or 4K-4K")
        print("Found",use_case)
        print("Terminating execution\n")
        exit(1)
    else:
        logger.info("Use case is valid. Found "+use_case)
        print("\nUse case is valid")
        print("Found",use_case,"\n")

    if validate_Aend(json_file, use_case, protection, epnm_ip, epnm_username, epnm_password):
        print("A End section control passed with no errors\n")
    else:
        print("***** A End section control FAILED *****\n")
        master_control = False

    if validate_Zend(json_file,use_case, protection, epnm_ip, epnm_username, epnm_password):
        print("Z End section control passed with no errors\n")
    else:
        print("***** Z End section control FAILED *****\n")
        master_control = False

    control, list = validate_midpoints(json_file,epnm_ip, epnm_username, epnm_password,"Working",protection)
    if list:
        if control:
            print("Working path section control passed with no errors\n")
        else:
            print("***** Working path section control FAILED *****\n")
            master_control = False

    control, list = validate_midpoints(json_file, epnm_ip, epnm_username, epnm_password, "Protected",protection)
    if list:
        if control:
            print("Protected path section control passed with no errors\n")
        else:
            print("***** Protected path section control FAILED *****\n")
            master_control = False

    return master_control

#############################
### MAIN
#############################

if __name__ == '__main__':

    if len(sys.argv)!=3:
      print('\nMust pass EPNM IP address and service file name as script arguments\n')
      print('EX: validate_input_file.py 10.58.111.222 2K_2K_prot.json\n')
      exit()
    scripts, epnm_ip, input_file = sys.argv

    if not exists(input_file):
        print("\nFile", input_file, "not found\n")
        exit(1)

# Open input fie and
# Control if it has valid JSON content and can be passed to further controls

    f = open(input_file, 'r')
    content_file = f.read()
    f.close()
    try:
        json_file = json.loads(content_file)
    except:
        print("\nERROR: Input file has not valid JSON structure")
        print("Cannot proceed. Terminating execution\n")
        exit(1)

    epnm_username = input("Enter Username: ")
    epnm_password = getpass.getpass()

    runBasicControls(epnm_ip, epnm_username, epnm_password)

    try:
        protection = json_file["service_instance"]["service_details"]["protection"]
    except:
        print("\nERROR: Z endpoint is present but cannot find node_type")
        print("Terminating execution\n")
        exit(1)
    if protection not in ["protected","unprotected"]:
        print("\nERROR: invalid protection: "+str(protection))
        print("Protection must either be protected or unprotected")
        print("Terminating execution\n")
        exit(1)

    master_control = runValidate(epnm_ip, epnm_username, epnm_password, json_file, protection)

    if master_control:
        print("\nAll good. Validation passed\n")
    else:
        print("\nPlease fix ERRORS and retry\n")
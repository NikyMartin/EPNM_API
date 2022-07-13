import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import logging.handlers as handlers
import logging

logger = logging.getLogger('nicola')
logger.setLevel(logging.INFO)

LOG_FILE="create4KNodeID.log"
open(LOG_FILE, 'w').close()
logHandler = handlers.RotatingFileHandler(LOG_FILE, maxBytes=100000, backupCount=2, mode='w')
logHandler.setLevel(logging.INFO)
logger.addHandler(logHandler)
logger.info("\nCreate 4K Node ID script started !!!\n")

def getLastIndex(payload):
    try:
       lastIndex=json.loads(payload)['com.response-message']['com.header']['com.lastIndex']
    except Exception as e:
        print ('Problem with lastIndex')
        logger.info('Problem with lastIndex')
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

def get4KNodeIP(nodeName,server_ip,user,pwd):
    logger.info("Retriving 4K Node Name")
    nd_fdn = 'MD=CISCO_EPNM!ND='+nodeName
    url = 'https://'+server_ip+'/restconf/data/v1/cisco-resource-physical:node?fdn='+nd_fdn
    logger.info("Sending GET")
    status, resp = sendGET(url,user,pwd)
    if not status:
        print("ERROR: It was not possible to run execute GET node")
        print("Server returned :",resp.status_code)
        exit(1)
    else:
        if getLastIndex(resp) == 0:
            nodeIP = json.loads(resp)['com.response-message']['com.data']['nd.node'][0]['nd.management-address']
            logger.info("4K Node IP is "+nodeIP)
            return nodeIP
        else:
            print("ERROR: Node",nodeName,"not found in the system")
            logger.info("getLastIndex returned "+str(getLastIndex(resp)))
            exit(1)

def get4K_nodeID(nodeName,server_ip,user,pwd):
    nodeIP = get4KNodeIP(nodeName,server_ip,user,pwd)
    parts = nodeIP.split('.')
    iaddr = (int(parts[0]) << 24) | (int(parts[1]) << 16) | (int(parts[2]) << 8) | int(parts[3])
    hex_val = hex(iaddr)
    nodeID = (f'{iaddr:x}').upper()
    logger.info("4K Node ID is " + nodeID)
    return nodeID

# print(get4KNodeID("10.58.234.32","root","Public!23"))
# print(get4KNodeName("input_file_option_A.json"))
# print(get4Kdetails("input_file_option_A.json","10.58.234.32","root","Public!23"))
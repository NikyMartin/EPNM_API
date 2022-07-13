import requests
import json

def getLastIndex(payload):
    try:
       lastIndex=json.loads(payload)['com.response-message']['com.header']['com.lastIndex']
    except Exception as e:
#        logger.info('Problem with lastIndex')
        exit(1)
#    logger.info("Last Index is "+str(lastIndex))
    return lastIndex

def getHeaders():
    headers = {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }
    return headers

def sendGET(url,user,pwd):
#    logger.info("Sending GET "+url)
    response = requests.get(url, headers=getHeaders(), verify=False, auth=(user, pwd))
    if response.status_code != 200:
        error_message = json.loads(response._content.decode())["errorDocument"]["message"]
#        logger.info(json.dumps(error_message, indent =4))
        return (False,response.status_code)
    else:
       return (True,response.text)

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

def is_4Kport_string_correct(string,lung):
    parts = string.split('/')
    if len(parts) != lung:
        return False
    else:
        return True

def is_2Kport_string_correct(string, lung):
    parts = string.split('-')
    if len(parts) != lung:
        return False
    else:
        return True

def isTpValid(tp_fdn,server_ip,user,pwd):
    url = 'https://'+server_ip+'/restconf/data/v1/cisco-resource-ems:termination-point?fdn='+tp_fdn
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

def is_number(tpn):
    try:
        num = int(tpn)
    except:
        return False

    return True
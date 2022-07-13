import logging
import socket
import logging.handlers as handlers
import cx_Oracle
import json
import requests

logger = logging.getLogger('nicola')
logger.setLevel(logging.INFO)


def isOpen(server_ip,port):
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   try:
      s.connect((server_ip, int(port)))
      s.shutdown(2)
      return True
   except:
      return False

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

def getNodeIP(node_name,server_ip,user,pwd):
    logger.info("Retriving Node IP")
    nd_fdn = 'MD=CISCO_EPNM!ND='+node_name
    url = 'https://'+server_ip+'/restconf/data/v1/cisco-resource-physical:node?fdn='+nd_fdn
    logger.info("Calling sendGET")
    status, resp = sendGET(url,user,pwd)
    if not status:
        print("ERROR: It was not possible to run execute GET node")
        print("Server returned :",resp.status_code)
        exit(1)
    else:
        if getLastIndex(resp) == 0:
            nodeIP = json.loads(resp)['com.response-message']['com.data']['nd.node'][0]['nd.management-address']
            logger.info("Node IP is "+nodeIP)
            return nodeIP
        else:
            print("\nERROR: Node",node_name,"not found in the system\n")
            logger.info("getLastIndex returned "+str(getLastIndex(resp)))
            exit(1)

def get_TL1_NodeID(node_name,server_ip):
    listener_port = 1522
    sid = 'wcs'
    dbauser = 'wcsdba'

    try:
        f = open('dbapassword', 'r')
    except Exception as e:
        print ('\nFailed loading dbapassword file')
        print (str(e))
        exit(1)
    dbapassword = f.readline().rstrip('\n')
    f.close()

    sid = cx_Oracle.makedsn(server_ip, listener_port, service_name=sid)

    # Check if Oracle Listner port is reachable and iptables disabled

    logger.info("Checking Oracle listener port")

    if not isOpen(server_ip, listener_port):
        print("\nERROR: Either Oracle is down or port ", listener_port, " is filtered")
        print("Make sure you have open port 1522 on EPNM Server with: sudo iptables -I INPUT 1 -p tcp --dport 1522 -j ACCEPT\n")
        exit()

    logger.info("Listener port is open")
    logger.info("Extracting node name from Listener port is open")

    logger.info("Execute GET node ID")
    logger.info("Connecting to Oracle listener")

    try:
        connection = cx_Oracle.connect(dbauser, dbapassword, sid, encoding="UTF-8")
    except Exception as e:
        print("C1")
        print('Failed to connect Database')
        print(str(e))
        exit(1)

    logger.info("Oracle listener connected")

    cursor = connection.cursor()

    SQL = 'select name, nodeid from NetworkResource where name = \'' + node_name + '\''

    # print(SQL)

    logger.info("Performing SQL Select")

    try:
        cursor.execute(SQL)
    except Exception as e:
        print('Failed to perform select')
        print(str(e))
        exit(1)

    for row in cursor:
        xx = row[0]
        node_id = row[1]

    cursor.close()
    connection.close()

    return node_id

def get_2Kport_TL1_string(clientPort_string):
    logger.info("Checking if string has format chassis-slot-port-sub")
    logger.info("making TL1 port name")
    parts = clientPort_string.split('-')
    basePort = parts[0] + "-" + parts[1] + "-" + parts[2] + "-1-"
    clientPort = "VLINE-" + basePort + parts[3]
    logger.info("VLINE name from "+clientPort_string+" is "+clientPort)
    return clientPort

def get_index(node_name, clientPort_string, server_ip, epnm_username, epnm_password):
    listener_port = 1522
    sid = 'wcs'
    dbauser = 'wcsdba'

    try:
        f = open('dbapassword', 'r')
    except Exception as e:
        print ('\nFailed loading dbapassword file')
        print (str(e))
        exit(1)
    dbapassword = f.readline().rstrip('\n')
    f.close()

    sid = cx_Oracle.makedsn(server_ip, listener_port, service_name=sid)

    node_ip = getNodeIP(node_name, server_ip, epnm_username, epnm_password)
    pep_name = get_2Kport_TL1_string(clientPort_string)


    logger.info("Checking Oracle listener port")

    if not isOpen(server_ip, listener_port):
        print("\nERROR: Either Oracle is down or port ", listener_port, " is filtered")
        print("Make sure you have open port 1522 on EPNM Server with: sudo iptables -I INPUT 1 -p tcp --dport 1522 -j ACCEPT\n")
        exit()

    logger.info("Listener port is open")
    logger.info("Extracting node name from Listener port is open")

    logger.info("Execute GET node ID")
    logger.info("Connecting to Oracle listener")

    try:
        connection = cx_Oracle.connect(dbauser, dbapassword, sid, encoding="UTF-8")
    except Exception as e:
        print('Failed to connect Database')
        print(str(e))
        exit(1)

    logger.info("Oracle listener connected")

    cursor = connection.cursor()

    SQL = "select pep.name, opep.ifindex from protocolEndpoint pep,OPTICALINTERFACEPEP opep where  pep.id = opep.OPTICALINTERFACEPEP_ID and pep.name = '" + pep_name + "' and pep.owningEntityId like '%" + node_ip + "%'"

    try:
        cursor.execute(SQL)
    except Exception as e:
        print('Failed to perform select')
        print(str(e))
        exit(1)

    for row in cursor:
        yy = row[0]
        ifIndex = row[1]

    return ifIndex

get_TL1_NodeID('pippo','10.58.234.32')
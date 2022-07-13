"""
    Created by:
    Nicola Martino, nmartino@cisco.com

    April 28th
    Added createPayload_unprot_2Kend_Z function
    - Could combine both in oe function but risk
    is to broke existing one -

    March 8th, 2022
    Original version

"""

from getTL1details import get_TL1_NodeID,get_index

import json
import logging

logger = logging.getLogger('nicola')
logger.setLevel(logging.INFO)

def createPayload2Kend_A(input_file,serviceName,serviceID,protection,server_ip,epnm_username, epnm_password):
    f = open(input_file, 'r')
    content_file = f.read()
    f.close()
    json_object = json.loads(content_file)

    node_2K_A = json_object["service_instance"]["service_termination_points"]["A_endpoint"]
    node_2K_Z = json_object["service_instance"]["service_termination_points"]["Z_endpoint"]
    node_name_A = node_2K_A["node_name"]
    node_name_Z = node_2K_Z["node_name"]

    w_tpn = node_2K_A["w_tpn"]

    input_wtrunkport = node_2K_A["w_trunk_port"]
    wOduPort = "ODU-" + input_wtrunkport + "-1-1-" + w_tpn

    input_clientport = node_2K_A["client_port"]
    parts = input_clientport.split('-')
    basePort = parts[0] + "-" + parts[1] + "-" + parts[2] + "-1-"
    clientPort = "VLINE-" + basePort + parts[3]
    oduClientPort = "ODU-" + basePort + parts[3] + "-1"

    input_clientport_Z = node_2K_Z["client_port"]

    sourceNodeID = get_TL1_NodeID(node_name_A,server_ip)
    dropNodeID = get_TL1_NodeID(node_name_Z,server_ip)
    clientPort_string_A = input_clientport
    sourceIndex = get_index(node_name_A, clientPort_string_A, server_ip, epnm_username, epnm_password)
    clientPort_string_Z = input_clientport_Z
    dropIndex = get_index(node_name_Z, clientPort_string_Z, server_ip, epnm_username, epnm_password)

    sourceTP = sourceNodeID + "/0x" + sourceIndex + "/1"
    dropTP = dropNodeID + "/0x" + dropIndex + "/1"

    paramList2Kend = [
                 {
                     "name": "w_odu_port",
                     "value": wOduPort
                 },
                 {
                     "name": "client_port",
                     "value": clientPort
                 },
                 {
                     "name": "service_name",
                     "value": serviceName
                 },
                 {
                     "name": "source_tp",
                     "value": sourceTP
                 },
                 {
                     "name": "drop_tp",
                     "value": dropTP
                 },
                 {
                     "name": "service_id",
                     "value": serviceID
                 },
                 {
                     "name": "odu_client_port",
                     "value": oduClientPort
                 }]

    if protection == "protected":

        p_tpn = node_2K_A["p_tpn"]

        input_ptrunkport = node_2K_A["p_trunk_port"]
        pOduPort = "ODU-" + input_ptrunkport + "-1-1-" + p_tpn

        protectionParamList = [
            {
                "name": "p_odu_port",
                "value": pOduPort
            }
        ]
        paramList2Kend = paramList2Kend + protectionParamList

    return paramList2Kend


# param_list = createPayload2Kend_A("2K-2K.json", "serviceName", "serviceID", "protected", "10.58.234.32", "root", "Public!23")
# print(json.dumps(param_list, indent=4))

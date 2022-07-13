
"""
    Created by:
    Nicola Martino, nmartino@cisco.com

    April 28th
    Combined createPayload_4K_A() with createPayload_4K_Z()
    in new createPayload_4K_End()
    Added control if protection is needed for
    Unprotected 10G services

    March 8th, 2022
    Original version

"""

# This is for extracting all inputs from JSON file when A-End is a 4K
#
# createPayload_4K_End() does following:
# - gets JSON input file (can pass the file content directly but. I'm using the file so
#       I can test it here (see last two lines)
# - Extracts the ["A_endpoint"] or ["Z_endpoint"] section
# - Some parameters from endpoint will be passed to paramList directly. Some other will
#       be processed
#
#
# createPayload_4K_End() returns a list (paramList) where each item is a JSON object
#

import json

def createPayload_4K_End(input_file,serviceName,serviceID,nodeID,AZend,protection):
    f = open(input_file, 'r')
    content_file = f.read()
    f.close()
    json_object = json.loads(content_file)

    if AZend == "A-End":
        node_4K = json_object["service_instance"]["service_termination_points"]["A_endpoint"]
    if AZend == "Z-End":
        node_4K = json_object["service_instance"]["service_termination_points"]["Z_endpoint"]

    input_clientport = node_4K["client_port"]
    clientPort = "TenGigECtrlr" + input_clientport
    clientOdu = "ODU2E" + input_clientport

    input_wtrunkport = node_4K["w_trunk_port"]
    wTrunkPort = "ODU4" + input_wtrunkport

    w_tpn = node_4K["w_tpn"]

    baseTs = [0, 1, 2, 3, 4, 5, 6, 7]
    for ts in baseTs:
        baseTs[ts] = str((baseTs[ts] * 10) + int(w_tpn))
    w_tsList = ':'.join(baseTs)

    oduGroup = node_4K["odu_group"]
    wController = "ODU2E" + input_wtrunkport + "/" + str(int(w_tpn) * 10)
    xConnectID = node_4K["xconnect_id"]

    paramList4Kend = [
                {
                    "name": "client_port",
                    "value": clientPort
                },
                {
                    "name": "client_odu",
                    "value": clientOdu
                },
                {
                    "name": "w_trunk_port",
                    "value": wTrunkPort
                },
                {
                    "name": "w_tpn",
                    "value": w_tpn
                },
                {
                    "name": "w_ts_list",
                    "value": w_tsList
                },
                {
                    "name": "odu_group",
                    "value": oduGroup
                },
                {
                    "name": "w_controller",
                    "value": wController
                },
                {
                    "name": "node_id",
                    "value": nodeID
                },
                {
                    "name": "service_id",
                    "value": serviceID
                },
                {
                    "name": "service_name",
                    "value": serviceName
                },
                {
                    "name": "xconnect_id",
                    "value": xConnectID
                }]

    if protection == "protected":
        input_ptrunkport = node_4K["p_trunk_port"]
        pTrunkPort = "ODU4" + input_ptrunkport

        p_tpn = node_4K["p_tpn"]

        baseTs = [0, 1, 2, 3, 4, 5, 6, 7]
        for ts in baseTs:
            baseTs[ts] = str((baseTs[ts] * 10) + int(p_tpn))
        p_tsList = ':'.join(baseTs)

        pController = "ODU2E" + input_ptrunkport + "/" + str(int(p_tpn) * 10)

        protectionParamList = [
            {
                "name": "p_trunk_port",
                "value": pTrunkPort
            },
            {
                "name": "p_tpn",
                "value": p_tpn
            },
            {
                "name": "p_ts_list",
                "value": p_tsList
            },
            {
                "name": "p_controller",
                "value": pController
            }
        ]
        paramList4Kend = paramList4Kend + protectionParamList

    return paramList4Kend

# param_list = createPayload_4K_End("4K-4K.json","pippo","69","nodeID","Z-End","protected")
# print(json.dumps(param_list, indent =4))
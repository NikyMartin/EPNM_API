"""
    Created by:
    Nicola Martino, nmartino@cisco.com

    April 28th
    Added control if protection is needed for
    Unprotected 10G services
    Changed function name to deletePayload_4K_End()

    March 8th, 2022
    Original version

"""

import json

def deletePayload_4K_End(input_file,AZend, protection):
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

    input_wtrunkport = node_4K["w_trunk_port"]
    wTrunkPort = "ODU4" + input_wtrunkport

    w_tpn = node_4K["w_tpn"]

    oduGroup = node_4K["odu_group"]
    xConnectID = node_4K["xconnect_id"]

    paramList4Kend = [
                {
                    "name": "client_port",
                    "value": clientPort
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
                    "name": "odu_group",
                    "value": oduGroup
                },
                {
                    "name": "xconnect_id",
                    "value": xConnectID
                }]

    if protection == "protected":
        input_ptrunkport = node_4K["p_trunk_port"]
        pTrunkPort = "ODU4" + input_ptrunkport

        p_tpn = node_4K["p_tpn"]

        protectionParamList = [
            {
                "name": "p_trunk_port",
                "value": pTrunkPort
            },
            {
                "name": "p_tpn",
                "value": p_tpn
            }
        ]
        paramList4Kend = paramList4Kend + protectionParamList

    return paramList4Kend


# param_list = deletePayload_4K_End("4K-2K_unprot.json", "A-End", "aprotected")
# print(json.dumps(param_list, indent=4))

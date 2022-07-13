import json

def createPayloadMid(input_file,serviceName,serviceID,nodeID,isWorking):
    f = open(input_file, 'r')
    content_file = f.read()
    f.close()
    json_object = json.loads(content_file)

    param_list = {}
    node_type_list = {}

    if isWorking:
        node_list = json_object["service_instance"]["service_termination_points"]["midpoints_working"]
    else:
        node_list = json_object["service_instance"]["service_termination_points"]["midpoints_protected"]

    index = 0
    for node in node_list:

        if node["node_type"] == "2K":

            input_wtrunkport = node["w_trunk_port"]
            w_tpn = node["w_tpn"]
            oduPort1 = "ODU-" + input_wtrunkport + "-1-1-" + w_tpn

            input_ptrunkport = node["p_trunk_port"]
            p_tpn = node["p_tpn"]
            oduPort2 = "ODU-" + input_ptrunkport + "-1-1-" + p_tpn

            node_type_list[index] = "2K"
            param_list[index] = [
                     {
                         "name": "odu_port_1",
                         "value": oduPort1
                     },
                     {
                         "name": "odu_port_2",
                         "value": oduPort2
                     },
                     {
                         "name": "service_name",
                         "value": serviceName
                     },
                     {
                         "name": "node_id",
                         "value": nodeID
                     },
                     {
                         "name": "service_id",
                         "value": serviceID
                     }]

        if node["node_type"] == "4K":

            input_wtrunkport = node["w_trunk_port"]
            wTrunkPort = "ODU4" + input_wtrunkport

            input_ptrunkport = node["p_trunk_port"]
            pTrunkPort = "ODU4" + input_ptrunkport

            w_tpn = node["w_tpn"]
            p_tpn = node["p_tpn"]

            baseTs = [0, 1, 2, 3, 4, 5, 6, 7]
            for ts in baseTs:
                baseTs[ts] = str((baseTs[ts] * 10) + int(w_tpn))
            w_tsList = ':'.join(baseTs)

            baseTs = [0, 1, 2, 3, 4, 5, 6, 7]
            for ts in baseTs:
                baseTs[ts] = str((baseTs[ts] * 10) + int(p_tpn))
            p_tsList = ':'.join(baseTs)

            wController = "ODU2E" + input_wtrunkport + "/" + str(int(w_tpn) * 10)
            pController = "ODU2E" + input_ptrunkport + "/" + str(int(p_tpn) * 10)
            xConnectID = node["xconnect_id"]

            node_type_list[index] = "4K"
            param_list[index] = [
                {
                    "name": "w_trunk_port",
                    "value": wTrunkPort
                },
                {
                    "name": "p_trunk_port",
                    "value": pTrunkPort
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
                    "name": "p_tpn",
                    "value": p_tpn
                },
                {
                    "name": "p_ts_list",
                    "value": p_tsList
                },
                {
                    "name": "w_controller",
                    "value": wController
                },
                {
                    "name": "p_controller",
                    "value": pController
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

        index += 1

    return node_type_list, param_list

# input file name is dummy with 2 working and 2 protected mid nodes
# Test it with isWorking True and False
# node_type_list, param_list = createPayloadMid("validate_input_file_example.json","serviceName","serviceID","nodeID",True)
# print(json.dumps(param_list, indent =4))
# print(json.dumps(node_type_list, indent =4))
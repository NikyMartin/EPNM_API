import json

def deletePayloadMid(input_file,isWorking):
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
                     }]

        if node["node_type"] == "4K":
            input_wtrunkport = node["w_trunk_port"]
            wTrunkPort = "ODU4" + input_wtrunkport

            input_ptrunkport = node["p_trunk_port"]
            pTrunkPort = "ODU4" + input_ptrunkport

            w_tpn = node["w_tpn"]
            p_tpn = node["p_tpn"]
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
                    "name": "p_tpn",
                    "value": p_tpn
                },
                {
                        "name": "xconnect_id",
                        "value": xConnectID
                }]

        index += 1

    return node_type_list, param_list

# input file name is dummy with 2 working and 2 protected mid nodes
# Test it with True and False
# node_type_list, param_list = deletePayloadMid("validate_input_file_example.json",True)
# print(json.dumps(param_list, indent =4))
# print(json.dumps(node_type_list, indent =4))

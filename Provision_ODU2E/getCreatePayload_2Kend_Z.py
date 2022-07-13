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




import json

def createPayload2Kend_Z(input_file,serviceName,serviceID,nodeID,protection):
    f = open(input_file, 'r')
    content_file = f.read()
    f.close()
    json_object = json.loads(content_file)

    node_2K = json_object["service_instance"]["service_termination_points"]["Z_endpoint"]

    w_tpn = node_2K["w_tpn"]

    input_wtrunkport = node_2K["w_trunk_port"]
    wOduPort = "ODU-" + input_wtrunkport + "-1-1-" + w_tpn

    input_clientport = node_2K["client_port"]
    parts = input_clientport.split('-')
    basePort = parts[0] + "-" + parts[1] + "-" + parts[2] + "-1-"
    clientPort = "VLINE-" + basePort + parts[3]
    oduClientPort = "ODU-" + basePort + parts[3] + "-1"

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
                     "name": "node_id",
                     "value": nodeID
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

        p_tpn = node_2K["p_tpn"]

        input_ptrunkport = node_2K["p_trunk_port"]
        pOduPort = "ODU-" + input_ptrunkport + "-1-1-" + p_tpn

        protectionParamList = [
            {
                "name": "p_odu_port",
                "value": pOduPort
            }
        ]
        paramList2Kend = paramList2Kend + protectionParamList

    return paramList2Kend


# param_list = createPayload2Kend("validate_input_file_example.json","serviceName","serviceID","nodeID")
# print(json.dumps(param_list, indent =4))

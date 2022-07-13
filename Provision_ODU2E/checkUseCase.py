import json

def isValidUseCase(json_file):
    control = True

    # Retrieve node type for A End
    try:
        a_node = json_file["service_instance"]["service_termination_points"]["A_endpoint"]
#        print(json.dumps(a_node, indent =4))
    except:
        print("perche?")
        print("\nERROR: Cannot find A End")
        print("Terminating execution\n")
        control = False
        exit(1)

    try:
        a_node_type = a_node["node_type"]
    except:
        print("\nERROR: A endpoint is present but cannot find node_type")
        print("Terminating execution\n")
        control = False
        exit(1)

    # Retrieve node type for Z End
    try:
        z_node = json_file["service_instance"]["service_termination_points"]["Z_endpoint"]
    except:
        print("\nERROR: Cannot find Z End")
        print("Terminating execution\n")
        control = False
        exit(1)

    try:
        z_node_type = z_node["node_type"]
    except:
        print("\nERROR: Z endpoint is present but cannot find node_type")
        print("Terminating execution\n")
        control = False
        exit(1)

    use_case = a_node_type+"-"+z_node_type

    if use_case not in ["4K-2K","2K-2K","4K-4K"]:
        control = False

    return control, use_case


def getFileProtection(json_file):
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

    return protection


from commonControls import isNodeValid,isTpValid,is_number,is_2Kport_string_correct
import logging

logger = logging.getLogger('nicola')
logger.setLevel(logging.INFO)

def validate_2K(node_2K, midnode, endnode, protection, epnm_ip, epnm_username, epnm_password):

    control = True

####
#### 2K endpoint name control
####

# Checking if node name is present in input file

    is_name_present = True
    try:
        logger.info("Checking if node_name exists")
        nodeName = node_2K["node_name"]
    except:
        print("\nERROR: Cannot find 2K Node name in input file")
        print("Cannot continue with further controls on this section\n")
        is_name_present = False
        control = False

    if is_name_present:
        logger.info("Running isNodeValid()")
        if not isNodeValid(epnm_ip, epnm_username, epnm_password, nodeName):
            print('\nERROR: ' + nodeName, 'is not found in EPN-M inventory')
            print('Cannot continue with further controls on this section\n')
            is_name_present = False
            control = False

    if is_name_present:
        print("Node name is",nodeName)

####
#### 2K Client port control
#### Only if not midnode
####

        if not midnode:
            logger.info("Node is not midnode")
# Checking if client port is present in input file
            is_client_port_present = True
            try:
                logger.info("Checking if client_port exists")
                clientPort_string = node_2K["client_port"]
            except:
                print("\nERROR: Cannot find 2K client port in input file")
                print("Continuing with 2K endpoint section controls\n")
                is_client_port_present = False
                control = False

            if is_client_port_present:
# Checking if client port has correct format
                logger.info("Checking if client port has correct format")
                logger.info("Running is_2Kport_string_correct()")
                if not is_2Kport_string_correct(clientPort_string, 4):
                    print("ERROR: Client Port", clientPort_string, "is not in chassis-slot-port-sub format")
                    control = False
# If format is correct, check if client port is present in EPNM
                else:
                    logger.info("Checking if client port is present in EPNM")
                    parts = clientPort_string.split('-')
                    basePort = parts[0] + "-" + parts[1] + "-" + parts[2] + "-1-"
                    clientPort = "VLINE-" + basePort + parts[3]
                    clientPort_fdn = "MD=CISCO_EPNM!ND=" + nodeName + "!CTP=name=" + clientPort + ";lr=lr-dsr-10gigabit-ethernet"
                    logger.info("Running isTpValid()")
                    if not isTpValid(clientPort_fdn, epnm_ip, epnm_username, epnm_password):
                        print('ERROR: Client Port', clientPort, 'is not found in EPN-M inventory TP list')
                        control = False

####
#### 2K W and P tpn control
####

# Checking if tpn  is present in input file
        tpn_control = True
        for tpn in ["w_tpn","p_tpn"]:

            if tpn == "p_tpn" and protection == "unprotected":
                break

            is_tpn_present = True
            try:
                logger.info("Checking if "+tpn+" tpn exists")
                ctpn = node_2K[tpn]
            except:
                print("\nERROR: Cannot find",tpn,"in input file")
                print("Continuing with 2K endpoint section controls\n")
                is_tpn_present = False
                tpn_control = False
                control = False

# Checking if TPN is a number and is within 0 .. 10 range
            if is_tpn_present:
                logger.info("Checking if tpn is a number and is within 0 .. 10 range")
                if not is_number(ctpn):
                    print('ERROR: TPN', ctpn, 'is not a number')
                    tpn_control = False
                    control = False
                else:
                    if not 1 <= int(ctpn) <= 20:
                        print('ERROR: TPN', ctpn, 'is not in range (1..20)')
                        tpn_control = False
                        control = False


####
#### 2K w trunk port control
####

        if tpn_control:

# Checking if trunk port is present in input file
            is_wtrunk_port_present = True
            try:
                logger.info("Checking if w_trunk_port exists")
                wTrunkPort_string = node_2K["w_trunk_port"]
            except:
                print("\nERROR: Cannot find 2K W trunk port in input file")
                print("Continuing with 2K endpoint section controls\n")
                is_wtrunk_port_present = False
                control = False

# Checking if trunk port has correct format and is present in EPNM
            if is_wtrunk_port_present:
                logger.info("Checking if w_trunk_port has correct format and is present in EPNM")
                logger.info("Running is_2Kport_string_correct()")
                if not is_2Kport_string_correct(wTrunkPort_string, 3):
                    print("ERROR: W Trunk Port", wTrunkPort_string, "is not in chassis-slot-port format")
                    control = False
                else:
                    wTrunkPort = "VFAC-" + wTrunkPort_string + "-1"
                    wTrunkPort_fdn = "MD=CISCO_EPNM!ND=" + nodeName + "!CTP=name=" + wTrunkPort + ";lr=lr-och-data-unit-4"
                    logger.info("Running isTpValid()")
                    if not isTpValid(wTrunkPort_fdn, epnm_ip, epnm_username, epnm_password):
                        print('ERROR: W Trunk Port', wTrunkPort, 'is not found in EPN-M inventory TP list')
                        control = False


            if protection == "protected":
####
#### 2K p trunk port control
####

# Checking if trunk port is present in input file
                is_ptrunk_port_present = True
                try:
                    logger.info("Checking if p_trunk_port exists")
                    pTrunkPort_string = node_2K["p_trunk_port"]
                except:
                    print("\nERROR: Cannot find 2K P trunk port in input file")
                    print("Continuing with 2K endpoint section controls\n")
                    is_ptrunk_port_present = False
                    control = False

            # Checking if trunk port has correct format and is present in EPNM
                if is_ptrunk_port_present:
                    logger.info("Checking if p_trunk_port has correct format and is present in EPNM")
                    logger.info("Running is_2Kport_string_correct()")
                    if not is_2Kport_string_correct(pTrunkPort_string, 3):
                        print("ERROR: P Trunk Port", pTrunkPort_string, "is not in chassis-slot-port format")
                        control = False
                    else:
                        pTrunkPort = "VFAC-" + pTrunkPort_string + "-1"
                        pTrunkPort_fdn = "MD=CISCO_EPNM!ND=" + nodeName + "!CTP=name=" + pTrunkPort + ";lr=lr-och-data-unit-4"
                        logger.info("Running isTpValid()")
                        if not isTpValid(pTrunkPort_fdn, epnm_ip, epnm_username, epnm_password):
                            print('ERROR: P Trunk Port', pTrunkPort, 'is not found in EPN-M inventory TP list')
                            control = False

    return control

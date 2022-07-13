from commonControls import isNodeValid,isTpValid,is_number,is_4Kport_string_correct
import logging

logger = logging.getLogger('nicola')
logger.setLevel(logging.INFO)

def validate_4K(node_4K, midnode, protection, epnm_ip, epnm_username, epnm_password):
    control = True

    ####
    #### 4K Node name control
    ####

    # Checking if node name is present in input file

    is_name_present = True
    try:
        logger.info("Checking if node_name exists")
        nodeName = node_4K["node_name"]
    except:
        print("\nERROR: Cannot find 4K Node name in input file")
        print("Cannot continue with further controls on this section\n")
        is_name_present = False
        control = False

    # Checking if node name is present in EPNM
    # Reusing is_name_valid as returned value. Considering different control variable

    if is_name_present:
        logger.info("Running isNodeValid()")
        if not isNodeValid(epnm_ip, epnm_username, epnm_password, nodeName):
            print('\nERROR: ' + nodeName, 'is not found in EPN-M inventory')
            print('Cannot continue with further controls on this section\n')
            is_name_present = False
            control = False

    if is_name_present:
        print("Node name is", nodeName)

        # If mid node, skip client port and odu group control !!!!!!!

        ####
        #### 4K Client port control
        ####

        if not midnode:
            logger.info("Node is not midnode")
            # Checking if client port is present in input file
            is_client_port_present = True
            try:
                logger.info("Checking if client_port exists")
                clientPort_string = node_4K["client_port"]
            except:
                print("\nERROR: Cannot find 4K client port in input file")
                print("Continuing with 4K endpoint section controls\n")
                is_client_port_present = False
                control = False

            if is_client_port_present:
                # Checking if client port has correct format
                logger.info("Checking if client port has correct format")
                logger.info("Running is_4Kport_string_correct()")
                if not is_4Kport_string_correct(clientPort_string, 5):
                    print("ERROR: Client Port", clientPort_string, "is not in rack/slot/module/port/sub format")
                    control = False
                # If format is correct, check if client port is present in EPNM
                else:
                    clientPort = "TenGigECtrlr" + clientPort_string
                    clientPort_fdn = "MD=CISCO_EPNM!ND=" + nodeName + "!CTP=name=" + clientPort + ";lr=lr-dsr-10gigabit-ethernet"
                    logger.info("Checking if client port is present in EPNM")
                    logger.info("Running isTpValid()")
                    if not isTpValid(clientPort_fdn, epnm_ip, epnm_username, epnm_password):
                        print('ERROR: Client Port', clientPort, 'is not found in EPN-M inventory TP list')
                        control = False

            ####
            #### 4K ODU Group control
            ####

            # Checking if ODU Group  is present in input file
            is_oduGroup_present = True
            try:
                logger.info("Checking if odu_group exists")
                oduGroup = node_4K["odu_group"]
            except:
                print("\nERROR: Cannot find ODU Group in input file")
                print("Continuing with 4K endpoint section controls\n")
                is_oduGroup_present = False
                control = False

            # Checking if ODU Group is a number and is within 0 .. 65535 range
            if is_oduGroup_present:
                logger.info("Checking if ODU Group is a number and is within 0 .. 65535 range")
                logger.info("Running is_number()")
                if not is_number(oduGroup):
                    print('ERROR: ODU Group', oduGroup, 'is not a number')
                    control = False
                else:
                    if not 0 <= int(oduGroup) <= 65535:
                        print('ERROR: ODU Group', oduGroup, 'is not in range (0..65535)')
                        control = False

        ####
        #### 4K w trunk port control
        ####

        # Checking if trunk port is present in input file
        is_wtrunk_port_present = True
        try:
            logger.info("Checking if w_trunk_port exists")
            wTrunkPort_string = node_4K["w_trunk_port"]
        except:
            print("\nERROR: Cannot find 4K W trunk port in input file")
            print("Continuing with 4K endpoint section controls\n")
            is_wtrunk_port_present = False
            control = False

        # Checking if trunk port has correct format and is present in EPNM
        if is_wtrunk_port_present:
            logger.info("Checking if W trunk port has correct format and is present in EPNM")
            logger.info("Running is_4Kport_string_correct()")
            if not is_4Kport_string_correct(wTrunkPort_string, 4):
                print("ERROR: W Trunk Port", wTrunkPort_string, "is not in rack/slot/module/port format")
                control = False
            else:
                wTrunkPort = "ODU4" + wTrunkPort_string
                wTrunkPort_fdn = "MD=CISCO_EPNM!ND=" + nodeName + "!CTP=name=" + wTrunkPort + ";lr=lr-och-data-unit-4"
                logger.info("Running isTpValid()")
                if not isTpValid(wTrunkPort_fdn, epnm_ip, epnm_username, epnm_password):
                    print('ERROR: W Trunk Port', wTrunkPort, 'is not found in EPN-M inventory TP list')
                    control = False

        if protection == "protected":

        ####
        #### 4K p trunk port control
        ####

        # Checking if trunk port is present in input file
            is_ptrunk_port_present = True
            try:
                logger.info("Checking if p_trunk_port exists")
                pTrunkPort_string = node_4K["p_trunk_port"]
            except:
                print("\nERROR: Cannot find 4K P trunk port in input file")
                print("Continuing with 4K endpoint section controls\n")
                is_ptrunk_port_present = False
                control = False

            # Checking if trunk port has correct format and is present in EPNM
            if is_ptrunk_port_present:
                logger.info("Checking if P trunk port has correct format and is present in EPNM")
                logger.info("Running is_4Kport_string_correct()")
                if not is_4Kport_string_correct(pTrunkPort_string, 4):
                    print("ERROR: P Trunk Port", pTrunkPort_string, "is not in rack/slot/module/port format")
                    control = False
                else:
                    pTrunkPort = "ODU4" + pTrunkPort_string
                    pTrunkPort_fdn = "MD=CISCO_EPNM!ND=" + nodeName + "!CTP=name=" + pTrunkPort + ";lr=lr-och-data-unit-4"
                    logger.info("Running isTpValid()")
                    if not isTpValid(pTrunkPort_fdn, epnm_ip, epnm_username, epnm_password):
                        print('ERROR: P Trunk Port', wTrunkPort, 'is not found in EPN-M inventory TP list')
                        control = False

        ####
        #### 4K W and P tpn control
        ####

        # Checking if tpn  is present in input file
        for tpn in ["w_tpn", "p_tpn"]:

            if tpn == "p_tpn" and protection == "unprotected":
                break

            is_tpn_present = True
            try:
                logger.info("Checking if "+tpn+" exists")
                ctpn = node_4K[tpn]
            except:
                print("\nERROR: Cannot find", tpn, "in input file")
                print("Continuing with 4K endpoint section controls\n")
                is_tpn_present = False
                control = False

            # Checking if TPN is a number and is within 0 .. 10 range
            if is_tpn_present:
                logger.info("Checking if tpn is a number and is within 0 .. 10 range")
                logger.info("Running is_number()")
                if not is_number(ctpn):
                    print('ERROR: TPN', ctpn, 'is not a number')
                    control = False
                else:
                    if not 1 <= int(ctpn) <= 10:
                        print('ERROR: TPN', ctpn, 'is not in range (1..10)')
                        control = False

        ####
        #### 4K xconnect control
        ####

        # Checking if xconnect ID  is present in input file
        is_xConnectID_present = True
        try:
            logger.info("Checking if xconnect_id exists")
            xConnectID = node_4K["xconnect_id"]
        except:
            print("\nERROR: Cannot find xconnect ID in input file")
            is_xConnectID_present = False
            control = False

        # Checking if xconnect ID  is a number and is within 0 .. 65535 range
        if is_xConnectID_present:
            logger.info("Checking if xconnect ID  is a number and is within 0 .. 65535 range")
            logger.info("Running is_number()")
            if not is_number(xConnectID):
                print('ERROR: xconnect ID', xConnectID, 'is not a number')
                control = False
            else:
                if not 1 <= int(xConnectID) <= 32767:
                    print('ERROR: xconnect ID', xConnectID, 'is not in range (1..10)')
                    control = False

    return control

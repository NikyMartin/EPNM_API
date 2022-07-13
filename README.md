# EPN Manager API Examples

### Product overview

The Cisco Evolved Programmable Network (EPN) Manager is an all-in-one management solution for today’s converging packet and optical networks, supporting the Cisco Routed Optical Network architecture

This next-generation product provides device management, network service provisioning, and network assurance across core, edge, aggregation, and access networks consisting of a wide range of Cisco device families

### Main Features
**Graphical user interface:** The rich set of device and network management functions is easily accessible to network operators via a graphical user interface. The following subsections use screenshots of the graphical user interface to illustrate the device and network management functions. The usual home screen of the Cisco EPN Manager is a dashboard view that users can configure to display key information to summarize the status of the network. Users can add, remove, and configure dashlets to suit their needs for a quick view of the network when first logging in.

**Provisioning:** The Cisco EPN Manager helps reduce time to service and, thereby, time to value via point-and-click, wizard-driven provisioning features for end-to-end provisioning flows. Using simplified, end-to-end, point-and-click service provisioning across Layers 0 through 3, services can be easily created and visualized, and human errors can be avoided. Using the RESTCONF API, external applications can programmatically instruct the Cisco EPN Manager to activate network services. 

**Network visibility:** Accurate troubleshooting depends on detailed information about the managed network elements and network services. The Cisco EPN Manager discovers and represents the physical and logical configuration of managed devices. A graphical chassis view with status indications gives network operators a live-live view of the device.

**Monitoring:** The Cisco EPN Manager helps reduce the time to know about network- or service-affecting conditions by correlating raw events and associating alarm conditions with affected managed network elements, network connectivity, and network services. Contextual dashboards and 360-degree views (device and port levels) display the most relevant information for fast and efficient problem identification and remediation.

# Northbound interfaces

### RESTCONF

The EPN Manager implements the RESTCONF API as a standards-based northbound interface for integrating Cisco EPN Manager with a standards-compliant OSS. It is a set of REST services adopted to the RESTCONF/YANG specifications.

The EPN Manager implementation of the RESTCONF/YANG interface supports the retrieval of device inventory, circuit inventory, circuit provisioning, and notifications about respective resource changes and provisioning. This includes:

●     Managed Elements and Equipment Inventory

●     Termination Point and Topological Link Inventory

●     Virtual Connection (RFS) Resource Inventory

●     Service (CFS) Inventory

●     Service Provisioning

●     Inventory Object Create, Delete, and Attribute Value Change (AVC) Notifications

### REST

The EPN Manager REST API is a language-independent interface that can be used by any program or script capable of making HTTP requests. The REST API can be used to retrieve Cisco EPN Manager reports on physical and virtual devices, networks, groups and users, policies, and other monitored entities within your Cisco EPN Manager domains.

### SNMP

To integrate with SNMP-based Fault Manager of Managers, the EPN Manager can forward notifications in SNMPv2 or SNMPv3 format as specified via the CISCO-EPM-NOTIFICATION-MIB. Notifications can also be forwarded to email recipients. The EPN Manager forwards alarms and events that are generated by the processing of received syslogs, traps, and TL/1 alarms to a northbound notification receiver. Alarms of any severity can be forwarded.


Those two examples can be used to retrieve interface details from EPN-M

First script will return details for ethernet interfaces

Second script will return details for IP interfaces

Those script only run for devices in the "Routers" product family. There is a control that terminates 
the execution in case others are detected. Most probably can be extended to others but as of today,
I didnt want to investigate which one.For example, on Optical Networking, it doesnt make much sense 

Both scripts use deviceID in the URI

Before executing them you must execute another script that generates a json file, containing device name and deviceID

Syntax to be used:

```python
python getDeviceID.py <EPNM IP>
python get_ethernet_interfaces.py <EPNM IP> <DEVIDE_NAME>
python get_ip_interfaces.py <EPNM IP> <DEVIDE_NAME>
```
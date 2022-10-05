Those two examples can be used to retrieve device inventory details from EPN-M using either REST or RESTCONF

Output will be slightly different on content

RESTCONF Script will return

      - Module Name
      - Module Description
      - Module Type
      - Part Number
      - Serial Number
      - Product ID

REST Script will return:

      - Module Name
      - Module Description
      - Module Type
      - Serial Number
      - Product ID

REST Script uses deviceID in the URI

It will require a json file to be created first, containing device name and deviceID

Syntax to be used:

RESTCONF

```python
python get_inventory_REST.py <EPNM IP> <DEVIDE_NAME>
```

REST

```python
python getDeviceID.py <EPNM IP>
python get_inventory_RESTCONF.py <EPNM IP> <DEVIDE_NAME>
```
#!/usr/bin/env python

from netmiko import ConnectHandler
from getpass import getpass

RoS = input('Enter Hostname/IP: ')
# user = input('Enter USername')
passd = input('Enter RSA CODE: ')

Cisco1 = {
    'device_type' : 'cisco_ios',
    'host' : RoS,
    'username' : 'casseug',
    'password' : passd,    
}

net_conn = ConnectHandler(**Cisco1)
output = net_conn.send_command("sh ip inter br | e una")
print()
print(output)
print()
net_conn.disconnect()

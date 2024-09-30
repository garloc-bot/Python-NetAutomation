# -*- coding: utf-8 -*-
"""
This script is based on the last issue with DSL Customer X links
where the were down when the BPE was upgrading. This script will  
be able to:

    1. conf t, vpdn softshut on all LNS's
    2. Clear interface *santander interface*
    3. wait 5-10 mins
    4. no vpdn softshut

"""

import re
import time
from netmiko import ConnectHandler
from getpass import getpass
from paramiko.ssh_exception import SSHException
from netmiko.exceptions import NetMikoAuthenticationException
from netmiko.exceptions import NetMikoTimeoutException

user = input('Username: ')
rsa = getpass('RSA: ')

def lns_connect(lns):


    for devices in lns:
        deviceList = {
            'device_type': 'cisco_xe',
            'ip': devices, 
            'username': user,
            'password':  rsa,             
            
        }
    
        try:
            f = open('DSL-interfaces-output.txt', 'a')
            net_conn = ConnectHandler(**deviceList)
            hostname = net_conn.find_prompt()[:-1]
            interfaces = net_conn.send_command("sh ip vrf interfaces | i customer X") # >>>>>>>>>>>>>>> Command to execute

            f.write('> '*15 + hostname + ' <'*15 + '\n')
            print ('* '*15 + hostname +' *'*15)
            print("Connected to "+ hostname +' executing..\n')
            print('Interfaces belong to customer X: \n', interfaces)
            
            for line in interfaces.splitlines():
                if line.startswith('Vi'): #Seaching the Virtual interfaces
                    match = re.search('\S+',line).group()
                    if match:
                        f.writelines('clear interface '+match+'\n') #>>>>>>>>>>> config to send
						net_conn.send_config_set('vpdn softshut') #>>>>>>>>>>> send command "vpdn softshut"
                        net_conn.send_command('clear interface '+match) #>>>>>>>>>>> clear config
            print('tasks done, now sleeping for 10 minutes')
            for i in range(600,0,-1):
                print (i, end=' \r')
                time.sleep(1)
			net_conn.send_config_set('no vpdn softshut') #>>>>>>>>>>> enabling vpdn sessions
            
			f.close()


        except NetMikoAuthenticationException:
            print ('Authentication Failure')
        except NetMikoTimeoutException:
            print('Device not reachable')
        except SSHException:
            print('Make sure SSH is enabled')


        

list_devices = ['x.x.x.x','x.x.x.x','x.x.x.x','x.x.x.x']  #Slugh/Elland Lns devices
print(lns_connect(list_devices))
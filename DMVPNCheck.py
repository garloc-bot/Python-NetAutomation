#!/usr/bin/env python

import sys
from netmiko import ConnectHandler
from getpass import getpass
import pandas as pd
from paramiko.ssh_exception import SSHException
from netmiko.exceptions import NetMikoAuthenticationException
from netmiko.exceptions import NetMikoTimeoutException
from netmiko import ConnLogOnly

#RoS = input('Enter Hostname/IP: ')
# user = input('Enter USername')
passd = input('Enter RSA CODE: ')

hosts_csv = "~/host_csv.csv"

def device_conf(hostname,passd,device_type):

    deviceList = {
        'device_type': device_type,
        #'ip': ip,
        'host': hostname,
        'username': 'casseug',
        'password': passd,     
    }

    print ('\n #### Connecting to ' + hostname + ' ####\n')
    try:
        net_conn = ConnectHandler(**deviceList)
        print("Connected to "+ hostname + ' executing..\n')

        conn = ConnLogOnly(**deviceList)
        if conn is None:
            sys.exit("Loggin FAILED")
        print(conn.find_prompt())
        conn.disconnect

        

        #Number total of DMVPN tunnels
        Tnhrp = net_conn.send_command("sh ip nhrp | count Tunnel")
        print()
        print("Total DMVPN tunnels: " + Tnhrp.split().pop(-1) + "\n")
        #number of dmvpn tunnels UP
        UPnhrp = net_conn.send_command("sh dmvpn | count UP")
        print("Total DMVPN tunnels UP: " + UPnhrp.split().pop(-1) + "\n")
        #number of bgp session
        SBGP = net_conn.send_command("sh bgp all neighbors | count BGP state")
        print("Total BGP sesions: " + SBGP.split().pop(-1) + "\n")
        #number of bgp session up
        UPBGP = net_conn.send_command("sh bgp all neighbors | count up for")
        print("Total BGP sesions UP: " + UPBGP.split().pop(-1) + "\n")
        net_conn.disconnect()
        
    except NetMikoAuthenticationException:
        print ('Authentication Failure')
        #continue
    except NetMikoTimeoutException:
        print('Device not reachable')
        #continue
    except SSHException:
        print('Make sure SSH is enabled')
        #continue

def device_detail(hosts_csv):
    df = pd.read_csv('hosts_csv.csv')
    for index, row in df.iterrows():
        device_type=row["device_type"]
        hostname=row["Hname"]
        #ip=["IP"]

        device_conf(hostname,passd,device_type)

device_detail(hosts_csv)



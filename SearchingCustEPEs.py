#!/usr/bin/env python

from netmiko import ConnectHandler
from getpass import getpass
import pandas as pd
from paramiko.ssh_exception import SSHException
from netmiko.exceptions import NetMikoAuthenticationException
from netmiko.exceptions import NetMikoTimeoutException
from datetime import datetime
import re

print(datetime.now())
passd = input('Enter RSA CODE: ')

hosts_csv = "~/host_csv.csv"
CPE = input("please enter the CPE hostname: ")
#pprt1475220001

def device_conf(hostname,passd,device_type,ip,kind):

    deviceList = {
        'device_type': device_type,
        'ip': ip,
        'host': hostname,
        'username': 'casseug',
        'password': passd,     
    }
    
    if kind == "bpe":
          try:
        
              print ('\n ***************************** ' + hostname + ' *****************************')
              net_conn = ConnectHandler(**deviceList)
              #Checking if CPE is there
              output = net_conn.send_command("show interface description | i " + CPE)
              net_conn.disconnect()
              print(output)

          except NetMikoAuthenticationException:
                print ('Authentication Failure')
          except NetMikoTimeoutException:
                print(hostname +' '+ ip + ' Device not reachable')
          except SSHException:
                print('Make sure SSH is enabled')
    return kind

def device_detail(hosts_csv):
    df = pd.read_csv('hosts_csv.csv')
    for index, row in df.iterrows():
        device_type=row["device_type"]
        hostname=row["Hname"]
        kind=row["kind"]
        ip=row["IP"]


        device_conf(hostname,passd,device_type,ip,kind)

device_detail(hosts_csv)

#!/usr/bin/env python

import sys
from netmiko import ConnectHandler
from getpass import getpass
from paramiko.ssh_exception import SSHException
from netmiko.exceptions import NetMikoAuthenticationException
from netmiko.exceptions import NetMikoTimeoutException
from netmiko import ConnLogOnly
from datetime import datetime


#RoS = input('Enter Hostname/IP: ')
user = input('Enter USername')

print(datetime.now())
passd = input('Enter RSA CODE: ')

hosts_csv = "~/host_csv.csv"

def device_conf(hostname,passd,device_type,kind,ip):

    deviceList = {
        'device_type': device_type,
        'ip': ip,
        'host': hostname,
        'username': user,
        'password': passd,     
    }
    
    print ('\n ***************************** ' + hostname + ' *****************************')
    try:
        net_conn = ConnectHandler(**deviceList)

        print("Connected to "+ hostname + ' executing..\n')

        if kind == "dmvpn":

            #Number total of DMVPN tunnels
            Tnhrp = net_conn.send_command("sh ip nhrp | count Tunnel")
            print()
            print("Total DMVPN tunnels: " + Tnhrp.split().pop(-1))
            #number of dmvpn tunnels UP
            UPnhrp = net_conn.send_command("sh dmvpn | count UP")
            print("Total DMVPN tunnels UP: " + UPnhrp.split().pop(-1))
            #number of bgp session
            SBGP = net_conn.send_command("sh bgp all neighbors | count BGP state")
            print("Total BGP sesions: " + SBGP.split().pop(-1))
            #number of bgp session up
            UPBGP = net_conn.send_command("sh bgp all neighbors | count up for")
            print("Total BGP sesions UP: " + UPBGP.split().pop(-1))

        elif kind == "lns":
            #Number total of VPDN sessions
            Tvpdn = net_conn.send_command("sh vpdn session | i To")
            print()
            print(Tvpdn)
            #VPDN Tunnels
            Svpdn = net_conn.send_command("sh vpdn Tunnel | i To")
            print(Svpdn)
            #LNS connections
            Clns = net_conn.send_command("sh user wide | c Vi")
            print("Total LNS sessions: " + Clns.split().pop(-1))
            #number of bgp session
            SBGP = net_conn.send_command("sh bgp all neighbors | count BGP state")
            print("Total BGP sessions: " + SBGP.split().pop(-1))
            #number of bgp session up
            UPBGP = net_conn.send_command("sh bgp all neighbors | count up for")
            print("Total BGP sessions UP: " + UPBGP.split().pop(-1))

        elif kind == "isg":
            #number of bgp session
            SBGP = net_conn.send_command("sh bgp all neighbors | count BGP state")
            print("Total BGP sessions: " + SBGP.split().pop(-1))
            #number of bgp session up
            UPBGP = net_conn.send_command("sh bgp all neighbors | count up for")
            print("Total BGP sessions UP: " + UPBGP.split().pop(-1))
            #number of buncies sesion in BGP
            BunBGP = net_conn.send_command("sh bgp all summ | ex w|d")
            with open('FlapsPeerISG.txt', 'w') as temp:
                for line in BunBGP:
                    temp.write(line)

            with open('FlapsPeerISG.txt', 'r') as f:
                omited = f.readlines()[10:]
                print("The peers Bouncing or UP within last 24hrs are: ")
                i = 11
                for line in omited:
                    print(line)
                    i+=1

            temp.close()
        net_conn.disconnect()
            
    except NetMikoAuthenticationException:
        print ('Authentication Failure')
        #continue
    except NetMikoTimeoutException:
        print('Device not reachable')
        #continue
    except SSHException:
        print('Make sure SSH is enabled')


def device_detail(hosts_csv):
    df = pd.read_csv('hosts_csv.csv')
    for index, row in df.iterrows():
        device_type=row["device_type"]
        hostname=row["Hname"]
        kind=row["kind"]
        ip=row["IP"]


        device_conf(hostname,passd,device_type,kind,ip)

device_detail(hosts_csv)



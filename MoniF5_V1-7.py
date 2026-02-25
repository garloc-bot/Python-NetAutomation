#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
 *** MoniF5 - F5 Pool statistics monitor (single device, user-selectable) ***

Version 1.7 - date: 25-02-2025

Description:
- Connects via SDK to the F5 BIG-IP device and retrieves information from the Request GET API
- Pulls:
  * Hostname, F5 software version and HA status
  * Current pool statistics (current connections)
  * number of pools, virtual servers and nodes
  * graphs of active pools and pools with more than 100 connections
- The information is printed to the console and also saved to a text file and a PNG chart for future reference.
- This version allows selection of device from predefined lists
- This version allow user to run one device at a time

Version 1.7 changes:
- Save the chart to a file (PNG) and the resume details to a text file for future reference.
- Save the chart and text file with a timestamp in the filename to avoid overwriting previous files.
- Added a grid to the charts for better readability.
- Added a timestamp to the chart for reference.
- Improved the text file output to include more details about the pools and their current connections.
- Menu to select the device to monitor from a predefined list of devices.

Next versions may include:
- Connect to multiple devices and compare the results in a single chart or report
- Add more statistics to the report (eg. CPU usage, memory usage, etc.)
- Add more detailed information about the pools and their members (eg. status, response time, etc.)
- Graph the changes in pool statistics over time (eg. current connections over the last hour)
- Other requests from users, feel free to reach out with suggestions or feedback!

Author: Garlo Casseus (with a bit of help from AI :))
'''

import requests
requests.packages.urllib3.disable_warnings()
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from datetime import datetime
from f5.bigip import ManagementRoot

device_group = {
		"1": {"ip": "10.57.193.168", "name": "manch-f5-01", "site": "Manchester"},
		"2": {"ip": "10.57.193.149", "name": "manch-f5-02", "site": "Manchester"},
		"3": {"ip": "10.47.211.168", "name": "londr-f5-01", "site": "Londres"},
		"4": {"ip": "10.47.211.149", "name": "londr-f5-02", "site": "Londres"},
		}
		
print("\nAvailable F5: ")
f5s = device_group
for iddevice, name in f5s.items():
	print(f"{iddevice}. {name['name']:15} < ----- > {name['ip']:12} < ----- > {name['site']}")
print("=" * 60)

selected_id = input("Select the F5 by entering the corresponding number: ")
if selected_id in device_group:
    selected_f5 = device_group[selected_id]
else:
    print("Invalid selection. Please run the program again and select a valid number.")
    exit(1)

BIGIP = selected_f5['ip']
USER = input("Username: ")
PASS = input("RSA: ")

url = f"https://{BIGIP}/mgmt/tm/ltm/pool"

try:
    mgmt = ManagementRoot(BIGIP, USER, PASS)
    ltm = mgmt.tm.ltm

    hotname = mgmt.tm.sys.global_settings.load().hostname
    print(f"Connected to BIG-IP: {hotname}\nversion: {mgmt.tmos_version}\nIP: {BIGIP}\n")

    print(f"Failover states:") 
    device_info = mgmt.tm.cm.devices.get_collection()
    for device in device_info:
        print(f"Device Name: {device.name}, Failover State: {device.failoverState}")

    pools = ltm.pools.get_collection()
    virtuals = ltm.virtuals.get_collection()
    nodes = ltm.nodes.get_collection()
    print('#'*50 + '\n')
    print(f"Found {len(pools)} pools, {len(virtuals)} virtual servers, and {len(nodes)} nodes.\n")

    poolUpCount = 0
    for pool in pools:
      if "none" in pool.serviceDownAction:
        poolUpCount += 1
        # print(f"Pool: {pool.name}, Load Balancing Method: {pool.loadBalancingMode}, Down Services: {pool.serviceDownAction}") # *Optional to show all pools with no down services, but it can be a lot of information if you have many pools.
    print(f"Pools with no down services: {poolUpCount} out of {len(pools)} total pools.\n")
 
    #for pool in pools:
    #  if "none" not in pool.serviceDownAction:
    #    print(f"The following are down: {pool.name}, Down Services: {pool.serviceDownAction}")
 
    print(f"Number of pools with down services: {len(pools) - poolUpCount} out of {len(pools)} total pools.\n")
    print('#'*50 + '\n')

# *Optional to save all pool details to a text file, but it can be a lot of information if you have many pools.

    #with open(f'pool_details_{hostname}_{datetime.now():%Y-%m-%d_%H-%M-%S}.txt', 'w') as f:
    #    f.write(f"Pool details for BIG-IP: {hotname} (IP: {BIGIP})\n")
    #    f.write(f"Generated on: {datetime.now():%Y-%m-%d %H:%M:%S}\n")
    #    f.write(f"Total Pools: {len(pools)}\n")
    #    f.write(f"Pools with no down services: {poolUpCount}\n")
    #    f.write(f"Pools with down services: {len(pools) - poolUpCount}\n")
    #    f.write('-' * 40 + '\n')
    #    for pool in pools:
    #        f.write(f"Pool Name: {pool.name}\n")
    #        f.write(f"Load Balancing Method: {pool.loadBalancingMode}\n")
    #        f.write(f"Down Services: {pool.serviceDownAction}\n")
    #        f.write('-' * 40 + '\n')

except Exception as e:
    print(f"Failed to connect to F5 BIG-IP at {BIGIP}: {e}")
    exit(1)


pools = requests.get(url, auth=(USER, PASS), verify=False).json()['items']

# Device failover status
device_info = mgmt.tm.cm.devices.get_collection()
for device in device_info:
    failover_status = f"Device Name: {device.name}, Failover State: {device.failoverState}"
    
hostname = mgmt.tm.sys.global_settings.load().hostname
version = mgmt.tmos_version

print("Loading active sessions per pools...")

active_pools = {}
active_poolsG1 = {}

for pool in pools:
    pool_name = pool['name']
    members_url = f"{url}/{pool_name}/members/stats"
    stats = requests.get(members_url, auth=(USER, PASS), verify=False).json()

    total = 0
    for entry in stats['entries'].values():
        cur = entry['nestedStats']['entries']['serverside.curConns']['value']
        total += cur

    if total > 0 and total < 100:
        active_pools[pool_name] = total
        print(f"Pool: {pool_name}, Total: {total}")
    elif total >= 100:
        active_poolsG1[pool_name] = total
        print(f"Pool: {pool_name}, Total: {total}")
        
Now = f"{datetime.now():%Y-%m-%d_%H:%M:%S}"

name = list(active_pools.keys())
values = list(active_pools.values())

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10), constrained_layout=True)    

ax1.barh(name, values, color='blue')
ax1.set_ylabel('Pool Name')
ax1.set_xlabel('Current Connections')
ax1.set_title('Active Pools and Current Connections')
ax1.grid(True) # Add grid for better readability

nameG1 = list(active_poolsG1.keys())
valuesG1 = list(active_poolsG1.values())

ax2.bar(nameG1, valuesG1, color='red')
ax2.set_xlabel('Pool Name')
ax2.set_ylabel('Current Connections')
ax2.set_title('Active Pools with Connections > 100')
ax2.tick_params(axis='x', rotation=45)

plt.figtext(0.5, 0.04, f'Generated by F5 SDK Script: {Now}', ha='center', fontsize=10, color='black', style='italic', alpha=0.7, fontfamily='monospace')
plt.grid(True)
plt.savefig(f'active_pools_combined_{Now}.png') # Save the Chart to a file
plt.show()

with open(f'Resume_pools_{hostname}_{Now}.txt', 'w') as f: # Save the resume details to a text file
    f.write(f"Pool details for BIG-IP: {hostname} (IP: {BIGIP})\n")
    f.write(f"version: {version}\n")
    f.write(f"{failover_status}\n")
    f.write(f"Generated on: {datetime.now():%Y-%m-%d %H:%M:%S}\n")
    f.write('-' * 50 + '\n')
    f.write(f"Total Pools: {len(pools)}\n")
    f.write(f"Active Pools: {len(active_pools)}\n")
    f.write(f"Active Pools with Connections > 100: {len(active_poolsG1)}\n")
    f.write(f"Active Pools with Connections <= 100: {len(active_pools) - len(active_poolsG1)}\n")
    f.write(f"Active Pools with no connections: {len(pools) - len(active_pools)}\n")
    f.write('-' * 50 + '\n')
    f.write(f"Active Pools with Current Connections (Generated on: {Now})\n")
    f.write('-' * 50 + '\n')
    for pool_name, total in active_pools.items():
        f.write(f"Pool: {pool_name}, Current Connections: {total}\n")
    f.write('\nActive Pools with Connections > 100:\n')
    f.write('-' * 50 + '\n')
    for pool_name, total in active_poolsG1.items():
        f.write(f"Pool: {pool_name}, Current Connections: {total}\n")

print(f"\n *** Resume details saved to Resume_pools_{hostname}_{Now}.txt ***")
print(f"\n *** Chart saved to active_pools_combined_{Now}.png *** \n")
print("Script execution completed.")

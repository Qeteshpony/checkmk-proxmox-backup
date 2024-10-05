#!/usr/bin/env python3

import json
import os
import sys
import subprocess
import time
import configparser
from datetime import datetime

# read config
config = configparser.ConfigParser()
config.read("/root/proxmoxbackupclient.ini")

datafile = "/tmp/backupstatus.json"

# warn and critical levels for backup-age in seconds
warnage = 60*60*24 + 60*60  # 1 day and 1 hour
critage = 60*60*24*7 + 60*60  # 1 week and 1 hour

def getClientData(namespace=False) -> dict:
    # Call the proxmox backup client to get information about stored backups
    for name, value in config["environment"].items():
        os.environ[name.upper()] = value

    # Get the results and check if the command was successful - exit if not
    if namespace:
        result = subprocess.run((config["paths"]["backupclient"], "list", "--output-format", "json", "--ns", namespace), capture_output=True)
    else:
        result = subprocess.run((config["paths"]["backupclient"], "list", "--output-format", "json"), capture_output=True)
    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        print(result.stderr.decode(), file=sys.stderr)
        exit(1)

if __name__ == "__main__":
    try:
        # load stored timestamps if possible
        with open(datafile, "r") as f:
            storeddata = json.load(f)
    except FileNotFoundError:
        storeddata = {}
    changed = False

    data = getClientData()
    if "namespaces" in config["paths"]:
        for name in config["paths"]["namespaces"].split(','):
            data += getClientData(name.strip())
    for host in data:
        # get the data for each stored backup and process it
        timestamp = host.get("last-backup")
        hostname = f'{host.get("backup-type")}/{host.get("backup-id")}'
        if timestamp is None:
            status = 2
            date = "unknown"
        else:
            # compare reported timestamp to stored one and update/overwrite if necessary
            if hostname in storeddata.keys():
                if timestamp < storeddata[hostname]:
                    timestamp = storeddata[hostname]
                elif timestamp > storeddata[hostname]:
                    storeddata[hostname] = timestamp
                    changed = True
            else:
                storeddata[hostname] = timestamp
                changed = True

            date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
            if timestamp + critage < time.time():
                status = 2
            elif timestamp + warnage < time.time():
                status = 1
            else:
                status = 0
        print(f'{status} "Backup Status {hostname}" - Last backup: {date}, Backup-Count: {host.get("backup-count")}, Owner: {host.get("owner")}')
    if changed:
        # store the new data if there were any changes
        with open(datafile, "w") as f:
            json.dump(storeddata, f)


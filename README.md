# Local checkmk agent extension for reading the status of stored backups on a Proxmox Backup Server

## Installation

- Create a new user on your Proxmox Backup Server in the pbs realm and give it DatastoreAudit permissions 
for your datastore  

- Copy `proxmoxbackupclient.example.ini` to `/root/proxmoxbackupclient.ini` and edit it to set the needed values

- Copy `proxmoxbackupclient.py` to `/usr/lib/check_mk_agent/local/proxmoxbackupclient.py` and make it executable 
with `chmod +x /usr/lib/check_mk_agent/local/proxmoxbackupclient.py`

- Running a service discovery in checkmk for the PBS should now find a new service for every stored backup. 

That's it... 
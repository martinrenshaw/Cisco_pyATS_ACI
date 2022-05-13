# Cisco ACI state testing with python and Cisco pyATS

## python file

run the `devnet_aci.py` file, this will output Tenanst, fabric devices, mac_endpoints, ip_endpoints & the RIB to stdout and a text file.

## pyATS - to ACI rest
## Installation

Install pyATS|Genie and Rest Connector.
```
pip install 'pyats[full]' rest.connector
pip install genie.libs.sdk --upgrade --pre


```

## Running

By pyats run job command
```
pyats run job job.py --testbed-file aci_devnet_sandbox.yaml --trigger-datafile pre_trigger_datafile.yaml --html-logs pre_snapshots

(configure by Ansible)

pyats run job job.py --testbed-file aci_devnet_sandbox.yaml --trigger-datafile post_trigger_datafile.yaml --html-logs post_snapshots
```

HTML report and JSON files (snapshots) will be generated under `pre|post_snapshots` folders.

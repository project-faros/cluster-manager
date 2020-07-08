# NETWORK ROUTER CONFIGURATION
export ROUTER_LAN_INT='[]'
export SUBNET=192.168.8.0
export SUBNET_MASK=24
export ALLOWED_SERVICES='["SSH to Bastion"]'
# CLUSTER CONFIGURATION
export ADMIN_PASSWORD='admin'
export PULL_SECRET=''
# CLUSTER HARDWARE
export MGMT_PROVIDER='ilo'
export MGMT_USER='Administrator'
export MGMT_PASSWORD='ilo-pass'
export BASTION_MGMT_MAC='ff:ff:ff:ff:ff:ff'
export CP_NODES='[{"name": "node-0", "mac": "ff:ff:ff:ff:ff:ff", "mgmt_mac": "ff:ff:ff:ff:ff:ff"}, {"name": "node-1", "mac": "ff:ff:ff:ff:ff:ff", "mgmt_mac": "ff:ff:ff:ff:ff:ff"}, {"name": "node-2", "mac": "ff:ff:ff:ff:ff:ff", "mgmt_mac": "ff:ff:ff:ff:ff:ff"}]'

# ROUTER CONFIGURATION
export ROUTER_LAN_INT='[]'
export SUBNET=192.168.8.0
export SUBNET_MASK=24
export ALLOWED_SERVICES='["SSH to Bastion"]'
# CLUSTER CONFIGURATION
export ADMIN_PASSWORD='admin'
export PULL_SECRET=''
# CLUSTER DNS CONFIGURATION
export DNS_PROVIDER='openwrt'
export DNS_HOST_NAME='router'
export DNS_USER='root'
export DNS_PASSWORD=''
# CLUSTER DHCP CONFIGURATION
export DHCP_PROVIDER='openwrt'
export DHCP_HOST_NAME='router'
export DHCP_USER='root'
export DHCP_PASSWORD=''
# CLUSTER ARCHITECTURE
export MGMT_PROVIDER='ilo'
export MGMT_USER='Administrator'
export MGMT_PASSWORD='ilo-pass'
export CP_NODES='[{"name": "node-0", "mac": "00:fd:45:ff:ff:ff", "mgmt_mac": "00:fd:45:ff:ff:ff"}, {"name": "node-1", "mac": "00:fd:45:ff:ff:ff", "mgmt_mac": "00:fd:45:ff:ff:ff"}, {"name": "node-2", "mac": "00:fd:45:ff:ff:ff", "mgmt_mac": "00:fd:45:ff:ff:ff"}]'

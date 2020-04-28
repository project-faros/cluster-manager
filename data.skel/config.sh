# CLUSTER CONFIGURATION
export CLUSTER_NAME='beaconXX'
export CLUSTER_DOMAIN='faros.site'
export ADMIN_PASSWORD='admin'
export USER_PASSWORD='user'
# BASTION NODE CONFIGURATION
export BASTION_HOST_NAME='bastion'
export BASTION_IP_ADDR='192.168.8.50'
export BASTION_SSH_USER='core'
# CLUSTER DNS CONFIGURATION
export DNS_PROVIDER='openwrt'
export DNS_HOST_NAME='router'
export DNS_CREDENTIALS='root'
# CLUSTER DHCP CONFIGURATION
export DHCP_PROVIDER='openwrt'
export DHCP_HOST_NAME='router'
export DHCP_CREDENTIALS='root'
# CLUSTER ARCHITECTURE
export MGMT_PROVIDER='ilo'
export IP_POOL='192.168.8.64/27'
export CP_NODES='[{"name": "node-0", "mac": "00:fd:45:ff:ff:ff", "mgmt_mac": "00:fd:45:ff:ff:ff"}, {"name": "node-1", "mac": "00:fd:45:ff:ff:ff", "mgmt_mac": "00:fd:45:ff:ff:ff"}, {"name": "node-2", "mac": "00:fd:45:ff:ff:ff", "mgmt_mac": "00:fd:45:ff:ff:ff"}]'

#!/usr/bin/env python3
import argparse
from collections import defaultdict
import ipaddress
import json
import os
import sys
import pickle

SSH_PRIVATE_KEY = '/data/id_rsa'
IP_RESERVATIONS = '/data/ip_addresses'


class InventoryGroup(object):

    def __init__(self, parent, name):
        self._parent = parent
        self._name = name

    def add_group(self, name, **groupvars):
        return(self._parent.add_group(name, self._name, **groupvars))

    def add_host(self, name, hostname=None, **hostvars):
        return(self._parent.add_host(name, self._name, hostname, **hostvars))

    def host(self, name):
        return self._parent.host(name)


class Inventory(object):

    _modes = ['list', 'host', 'verify', 'none']
    _data = {"_meta": {"hostvars": defaultdict(dict)}}

    def __init__(self, mode=0, host=None):
        if mode==1:
            # host info requested
            # current, only list and none are implimented
            raise NotImplementedError()

        self._mode = mode
        self._host = host

    def __del__(self):
        if self._mode == 0:
            print(self.to_json())

    def host(self, name):
        return self._data['_meta']['hostvars'].get(name)

    def group(self, name):
        if name in self_data:
            return InventoryGroup(self, name)
        else:
            return None

    def add_group(self, name, parent=None, **groupvars):
        self._data[name] = {'hosts': [], 'vars': groupvars, 'children': []}

        if parent:
            if parent not in self._data:
                self.add_group(parent)
            self._data[parent]['children'].append(name)

        return InventoryGroup(self, name)

    def add_host(self, name, group=None, hostname=None, **hostvars):
        if not group:
            group = 'all'
        if group not in self._data:
            self.add_group(group)

        if hostname:
            hostvars.update({'ansible_host': hostname})

        self._data[group]['hosts'].append(name)
        self._data['_meta']['hostvars'][name].update(hostvars)

    def to_json(self):
        return json.dumps(self._data, sort_keys=True,
            indent=4, separators=(',', ': '))


class IPAddressManager(dict):

    def __init__(self, save_file, subnet, subnet_mask):
        super().__init__()
        self._save_file = save_file

        # parse the subnet definition into a static and dynamic pool
        subnet = ipaddress.ip_network(f'{subnet}/{subnet_mask}', strict=False)
        divided = subnet.subnets()
        self._static_pool = next(divided)
        self._dynamic_pool = next(divided)
        self._generator = self._static_pool.hosts()

        # calculate reverse dns zone
        classful_prefix = [32, 24, 16, 8, 0]
        classful = subnet
        while classful.prefixlen not in classful_prefix:
            classful = classful.supernet()
        host_octets = classful_prefix.index(classful.prefixlen)
        self._reverse_ptr_zone = \
            '.'.join(classful.reverse_pointer.split('.')[host_octets:])

        # load the last saved state
        try:
            restore = pickle.load(open(save_file, 'rb'))
        except:
            restore = {}
        self.update(restore)

        # reserve the first ip for the bastion
        _ = self['bastion']

    def __getitem__(self, key):
        key = key.lower()
        try:
            return super().__getitem__(key)
        except KeyError:
            new_ip = self._next_ip()
            self[key] = new_ip
            return new_ip

    def __setitem__(self, key, value):
        return super().__setitem__(key.lower(), value)

    def _next_ip(self):
        used_ips = list(self.values())
        loop = True

        while loop:
            new_ip = next(self._generator).exploded
            loop = new_ip in used_ips
        return new_ip

    def get(self, key, value=None):
        if value and value not in self.values():
            self[key] = value
        return self[key]

    def save(self):
        with open(self._save_file, 'wb') as handle:
            pickle.dump(dict(self), handle)

    @property
    def static_pool(self):
        return str(self._static_pool)

    @property
    def dynamic_pool(self):
        return str(self._dynamic_pool)

    @property
    def reverse_ptr_zone(self):
        return str(self._reverse_ptr_zone)


class Config(object):
    _last_key = None

    def __getitem__(self, key):
        return self.get(key)

    def get(self, key, default=None):
        self._last_key = key
        return os.environ.get(key, default).replace('\\n', '\n')

    @property
    def error(self):
        return f'\n\033[31mThere was an error parsing the configuration\nPlease check the value for {self._last_key}.\033[0m\n\n'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', action = 'store_true')
    parser.add_argument('--verify', action = 'store_true')
    parser.add_argument('--host', action = 'store')
    args = parser.parse_args()
    return args

def main(config, ipam, inv):
    # GATHER INFORMATION FOR EXTRA NODES
    extra_nodes = json.loads(config.get('EXTRA_NODES', '[]'))
    for idx, item in enumerate(extra_nodes):
        addr = ipam.get(item['mac'], item.get('ip'))
        extra_nodes[idx].update({'ip': addr})

    # CREATE INVENTORY
    inv.add_group('all', None,
        ansible_ssh_private_key_file=SSH_PRIVATE_KEY,
        cluster_name=config['CLUSTER_NAME'],
        cluster_domain=config['CLUSTER_DOMAIN'],
        admin_password=config['ADMIN_PASSWORD'],
        pull_secret=json.loads(config['PULL_SECRET']),
        mgmt_provider=config['MGMT_PROVIDER'],
        mgmt_user=config['MGMT_USER'],
        mgmt_password=config['MGMT_PASSWORD'],
        install_disk=config['BOOT_DRIVE'],
        loadbalancer_vip=ipam['loadbalancer'],
        dynamic_ip_range=ipam.dynamic_pool,
        reverse_ptr_zone=ipam.reverse_ptr_zone,
        subnet=config['SUBNET'],
        subnet_mask=config['SUBNET_MASK'],
        wan_ip=config['BASTION_IP_ADDR'],
        extra_nodes=extra_nodes,
        ignored_macs=config['IGNORE_MACS'],
        dns_forwarders=[item['server'] for item in json.loads(config.get('DNS_FORWARDERS', '[]'))],
        proxy=config['PROXY']=="True",
        proxy_http=config.get('PROXY_HTTP', ''),
        proxy_https=config.get('PROXY_HTTPS', ''),
        proxy_noproxy=[item['dest'] for item in json.loads(config.get('PROXY_NOPROXY', '[]'))],
        proxy_ca=config.get('PROXY_CA', ''))

    infra = inv.add_group('infra')
    router = infra.add_group('router',
        wan_interface=config['WAN_INT'],
        lan_interfaces=json.loads(config['ROUTER_LAN_INT']),
        all_interfaces=config['BASTION_INTERFACES'].split(),
        allowed_services=json.loads(config['ALLOWED_SERVICES']))
    # ROUTER INTERFACES
    router.add_host('wan',
        config['BASTION_IP_ADDR'],
        ansible_become_pass=config['ADMIN_PASSWORD'],
        ansible_ssh_user=config['BASTION_SSH_USER'])
    router.add_host('lan',
        ipam['bastion'],
        ansible_become_pass=config['ADMIN_PASSWORD'],
        ansible_ssh_user=config['BASTION_SSH_USER'])
    # DNS NODE
    router.add_host('dns',
        ipam['bastion'],
        ansible_become_pass=config['ADMIN_PASSWORD'],
        ansible_ssh_user=config['BASTION_SSH_USER'])
    # DHCP NODE
    router.add_host('dhcp',
        ipam['bastion'],
        ansible_become_pass=config['ADMIN_PASSWORD'],
        ansible_ssh_user=config['BASTION_SSH_USER'])
    # LOAD BALANCER NODE
    router.add_host('loadbalancer',
        ipam['loadbalancer'],
        ansible_become_pass=config['ADMIN_PASSWORD'],
        ansible_ssh_user=config['BASTION_SSH_USER'])

    # BASTION NODE
    bastion = infra.add_group('bastion_hosts')
    bastion.add_host(config['BASTION_HOST_NAME'],
            ipam['bastion'],
            ansible_become_pass=config['ADMIN_PASSWORD'],
            ansible_ssh_user=config['BASTION_SSH_USER'])

    # CLUSTER NODES
    cluster = inv.add_group('cluster')
    # BOOTSTRAP NODE
    ip = ipam['bootstrap']
    cluster.add_host('bootstrap', ip,
            ansible_ssh_user='core',
            node_role='bootstrap')
    # CLUSTER CONTROL PLANE NODES
    cp = cluster.add_group('control_plane', node_role='master')
    node_defs = json.loads(config['CP_NODES'])
    for count, node in enumerate(node_defs):
        ip = ipam[node['mac']]
        mgmt_ip = ipam[node['mgmt_mac']]
        cp.add_host(node['name'], ip,
           mac_address=node['mac'],
           mgmt_mac_address=node['mgmt_mac'],
           mgmt_hostname=mgmt_ip,
           ansible_ssh_user='core',
           cp_node_id=count)
        if node.get('install_drive'):
            cp.host(node['name'])['install_disk'] = node['install_drive']

    # VIRTUAL NODES
    virt = inv.add_group('virtual',
            mgmt_provider='kvm',
            mgmt_hostname='bastion',
            install_disk='vda')
    virt.add_host('bootstrap')

    # MGMT INTERFACES
    mgmt = inv.add_group('management',
        ansible_ssh_user=config['MGMT_USER'],
        ansible_ssh_pass=config['MGMT_PASSWORD'])
    for count, node in enumerate(node_defs):
        mgmt.add_host(node['name'] + '-mgmt', ipam[node['mgmt_mac']])


if __name__ == "__main__":
    # PARSE ARGUMENTS
    args = parse_args()
    if args.list:
        mode = 0
    elif args.verify:
        mode = 2
    else:
        mode = 1

    # INITIALIZE CONFIG HANDLER
    config = Config()

    # INTIALIZE IPAM
    ipam = IPAddressManager(
        IP_RESERVATIONS,
        config['SUBNET'], config['SUBNET_MASK'])

    # INITIALIZE INVENTORY
    inv = Inventory(mode, args.host)

    # CREATE INVENTORY
    try:
        main(config, ipam, inv)
    except Exception as e:
        if mode == 2:
            sys.stderr.write(config.error)
            sys.exit(1)
        raise(e)

    # DONE
    ipam.save()
    sys.exit(0)

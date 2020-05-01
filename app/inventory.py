#!/usr/bin/env python3
import argparse
from collections import defaultdict
import ipaddress
import json
import os
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


class Inventory(object):

    _modes = ['list', 'host', 'none']
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

    def __init__(self, save_file, pool):
        super().__init__()
        self._pool = pool
        self._save_file = save_file

        subnet = ipaddress.ip_network(pool)
        self._generator = subnet.hosts()

        try:
            restore = pickle.load(open(save_file, 'rb'))
        except:
            restore = {}
        self.update(restore)

    def __getitem__(self, key):
        key = key.lower()
        try:
            return super().__getitem__(key)
        except KeyError:
            new_ip = self._next_ip()
            self[key] = new_ip
            return new_ip

    def _next_ip(self):
        used_ips = list(self.values())
        loop = True

        while loop:
            new_ip = next(self._generator).exploded
            loop = new_ip in used_ips
        return new_ip

    def save(self):
        with open(self._save_file, 'wb') as handle:
            pickle.dump(dict(self), handle)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', action = 'store_true')
    parser.add_argument('--host', action = 'store')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    inv = Inventory(0 if args.list else 1, args.host)
    inv.add_group('all', None,
        ansible_ssh_private_key_file=SSH_PRIVATE_KEY,
        cluster_name=os.environ['CLUSTER_NAME'],
        cluster_domain=os.environ['CLUSTER_DOMAIN'],
        admin_password=os.environ['ADMIN_PASSWORD'],
        user_password=os.environ['USER_PASSWORD'],
        pull_secret=json.loads(os.environ['PULL_SECRET']),
        mgmt_provider=os.environ['MGMT_PROVIDER'],
        install_disk='sda')

    infra = inv.add_group('infra')
    # BASTION NODE
    bastion = infra.add_group('bastion_hosts')
    bastion.add_host(os.environ['BASTION_HOST_NAME'],
            os.environ['BASTION_IP_ADDR'],
            ansible_become_pass=os.environ['USER_PASSWORD'],
            ansible_ssh_user=os.environ['BASTION_SSH_USER'])
    # DNS NODE
    infra.add_host('dns',
          os.environ['DNS_HOST_NAME'],
          provider=os.environ['DNS_PROVIDER'],
          credentials=os.environ['DNS_CREDENTIALS'],
          ansible_ssh_user=os.environ['DNS_CREDENTIALS'].split(':', 1)[0])
    # DHCP NODE
    infra.add_host('dhcp',
          os.environ['DHCP_HOST_NAME'],
          provider=os.environ['DHCP_PROVIDER'],
          credentials=os.environ['DHCP_CREDENTIALS'],
          ansible_ssh_user=os.environ['DHCP_CREDENTIALS'].split(':', 1)[0])

    cluster = inv.add_group('cluster')
    ipam = IPAddressManager(
        IP_RESERVATIONS,
        os.environ['IP_POOL'])
    # BOOTSTRAP NODE
    ip = ipam['bootstrap']
    cluster.add_host('bootstrap', ip,
            ansible_ssh_user='core',
            node_role='bootstrap')
    # CLUSTER CONTROL PLANE NODES
    cp = cluster.add_group('control_plane', node_role='master')
    node_defs = json.loads(os.environ['CP_NODES'])
    for count, node in enumerate(node_defs):
        ip = ipam[node['mac']]
        mgmt_ip = ipam[node['mgmt_mac']]
        cp.add_host(node['name'], ip,
           mac_address=node['mac'],
           mgmt_mac_address=node['mgmt_mac'],
           mgmt_hostname=mgmt_ip,
           ansible_ssh_user='core',
           cp_node_id=count)

    virt = inv.add_group('virtual', mgmt_provider='kvm', install_disk='vda')
    # VIRTUAL NODES
    virt.add_host('bootstrap')
    ipam.save()


if __name__ == "__main__":
    main()

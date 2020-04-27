#!/usr/bin/env python3
import argparse
import ipaddress
import json
import os
import pickle 

SSH_PRIVATE_KEY = '/data/id_rsa'
IP_RESERVATIONS = '/data/ip_addresses'


class Inventory(object):

    _modes = ['list', 'host', 'none']
    _data = {"_meta": {"hostvars": {}}}

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

    def add_host(self, name, group, hostname, **hostvars):
        if group not in self._data:
            self.add_group(group)

        hostvars.update({'ansible_hostname': hostname})
        self._data[group]['hosts'].append(name)
        self._data['_meta']['hostvars'][name] = hostvars

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
        mgmt_provider=os.environ['MGMT_PROVIDER'])
    # BASTION NODE
    inv.add_host('bastion', 'infra', 
        os.environ['BASTION_HOST_NAME'],
        ansible_ssh_user=os.environ['BASTION_SSH_USER'])
    # DNS NODE
    inv.add_host('dns', 'infra',
        os.environ['DNS_HOST_NAME'],
        provider=os.environ['DNS_PROVIDER'],
        credentials=os.environ['DNS_CREDENTIALS'])
    # DHCP NODE
    inv.add_host('dhcp', 'infra',
        os.environ['DHCP_HOST_NAME'],
        provider=os.environ['DHCP_PROVIDER'],
        credentials=os.environ['DHCP_CREDENTIALS'])
    # CLUSTER CONTROL PLANE NODES
    inv.add_group('cluster')
    inv.add_group('control_plane', 'cluster')
    ipam = IPAddressManager(
        IP_RESERVATIONS,
        os.environ['IP_POOL'])
    node_defs = json.loads(os.environ['CP_NODES'])
    for node in node_defs:
        ip = ipam[node['mac']]
        mgmt_ip = ipam[node['mgmt_mac']]
        inv.add_host(node['name'], 'control_plane', ip,
            mac_address=node['mac'],
            mgmt_mac_address=node['mgmt_mac'],
            mgmt_hostname=mgmt_ip)
    ipam.save()


if __name__ == "__main__":
    main()

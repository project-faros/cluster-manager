#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from conftui import (Configurator, ParameterCollection, Parameter,
                     ListDictParameter, PasswordParameter, ChoiceParameter,
                     CheckParameter, StaticParameter, BooleanParameter)

CONFIG_PATH = '/data/config.sh'
CONFIG_FOOTER = ''

class ClusterConfigurator(Configurator):

    def __init__(self, path, footer, rtr_interfaces):
        self._path = path
        self._footer = footer

        self.router = ParameterCollection('router', 'Router Configuration', [
            CheckParameter('ROUTER_LAN_INT', 'LAN Interfaces', rtr_interfaces),
            Parameter('SUBNET', 'Subnet'),
            ChoiceParameter('SUBNET_MASK', 'Subnet Mask', ['20', '21', '22', '23', '24', '25', '26', '27']),
            CheckParameter('ALLOWED_SERVICES', 'Permitted Ingress Traffic', ['SSH to Bastion', 'HTTPS to Cluster API', 'HTTP to Cluster Apps', 'HTTPS to Cluster Apps', 'HTTPS to Cockpit Panel', 'External to Internal Routing - DANGER']),
            ListDictParameter('DNS_FORWARDERS', 'Upstream DNS Forwarders',
                [('server', 'DNS Server')],
                default='[{"server": "1.1.1.1"}]')
            ])
        self.cluster = ParameterCollection('cluster', 'Cluster Configuration', [
            PasswordParameter('ADMIN_PASSWORD', 'Adminstrator Password'),
            PasswordParameter('PULL_SECRET', 'Pull Secret'),
            BooleanParameter('FIPS_MODE', 'FIPS Mode', 'False')
            ])
        self.architecture = ParameterCollection('architecture', 'Host Record Configuration', [
            StaticParameter('MGMT_PROVIDER', 'Machine Management Provider', 'ilo'),
            Parameter('MGMT_USER', 'Machine Management User'),
            PasswordParameter('MGMT_PASSWORD', 'Machine Management Password'),
            ListDictParameter('CP_NODES', 'Control Plane Machines',
                [('name', 'Node Name'),
                 ('nic', 'Network Interface'), ('mac', 'MAC Address'),
                 ('mgmt_mac', 'Management MAC Address'),
                 ('install_drive', 'OS Install Drive',
                     os.environ.get('BOOT_DRIVE'))]),
            Parameter('CACHE_DISK', 'Container Cache Disk')])
        self.extra = ParameterCollection('extra', 'Extra DNS/DHCP Records', [
            ListDictParameter('EXTRA_NODES', 'Static IP Reservations',
                [('name', 'Node Name'), ('mac', 'MAC Address'), ('ip', 'Requested IP Address')]),
            ListDictParameter('IGNORE_MACS', 'DHCP Ignored MAC Addresses',
                [('name', 'Entry Name'), ('mac', 'MAC Address')])
            ])

        self.all = [self.router, self.cluster, self.architecture, self.extra]


def main():
    rtr_interfaces = os.environ['BASTION_INTERFACES'].split()
    return ClusterConfigurator(
            CONFIG_PATH,
            CONFIG_FOOTER,
            rtr_interfaces).configurate()


if __name__ == "__main__":
    sys.exit(main())

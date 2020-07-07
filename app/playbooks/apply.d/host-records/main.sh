#!/bin/bash

ME=$(dirname $0)

ansible-playbook $ME/dhcp.yml $@ || exit 1
ansible-playbook $ME/dns.yml $@ || exit 1
ansible-playbook $ME/cockpit.yml $@ || exit 1

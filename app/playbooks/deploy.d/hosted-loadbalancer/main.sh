#!/bin/bash
ME=$(dirname $0)
ansible-playbook $ME/hosted-loadbalancer.yml $@

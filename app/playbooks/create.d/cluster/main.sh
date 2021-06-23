#!/bin/bash

ME=$(dirname $0)

ansible-playbook $ME/create.yml $@ || exit 1
/bin/bash wait.sh
ansible-playbook $ME/cleanup.yml $@ || exit 1
cat /tmp/install.log

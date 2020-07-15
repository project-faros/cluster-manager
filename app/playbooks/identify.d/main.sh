#!/bin/bash

ME=$(dirname $0)
HELP="""identify HOST_LIST ANSIBLE_ARGS

Arguments:
  HOST_LIST: comma seperated list of hosts to identify
  ANSIBLE_ARGS: arguments to send to Ansible
"""

if [ $# != 1 ]; then
    echo "$HELP"
    exit 1
elif [ "$1" == "help" ]; then
    echo "$HELP"
    exit 0
fi

targets=$1
shift

ansible-playbook $ME/uid_on.yml -l "$targets" $@ || exit
echo """
UID light is on.
Press Ctrl+C to leave on.
Press Ctrl+D to turn off.
"""
read
ansible-playbook $ME/uid_off.yml -l "$targets" $@ || exit

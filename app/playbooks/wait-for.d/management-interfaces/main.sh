#!/bin/bash

ME=$(dirname $0)

echo """
!!! Please connect the managment interfaces to the network now. !!!
"""

ansible-playbook $ME/wait.yaml $@ || exit 1

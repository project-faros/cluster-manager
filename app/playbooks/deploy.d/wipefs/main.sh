#!/bin/bash

ME=$(dirname $0)

STATS_FILE=/tmp/pipeline ansible-playbook $ME/gather-facts.yml $@ || exit 1
STATS_FILE=/tmp/pipeline python3 $ME/configure.py $@ || exit 1
ansible-playbook $ME/wipe-local-storage.yml -e @/tmp/pipeline $@ || exit 1

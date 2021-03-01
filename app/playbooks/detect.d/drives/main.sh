#!/bin/bash

ME=$(dirname $0)

STATS_FILE=/tmp/drives.yml ansible-playbook $ME/detect-drives.yml "${@}" || exit $?
cp /tmp/drives.yml /data/drives.yml

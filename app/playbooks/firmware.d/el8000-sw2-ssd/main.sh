#!/bin/bash
ME=$(dirname $0)
ALL_NODES=$(echo "$1" | tr ',' ' '); shift

for node in $ALL_NODES; do
    printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' -
    echo '|'
    echo "|-- Configuring ${node}"
    echo '|'
    printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' -
    ansible-playbook $ME/apply.yml -l $node $@ || exit 1
done

#!/bin/bash

HEADER="Host,IP Address, MAC Address, Reachable (SSH)"
REPORT=""
INVENTORY=$(ansible-inventory --list 2> /dev/null)
EXTRA=$(ansible-inventory --host bootstrap 2> /dev/null| jq '.extra_nodes')

function len() { echo $#; }

function progress() {
    # screen_len=$(tput cols)
    screen_len=80
    pos=$1
    total=$2
    bar_len=$(python3 -c "import math; print(math.ceil($pos/$total * $screen_len))")
    printf '%*s' "${bar_len}" '' | tr ' ' +
    printf '%*s\r' "$(expr $screen_len - $bar_len)" '' | tr ' ' -
}

function _reachable() {
    target=$1
    timeout --signal=9 3 ansible $target -m setup &> /dev/null
    retcode=$?
    if [[ $retcode == 0 ]]; then
        echo '\e[32m+ YES\e[0m'
        return 0
    else
        echo '\e[1m- NO\e[0m'
        return 1
    fi
}

function _divider() {
    echo $1 "$(printf '%*s\n' "80" '' | tr ' ' -)\n"
}

function _row() {
    if [ $# -lt 2 ]; then
        ip=$(echo "$INVENTORY" | jq -rc "._meta.hostvars.\"$1\".ansible_host")
    else
        ip=$2
    fi
    if [ $# -lt 3 ]; then
        mac=$(echo "$INVENTORY" | jq -rc "._meta.hostvars.\"$1\".mac_address")
        echo "$1\t$ip\t$mac\t$(_reachable $1)\n"
    else
        mac=$3
        echo "$1\t$ip\t$mac\t- N/A\n"
    fi
}

function main() {
    all_hosts=$(echo "$INVENTORY" | jq -c '._meta.hostvars | keys' | jq -r @sh | xargs echo)
    extra_hosts=$(echo "$EXTRA" | jq -rc '.[].name')
    n_hosts=$(len $all_hosts $extra_hosts)
    index=0

    REPORT+=$(_divider)
    for host in $all_hosts; do
        progress $index $n_hosts
        REPORT+=$(_row $host)
        index=$(expr $index + 1)
    done
    count=0
    for host in $extra_hosts; do
        progress $index $n_hosts
        ip=$(echo "$EXTRA" | jq -rc ".[$count].ip")
        mac=$(echo "$EXTRA" | jq -rc " .[$count].mac")
        REPORT+=$(_row $host $ip $mac)
        index=$(expr $index + 1)
        count=$(expr $count + 1)
    done
    progress $index $n_hosts

    echo ""
    echo -e "$REPORT" | column -c 80 -E Host -t -N "$HEADER" -s $'\t' -o ' | '
    _divider -e
}

main

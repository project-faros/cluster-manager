#!/bin/bash

HEADER="Host,IP Address,Reachable"
REPORT=""

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
    port=$2
    if (timeout --signal=9 1 telnet $target $port 2>&1 | grep 'Connected to' > /dev/null); then
        echo '\e[32m☑ YES\e[0m'
        return 0
    else
        echo '\e[1m☐ NO\e[0m'
        return 1
    fi
}

function _divider() {
    echo $1 "$(printf '%*s\n' "80" '' | tr ' ' -)\n"
}

function _row() {
    ip=$(ansible-inventory --list | jq -rc "._meta.hostvars.\"$1\".ansible_host")
    echo "$1\t$ip\t$(_reachable $ip 22)\n"
}

function main() {
    all_hosts=$(ansible-inventory --list 2> /dev/null | jq -c '._meta.hostvars | keys' | jq -r @sh | xargs echo)
    n_hosts=$(len $all_hosts)
    index=0

    REPORT+=$(_divider)
    for host in $all_hosts; do
        progress $index $n_hosts
        REPORT+=$(_row $host)
        index=$(expr $index + 1)
    done
    progress $index $n_hosts

    echo ""
    echo -e "$REPORT" | column -c 80 -E Host -t -N "$HEADER" -s $'\t' -o ' | '
    _divider -e
}

main

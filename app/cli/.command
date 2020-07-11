#!/bin/bash

action=$(basename $0)

export COOKBOOK=/app/playbooks/${action}.d
test -e $COOKBOOK/all/main.sh
HAS_ALL=$?
CMDS=$(cd $COOKBOOK; ls -d * | awk '{ print "    " $1; }')
HELP="""
USAGE: ${action} COMMAND [COMMAND_ARGS]

Available Commands:
    help
$CMDS
"""

## PARSE INPUTS
if [ $# -eq 0 ] && $(exit ${HAS_ALL}); then
    RECIPE="all"
elif [ $# -eq 0 ]; then
    echo "$HELP"
    exit 0
elif [ "$1" == "help" ]; then
    echo "$HELP"
    exit 0
elif ! echo "$CMDS" | grep "$1" &>/dev/null; then
    echo "$HELP"
    exit 1
else
    RECIPE=$1
    shift
fi

## PREPARE ENVIRONMENT
cd /app
source /data/config.sh
export KUBECONFIG=/data/openshift-installer/auth/kubeconfig

## EXECUTE
/bin/bash $COOKBOOK/$RECIPE/main.sh $@

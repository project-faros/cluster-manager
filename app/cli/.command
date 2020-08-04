#!/bin/bash

# Find supporting scripts
action=$(basename $0)
export COOKBOOK=/app/playbooks/${action}.d


# function to execute commands
function _run() {
    ## PREPARE ENVIRONMENT
    cd /app
    source /data/config.sh
    export KUBECONFIG=/data/openshift-installer/auth/kubeconfig
    ## EXECUTE
    /bin/bash $COOKBOOK/$RECIPE/main.sh $@
    return $?
}


# Handle flat commands first
if [ -e $COOKBOOK/main.sh ]; then
    RECIPE=""
    _run $@
    exit $?
fi


# Handle commands with nested subcommands
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

_run $@
RETCODE=$?

if [ $RETCODE -eq 0 ]; then
    echo -e "\n\n\033[32m$0 Completed Successfully\033[0m\n\n"
else
    echo -e "\n\n\033[31m$0 Failed\033[0m\n\n"
fi
exit $RETCODE

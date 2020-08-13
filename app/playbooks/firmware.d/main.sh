#!/bin/bash

ME=$(dirname $0)
ALL_TARGETS=$(ansible-inventory --graph cluster |
              grep -v $(ansible-inventory --graph virtual |
                        grep -Po '[[:alpha:]].*$' |
                        xargs echo | sed 's/ /\\\|/g'))
ALL_PROFILES=$(find $ME/* -type d -exec basename {} \;)
HELP="""
firmware PROFILE TARGET

Apply the specified firmware profile to the specified target. The target may be
an individual host or a group of hosts.

Available Profiles:
$(echo "$ALL_PROFILES" | sed 's/^/    /g')

Available Targets:
$(echo "$ALL_TARGETS" | sed 's/^/    /g')
"""

# Validate input arguments
if [ $# -lt 2 ]; then
    echo "$HELP" >&2
    exit 1
fi
PROFILE=$1; shift
TARGET=$1; shift
if ! (echo $ALL_PROFILES | grep "$PROFILE") &>/dev/null; then
    echo -e "Unrecognized Profile." >&2
    echo "$HELP" >&2
    exit 2
fi
if ! (echo $ALL_TARGETS | grep "$TARGET") &>/dev/null; then
    echo -e "Unrecognized Target." >&2
    echo "$HELP" >&2
    exit 2
fi

# Convert groups to a host list
NODE_LKP=$(ansible-inventory --graph $TARGET 2> /dev/null)
if [ $? -ne 0 ]; then NODE_LKP="$TARGET"; fi
ALL_NODES=$(echo "$NODE_LKP" | grep -v '@' | grep -oP '[[:alpha:]].*' |
            grep -v $(ansible-inventory --graph virtual |
                      grep -Po '[[:alpha:]].*$' |
                      xargs echo | sed 's/ /\\\|/g') |
            xargs echo | tr ' ' ',')

$ME/$PROFILE/main.sh "$ALL_NODES" $@

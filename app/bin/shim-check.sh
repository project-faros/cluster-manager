#!/bin/bash

NEEDED_VERSION=$(python3 <<EOM
import configparser
config = configparser.ConfigParser()
config.read('/app/versions.ini')
print(config['host']['shim'])
EOM
)

if [ $SHIM_VERSION -lt $NEEDED_VERSION ]; then
    cat >&2 <<EOM

Your version of the farosctl shim is out of date.
Please run the following command to update the shim.

${SHIM_PATH} extract farosctl ${SHIM_PATH}

EOM
    exit 1
fi

unset NEEDED_VERSION

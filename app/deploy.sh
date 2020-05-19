#!/bin/bash

export KUBECONFIG=/data/openshift-installer/auth/kubeconfig
COMMAND=$1
shift

if [ ! -e /app/cookbook/${COMMAND}.yml ]; then
    echo "Recipe for ${COMMAND} not found." >&2
    exit 1
fi

ansible-playbook /app/cookbook/${COMMAND}.yml $@

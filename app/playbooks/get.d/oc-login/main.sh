#!/bin/bash

if [ ! -e /data/openshift-installer/auth/kubeadmin-password ]; then
    echo "No cluster appears to be deployed." >&2
    exit 1
fi

password=$(cat /data/openshift-installer/auth/kubeadmin-password)
echo "oc login -u kubeadmin -p \"$password\" https://api.${CLUSTER_NAME}.${CLUSTER_DOMAIN}:6443"

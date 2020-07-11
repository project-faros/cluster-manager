#!/bin/bash

# lookup routing type
if echo ${ALLOWED_SERVICES} | grep 'External to Internal Routing' &> /dev/null; then
    gateway_is_nat=1
else
    gateway_is_nat=0
fi

if $(exit ${gateway_is_nat}); then
    cluster_ip=${BASTION_IP_ADDR}
else
    cluster_ip=$(ansible-inventory --host wan | jq -r '.loadbalancer_vip')
fi

echo """
; Public DNS records for ${CLUSTER_DOMAIN} zone.
bastion.${CLUSTER_NAME}.${CLUSTER_DOMAIN}.   IN  A   ${BASTION_IP_ADDR}
api.${CLUSTER_NAME}.${CLUSTER_DOMAIN}.       IN  A   ${cluster_ip}
*.apps.${CLUSTER_NAME}.${CLUSTER_DOMAIN}.    IN  A   ${cluster_ip}
"""

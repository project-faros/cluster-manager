#!/bin/bash

# source
# https://www.openshift.com/blog/how-to-use-entitled-image-builds-to-build-drivercontainers-with-ubi-on-openshift

ME=$(dirname $0)

ansible-playbook $ME/deploy_certs.yaml $@ || exit 1

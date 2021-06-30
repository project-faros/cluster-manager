#!/bin/bash

cat /data/upgrade-status 2> /dev/null
echo; echo;
timeout 1 oc get clusterversion version --no-headers=true | tr -s ' ' | cut -d ' ' -f5-;
echo; timeout 1 oc get nodes;
echo; timeout 1 oc get co;

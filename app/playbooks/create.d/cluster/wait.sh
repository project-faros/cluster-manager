#!/bin/bash
cd /data/openshift-installer

function _watch_progress() {
    watch -td "
        cat /tmp/status
        echo; echo;
        oc get clusterversion version --no-headers=true | tr -s ' ' | cut -d ' ' -f6-;
        echo; oc get nodes;
        echo; oc get co;"
}


function _install() {
    echo 'Waiting for cluster to bootstrap...' > /tmp/status
    ./openshift-install wait-for bootstrap-complete &> /tmp/install.log
    echo 'Waiting for install to complete...' > /tmp/status
    ./openshift-install wait-for install-complete &> /tmp/install.log
    _quit
}

function _quit() {
    sleep 1
    kill -s SIGINT $(pidof -sc watch)
}

_install &
_watch_progress

#!/bin/bash

# data directory initialization
if [ ! -e /data/config.sh ]; then
  cp /data.skel/config.sh /data/config.sh
fi
mkdir -p /data/ansible


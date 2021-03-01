#!/bin/bash

# data directory initialization
if [ ! -e /data/config.yml ]; then
  cp /data.skel/config.yml /data/config.yml
fi
mkdir -p /data/ansible

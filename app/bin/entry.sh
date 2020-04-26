#!/bin/bash

if [ ! -e /data/config.sh ]; then
  cp /data.skel/config.sh /data/config.sh
fi

mkdir -p /data/ansible
if [ ! -e /data/ansible/inventory ]; then
    touch /data/ansible/inventory
fi

/bin/bash

#!/bin/bash

cd /app
source /data/config.sh 2> /dev/null
source /data/proxy.sh 2> /dev/null
python3 /app/playbooks/config.d/proxy/config.py
source /data/config.sh 2> /dev/null
source /data/proxy.sh 2> /dev/null
python3 /app/inventory.py --verify > /dev/null

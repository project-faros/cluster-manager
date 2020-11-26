#!/bin/bash

cd /app
source /data/config.sh
source /data/proxy.sh
python3 /app/playbooks/config.d/proxy/config.py
source /data/config.sh
source /data/proxy.sh
python3 /app/inventory.py --verify > /dev/null

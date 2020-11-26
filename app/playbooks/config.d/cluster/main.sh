#!/bin/bash

cd /app
source /data/config.sh
python3 /app/playbooks/config.d/cluster/config.py
source /data/config.sh
python3 /app/inventory.py --verify > /dev/null

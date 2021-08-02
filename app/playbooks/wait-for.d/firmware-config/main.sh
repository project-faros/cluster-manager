#!/bin/bash

echo -e "\e[93m"
cat <<EOM

Wait for cluster firmware configuration.

Please ensure the all cluster nodes have properly configured firmware.
See the documentation for details:
    https://faros.dev/configuration.html#hardware-configuration

EOM
echo -e "\e[0m"

for node in $(ansible-inventory --graph control_plane); do
    clean=$(echo "${node}" | grep -oP '[[:alpha:]].*')
    mgmt=$(ansible-inventory --host "${clean}" 2>/dev/null | jq -r '.mgmt_hostname' 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo -e "$node\tManagement IP: $mgmt"
    else
        echo $node
    fi
done

echo -e "\nPress Enter to continue of Ctrl+C to cancel."
read

echo -e "\e[93m"
cat <<EOM

Please manually configure the node firmware to the specs provided in the
documentation. See the documentation for details:
    https://faros.dev/configuration.html#hardware-configuration

EOM
echo -e "\e[0m"

ALL_NODES=$(echo "$1" | tr ',' ' ')
OUTPUT=""

for node in $ALL_NODES; do
    mgmt=$(ansible-inventory --host "${node}" 2>/dev/null | jq -r '.mgmt_hostname' 2>/dev/null)
    OUTPUT+="$node\tManagement IP: $mgmt\n"
done

echo -e "$OUTPUT" | column -t -s $'\t'

echo -e "\nPress Enter to continue of Ctrl+C to cancel."
read

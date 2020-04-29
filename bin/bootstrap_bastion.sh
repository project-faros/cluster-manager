#!/bin/bash

# contstants
# these should be true provided instructions are followed
CONFIG_DIR='~/.config/faros'
REPO="https://raw.githubusercontent.com/redhat-faros/deployer/master"
OC="https://mirror.openshift.com/pub/openshift-v4/clients/oc/latest/linux/oc.tar.gz"
SELINUX_MODULE="""
module faros 1.0;

require {
	type fusefs_t;
	type container_t;
	class file relabelto;
}

#============= container_t ==============
allow container_t fusefs_t:file relabelto;
"""

function _validate() {
# validate inputs
if [[ $1 == "pubkey" ]]; then
    ssh-keygen -l -f "$2" &> /dev/null && ! grep PRIVATE "$2" &> /dev/null && return 0
    echo "$2 is not a public key."
    return 1
elif [[ $1 == "privkey" ]]; then
    ssh-keygen -l -f "$2" &> /dev/null && grep PRIVATE "$2" &> /dev/null && return 0
    echo "$2 is not a private key."
    return 1
elif [[ $1 == "text" ]]; then
    test "x${2}" != "x" && return 0
    echo "respoinse is empty"
    return 1
fi
echo "$0 is not a valid option."
return 1
}

function main() {
## gather input
_validate pubkey "$pubkey" &> /dev/null
while [[ "$?" -gt 0 ]]; do
    echo ''
    echo 'Path to SSH public key: '
    read pubkey
    _validate pubkey "$pubkey"
done
_validate privkey "$privkey" &> /dev/null
while [[ "$?" -gt 0 ]]; do
    echo ''
    echo 'Path to SSH private key: '
    read privkey
    _validate privkey "$privkey"
done
echo ''

## copy files
echo 'Installing SSH Keys'
cp "$privkey" ~/.ssh/id_rsa
cp "$pubkey" ~/.ssh/id_rsa.pub
chmod 600 ~/.ssh/id_rsa*
mkdir -p $CONFIG_DIR/default
cp "$privkey" $CONFIG_DIR/default
cp "$pubkey" $CONFIG_DIR/default

## install dependencies
echo 'Installing Dependencies'
mkdir -p ~/bin
cd ~/bin
wget -O ~/bin/farosctl $REPO/bin/farosctl
chmod +x ~/bin/farosctl
wget -O ~/bin/oc.tgz $OC
tar xvzf oc.tgz

## CONFIGURE SELINUX
if [ $(getenforce) == "Enforcing" ]; then
    echo 'Configuring SELinux'
	te=faros.te
	mod=faros.mod
	pp=faros.pp
	mkdir -p /tmp/faros_install
	cd /tmp/faros_install
    echo "$SELINUX_MODULE" > "$te"
    sudo checkmodule -M -m -o "$mod" "$te" && semodule_package -o "$pp" -m "$mod" && semodule -i "$pp"
	rm -rf /tmp/faros_install
fi
}


main $@
exit $?

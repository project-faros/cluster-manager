#!/bin/bash

# contstants
# these should be true provided instructions are followed
USER=core
BASTION=192.168.8.50
CONFIG_DIR='~/.config/faros'
REPO="https://raw.githubusercontent.com/redhat-faros/deployer/master"

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
elif [[ $1 == "pass" ]]; then
    test "x${2}" != "x" && return 0
    echo "password is empty"
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
_validate pass "$adminpass" &> /dev/null
while [[ "$?" -gt 0 ]]; do
    echo ''
    echo 'Environment admin password: '
    read adminpass
    _validate pass "$adminpass"
done
_validate pass "$userpass" &> /dev/null
while [[ "$?" -gt 0 ]]; do
    echo ''
    echo 'Environment user password: '
    read userpass
    _validate pass "$userpass"
done
echo ''

## copy files
ssh-add $privkey
echo 'Installing SSH Keys'
scp "$privkey" $USER@$BASTION:~/.ssh/id_rsa
scp "$pubkey" $USER@$BASTION:~/.ssh/id_rsa.pub

## copy secrets
echo 'Writing Secrets'
ssh $USER@$BASTION "mkdir -p $CONFIG_DIR/default"
echo -e "admin_password: '$adminpass'\nuser_password: '$userpass'\n" | ssh $USER@$BASTION -T "cat > $CONFIG_DIR/default/secrets.yaml"

## install dependencies
echo 'Installing Dependencies'
ssh $USER@$BASTION "mkdir -p ~/bin; wget -O ~/bin/farosctl $REPO/bin/farosctl; chmod +x ~/bin/farosctl"
}


main $@
exit $?

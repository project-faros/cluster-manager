#!/bin/bash

# contstants
# these should be true provided instructions are followed
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

function die() {
echo -e "\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" >&2
echo "$1" >&2
echo -e "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n" >&2
exit 1
}

function main() {
## gather input
echo ''
sudo -v
can_sudo=$?
if [ $can_sudo -eq 0 ]; then
    echo 'The installer will continue with sudo rights.'
else
    echo 'The installer will attempt to continue without sudo rights.'
fi
echo ''

## CONFIGURE SELINUX
if [ $(getenforce) == "Enforcing" ]; then
    if [ $can_sudo -eq 0 ]; then
        echo 'Configuring SELinux'
        te=faros.te
        mod=faros.mod
        pp=faros.pp
        mkdir -p /tmp/faros_install
        cd /tmp/faros_install
        echo "$SELINUX_MODULE" > "$te"
        sudo checkmodule -M -m -o "$mod" "$te" && sudo semodule_package -o "$pp" -m "$mod" && sudo semodule -i "$pp" || die "Error configuring SELinux"
	cd -
        rm -rf /tmp/faros_install
    else
        die 'Sudo is requried when installing on a machine with SELinux enabled.'
    fi
fi

## configure cockpit
if [ $can_sudo -eq 0 ]; then
    echo 'Configure cockpit'
    sudo yum install -y cockpit cockpit-podman cockpit-system || die "Error installing cockpit"
    sudo systemctl start cockpit.socket || die "Error starting cockpit"
    sudo systemctl enable cockpit.socket || die "Error enabling cockpit"
fi

## ensure podman is installed
if ! rpm -qa | grep -Po '^podman-\d' &> /dev/null; then
    if [ $can_sudo -eq 0 ]; then
        echo 'Install Podman'
        sudo yum install -y podman || die "Error installing podman"
    else
        die 'Sudo is required to install podman.'
    fi
fi

## install faros
echo 'Installing Faros'
mkdir -p ~/bin || die "Error installing Faros"
cd ~/bin || die "Error installing Faros"
wget -O ~/bin/farosctl $REPO/bin/farosctl || die "Error installing Faros"
chmod +x ~/bin/farosctl || die "Error installing Faros"
wget -O ~/bin/oc.tgz $OC || die "Error installing Faros"
tar xvzf oc.tgz || die "Error installing Faros"
cd - || die "Error installing Faros"

echo -e '\n\nFAROS INSTALLATION COMPLETED SUCCESSFULLY\n\n'
}


main $@
exit $?

# Faros Installation

## Prerequisites

Before cluster configuration and deployment, you must have basic networking
available for your network. This includes layer 3 routing, egress firewall, DNS
services, and DHCP services. You must have an SSH key to use for the cluster.
Finally, each server that is used must have out-of-band management configure.

### Generate SSH Key

From a Linux or Mac machine, use the following command to create an SSH key:

```bash
ssh-keygen -f id_cluster -N ""
```

This will generate public (id_cluster.pub) and private (id_cluster) key files
for use during the install.

### DHCP Configuration

The following DHCP providers are supported:

1. [OpenWRT](./openwrt.md)

### DNS Configuration

The following DNS providers are supported:

1. [OpenWRT](./openwrt.md)

### Out of Band Management

The following management providers are supported:

1. [iLO](./ilo.md)
1. [KVM](./kvm.md)

With the exception of the bootstrap node and the bastion app node, all machines
in the cluster must use the same management interface. All machines must also
use the same credentials on their management interfaces.

### Machine BIOS Setup

Faros is not impacted by much of the BIOS configurations on nodes. However, the
system must be configured for BIOS boot, not UEFI. The internal hard drive
should be the only boot device. If a RAID card is present in the machine,
hardware RAID may also be configured.

## Bastion Host

The Faros Bastion host has many purposes. Primarily, it is the node from which
you will create and control your cluster. This node will host a PXE boot (tftp)
server, a web server (http), the cluster load balancer (haproxy), a virtual
bootstrap server, and a cluster control interface (cockpit).

The bastion node should be a physical node in your cluster. To prepare it,
simply install RHEL or CentOS 8 using the standard server software packages. 
RHEL 7 and CentOS 7 should work as well, but they are not tested.
You may use the default install, but you should set a static IP address during
the install process. The IP address should be in your subnet but outside of
the DHCP range and outside the range you will give to Faros. The hostname for
this node should be `bastion.CLUSTER_NAME.CLUSTER_DOMAIN`. For example purposes,
this documentation will use `bastion.beacon01.faros.site`. The user created
during the install process must be made a system administrator.

When the operating system install is complete, copy to the server the SSH keys
that were generated earlier. This can be accomplished with the following
commands on a Linux or Mac computer. For simplicity, simply place the SSH keys
into the user's home directory.

```bash
ssh-copy-id -i id_cluster.pub USER@BASTION_IP
scp id_cluster* USER@BASTION_IP:
```

If you are using Red Hat, subscribe to RHSM. For all operating systems: apply
all available patches and reboot.

Once the server has rebooted, connect to it and run the following command to
install Faros.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/project-faros/cluster-manager/master/bin/bootstrap_bastion.sh)"
```

The installer will first have you log in with the user's
password to allow root access. Then, the installer will prompt for the path to
the ssh keys. If you followed the examples in this documentation, they will be:

- **Public Key:** ~/id_cluster.pub
- **Private Key:** ~/id_cluster


# Project Faros [![Docker Repository on Quay](https://quay.io/repository/faros/cluster-manager/status "Docker Repository on Quay")](https://quay.io/repository/faros/cluster-manager)

Project Faros is a reference implimentation of Red Hat OpenShift 4 on small
footprint, bare-metal clusters. The project includes reference architectures
and automated deployment tools. We are looking to bring OpenShift everywhere,
even to the edge.

![Cluster Install](https://raw.githubusercontent.com/project-faros/assets/master/demos/install/8-cluster.gif)

## Hardware and Architecture

The Faros installer assumes a 4 node cluster with a layer 2 Ethernet
interconnect. Each node in the cluster must have out-of-band management and
management interfaces must be on the same layer 2 network. One node in the
cluster will be used as a bastion node and router. The remaining three will be
used as a schedulable OpenShift Control Plane. It is preferred to run RHEL8 on
the bastion/router node. CentOS 8 should work, but it is untested. The
bastion/router node will require an uplink to either a corporate network or
directly to the internet. This uplink will be called the WAN link.

## Prerequisites

### DNS

Before begining, determine the cluster name and DNS domain/zone you would like
to use for the install. The DNS zone should be one that you are able to modify.
All of the required DNS entries for the cluster will exist in a subdomain
that matches: `CLUSTER_NAME.DNS_ZONE`. For example: If you named your cluster
`edge` and used the DNS zone `mycompany.com`, then your Kubernetes API will be
hosted at `api.edge.mycompany.com`. It is very important that you are able to
create the public DNS entries for the cluster. This is not handled by the
installer.

### Hardware and Bastion Node

To prepare your cluster for installation:
- Ensure the Layer 2 interconnect connects to all nodes. It is preferred to
  leave the out of band management interfaces off the network for the time
  being. They will be connected later.
- In the BIOS for each node:
  - Ensure the boot order is set to Hard Drive and then the NIC that will be
    used by the cluster.
  - All cluster nodes must use the same username and password for their out of
    band management.
- Connect the WAN link to the bastion/router node.
- Install RHEL 8 onto the bastion/router node. During the install:
  - The hostname *must* be statically set to `bastion.CLUSTER_NAME.DNS_ZONE`.
  - The WAN interface should be configured during the install. This may be
    configured as a normal network connection.
  - It is highly recommended to perform a standard RHEL 8 install with the
    package set called: `RHEL Server without GUI`.
  - A single user should be configured on the bastion node that will be used
    for deploying the cluster. The password for this user should be the same as
    the cluster admin password that will be configured during installation.

If you are using Red Hat, subscribe to RHSM. For all operating systems: apply
all available patches and reboot.

### Install Faros

Run the following command to install Faros.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/project-faros/cluster-manager/master/bin/bootstrap_bastion.sh)"
```

The installer requires SUDO rights as it will need to install dependencies,
configure SELinux, and enable cockpit. Cockpit may be disabled once the install
is complete.

## Cluster Deployment

Run the following commands from your bastion node:

```bash
# Launch the interactive cluster configuration TUI
farosctl config

# Configure the edge router, DNS server, and DHCP server
farosctl apply router

# Create the required virtual infrastructure
# (bootstrap and virtual bastion app node)
farosctl create machines

# Configure network infrastructure records and cockpit links
farosctl apply host-records

# Manually connect out-of-band controllers to the network
# Then, wait for them to get their IP
farosctl wait-for management-interfaces

# Create the cluster load balancer
farosctl create load-balancer

# Create the installation source and config repositories
farosctl create install-repos

# Create the OpenShift cluster
farosctl create cluster
```

That's it!

## Connecting the the Cluster

During install, cockpit is installed on the bastion node and hosted on port
9090. Check that out [here](http://bastion:9090). Log in with the standard user
account. This interface can be used to check virtual machines and get a
terminal session on the server. There will also be a Faros tab with helpful
links to various cluster resources.

The farosctl command can be used to connect to the cluster as well.

```bash
farosctl oc get nodes
```

Any of the `oc` commands can be executed this way. They will be run as the
default `kubeadmin` user.

## Starting and Stopping the Cluster

Before shutting down the cluster, it should be left powered on for at least 25
hours. This gives the bootstrap certificate authority time to rotate the
certificates used to verify node identity. The initial bootstrap CA is only
valid for 24 hours.

After the first 25 hours, the cluster can be safely shutdown. However, the
cluster should be powered on inside of every 30 days to allow the certs to be
rotated. The standard cluster CA certificates are only valid for 30 days.

*This is very important! If the certificates are allowed to expire, your
cluster will be unrecoverable!*

```bash
# Safely bring down the cluster
farosctl shutdown

# Once the cluster has stopped, the bastion node can be shutdown
poweroff

# To bring the cluster back up, first power on the bastion node
# Then, bring the cluster up and restore operations
farosctl startup
```

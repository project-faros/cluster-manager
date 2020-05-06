# OpenWRT DNS and DHCP Provider

[OpenWRT](https://openwrt.org/) is an Open Source router firmware that is
flexible and powerful. It can be very useful for building low-power,
small-foorprint clusters because of its ability to run on very small gear.
OpenWRT is capable of providing DNS, DHCP, routing, and firewall services to a
Faros cluster.

These instructions assume that the router's WAN connection, admin password, and
WiFi settings have already been configured properly. It also never hurts to
update all the firmware to the latest version.

## General Configuration
Faros will connect to your OpenWRT router via SSH to manage cluster
configuration. To allow this to happen, you must upload your public SSH key to
the OpenWRT router. You can do this in the LuCi web interface by navigating to
`System -> Administration` and copy-pasting the public key to the text box
labeled `SSH-Keys`.

Faros will require a number of packages to be installed on the OpenWRT router.
You can install packages from the LuCi interface by navigating to `System ->
Software` and clicking the `Update lists` button. Then you can search for
packages by typing their name in the `Filter` box. When you find the package
you would like to install, click the `Install` button to the right.

The following packages are required:
* ca-certificates
* ca-bundle
* python-light
* python-logging
* python-codecs
* python-crypto
* openssh-sftp-server (technically optional, but recommended)
* openssh-sftp-client (technically optional, but recommended)

## DNS and DHCP Configuration

OpenWRT uses Dnsmasq to provide DNS and DHCP services. This means that they are
configured together.

### DNS Search Domain

To configure this setting, navigate to `Network -> DHCP and DNS` and edit the
value called `Network Domain`.

This must be of the format `CLUSTER_NAME.CLUSTER_DOMAIN`. For the examples in
this documentation, the cluster name is `beacon01` and the domain is
`faros.site`. This means the Local Domain is set to `beacon01.faros.site`.

### Network Subnet and DHCP Pool

The Faros installer does not have an opinion on the subnet address. However,
you will require a pool of IP addresses that live outside of the DHCP pool but
inside the subnet. To configure this, navigate to `Network -> Interfaces` and
click the `Edit` button next to `LAN`.

For the examples in this documentation, we will use 192.168.1 as the IPv4
Address, 255.255.255.0 as the IPv4 netmask, and the DHCP server will Start at
100.

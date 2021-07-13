#!/bin/bash

ME=$(dirname $0)

ansible-playbook $ME/nvidia-drivers.yml $@ || exit 1

#!/bin/bash

ME=$(dirname $0)

ansible-playbook $ME/odh-demo.yml $@ || exit 1

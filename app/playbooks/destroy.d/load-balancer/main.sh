#!/bin/bash

ME=$(dirname $0)

ansible-playbook $ME/destroy.yml $@ || exit 1

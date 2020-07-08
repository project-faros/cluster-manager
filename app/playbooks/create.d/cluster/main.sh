#!/bin/bash

ME=$(dirname $0)

ansible-playbook $ME/create.yml $@ || exit 1

#!/bin/bash

ME=$(dirname $0)

ansible-playbook $ME/apply.yml $@ || exit 1

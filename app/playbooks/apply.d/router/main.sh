#!/bin/bash

ME=$(dirname $0)

ansible-playbook $ME/create_router.yml $@ || exit 1

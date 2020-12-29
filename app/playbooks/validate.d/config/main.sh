#!/bin/bash

ME=$(dirname $0)

ansible-playbook $ME/validate.yml $@ || exit 1

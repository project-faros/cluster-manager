#!/usr/bin/env python3
# This should grow to be a proper library with actual tests at some point

from faros_config import FarosConfig

config = FarosConfig.from_yaml('example_config.yml')

print(config)
print()
for port in config.network.port_forward:
    print(port)

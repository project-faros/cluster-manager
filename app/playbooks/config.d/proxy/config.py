#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from conftui import (Configurator, ParameterCollection, Parameter,
                     ListDictParameter, PasswordParameter,
                     BooleanParameter)

CONFIG_PATH = '/data/proxy.sh'
CONFIG_FOOTER = ''

class ProxyConfigurator(Configurator):

    def __init__(self, path, footer):
        self._path = path
        self._footer = footer

        self.proxy = ParameterCollection('proxy', 'Proxy Configuration', [
            BooleanParameter('PROXY', 'Setup cluster proxy'),
            Parameter('PROXY_HTTP', 'HTTP Proxy'),
            Parameter('PROXY_HTTPS', 'HTTPS Proxy'),
            ListDictParameter('PROXY_NOPROXY', 'No Proxy Destinations',
                [('dest', 'Destination')]),
            PasswordParameter('PROXY_CA', 'Additional CA Bundle')
            ])

        self.all = [self.proxy]


def main():
    return ProxyConfigurator(
            CONFIG_PATH,
            CONFIG_FOOTER).configurate()


if __name__ == "__main__":
    sys.exit(main())

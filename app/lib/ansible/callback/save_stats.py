# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = ''

import os
import sys
import yaml
from ansible.parsing.yaml.objects import AnsibleUnicode
from ansible.plugins.callback import CallbackBase
from ansible.utils.unsafe_proxy import AnsibleUnsafeText


class CallbackModule(CallbackBase):

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'save_stats'
    CALLBACK_NEEDS_WHITELIST = False

    def playbook_on_stats(self, stats):
        self.v2_playbook_on_stats(stats)

    def v2_playbook_on_stats(self, stats):
        # save stats
        stats_file = os.environ.get('STATS_FILE')
        if stats_file:
            # convert ansible types to python types
            def rep_UnsafeText(dumper, data):
                return dumper.represent_str(str(data))
            yaml.add_representer(AnsibleUnsafeText, rep_UnsafeText)
            yaml.add_representer(AnsibleUnicode, rep_UnsafeText)

            # write yaml file
            with open(stats_file, 'w') as fptr:
                yaml.dump(stats.custom.get('_run', {}), fptr)

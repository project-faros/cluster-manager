# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = ''

import sys
from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'post_message'
    CALLBACK_NEEDS_WHITELIST = False

    def playbook_on_stats(self, stats):
        self.v2_playbook_on_stats(stats)

    def v2_playbook_on_stats(self, stats):
        # print post message
        post_message = stats.custom.get('_run', {}).get('post_message')
        if post_message:
            if isinstance(post_message, str):
                sys.stdout.write('\n')
                sys.stdout.write(post_message)
                return
            for line in post_message:
                sys.stdout.write('\n')
                sys.stdout.write(line)
        sys.stdout.write('\n')

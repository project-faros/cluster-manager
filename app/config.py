#!/usr/bin/env python
import sys
import os
import json
from PyInquirer import prompt, Separator, default_style
from prompt_toolkit.shortcuts import Token, print_tokens


CONFIG_PATH = '/data/config.sh'
CONFIG_FOOTER = ''
STYLE = default_style



class Parameter(object):
    disabled = False
    _value_reprfun = str

    def __init__(self, name, prompt, disabled=False):
        self._name = name
        self._value = os.environ.get(self._name, '')
        self._prompt = prompt
        self.disabled = disabled

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def prompt(self):
        return self._prompt

    def update(self):
        question = [
            {
                'type': 'input',
                'name': 'newval',
                'message': self.prompt,
                'default': self.value,
            }
        ]
        answer = prompt(question)
        self.value = answer['newval']

    def __repr__(self):
        return '{}: {}'.format(self.prompt, self._value_reprfun(self.value))

    def to_bash(self):
        return "export {}='{}'".format(self.name, self.value)


class PasswordParameter(Parameter):

    def __init__(self, name, prompt, disabled=False):
        super().__init__(name, prompt, disabled)

    def _value_reprfun(self, password):
        if not password:
            return ''
        return '*********'

    def update(self):
        question = [
            {
                'type': 'password',
                'name': 'newval',
                'message': self.prompt
            }
        ]
        answer = prompt(question)
        self.value = answer['newval']

class ChoiceParameter(Parameter):

    def __init__(self, name, prompt, choices, value_reprfun=str):
        self._name = name
        self._value = os.environ.get(self._name, '')
        self._prompt = prompt
        self._choices = choices
        self._value_reprfun = value_reprfun

    def update(self):
        question = [
            {
                'type': 'list',
                'message': self._prompt,
                'name': 'choice',
                'default': self._value,
                'choices': self._choices
            }
        ]
        answer = prompt(question)
        self._value = answer['choice']


class CheckParameter(Parameter):

    def __init__(self, name, prompt, choices):
        self._name = name
        self._value = json.loads(os.environ.get(self._name, ''))
        self._prompt = prompt
        self._choices = choices
        self._choices = [{'name': f'{choice}',
                          'checked': f'{choice}' in self._value}
                         for choice in choices]

    def update(self):
        question = [
            {
                'type': 'checkbox',
                'message': self._prompt,
                'name': 'choice',
                'choices': self._choices
            }
        ]
        answer = prompt(question)
        self._value = answer['choice']

    def to_bash(self):
        return "export {}='{}'".format(self.name, json.dumps(self.value))


class StaticParameter(Parameter):

    def __init__(self, name, prompt, value):
        super().__init__(name, prompt, 'Static Value')
        self._value = value


class ListDictParameter(Parameter):

    def __init__(self, name, prompt, keys):
        self._name = name
        self._value = json.loads(os.environ.get(self._name, '[]'))
        self._prompt = prompt
        self._keys = keys
        self._primary_key = keys[0][0]

    def _value_reprfun(self, value):
        return '{} items'.format(len(self.value))

    def print_status(self):
        tokens = []
        tokens += [(Token.QuestionMark, '!'),
                   (Token.Question, f' Current {self._prompt}:\n')]
        for entry in self._value:
            for idx, key in enumerate(self._keys):
                if idx == 0:
                    ptr = '  - '
                else:
                    ptr = '    '
                tokens += [(Token.Pointer, ptr),
                           (Token.Arboted, f'{key[1]}: {entry.get(key[0], "")}\n')]
        print_tokens(tokens, style=STYLE)
        sys.stdout.write('\n\n')

    def update(self):
        done = False

        while not done:
            self.print_status()

            question = [
                {
                    'type': 'expand',
                    'message': '{}: What would you like to do?'.format(self.prompt),
                    'name': 'action',
                    'default': 'a',
                    'choices': [
                        {
                            'key': 'a',
                            'name': 'Add Entry',
                            'value': 'a'
                        },
                        {
                            'key': 'e',
                            'name': 'Edit Entry',
                            'value': 'e'
                        },
                        {
                            'key': 'r',
                            'name': 'Remove Entry',
                            'value': 'r'
                        },
                        {
                            'key': 'd',
                            'name': 'Done',
                            'value': 'd'
                        }
                    ]
                }
            ]
            answer = prompt(question)

            if answer['action'] == 'd':
                done = True
            elif answer['action'] in 'er':
                self._update_edit(answer['action'])
            elif answer['action'] == 'a':
                self._value.append(self._mkentry({}))

    def _update_edit(self, action_code):
        if action_code == 'r':
            action = 'remove'
        else:
            action = 'edit'

        question = [
            {
                'type': 'list',
                'name': 'index',
                'message': 'Which item would you like to {}?'.format(action),
                'choices': [{'name': item[self._primary_key],
                             'value': index} for (index, item) in enumerate(self.value)]
            }
        ]
        answer = prompt(question)

        if action_code == 'r':
            self.value.pop(answer['index'])
        else:
            self.value[answer['index']] = self._mkentry(self.value[answer['index']])

    def _mkentry(self, defaults):
        questions = [ {'type': 'input',
                       'message': item[1],
                       'name': item[0],
                       'default': defaults.get(item[0], '')}
                     for item in self._keys]
        return prompt(questions)

    def to_bash(self):
        return "export {}='{}'".format(self.name, json.dumps(self.value))


class ParameterCollection(list):

    def __init__(self, name, prompt, values):
        super().__init__(values)
        self._name = name
        self._prompt = prompt

    def to_choices(self):
        out = [Separator(self._prompt)]
        for item in self:
            out += [{'name': repr(item),
                     'description': str(item.value),
                     'value': '{}|{}'.format(self._name, item.name)}]
            if item.disabled:
                out[-1].update({'disabled': item.disabled})
        return out

    def to_bash(self):
        return ['# {}'.format(self._prompt.upper())] + [item.to_bash() for item in self]

    def get_param(self, pname):

        def filter_fun(val):
            return val.name == pname

        return list(filter(filter_fun, self))[0]


class configurator(object):

    def __init__(self, path, footer, rtr_interfaces):
        self._path = path
        self._footer = footer

        self.router = ParameterCollection('router', 'Router Configuration', [
            CheckParameter('ROUTER_LAN_INT', 'LAN Interfaces', rtr_interfaces),
            Parameter('SUBNET', 'Subnet'),
            ChoiceParameter('SUBNET_MASK', 'Subnet Mask', ['20', '21', '22', '23', '24', '25', '26', '27']),
            CheckParameter('ALLOWED_SERVICES', 'Permitted Ingress Traffic', ['SSH to Bastion', 'HTTPS to Cluster API', 'HTTP to Cluster Apps', 'HTTPS to Cluster Apps', 'HTTPS to Cockpit Panel', 'External to Internal Routing - DANGER'])])
        self.cluster = ParameterCollection('cluster', 'Cluster Configuration', [
            PasswordParameter('ADMIN_PASSWORD', 'Adminstrator Password'),
            PasswordParameter('PULL_SECRET', 'Pull Secret')])
        self.architecture = ParameterCollection('architecture', 'Host Record Configuration', [
            StaticParameter('MGMT_PROVIDER', 'Machine Management Provider', 'ilo'),
            Parameter('MGMT_USER', 'Machine Management User'),
            PasswordParameter('MGMT_PASSWORD', 'Machine Management Password'),
            ListDictParameter('CP_NODES', 'Control Plane Machines',
                [('name', 'Node Name'), ('mac', 'MAC Address'),
                 ('mgmt_mac', 'Management MAC Address')])])
        self.extra = ParameterCollection('extra', 'Extra DNS/DHCP Records', [
            ListDictParameter('EXTRA_NODES', 'Extra Records',
                [('name', 'Node Name'), ('mac', 'MAC Address'), ('ip', 'Requested IP Address')]),
            ListDictParameter('IGNORE_MACS', 'Ignored MAC Addresses',
                [('name', 'Entry Name'), ('mac', 'MAC Address')])])

        self.all = [self.router, self.cluster, self.architecture, self.extra]

    def _main_menu(self):
        question = [
            {
                'type': 'checkbox',
                'message': 'Which items would you like to change?',
                'name': 'parameters',
                'choices': [val for section in self.all for val in section.to_choices()]
            }
        ]
        return prompt(question)

    def _update_param(self, raw_param):
        (collection, param_name) = raw_param.split('|')
        try:
            getattr(self, collection).get_param(param_name).update()
        except AttributeError:
            raise ValueError('{} not a valid collection'.format(collection))

    def dump(self):
        with open(self._path, 'w') as outfile:
            _ = [outfile.write(line + '\n') for section in self.all for line in section.to_bash()]
            outfile.write(self._footer)

    def configurate(self):
        loop = True

        while loop:
            to_update = self._main_menu()
            print('')

            for parameter in to_update['parameters']:
                self._update_param(parameter)
            print('')

            loop = bool(to_update['parameters'])

        self.dump()


def main():
    rtr_interfaces = os.environ['BASTION_INTERFACES'].split()
    return configurator(
            CONFIG_PATH,
            CONFIG_FOOTER,
            rtr_interfaces).configurate()


if __name__ == "__main__":
    sys.exit(main())

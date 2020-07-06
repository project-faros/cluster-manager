#!/usr/bin/env python
import sys
import os
import json
from PyInquirer import Token, prompt, Separator

CONFIG_PATH = '/data/config.sh'
CONFIG_FOOTER = ''


def password_repr(password):
    if not password:
        return ''
    return '*********'


class Parameter(object):

    def __init__(self, name, prompt, value_reprfun=str):
        self._name = name
        self._value = os.environ.get(self._name, '')
        self._prompt = prompt
        self._value_reprfun = value_reprfun

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

    def __init__(self, name, prompt, choices, value_reprfun=str):
        self._name = name
        self._value = json.loads(os.environ.get(self._name, ''))
        self._prompt = prompt
        self._choices = choices
        self._value_reprfun = value_reprfun
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


class ListDictParameter(Parameter):

    def __init__(self, name, prompt, keys):
        self._name = name
        self._value = json.loads(os.environ.get(self._name, '[]'))
        self._prompt = prompt
        self._keys = keys
        self._primary_key = keys[0][0]

    def _value_reprfun(self, value):
        return '{} items'.format(len(self.value))

    def update(self):
        # expand - remove add edit done
        # remove:edit -> list -> 3xinput
        # add -> 3xinput
        done = False

        while not done:
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
        return [Separator(self._prompt)] + \
            [{'name': repr(item),
              'description': str(item.value),
              'value': '{}|{}'.format(self._name, item.name)} for item in self]

    def to_bash(self):
        return ['# {}'.format(self._prompt.upper())] + [item.to_bash() for item in self]

    def get_param(self, pname):

        def filter_fun(val):
            return val.name == pname

        return list(filter(filter_fun, self))[0]


class configurator(object):

    def __init__(self, path, footer, rtr_interfaces, dns_providers, dhcp_providers, mgmt_providers):
        self._path = path
        self._footer = footer

        self.router = ParameterCollection('router', 'Network Router Configuration', [
            CheckParameter('ROUTER_LAN_INT', 'LAN Interfaces', rtr_interfaces),
            Parameter('SUBNET', 'Subnet'),
            ChoiceParameter('SUBNET_MASK', 'Subnet Mask', ['20', '21', '22', '23', '24', '25', '26', '27']),
            CheckParameter('ALLOWED_SERVICES', 'Permitted Ingress Traffic', ['SSH to Bastion', 'HTTPS to Cluster API', 'HTTP to Cluster Apps', 'HTTPS to Cluster Apps', 'External to Internal Routing - DANGER'])])
        self.cluster = ParameterCollection('cluster', 'Cluster Configuration', [
            Parameter('ADMIN_PASSWORD', 'Adminstrator Password', password_repr),
            Parameter('PULL_SECRET', 'Pull Secret', password_repr)])
        self.dns = ParameterCollection('dns', 'Cluster DNS Configuration', [
            ChoiceParameter('DNS_PROVIDER', 'DNS Provider', dns_providers),
            Parameter('DNS_HOST_NAME', 'DNS Host Name'),
            Parameter('DNS_USER', 'DNS Admin User'),
            Parameter('DNS_PASSWORD', 'DNS Admin Password', password_repr)])
        self.dhcp = ParameterCollection('dhcp', 'Cluster DHCP Configuration', [
            ChoiceParameter('DHCP_PROVIDER', 'DHCP Provider', dhcp_providers),
            Parameter('DHCP_HOST_NAME', 'DHCP Host Name'),
            Parameter('DHCP_USER', 'DHCP Admin User'),
            Parameter('DHCP_PASSWORD', 'DHCP Admin Password', password_repr)])
        self.architecture = ParameterCollection('architecture', 'Cluster Architecture', [
            ChoiceParameter('MGMT_PROVIDER', 'Machine Management Provider', mgmt_providers),
            Parameter('MGMT_USER', 'Machine Management User', password_repr),
            Parameter('MGMT_PASSWORD', 'Machine Management Password', password_repr),
            ListDictParameter('CP_NODES', 'Control Plane Machines',
                [('name', 'Node Name'), ('mac', 'MAC Address'),
                 ('mgmt_mac', 'Management MAC Address')])])

        self.all = [self.router, self.cluster, self.dns, self.dhcp, self.architecture]

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
    dhcp_providers = ['.'.join(item.split('.')[:-1])
                      for item in
                      next(os.walk('/app/providers/dhcp/tasks'))[2]]
    dns_providers = ['.'.join(item.split('.')[:-1])
                     for item in
                     next(os.walk('/app/providers/dns/tasks'))[2]]
    mgmt_providers = ['.'.join(item.split('.')[:-1])
                      for item in
                      next(os.walk('/app/providers/management/tasks/netboot'))[2]]
    rtr_interfaces = os.environ['BASTION_INTERFACES'].split()
    return configurator(
            CONFIG_PATH,
            CONFIG_FOOTER,
            rtr_interfaces,
            dns_providers,
            dhcp_providers,
            mgmt_providers).configurate()


if __name__ == "__main__":
    sys.exit(main())

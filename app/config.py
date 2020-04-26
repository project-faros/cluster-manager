#!/usr/bin/env python
import sys
import os
import json
from PyInquirer import Token, prompt, Separator

CONFIG_PATH = '/data/config.sh'
CONFIG_FOOTER = ''
DNS_PROVIDERS = ['openwrt']
DHCP_PROVIDERS = ['openwrt']
DDNS_PROVIDERS = ['none', 'openwrt']
DDNS_SERVICES = ['route53']
MGMT_PROVIDERS = ['ilo']


def password_repr(password):
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

    def __init__(self, path, footer, dns_providers, dhcp_providers, mgmt_providers):
        self._path = path
        self._footer = footer
        self.cluster = ParameterCollection('cluster', 'Cluster Configuration', [
            Parameter('CLUSTER_NAME', 'Cluster Name'),
            Parameter('ADMIN_PASSWORD', 'Adminstrator Password', password_repr),
            Parameter('USER_PASSWORD', 'User Password', password_repr)])
        self.bastion = ParameterCollection('bastion', 'Bastion Node Configuration', [
            Parameter('BASTION_HOST_NAME', 'Bastion Host Name'),
            Parameter('BASTION_ID_ADDR', 'Bastion IP Address'),
            Parameter('BASTION_SSH_USER', 'Bastion SSH User')])
        self.dns = ParameterCollection('dns', 'Cluster DNS Configuration', [
            ChoiceParameter('DNS_PROVIDER', 'DNS Provider', dns_providers),
            Parameter('DNS_HOST_NAME', 'DNS Host Name'),
            Parameter('DNS_CREDENTIALS', 'DNS Credentials')])
        self.dhcp = ParameterCollection('dhcp', 'Cluster DHCP Configuration', [
            ChoiceParameter('DHCP_PROVIDER', 'DHCP Provider', dhcp_providers),
            Parameter('DHCP_HOST_NAME', 'DHCP Host Name'),
            Parameter('DHCP_CREDENTIALS', 'DHCP Credentials')])
        self.architecture = ParameterCollection('architecture', 'Cluster Architecture', [
            ChoiceParameter('MGMT_PROVIDER', 'Machine Management Provider', mgmt_providers),
            Parameter('IP_POOL', 'Static IP Address Pool'),
            ListDictParameter('CP_NODES', 'Control Plane Machines', 
                [('name', 'Node Name'), ('mac', 'MAC Address'), ('mgmt_mac', 'Management MAC Address')])])

    def _main_menu(self):
        question = [
            {
                'type': 'checkbox',
                'message': 'Which items would you like to change?',
                'name': 'parameters',
                'choices': self.cluster.to_choices() + \
                        self.bastion.to_choices() +  \
                        self.dns.to_choices() + \
                        self.dhcp.to_choices() + \
                        self.architecture.to_choices()
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
            for line in self.cluster.to_bash() + \
                    self.bastion.to_bash() + \
                    self.dns.to_bash() + \
                    self.dhcp.to_bash() + \
                    self.architecture.to_bash():
                outfile.write(line + '\n')
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
    print('Configurator 9000\n')
    return configurator(
            CONFIG_PATH, 
            CONFIG_FOOTER, 
            DNS_PROVIDERS, 
            DHCP_PROVIDERS, 
            MGMT_PROVIDERS).configurate()


if __name__ == "__main__":
    sys.exit(main())

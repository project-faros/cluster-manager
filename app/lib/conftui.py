#!/usr/bin/env python
import sys
import os
import json
from PyInquirer import prompt, Separator, default_style
from prompt_toolkit.shortcuts import Token, print_tokens

STYLE = default_style


class Parameter(object):
    disabled = False
    _value_reprfun = str

    def __init__(self, name, prompt, disabled=False, default=None):
        self._name = name
        self._value = os.environ.get(self._name, default or '')
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
        return "export {}={}".format(self.name, self.jsonify())

    def jsonify(self):
        try:
            json.loads(self.value)
            return "'" + self.value + "'"
        except json.decoder.JSONDecodeError:
            return json.dumps(self.value)


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

    def __init__(self, name, prompt, choices, value_reprfun=str, default=''):
        self._name = name
        self._value = os.environ.get(self._name, default)
        self._prompt = prompt
        self._choices = choices
        self._value_reprfun = value_reprfun

    def update(self):
        question = [
            {
                'type': 'list',
                'message': self._prompt,
                'name': 'choice',
                'default': self._value_reprfun(self._value),
                'choices':
                    [self._value_reprfun(item) for item in self._choices]
            }
        ]
        answer = prompt(question)
        self._value = answer['choice']


class BooleanParameter(ChoiceParameter):

    def __init__(self, name, prompt, default="True"):
        super().__init__(name, prompt, [True, False], default=default)

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

    def __init__(self, name, prompt, keys, default=None):
        self._name = name
        self._value = json.loads(os.environ.get(self._name, default or '[]'))
        self._prompt = prompt
        self._primary_key = keys[0][0]

        # normalize keys
        self._keys = []
        for key in keys:
            if len(key) < 3:
                self._keys += [(key[0], key[-1], "")]
                continue
            if len(key) == 3:
                self._keys += [key]

            for val in self._value:
                if not val.get(key[0]):
                    val[key[0]] = self._keys[-1][2]

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
                           (Token.Arboted, f'{key[1]}: {entry.get(key[0], key[2])}\n')]
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
                       'default': defaults.get(item[0], item[2])}
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


class Configurator(object):

    def __init__(self, path, footer):
        self._path = path
        self._footer = footer
        self.all = []

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

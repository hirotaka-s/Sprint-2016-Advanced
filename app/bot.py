#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tinydb import TinyDB, Query
import json
import requests
import re
import time

class Bot(object):
    def __init__(self):
        self.__commands = BotCommand()

    def is_bot_command(self, recv_message):
        split_message = recv_message.split(' ', 2)
        if split_message[0] == 'bot':
            return True

        return False


    def command(self, recv_message):
        # ['bot', 'cmd', 'data']
        split_message = recv_message.split(' ', 2)
        try:
            if split_message[1].startswith('_'):
                raise AttributeError
            func = getattr(self.__commands, split_message[1])
            params = split_message[2:]
            return func(*params)
        except AttributeError as e:
            print(e)
            return 'No such command: ' + split_message[1]
        except TypeError as e:
            print(e)
            return 'Arguments for command:' + split_message[1] + ' is invalid'


class TodoForBot(object):
    def __init__(self):
        self.__todo_db = TinyDB('todo_for_bot_db.json')
        self.__query = Query()

    def add(self, todo_name, todo_detail):
        try:
            self.__todo_db.insert({'todo_name' : todo_name, 'todo_detail' :todo_detail})
            return 'todo added'
        except:
            return 'todo add faild'


    def delete(self, todo_name):
        try:
            if self.__todo_db.remove(self.__query.todo_name == todo_name):
                return 'todo deleted'
            else:
                return 'todo delete faild. no such todo: ' + todo_name
        except:
            return 'todo delete failed'

    def list(self):
        todo_list = []
        for i, todo in enumerate(self.__todo_db.all()):
            tmp_list = []
            #tmp_list.append('todo'+str(i+1))
            tmp_list.append(todo['todo_name'])
            tmp_list.append(todo['todo_detail'])
            todo_list.append(' '.join(tmp_list))

        if todo_list:
            return '\n'.join(todo_list)
        else:
            return 'todo empty'


class TranslatorForBot(object) :
    def __init__(self):
        self.__html_tag_re = re.compile(r'<[^>]*?>')
        self.__access_token_last_update_time = None
        secrets_fp = open('secret.json')
        secrets = json.load(secrets_fp)
        self.__get_token_payload = {'client_secret': secrets['client_secret'],
                'client_id': secrets['client_id'],
                'scope': 'http://api.microsofttranslator.com',
                'grant_type': 'client_credentials'
        }
        secrets_fp.close()
        self.__access_token = self.__get_access_token()

    def __get_access_token(self):
        res = requests.post('https://datamarket.accesscontrol.windows.net/v2/OAuth2-13', data=self.__get_token_payload)
        self.__access_token_last_update_time = time.time()
        return json.loads(res.text)['access_token']

    def __generate_headers(self):
        return {'Authorization': 'Bearer ' + self.__access_token}

    def __generate_request_params(self, to, text):
        return {'to': to, 'text': text, 'oncomplete':'translated'}

    def translate(self, to, text):
        # if access_token is expired, get new access_token
        try:
            if time.time() - self.__access_token_last_update_time > 600:
                self.__access_token = self.__get_access_token()
            
            res = requests.get('https://api.microsofttranslator.com/v2/Http.svc/Translate', params=self.__generate_request_params(to, text), headers=self.__generate_headers())

            if res.status_code != requests.codes.ok:
                return 'bot: Invlid request! Check your params.'

            return 'bot: ' + self.__html_tag_re.sub('', res.text)
        except Exception as e:
            print(e)
            return 'bot: Some error occord!'
        

class BotCommand(object):
    def __init__(self):
        self.__todo = TodoForBot()
        self.__translator = TranslatorForBot()
        self.__alias_list = {}

    def ping(self):
        return 'pong'

    def todo(self, data):
        command_and_data = data.split(' ', 2)
        
        try:
            if command_and_data[0].startswith('_'):
                raise AttributeError
            func = getattr(self.__todo, command_and_data[0])
            # first element is command 
            params = command_and_data[1:]
            return func(*params)
        except AttributeError as e:
            print(e)
            return 'bot: No such command: ' + command_and_data[0]
        except TypeError as e:
            print(e)
            return 'bot:Arguments for command: "' + command_and_data[0] + '" is invalid or not require params'

    def translate(self, data):
        to_and_text = data.split(' ', 1)
        to = to_and_text[0]
        text = to_and_text[1]

        return self.__translator.translate(to, text)

    def clap(self):
        return 'bot: \U0001F44F'

    def thanks(self):
        return 'bot: You are welcome :)'

    def alias(self, data):
        command_and_alias = data.split(' ', 1)
        command = command_and_alias[0]
        alias = command_and_alias[1]

        try:
            if alias in self.__alias_list.keys():
                return 'bot: Alias:' + alias + ' is already exist.'
            func = getattr(self, alias)
            return 'bot: Already exist command:' + alias + ' is not using as alias.'
        except AttributeError as e:
            None

        try:
            if command.startswith('_'):
                raise AttributeError
            func = getattr(self, command)
            setattr(self, alias, func)

            self.__alias_list[alias] = command
            return 'bot: Set alias ' + command + ' -> ' + alias
        except AttributeError as e:
            return 'bot: No such command: ' + command_and_data[0]

    def unalias(self, data):
        alias = data

        if alias in self.__alias_list.keys():
            delattr(self, alias)
            command = self.__alias_list[alias]
            del self.__alias_list[alias]
            return 'bot: Alias ' + command + ' -> ' + alias + ' is deleted'
        return 'bot: Does not exit. No such alias: ' + alias

    def aliases(self):
        alias_list = [k+' -> '+v for k, v in self.__alias_list.items()]
        return '[' + ', '.join(alias_list) + ']'


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
            return 'No such command: ' + split_message[1]
        except TypeError as e:
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
        self.__expires_in = 600
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
        try:
            res = requests.post('https://datamarket.accesscontrol.windows.net/v2/OAuth2-13', data=self.__get_token_payload)
            self.__access_token_last_update_time = time.time()
            res_json = json.loads(res.text)
            self.__expires_in = int(res_json['expires_in'])
            return res_json['access_token']
        except Exception as e:
            raise e

    def __generate_headers(self):
        return {'Authorization': 'Bearer ' + self.__access_token}

    def __generate_request_params(self, to, text):
        return {'to': to, 'text': text, 'oncomplete':'translated'}

    def translate(self, to, text):
        # if access_token is expired, get new access_token
        try:
            if time.time() - self.__access_token_last_update_time > self.__expires_in:
                self.__access_token = self.__get_access_token()
            
            res = requests.get('https://api.microsofttranslator.com/v2/Http.svc/Translate', params=self.__generate_request_params(to, text), headers=self.__generate_headers())

            if res.status_code != requests.codes.ok:
                return 'bot: Invlid request! Check your params.'

            return 'bot: ' + self.__html_tag_re.sub('', res.text)
        except Exception as e:
            print(e)
            return 'bot: Some error occord!'

class WordCheckerForBot(object):
    def __init__(self):
        self.__is_enable = True
        self.__dict_db = TinyDB('dict_for_bot_db.json')
        self.__query = Query()

    def wordcheck(self, text):
        if self.__is_enable:
            for word in self.__dict_db.all():
                text = text.replace(word['bad_word'], ' [検閲により削除] ') 

        return text
        

    def add(self, word):
        try:
            if self.__dict_db.search(self.__query.bad_word == word):
                return 'bot wordchecker: The word is already added'
            self.__dict_db.insert({'bad_word' : word})
            return 'bot wordchecker: Add word: ' + word
        except Exception as e:
            return 'bot wordchecker: Add failed'


    def delete(self, word):
        try:
            if self.__dict_db.remove(self.__query.bad_word == word):
                return 'bot wordchecker: word deleted'
            else:
                return 'bot wordchecker: Word delete faild. no such word: ' + todo_name
        except Exception as e:
            return 'bot wordchecker: Delete failed'

    def is_enable(self):
        if self.__is_enable:
            return 'bot wordchecker: Enabled'
        else:
            return 'bot wordchecker: Disabled'

    def enable(self):
        if self.__is_enable:
            return 'bot wordchecker: Already enabled'
        else:
            self.__is_enable = True
            return 'bot wordchecker: Enabled'

    def disable(self):
        if self.__is_enable:
            self.__is_enable = False
            return 'bot wordchecker: Disabled'
        else:
            return 'bot wordchecker: Already disabled'

    def list(self):
        word_list = []
        for word in self.__dict_db.all():
            word_list.append(word['bad_word'])

        if word_list:
            return '[ ' + ', '.join(word_list) + ' ]'
        else:
            return 'bot wordchecker: Dictionary is empty'


class AliasForBot(object):
    def __init__(self, bot_command):
        self.__alias_db = TinyDB('alias_for_bot_db.json')
        self.__query = Query()
        self.__bot_command = bot_command
        [self.__register_function(a['command_name'], a['alias_name']) for a in self.__alias_db.all()]

    def __register_function(self, command_name, alias_name):
        func = getattr(self.__bot_command, command_name)
        setattr(self.__bot_command, alias_name, func)
        return True

    def alias(self, command_name, alias_name):
        try:
            if self.__alias_db.search(self.__query.alias_name == alias_name):
                return 'bot alias: Alias:' + alias_name + ' is already exist.'
            if self.__alias_db.search(self.__query.alias_name == command_name):
                return 'bot alias: '+ command_name + ' is alias. Not regist alias.'
            func = getattr(self.__bot_command, alias_name)
            return 'bot alias: Already exist command:' + alias_name + ' is not using as alias.'
        except AttributeError as e:
            None

        try:
            if command_name.startswith('_'):
                raise AttributeError
            if self.__register_function(command_name, alias_name):
                self.__alias_db.insert({'command_name' : command_name, 'alias_name' : alias_name})
                return 'bot alias: Set alias ' + command_name + ' -> ' + alias_name
        except AttributeError as e:
            return 'bot alias: No such command: ' + command_name

    def unalias(self, alias_name):
        if self.__alias_db.search(self.__query.alias_name == alias_name):
            remove_alias = self.__alias_db.search(self.__query.alias_name == alias_name)[0]
            if remove_alias:
                delattr(self.__bot_command, alias_name)
                command_name = remove_alias['command_name']
                self.__alias_db.remove(self.__query.alias_name == alias_name)
                return 'bot unalias: Alias ' + command_name + ' -> ' + alias_name + ' is deleted'
        return 'bot unalias: Does not exit. No such alias: ' + alias_name

    def aliases(self):
        alias_list = [a['command_name']+' -> '+a['alias_name'] for a in self.__alias_db.all()]
        return '[' + ', '.join(alias_list) + ']'
        

class BotCommand(object):
    def __init__(self):
        self.__todo = TodoForBot()
        self.__translator = TranslatorForBot()
        self.__alias = AliasForBot(self)
        self.__wordchecker = WordCheckerForBot()

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
            return 'bot todo: No such command: ' + command_and_data[0]
        except TypeError as e:
            return 'bot todo: Arguments for command: "' + command_and_data[0] + '" is invalid or not require params'

    def translate(self, data):
        to_and_text = data.split(' ', 1)
        if len(to_and_text) < 2:
            return 'bot tnraslate: Invalid param. bot translate [lang] [text]'
            
        to = to_and_text[0]
        text = to_and_text[1]

        return self.__translator.translate(to, text)

    def clap(self):
        return 'bot: \U0001F44F'

    def thanks(self):
        return 'bot: You are welcome :)'

    def alias(self, data):
        command_and_alias = data.split(' ', 1)
        if len(command_and_alias) < 2:
            return 'bot alias: Invalid param. bot alias [command_name] [alias_name]'
        command = command_and_alias[0]
        alias = command_and_alias[1]
        return self.__alias.alias(command, alias)

    def unalias(self, data):
        return self.__alias.unalias(data)

    def aliases(self):
        return self.__alias.aliases()

    def wordchecker(self, data):
        command_and_data = data.split(' ', 1)
        
        try:
            if command_and_data[0].startswith('_'):
                raise AttributeError
            func = getattr(self.__wordchecker, command_and_data[0])
            # first element is command 
            params = command_and_data[1:]
            return func(*params)
        except AttributeError as e:
            return 'bot wordchecker: No such command: ' + command_and_data[0]
        except TypeError as e:
            return 'bot wordchecker: Arguments for command: "' + command_and_data[0] + '" is invalid or not require params'

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tinydb import TinyDB, Query

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
            return 'no such command: ' + split_message[1]
        except TypeError as e:
            print(e)
            return 'arguments for command:' + split_message[1] + ' is invalid'


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



class BotCommand(object):
    def __init__(self):
        self.__todo = TodoForBot()

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
            return 'no such command: ' + command_and_data[0]
        except TypeError as e:
            print(e)
            return 'arguments for command:' + command_and_data[0] + ' is invalid'


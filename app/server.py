#!/usr/bin/env python3

from bottle import static_file, route, run
from threading import Thread

import asyncio
import websockets

from bot import Bot
import json

#serving index.html file on "http://localhost:9000"
def httpHandler():
    while True:
        @route('/')
        def index():
            static_file('index.css', root='./app')
            static_file('client.js', root='./app')
            return static_file("index.html", root='./app')

        @route('/<filename>')
        def server_static(filename):
            return static_file(filename, root='./app')    

        run(host='0.0.0.0', port=10010)


class WebSocketServer(object):
    def __init__(self):
        self.__bot = Bot()
        self.__connected = set()

    @asyncio.coroutine
    def receive_send(self, websocket, path):
        # Register
        self.__connected.add(websocket)
      
        try:
            print("Receiving ...")
            while True:
                message = yield from websocket.recv()
                checked_message = self.__bot.command('bot wordchecker wordcheck ' + message)
                send_message_json = {'data': checked_message}
                yield from asyncio.wait([ws.send(json.dumps(send_message_json)) for ws in self.__connected])
                if self.__bot.is_bot_command(message):
                    send_data = self.__bot.command(message)
                    send_message_json = {'data' : send_data}
                    yield from asyncio.wait([ws.send(json.dumps(send_message_json)) for ws in self.__connected])
        except websockets.exceptions.ConnectionClosed as e:
            print('Close connection. close_code:', e.code) 
        except KeyboardInterrupt:
            print('\nCtrl-C (SIGINT) caught. Exiting...')  
        finally:
            self.__connected.remove(websocket)

if __name__ == '__main__':
    ws_server = WebSocketServer()
    loop = asyncio.get_event_loop()
    start_server = websockets.serve(ws_server.receive_send, '0.0.0.0', 3000)
    server = loop.run_until_complete(start_server)
    print('Listen')

    t = Thread(target=httpHandler)
    t.daemon = True
    t.start()

    try:
        loop.run_forever()
    finally:
        server.close()
        start_server.close()
        loop.close()

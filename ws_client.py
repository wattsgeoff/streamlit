import websocket
import requests
import threading
import time
import json
import asyncio

class Client(threading.Thread):
    
    msg_data = None
    is_open = False
    did_close = False

    def __init__(self, url, exchange):
        super().__init__()
        # create websocket connection
        self.ws = websocket.WebSocketApp(
            url=url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )

        # exchange name
        self.exchange = exchange

    # keep connection alive
    def run(self):
        while True:
            self.ws.run_forever()

    # convert message to dict, process update
    def on_message(self, message):
        print(message)
        self.msg_data = json.loads(message)

    # catch errors
    def on_error(self, error):
        print(error,'**** error')
        if str(error) == 'Handshake status 429 Too Many Requests':
            print('**** timout error')
            self.ws.close()
            self.__del__()

    # run when websocket is closed
    def on_close(self):
        print("### closed ###")
        self.did_close = True

    # run when websocket is initialised
    def on_open(self):
        self.is_open = True
        print(f'Connected to {self.exchange}\n')

    def __del__(self):
        self.ws.close()
        self.ws = None
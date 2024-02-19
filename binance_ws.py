import pandas as pd
import numpy as np

import sys
sys.path.append("..")
import os 
dir_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
sys.path.append(dir_path)

from ws_client import Client
from pair_maps import *

import json
from datetime import datetime
import datetime as dt

class Binance_WS(Client):
    
    exchange='binance-futures'
    start_time = None
    ws_lag = 0
    subscriptions = dict()

    def __init__(self, url = "wss://stream.binance.com:9443/ws"):#"wss://fstream.binance.com/ws"): 
        super().__init__(url, self.exchange)

    # convert dict to string, subscribe to data streem by sending message
    def on_open(self):
        super().on_open()
        for s in self.subscriptions:
            print(s)
            try:
                self.ws.send(json.dumps(self.subscriptions[s]['params']))
            except Exception as e:
                print(e)
        self.start_time = pd.Timestamp.now(tz='UTC')

    def on_message(self, message):
        print(message)
        self.msg = message
        data = json.loads(message) 
        if 'u' in data:
            self.subscriptions['bookTicker']['msg_fun'](data)

    def bookTicker_sub(self, pair):
        self.subscriptions['bookTicker'] = {
                        'params' : self.get_params(pair),
                        'msg_fun' : self.bookTicker_msg
                    }
        self.bookTicker_data = {pair:{'ts':None, 'bid':None, 'ask':None, 'bid_size':None, 'bid_size':None}}

    def get_params(self, pair):
        params = {
                    "method": "SUBSCRIBE",
                    "params":
                    [
                        f"{pair.lower()}@bookTicker",
                    ],
                    "id": 1
                }
        print(params)
        return params
    
        #     {
        # "e":"bookTicker",         // event type
        # "u":400900217,            // order book updateId
        # "E": 1568014460893,       // event time
        # "T": 1568014460891,       // transaction time
        # "s":"BNBUSDT",            // symbol
        # "b":"25.35190000",        // best bid price
        # "B":"31.21000000",        // best bid qty
        # "a":"25.36520000",        // best ask price
        # "A":"40.66000000"         // best ask qty
        # }
    def bookTicker_msg(self, data):
        try:
            pair = data['s'].upper()
            self.bookTicker_data[pair] = {
                'ts': pd.to_datetime(float(data['u']),unit='ms'),
                'bid': float(data['b']),
                'ask': float(data['a']),
                'bid_size': float(data['B']),
                'ask_size': float(data['A']),
            }
        except Exception as e: print(e)
    


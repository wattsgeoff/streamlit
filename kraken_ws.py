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

class Kraken_WS(Client):
    
    exchange='kraken'
    start_time = None
    ws_lag = 0
    subscriptions = dict()

    def __init__(self, url = "wss://ws.kraken.com/"):
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
        self.msg = message
        data = json.loads(message) 
        if type(data)==list:
            self.subscriptions[data[2]]['msg_fun'](data)

    def spread_sub(self, pairs):
        self.subscriptions['spread'] = {
                        'params' : self.get_params(pairs, "spread"),
                        'msg_fun' : self.spread_msg
                    }
        self.spread_data = dict()
        for p in pairs:
            self.spread_data[p] = {'ts':None, 'bid':None, 'ask':None, 'bid_size':None, 'bid_size':None}

    def trade_sub(self, pairs, rsi_period = 14, back_trades=50):
        self.trades_back = back_trades
        self.rsi_period = rsi_period
        self.subscriptions['trade'] = {
                        'params' : self.get_params(pairs, "trade"),
                        'msg_fun' : self.trade_msg
                    }
        self.trade_data = dict()
        self.buy_ewma = 0
        self.sell_ewma = 0
        for p in pairs:
            self.trade_data[p] = pd.DataFrame(columns=['price','volume','side','orderType','misc'])

    def get_params(self, pairs, sub_name):

        pairs_ = list()
        for p in pairs:
                pairs_.append(pair_maps['kraken'][p])
        params = {
                                "event": "subscribe",
                                "pair": pairs_,
                                "subscription": {
                                    "name": sub_name
                                }
        }
        return params
        
    def spread_msg(self, data):
        try:
            pair = pair_maps['kraken'][data[3]]
            sp_data = data[1]
            self.spread_data[pair] = {
                'ts': pd.to_datetime(float(sp_data[2])*1000000,unit='us'),
                'bid': float(sp_data[0]),
                'ask': float(sp_data[1]),
                'bid_size': float(sp_data[3]),
                'ask_size': float(sp_data[4]),
            }
        except Exception as e: print(e)
    
    def trade_msg(self, data):
        pair = pair_maps['kraken'][data[3]]
        for t in data[1]:
            ts = pd.to_datetime(float(t.pop(2))*1000000,unit='us', utc=True)
            try:
                # if t[2] == 'b': self.buy_ewma = (self.buy_ewma*(self.rsi_period-1)+float(t[1]))/self.rsi_period
                # else : self.sell_ewma = (self.sell_ewma*(self.rsi_period-1)+float(t[1]))/self.rsi_period
                # t.extend([self.buy_ewma, self.sell_ewma, 100-(100/(1+(self.buy_ewma/self.sell_ewma)))])
                self.trade_data[pair].loc[ts] = t
            except Exception as e: print(e)
        self.trade_data[pair] = self.trade_data[pair].iloc[-self.trades_back:]
    


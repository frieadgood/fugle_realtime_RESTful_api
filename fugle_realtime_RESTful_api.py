#!/usr/bin/env python
# coding: utf-8

# <h1>Table of Contents<span class="tocSkip"></span></h1>
# <div class="toc"><ul class="toc-item"></ul></div>

# In[2]:


from fugle_realtime import intraday

import pandas as pd
import numpy as np
import datetime
import requests

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
import dash_daq as daq


# In[32]:


class chart_api():
    
    def __init__(self, api_token):
        
        self.api_token = api_token
        
    def get_chart_data(self, n, symbol_id):

        now = datetime.datetime.now()
        today = now.strftime('%Y-%m-%d')
        close_time = datetime.datetime(now.year,now.month,now.day, 13, 30)

        time_index = pd.date_range(start=f'{today} 09:00:00',
                                   end=f'{today} 13:30:00', freq=f'{n}T', closed='right')

        df_time = pd.DataFrame(time_index, columns=['at'])

        df = intraday.chart(
            symbolId=symbol_id, apiToken=self.api_token, output='dataframe')


        df['at'] = df['at'].apply(lambda x: x.astimezone(None) + datetime.timedelta(hours=8))
        df = df.set_index('at')

        df = df.asfreq('1T')
        df['close'] = df['close'].fillna(method='ffill')
        df['volume'] = df['volume'].fillna(0)
        df = df.fillna(axis=1, method='ffill')

        df = df[['open', 'high', 'low', 'close', 'volume']]

        df_ohlc = df.resample(f'{n}T', kind='period').agg({'open': 'first',
                                                           'high': 'max',
                                                           'low': 'min',
                                                           'close': 'last',
                                                           'volume': 'sum'
                                                          })

        df_ohlc.index = df_ohlc.index + datetime.timedelta(minutes=n-1)

        df_ohlc = df_ohlc.to_timestamp().reset_index()
        
        df_ohlc = pd.merge(df_time, df_ohlc, on='at', how='outer')
        df_ohlc['at'] = df_ohlc['at'].apply(lambda x: x if x <= close_time else close_time)
        
        return df_ohlc
    
    
    def plot_ohlc(self, df, rise_color, down_color):

        return {
            'type':'candlestick',
            'x':df['at'],
            'open':df['open'],
            'high':df['high'],
            'low':df['low'],
            'close':df['close'],
            'name':'K線圖',
            'increasing':{'line':{'color':rise_color}},
            'decreasing':{'line':{'color':down_color}}
        }
      
    def plot_MA(self, df, n, line_color, line_width):

        df[f'{n}MA'] = df['close'].rolling(n).mean()

        return {
            'type':'scatter',
            'x':df['at'],
            'y':df[f'{n}MA'],
            'mode':'lines',
            'line':{'color':line_color, 'width':line_width},
            'name':f'{n}MA'
        }

    def plot_volume_bar(self, df, rise_color, down_color):

        color = []
        for i in range(len(df)):
            try:
                if df['close'][i] > df['open'][i]:
                    color.append(rise_color)

                elif df['close'][i] < df['open'][i]:
                    color.append(down_color)

                elif df['close'][i] == df['open'][i]:

                    if df['close'][i] > df['close'][i-1]:
                        color.append(rise_color)
                    elif df['close'][i] < df['close'][i-1]:
                        color.append(down_color)
                    elif df['close'][i] == df['close'][i-1]:
                        color.append(color[-1])

            except (IndexError, KeyError):
                color.append(rise_color)

        return {
            'type':'bar',
            'x':df['at'],
            'y':df['volume']/1000,
            'marker':{'color':color},
            'name':'volume_bar',
            'xaxis':'x',
            'yaxis':'y2'
        }


# In[33]:


class quote_api():

    def __init__(self, api_token):

        self.api_token = api_token

    def get_first_quote_data(self, symbol_id):

        message = intraday.quote(apiToken= self.api_token, symbolId=symbol_id, output='raw')

        ask = message['order']['bestAsks']
        ask.reverse()
        
        df_ask = pd.DataFrame(ask, columns=['price', 'unit']).rename(columns={'unit': 'ask_unit'})

        bid = message['order']['bestBids']
        bid.reverse()
        
        df_bid = pd.DataFrame(bid, columns=['unit', 'price']).rename(
            columns={'unit': 'bid_unit'})

        df_quote = pd.merge(df_ask, df_bid, on='price', how='outer')
        df_quote = df_quote[['bid_unit', 'price', 'ask_unit']]

        price_list = list(df_quote['price'])

        return df_quote, price_list

    def get_new_quote_data(self,symbol_id, df_quote):

        df_quote2, price_list = self.get_first_quote_data(symbol_id)

        df_quote = pd.concat([df_quote, df_quote2], axis=0).drop_duplicates(subset='price', keep='last')
        df_quote = df_quote.sort_values('price', ascending=False).reset_index(drop=True)

        return df_quote, price_list

    def update_quote_data(self, input_symbol):

        global df_quote, symbol

        try:
            if input_symbol == symbol:
                df_quote, price_list = self.get_new_quote_data(symbol, df_quote)
            else:
                symbol = input_symbol
                df_quote, price_list = self.get_first_quote_data(symbol)
        except:
            symbol = input_symbol
            df_quote, price_list = self.get_first_quote_data(symbol)

        return df_quote, price_list, symbol

    def plot_order_book(self, dataframe, price_list, symbol_id):

        rows = []
        for i in range(len(dataframe)):
            row = []
            for col in dataframe.columns:
                value = dataframe.iloc[i][col]

                if col == 'price':

                    if value not in price_list:

                        cell = html.Td(html.A(href='https://www.fugle.tw/ai/'+symbol_id,
                                              children=value,
                                              style={'color': 'gray'}),
                                       style={'font-size': 16, 'text-align': 'center'})

                    elif value in price_list:

                        cell = html.Td(html.A(href='https://www.fugle.tw/ai/'+symbol_id,
                                              children=value),
                                       style={'font-size': 16, 'text-align': 'center'})

                else:
                    cell = html.Td(children=value,
                                   style={'font-size': 16, 'text-align': 'center'})

                row.append(cell)
            rows.append(html.Tr(row))

        return html.Table(
            [html.Tr([html.Th(col) for col in dataframe.columns],
                     style={'font-size': 16, 'text-align': 'center', 'table-align': 'center'})] + rows
        )


# In[34]:


class line_notify():
    
    def __init__(self, api_token, line_token):
        
        self.api_token = api_token
        self.line_token = line_token
        
    def lineNotifyMessage(self, msg):
    
        headers = {
           "Authorization": "Bearer " + self.line_token, 
           "Content-Type" : "application/x-www-form-urlencoded"
       }

        payload = {'message': msg}
        r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
        return r.status_code
    
    def target_price_strategy(self, symbol_id, rise_target_price, drop_target_price):

        message = intraday.quote(apiToken= self.api_token, symbolId=symbol_id, output='raw')
        current_price = message['trade']['price']

        if current_price > rise_target_price:
            self.lineNotifyMessage('快訊！' + symbol_id + '價格已經高過' + str(rise_target_price) + '元\n'+
                                   'https://www.fugle.tw/trade?symbol_id=' + symbol_id + '&openExternalBrowser=1')

        elif current_price < drop_target_price:
            self.lineNotifyMessage('快訊！' + symbol_id + '價格已經跌破' + str(drop_target_price) + '元\n'+
                                   'https://www.fugle.tw/trade?symbol_id=' + symbol_id + '&openExternalBrowser=1')

        else:
            pass
        
    def target_change_strategy(self, symbol_id, rise_target_change, drop_target_change):

        message = intraday.quote(apiToken=self.api_token, symbolId=symbol_id, output='raw')
        current_price = message['trade']['price']

        symbol_info = intraday.meta(symbolId= symbol_id, apiToken=self.api_token, output='raw')
        adjust_open = symbol_info['priceReference']

        if (current_price - adjust_open) / adjust_open > rise_target_change:
            self.lineNotifyMessage('快訊！' + symbol_id + '漲幅已經高過' + str(rise_target_change*100) + '%\n'+
                                   'https://www.fugle.tw/trade?symbol_id=' + symbol_id + '&openExternalBrowser=1')

        elif (current_price - adjust_open) / adjust_open < -drop_target_change:
            self.lineNotifyMessage('快訊！' + symbol_id + '跌幅已經低過' + str(drop_target_change*100) + '%\n'+
                                   'https://www.fugle.tw/trade?symbol_id=' + symbol_id + '&openExternalBrowser=1')

        else:
            pass

        return current_price, adjust_open


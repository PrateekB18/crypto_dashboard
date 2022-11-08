from binance.client import Client
from datetime import datetime
from pandas import DataFrame as df
import pandas as pd
import keys

def binance_price(symbol, time, days):
    client = Client(api_key=keys.pkey, api_secret=keys.skey)
    client.API_URL = 'https://api.binance.com/api'
    time = time
    interval = eval(f'Client.KLINE_INTERVAL_{time}')
    candles = client.get_historical_klines(symbol, interval, f'{days} days ago UTC')#f'1 Jan, {i}', limit = 1000)

    candles_data_frame = df(candles)
    candles_data_frame = candles_data_frame.drop_duplicates(subset=[0], keep='first')
    candles_data_frame_date = candles_data_frame[0]

    final_date = []

    for time in candles_data_frame_date.unique():
        readable = datetime.fromtimestamp(int(time/1000)).strftime("%d-%b-%Y %I:%M %p")
        final_date.append(readable)

    candles_data_frame.pop(0)
    candles_data_frame.pop(11)

    dataframe_final_date = df(final_date)
    dataframe_final_date.columns = ['date']
    final_dataframe = candles_data_frame.join(dataframe_final_date)
    final_dataframe.set_index('date', inplace=True)
    final_dataframe.columns = ['open', 'high', 'low', 'close', 'volume', 'close_time', 'asset_volume', 'trade_number', 'taker_buy_base', 'taker_buy_quote']
    cols = final_dataframe.columns
    final_dataframe[cols] = final_dataframe[cols].apply(pd.to_numeric, errors='coerce')
    return final_dataframe

def binance_symbols(currency):
    client = Client(api_key=keys.pkey, api_secret=keys.skey)
    symbols = []
    exchange_info = client.get_exchange_info()
    for s in exchange_info['symbols']:
        symbols.append(s['symbol'])
    l = len(currency)   
    symbols = [s for s in symbols if currency in s[-l:]]
    return symbols

def binance_intervals():
    options = dir(Client)
    intervals = [o[15:] for o in options if 'KLINE_INTERVAL' in o]
    return intervals

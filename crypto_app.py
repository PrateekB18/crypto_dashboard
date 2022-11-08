import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd
from datetime import datetime

from binance_data import binance_price 
from binance_data import binance_symbols
from binance_data import binance_intervals

purchase_currency = 'AUD'
crypto_list = pd.DataFrame([['BTC','Bitcoin'],['ETH','Ethereum'], ['XRP', 'Ripple'],
                       ['DOGE', 'Dogecoin'], ['SHIB', 'Shiba Inu'], ['UNI', 'Uniswap'],
                       ['TRX', 'Tron'], ['LINK', 'Chainlink'], ['SOL', 'Solana'], 
                       ['LUNA', 'Terra' ], ['BEAM', 'Beam'], ['MANA', 'Decentraland'],
                       ['ADA', 'Cardano']],
                       columns=['Symbol', 'Label'])

crypto_dict = dict(zip(crypto_list['Label'], crypto_list['Symbol']))

intervals = pd.DataFrame([['15 Minutes', '15MINUTE'],['30 Minutes', '30MINUTE'],['1 Hour', '1HOUR'],
                          ['4 Hours', '4HOUR'],['12 Hours', '12HOUR'],['24 Hours', '1DAY']],
                         columns=['Symbol', 'Label'])

interval_dict = dict(zip(intervals['Symbol'], intervals['Label']))

days  = list(range(1,366))
days_list = [str(i) for i in days]
hist_dict = dict(zip(days_list, days))


app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div(
        [
            
    dcc.Dropdown(
        id='dropdown1',
        options=[{'label':label, 'value': symbol} for label, symbol in interval_dict.items()], 
        placeholder="Select Time Interval",
        style=dict(
            width='40%',
            verticalAlign="middle"
            )
    ),

    dcc.Dropdown(
        id='dropdown2',
        options=[{'label':label, 'value': symbol} for label, symbol in crypto_dict.items()], 
        placeholder="Select Crypto",
        style=dict(
            width='40%',
            verticalAlign="middle"
            )
    ),
    
    dcc.Dropdown(
        id='dropdown3',
        options=[{'label':label, 'value': symbol}for label, symbol in hist_dict.items()], 
        placeholder="Select Days Range",
        style=dict(
            width='40%',
            verticalAlign="middle"
            )
    )
    
    ], style=dict(display='flex')
),
    
    dcc.Checklist(
    id='toggle-rangeslider',
    options=[{'label': 'Include Rangeslider', 'value': 'slider'}],
    value=['slider']
),
    
    dcc.Graph(id="graph"),
])

@app.callback(
    Output("graph", "figure"), 
    [Input('dropdown1', 'value'),
    Input('dropdown2', 'value'),
    Input('dropdown3', 'value'),
    Input('toggle-rangeslider', 'value')])
    
def make_dataframe(dropdown1, dropdown2, dropdown3, value):
    symbol = [s for s in binance_symbols(purchase_currency) if dropdown2 in s][0]
    df = binance_price(symbol, dropdown1, dropdown3)
    df['MA10'] = df.close.rolling(10).mean()
    df['MA20'] = df.close.rolling(20).mean()
    df['MA40'] = df.close.rolling(40).mean()
    
    fig = make_subplots(vertical_spacing = 1, rows=1, cols=1)
    fig.add_trace(go.Candlestick(
        x=df.index[:],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        increasing_line_color= 'rgb(37,202,160)', 
        decreasing_line_color= 'rgb(249,91,58)',
        name="Candlestick Chart"
    )),
    fig.add_trace(go.Scatter(x=df.index[:],y=df['MA10'], mode = 'lines',
                             name="10 step Moving Average",
                             line_color = 'rgb(279,179,71)'),row=1, col=1),
    fig.add_trace(go.Scatter(x=df.index[:],y=df['MA20'], mode = 'lines',
                             name="20 step Moving Average",
                             line_color = 'rgb(32,169,202)'),row=1, col=1),
    fig.add_trace(go.Scatter(x=df.index[:],y=df['MA40'], mode = 'lines',
                             name="40 step Moving Average",
                             line_color = 'rgb(51,61,71)'),row=1, col=1),

    fig.update_layout(
        autosize=True,
        height=700,
        xaxis_rangeslider_visible='slider' in value,
        title=f'{dropdown2} vs {purchase_currency} Candlestick Chart - {dropdown1}',
        titlefont = dict(size=28),
        yaxis_title=f'{dropdown2} Price ({purchase_currency})',
        plot_bgcolor='rgba(51,61,71,0.025)',
        font_family="Times New Roman",
        yaxis = dict(
            tickfont = dict(size=20),
            titlefont = dict(size=24),
            gridcolor='rgba(51,61,71,0.2)'
            ),
        xaxis = dict(
            tickfont = dict(size=20),
            gridcolor='rgba(51,61,71,0.2)'
            ),
        xaxis2 = dict(
            showticklabels=False,
            gridcolor='rgba(51,61,71,0.2)'
            ),
        yaxis2 = dict(
            showticklabels=False,
            gridcolor='rgba(51,61,71,0.2)'
            )
    )

    return fig

app.run_server(debug=True)

# fugle_realtime_RESTful_api
In this notebook, I will introduce how to build a real-time stock quote application. <br><br>
For that purpose, we will use Fugle Realtime API and Dash. <br><br>
## Documentations
* [Fugle Developer](https://developer.fugle.tw/) <br><br>
  * https://developer.fugle.tw/realtime <br><br>
* [GitHub](https://github.com/) <br><br>
  * https://github.com/fortuna-intelligence/fugle-realtime-py <br><br>
* [Dash](https://plot.ly/dash)
## Environment
* Python 3.6.9
## Installation
```python
pip install -r requirements.txt
```
## Usage
```py
from fugle_realtime_RESTful_api import *
```
### chart_api
```py
chart = chart_api(api_token = 'demo')
```
If you want to get your own `api_token`, please visit [Fugle Realtime API](https://developer.fugle.tw/realtime) for more information.
Otherwise, you just can use `api_token = 'demo'` and query Symbol ID 2884 for trial.
#### `get_chart_data`：Get min K data from this function
```py
df_ohlc = chart.get_chart_data(n = 5, symbol_id = '2884')
```
`n` represents the time interval of the min K data. <br>
`symbol_id` represents the stock code of the Taiwan stock market. <br>
#### `plot_ohlc` & `plot_volume_bar`：Plot cnadlestick chart from these functions
```py
chart.plot_ohlc(df = df_ohlc, rise_color = 'red', down_color = 'green')
chart.plot_volume_bar(df = df_ohlc, rise_color = 'red', down_color = 'green')
```
When close price is larger than open price, `rise_color` will be in `red`. <br>
On the other hands, when close price is less than open price, `down_color` will be in `green`.
#### `plot_MA`：Plot Moving Average(MA) line from this function
```py
chart.plot_MA(df = df_ohlc, n = 5, line_color = 'blue', line_width = 2)
```
`n` represents the time interval of the MA line. <br>
### quote_api
```py
quote = quote_api(api_token = 'demo')
```
#### `update_quote_data`：Update order book(最佳五檔) data from this function
```py
df_quote, price_list, symbol = quote.update_quote_data(symbol_id = '2884')
```
#### `plot_order_book`：Plot order book as html table
```py
quote.plot_order_book(df_quote, price_list, symbol)
```
`df_quote` represents an order book that records the historical price since the execution of the code. <br>
`price_list` represents the current price of the order book.
### line_notify
```py
line = line_notify(api_token = 'demo', line_token = 'YOUR LINE NOTIFY TOKEN')
```
#### `lineNotifyMessage`：Send any message to the line notify bot
```py
line.lineNotifyMessage(msg)
```
#### `target_price_strategy`：You can use this function to set the target price strategy in line notify bot.
```py
line.target_price_strategy(symbol_id = '2884', rise_target_price = 30, drop_target_price = 20)
```
`rise_target_price` and `drop_target_price` represent the upper and lower bound of the price strategy.
#### `target_change_strategy`：You can use this function to set the target change strategy in line notify bot.
```py
line.target_change_strategy(symbol_id = '2884', rise_target_change = 0.01, drop_target_change = 0.01)
```
`rise_target_change` and `drop_target_change` represent the upper and lower bound of the change strategy.
### Dashboard Demo
**We use Dash to build our real-time stock quote application.** <br>
[Dash](https://dash.plot.ly/introduction) is a productive Python framework for building web applications. <br>
It is really suited for everyone to bulid a dashboard with highly custom user interface in Python. <br><br>
![Demo](https://i.imgur.com/paVdkTa.png)
**At the end, we can see the results at `http://127.0.0.1:8050`！** <br>
If you want to get more informations, you can check `demo.ipynb`.

# fugle_realtime_restful_api
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
from fugle_realtime_restful_api import *
```
### `chart_api`
```py
chart = chart_api(api_token = 'demo')
```
#### `get min K data`
```py
df_ohlc = chart.get_chart_data(n = 5, symbol_id = '2884')
```
`n` represents the time interval of the min K data. <br>
`symbol_id` represents the stock code of the Taiwan stock market. <br>
#### `plot_ohlc` & `plot_volume_bar`
```py
chart.plot_ohlc(df = df_ohlc, rise_color = 'red', down_color = 'green')
chart.plot_volume_bar(df = df_ohlc, rise_color = 'red', down_color = 'green')
```
#### `plot_MA`
```py
chart.plot_MA(df = df_ohlc, n = 5, line_color = 'blue', line_width = 2)
```
### `quote_api`
```py
quote = quote_api(api_token = 'demo')
```
#### `update_quote_data`
```py
df_quote, price_list, symbol = quote.update_quote_data(symbol_id = '2884')
```
#### `plot_order_book`
```py
quote.plot_order_book(df_quote, price_list, symbol)
```
### `line_notify`
```py
line = line_notify(api_token = 'demo', line_token = 'YOUR LINE NOTIFY TOKEN')
```
#### `lineNotifyMessage`
```py
line.lineNotifyMessage(msg)
```
#### `target_price_strategy`
```py
line.target_price_strategy(symbol_id = '2884', rise_target_price = 30, drop_target_price = 20)
```
#### `target_change_strategy`
```py
line.target_change_strategy(symbol_id = '2884', rise_target_change = 0.01, drop_target_change = 0.01)
```

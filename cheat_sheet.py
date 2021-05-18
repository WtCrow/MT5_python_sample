import MetaTrader5 as mt5


login = int(input('Enter login '))
password = input('Enter password ')

warning = """
WARNING! This is NOT effective strategy. This script might start only on demo-account!
Author of code is not responsible for your financial losses.
Enter 'yes' for accept and continue: 
"""
answer = input(warning)
if answer != 'yes':
    quit(1)

# start terminal and login
mt5.initialize()
result = mt5.login(login=login, password=password)
if result:
    print('Login successful')
else:
    raise Exception('Not login')

symbol = 'EURUSD'
volume = 0.01

# current candle
print(mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 1)[0])
# get last closed candle
print(mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 1, 1)[0])
# get 20 last closed candles
print(mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 1, 20))

# open order by market
request = {
    'action': mt5.TRADE_ACTION_DEAL,
    'symbol': symbol,
    'volume': volume,
    'type': mt5.ORDER_TYPE_BUY,
    'magic': 12345,
    'sl': 1.1,
    'tp': 1.3,
    'type_time': mt5.ORDER_TIME_GTC,
}
result = mt5.order_send(request)
print('Open order by market result: ', result)
if result.retcode != 10009:
    raise Exception(f'Bad status {result.retcode}')
print('Current positions: ', mt5.positions_get(symbol='AUDCAD'))

# modify sl/tp in opened position
order = mt5.positions_get(symbol=symbol)[0]
request = {
    'action': mt5.TRADE_ACTION_SLTP,
    'position': order.ticket,
    'symbol': order.symbol,
    'sl': 1.05,
    'tp': 1.35,
}
result = mt5.order_send(request)
print('Update sl/tp result: ', result)
if result.retcode != 10009:
    raise Exception(f'Bad status {result.retcode}')
print('Current positions: ', mt5.positions_get(symbol='AUDCAD'))

# close opened order by market
order = mt5.positions_get(symbol=symbol)[0]
request = {
    'action': mt5.TRADE_ACTION_DEAL,
    'symbol': order.symbol,
    'volume': order.volume,
    'type': mt5.ORDER_TYPE_SELL,  # inverted type
    'position': order.ticket,  # specific ticker
    'type_time': mt5.ORDER_TIME_GTC,
}
result = mt5.order_send(request)
print('Close order result ', result)
if result.retcode != 10009:
    raise Exception(f'Bad status {result.retcode}')
print('Current positions: ', mt5.positions_get(symbol='AUDCAD'))

# check price on pending order
print("Price for pending order", mt5.order_calc_margin(mt5.ORDER_TYPE_BUY, symbol, volume, 1.22))
# open pending order
request = {
    'action': mt5.TRADE_ACTION_PENDING,
    'symbol': symbol,
    'volume': volume,
    'price': 1.22,
    'type': mt5.ORDER_TYPE_BUY_LIMIT,
    'sl': 1.1,
    'tp': 1.3,
    'magic': 12345,
    'type_time': mt5.ORDER_TIME_GTC,
    'type_filling': mt5.ORDER_FILLING_RETURN,
}
result = mt5.order_send(request)
print('Open pending order result ', result)
if result.retcode != 10009:
    raise Exception(f'Bad status {result.retcode}')
print('Current pending orders: ', mt5.orders_get(symbol='AUDCAD'))
print('Current positions: ', mt5.positions_get(symbol='AUDCAD'))

# update pending order
order = mt5.orders_get(symbol=symbol)[0]
request = {
    'action': mt5.TRADE_ACTION_MODIFY,
    'order': order.ticket,
    'price': order.price_open,
    'symbol': order.symbol,
    'sl': 1.05,
    'tp': 1.35,
}
result = mt5.order_send(request)
print('Result modify pending order ', result)
if result.retcode != 10009:
    raise Exception(f'Bad status {result.retcode}')
print('Current pending orders: ', mt5.orders_get(symbol='AUDCAD'))
print('Current positions: ', mt5.positions_get(symbol='AUDCAD'))

# delete pending order
request = {
    'action': mt5.TRADE_ACTION_REMOVE,
    'order': mt5.orders_get(symbol=symbol)[0].ticket,
}
result = mt5.order_send(request)
print('Result delete pending order ', result)
if result.retcode != 10009:
    raise Exception(f'Bad status {result.retcode}')
print('Current pending orders: ', mt5.orders_get(symbol='AUDCAD'))
print('Current positions: ', mt5.positions_get(symbol='AUDCAD'))

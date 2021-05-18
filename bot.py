import MetaTrader5 as mt5
from sma import SMA


class MovingTraderBot:

    def __init__(self, login, password, symbol, timeframe, fast_p=10, slow_p=20):
        self.login = login
        self.password = password

        self.symbol = symbol
        self.lot = 0.01
        self.timeframe = timeframe
        self.fast_p = fast_p
        self.slow_p = slow_p

        self.fast = SMA(fast_p)
        self.slow = SMA(slow_p)

        self.last_checked_time = None

    def init(self):
        mt5.initialize()
        mt5.login(login=self.login, password=self.password)
        self.last_checked_time = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 1, 1)[0][0]
        data_for_slow = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 1, self.slow_p)
        data_for_fast = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 1, self.fast_p)

        # 0-time 1-open 2-high 3-low 4-close 5-tick_volume 6-spread 7-real_volume
        for candle in data_for_slow:
            self.slow.append_value(candle[4])

        for candle in data_for_fast:
            self.fast.append_value(candle[4])

    def is_order_buy(self, order):
        return order.type in (mt5.ORDER_TYPE_BUY, mt5.ORDER_TYPE_BUY_LIMIT,
                              mt5.ORDER_TYPE_BUY_STOP, mt5.ORDER_TYPE_BUY_STOP_LIMIT)

    def open_by_market(self, volume, order_type):
        request = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': self.symbol,
            'volume': volume,
            'type': order_type,
            'type_time': mt5.ORDER_TIME_GTC,
        }
        result = mt5.order_send(request)
        if result.retcode != 10009:
            print(f'Error {result}')

    def close_all_orders(self):
        pending_orders = mt5.orders_get(symbol=self.symbol)
        for order in pending_orders:
            request = {
                'action': mt5.TRADE_ACTION_REMOVE,
                'order': order.ticket,
            }
            result = mt5.order_send(request)
            if result.retcode != 10009:
                print(f'Error {result}')

        positions = mt5.positions_get(symbol=self.symbol)
        for order in positions:
            request = {
                'action': mt5.TRADE_ACTION_DEAL,
                'symbol': order.symbol,
                'volume': order.volume,
                'type': mt5.ORDER_TYPE_SELL if self.is_order_buy(order) else mt5.ORDER_TYPE_BUY,
                'position': order.ticket,
                'type_time': mt5.ORDER_TIME_GTC,
            }
            result = mt5.order_send(request)
            if result.retcode != 10009:
                print(f'Error {result}')

    def trade(self, candle):
        self.fast.append_value(candle[4])
        self.slow.append_value(candle[4])

        pre_fast, pre_slow = self.fast[-2], self.slow[-2]
        fast, slow = self.fast[-1], self.slow[-1]

        print(fast, slow)

        if pre_fast <= pre_slow and fast > slow:
            print('Buy')
            if mt5.positions_get(symbol=self.symbol) or mt5.orders_get(symbol=self.symbol):
                self.close_all_orders()
            self.open_by_market(self.lot, mt5.ORDER_TYPE_BUY)
        elif pre_fast >= pre_slow and fast < slow:
            print('Sell')
            if mt5.positions_get(symbol=self.symbol) or mt5.orders_get(symbol=self.symbol):
                self.close_all_orders()
            self.open_by_market(self.lot, mt5.ORDER_TYPE_SELL)

    def run(self):
        self.init()

        while True:
            last_closed_candle = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 1, 1)[0]
            if self.last_checked_time == last_closed_candle[0]:
                continue
            self.last_checked_time = last_closed_candle[0]
            self.trade(last_closed_candle)


if __name__ == '__main__':
    login_acc = int(input('Enter login '))
    password_acc = input('Enter password ')

    warning = """
    WARNING! This is NOT effective strategy. This script might start only on demo-account!
    Author of code is not responsible for your financial losses.
    Enter 'yes' for accept and continue: 
    """
    answer = input(warning)
    if answer != 'yes':
        quit(1)

    MovingTraderBot(login_acc, password_acc, 'EURUSD', mt5.TIMEFRAME_M5, 10, 20).run()

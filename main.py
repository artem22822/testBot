import json
import websocket

from strategy import ObserverBTCUSD
from strategy.first import TestStrategy
from account import Account

configs = {
    'buy_amount': 1,
    'exchange': {
        'Bitfinex': {
            'url': 'wss://api.bitfinex.com/ws/2',
            'api_key': '',
            'api_secret': '',
        },
    },

    'btc_pairs': ['ETHBTC', 'LTCBTC', 'XMRBTC', 'XRPBTC', 'EOSBTC',
                  'BCHBTC', 'NEOBTC', 'IOTABTC', 'ETCBTC', 'OMGBTC',
                  'DASHBTC', 'TRXBTC', 'BTGBTC', 'ZECBTC', 'ETPBTC',
                  'SANBTC'],
    'usd_pairs': ['ETHUSD', 'LTCUSD', 'XMRUSD', 'XRPUSD', 'EOSUSD',
                  'BCHUSD', 'NEOUSD', 'IOTAUSD', 'ETCUSD', 'OMGUSD',
                  'DASHUSD', 'TRXUSD', 'BTGUSD', 'ZECUSD', 'ETPUSD',
                  'SANUSD']
}

x = {'xrm': {'usd': 1, 'btc': 2}}


class Bot(object):
    title = 'BOT1'

    def __init__(self):
        self.pairs = {}
        self.observer_btc_usd_instance = ObserverBTCUSD()
        self.ws = None
        self.order_book_ids = {}
        self.trades_ids = {}

        for pair in configs['btc_pairs']:
            self.pairs[pair[:-3]] = {'btc_ask': [], 'usd_bid': []}

    def run(self):
        print('RUN', self.title)

        self.ws = websocket.WebSocketApp(
            url=configs['exchange']['Bitfinex']['url'],
            on_message=self.on_message,
            on_open=self.on_open,
            on_close=self.on_close,

        )
        self.ws.run_forever()

    def on_close(self, ws):
        print('WS closed')
        self.run()

    def on_open(self, ws):
        self.subscribe(channel='book', symbol='BTCUSD')
        for pair in configs['btc_pairs']:
            self.subscribe(channel='book', symbol=pair)

        for pair in configs['usd_pairs']:
            self.subscribe(channel='book', symbol=pair)

    def on_message(self, ws, message):
        message = json.loads(message)
        if isinstance(message, dict):
            if message['event'] == 'subscribed':
                if message['channel'] == 'book':
                    self.order_book_ids[message['chanId']] = message['pair']
                if message['channel'] == 'trades':
                    self.trades_ids[message['chanId']] = message['pair']

        if isinstance(message, list):
            channel_id = message[0]
            data = message[1]

            """ Трейды """
            if channel_id in self.trades_ids.keys():
                if message[1] == 'te':
                    price = message[2][3]
                    amount = message[2][2]

            if len(data) == 3:
                """ data - order """
                price = data[0]
                amount = data[2]

                ask = None
                bid = None
                if amount > 0:
                    bid = float(price)
                else:
                    ask = float(price)

                if self.order_book_ids[channel_id] == 'BTCUSD':
                    if ask:
                        self.observer_btc_usd_instance.ask_orders.append(data)
                        if len(self.observer_btc_usd_instance.ask_orders) > 5:
                            del self.observer_btc_usd_instance.ask_orders[0]
                    if bid:
                        self.observer_btc_usd_instance.bid_orders.append(data)
                        if len(self.observer_btc_usd_instance.ask_orders) > 5:
                            del self.observer_btc_usd_instance.bid_orders

                pair = self.order_book_ids[channel_id]

                if pair == 'BTCUSD':
                    return

                if 'USD' in pair:
                    if bid:
                        self.pairs[pair[:-3]]['usd_bid'].append(data)
                        if len(self.pairs[pair[:-3]]['usd_bid']) > 5:
                            del self.pairs[pair[:-3]]['usd_bid'][0]

                elif 'BTC' in pair:
                    if ask:
                        self.pairs[pair[:-3]]['btc_ask'].append(data)
                        if len(self.pairs[pair[:-3]]['btc_ask']) > 5:
                            del self.pairs[pair[:-3]]['btc_ask'][0]

                strategy = TestStrategy(
                    data=self.pairs, buy_amount=configs['buy_amount'], btc_usd=self.observer_btc_usd_instance
                )
                strategy.analyze()

    def subscribe(self, channel, **kwargs):
        event = 'subscribe'
        kwargs['event'] = event
        kwargs['channel'] = channel
        self.ws.send(json.dumps(kwargs))


if __name__ == '__main__':
    account = Account()
    account.set_balance(1)
    print(f'Start balance: {Account.start_balance} BTC')
    bot = Bot()
    bot.run()

from . import AbstractStrategy
from . import ObserverBTCUSD
from account import Account


class TestStrategy(AbstractStrategy):

    def __init__(self, data, buy_amount, btc_usd):
        self.buy_amount = buy_amount
        self.btc_usd: ObserverBTCUSD = btc_usd
        super(TestStrategy, self).__init__(data)

    def analyze(self):
        min_price_btc_usd_ask, max_price_btc_usd_bid = None, None
        amount_coin_bid, amount_btcusd_ask = None, None
        amount_btc_ask = None

        if self.btc_usd.ask_orders:
            min_price_btc_usd_ask = max(btcusd[0] for btcusd in self.btc_usd.ask_orders)
            order_ask_btcusd = [order for order in self.btc_usd.ask_orders if min_price_btc_usd_ask in order][0]
            amount_btcusd_ask = abs(order_ask_btcusd[2])

        if self.btc_usd.bid_orders:
            max_price_btc_usd_bid = max(btcusd[0] for btcusd in self.btc_usd.bid_orders)
            order_bid_btcusd = [order for order in self.btc_usd.bid_orders if max_price_btc_usd_bid in order][0]
            amount_btcusd_bid = abs(order_bid_btcusd[2])

        for pair in self.data:
            min_price_coin_btc_ask, max_price_coin_usd_bid = None, None
            ask = self.data[pair]['btc_ask']
            bid = self.data[pair]['usd_bid']

            if ask:
                min_price_coin_btc_ask = max([price[0] for price in ask])
                order_ask = [order for order in ask if min_price_coin_btc_ask in order][0]
                order = [abs(order[2]) for order in ask]
                amount_order = sum(order)
                # print(ask)
                # print(f'{amount_order}- {pair}/BTC')
                amount_btc_ask = abs(order_ask[2])

            if bid:
                max_price_coin_usd_bid = max([price[0] for price in bid])
                order_bid = [order for order in bid if max_price_coin_usd_bid in order][0]
                amount_coin_bid = abs(order_bid[2])

            if min_price_coin_btc_ask and max_price_coin_usd_bid and min_price_btc_usd_ask:
                amount_coins = amount_btc_ask / min_price_coin_btc_ask

                if amount_btc_ask:
                    if min_price_coin_btc_ask and max_price_coin_usd_bid and min_price_btc_usd_ask:
                        amount_btc = round((amount_btc_ask / min_price_coin_btc_ask)
                                           * max_price_coin_usd_bid / min_price_btc_usd_ask, 3)
                        if amount_btc > amount_btc_ask:
                            x = amount_btc_ask * max_price_btc_usd_bid
                            y = amount_btc * max_price_btc_usd_bid
                            profit_usd = (y - x) - ((y - x) * 0.0045)
                            profit_btc = (amount_btc - amount_btc_ask) - ((amount_btc - amount_btc_ask) * 0.0045)

                            checked_array = [min_price_coin_btc_ask, max_price_coin_usd_bid, amount_btc_ask]
                            if checked_array not in Account.trades_array:
                                Account.trades_array.append(checked_array)

                                Account.plus_profit_usd(profit_usd)
                                Account.plus_profit_btc(profit_btc)

                                Account.add_trade()
                                print(f'{profit_usd} {pair} - profit USD {amount_btc_ask} - amount_ask BTC')
                                print(f'Total profit: {Account.profit_usd} USD, '
                                      f'{Account.profit_btc} BTC, '
                                      f'trades: {Account.trades}')

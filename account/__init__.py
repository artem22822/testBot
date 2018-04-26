class Singleton(type):
    _instance = dict()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instance:
            cls._instance[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance[cls]


class Account(metaclass=Singleton):
    start_balance = 0
    trades = 0
    trades_array = []
    profit_usd = 0
    profit_btc = 0

    @classmethod
    def set_balance(cls, amount):
        if amount:
            cls.start_balance = amount

    @classmethod
    def add_trade(cls):
        cls.trades += 1

    @classmethod
    def plus_profit_usd(cls, amount):
        cls.profit_usd += amount

    @classmethod
    def plus_profit_btc(cls, amount):
        cls.profit_btc += amount

class AbstractStrategy(object):
    def __init__(self, data):
        self.data = data

    def analyze(self):
        raise NotImplemented()


class ObserverBTCUSD(object):
    """
    Это класс для цены биткоина к долару
    """
    def __init__(self):
        self.ask_orders = []
        self.bid_orders = []

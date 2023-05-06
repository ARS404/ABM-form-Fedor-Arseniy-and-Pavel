class MarketHistory():
    def __init__(self):
        self._orders = list() #iter -> IterInfo

    def get_prices(self):
        return list(map(lambda x: x.price, self._orders))


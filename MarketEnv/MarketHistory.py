class MarketHistory():

    class _IterInfo():
        def __init__(self):
            self.data = list() # from, to, count
            self.price = 0.0

    def __init__(self):
        self._orders = list() #iter -> IterInfo
        raise NotImplementedError

    def get_prices(self):
        return list(map(lambda x: x.price, self._orders))

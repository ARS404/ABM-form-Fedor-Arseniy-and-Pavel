class MarketHistory():
    """
    This class contains classes:
        - Deal - primitive structure for storing deal information
        - IterInfo - price and list of deals made at this price during an iteration
    This class contains params:
        - _order :list of IterInfo: info about all previous iterations
    This class contains methods:
        - get_prices(self) :list of float: return list of prices set at previous iterations
    """
    class Deal():
        def __init__(self):
            self.buyer = None
            self.seller = None
            self.amount = None

    def __init__(self):
        self._orders = list() #iter -> IterInfo

    class _IterInfo():
        def __init__(self):
            self.data = list() # from, to, count
            self.price = 0.0

    def get_prices(self):
        return list(map(lambda x: x.price, self._orders))

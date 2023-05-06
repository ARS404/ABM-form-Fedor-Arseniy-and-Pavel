from copy import deepcopy


class MarketHistory(object):
    """
    This class contains classes:
        - Deal - primitive structure for storing deal information
        - IterInfo - price and list of deals made at this price during an iteration
    This class contains params:
        - _order :list of IterInfo: info about all previous iterations
    This class contains methods:
        - get_prices(self) :list of float: return list of prices set at previous iterations
    """
    class Deal(object):
        def __init__(self, buyer=None, seller=None, quantity=None):
            self.buyer = buyer
            self.seller = seller
            self.quantity = quantity

    def __init__(self):
        self.deals = list()
        self.offer_prices = list()
        self.bid_prices = list()
        self.deals_prices = list()

    def start_new_iter(self):
        self.deals.append(list())

    def add_deal(self, buyer, seller, quantity):
        self.deals[-1].append(MarketHistory.Deal(buyer, seller, quantity))

    def add_deal_price(self, price):
        self.deals_prices.append(price)

    def add_offer_price(self, price):
        self.offer_prices.append(price)

    def add_bid_price(self, price):
        self.bid_prices.append(price)

    def get_prices(self):
        return deepcopy(self.deals_prices)

    def get_bid_prices(self):
        return self.bid_prices

    def get_offer_prices(self):
        return self.offer_prices

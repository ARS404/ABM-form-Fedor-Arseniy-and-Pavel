from copy import copy

import numpy as np

from utils.Constants import OperationTypes
from utils.AgentMapping import AgentTypes


class OrderBookException(Exception):
    def __init__(self, message="You have to send some error message"):
        self.message = message
        super().__init__(self.message)


class OrderBook(object):
    """
    This class contains classes:
        - Order - primitive structure for order storing
    This class contains params:
        - data :list of Order: current order book
    This class contains methods:
        - clean(self) :void: cleaning the data
        - add_order(self, price, quantity, trader_id) :void: add order to the order book
        - buyers_at_price(self, price) :list of Order: return list of orders, which would try to buy at given price
        - sellers_at_price(self, price) :list of Order: return list of orders, which would try to sell at given price
        - get_price(self) :float: return the price set according to the order book
    """
    class Order:
        def __init__(self, price, quantity, operation_type, trader, time):
            if operation_type not in OperationTypes:
                raise OrderBookException("`quantity` value should be from `OperationTypes`")
            self.price = price
            self.quantity = quantity
            self.operation_type = operation_type
            self.trader = trader
            self.time = time

        def __str__(self):
            return f"trader with id {self.trader.id} and type {type(self.trader)} send offer of type " \
                   f"{self.operation_type} with price {self.price} and quantity {self.quantity}"

    def __init__(self):
        self.sell_data = dict()
        self.buy_data = dict()

    @staticmethod
    def _clean_book(book):
        for agent in book.keys():
            # TODO: fix this shit (looks like we have to add live time to each order and rewrite a lot of stuff)
            if type(agent) == AgentTypes.MM_TR:
                for ind, offer in enumerate(book[agent]):
                    if offer is None:
                        continue
                    if offer.price in [0.0, float('inf')]:
                        offer.trader.close_deal(offer.quantity, offer.operation_type)
                        book[agent][ind] = None
            book[agent] = [None] + book[agent]
            if book[agent][-1] is not None:
                book[agent][-1].trader.close_deal(book[agent][-1].quantity, book[agent][-1].operation_type)
            book[agent].pop()

    def clean(self):
        self._clean_book(self.buy_data)
        self._clean_book(self.sell_data)

    def add_order(self, price, quantity, operation_type, trader, time, report=False):
        if operation_type is OperationTypes.BUY:
            self.buy_data[trader][0] = (OrderBook.Order(price, quantity, operation_type, trader, time))
            if report:
                print(self.buy_data[trader][0])
        else:
            self.sell_data[trader][0] = (OrderBook.Order(price, quantity, operation_type, trader, time))
            if report:
                print(self.sell_data[trader][0])

    def buyers_at_price(self, price):
        ret = list()
        for x in self.buy_data.values():
            ret += list(map(lambda y: copy(y), list(y for y in x if y is not None and y.price >= price)))
        return ret

    def sellers_at_price(self, price):
        ret = list()
        for x in self.sell_data.values():
            ret += list(map(lambda y: copy(y), list(y for y in x if y is not None and y.price <= price)))
        return ret

    def get_price(self, prev_price):
        buys = list()
        sells = list()
        for x in self.buy_data.values():
            buys += list(filter(lambda y: y is not None, x))
        for x in self.sell_data.values():
            sells += list(filter(lambda y: y is not None, x))
        buys.sort(key=lambda x: x.price, reverse=True)
        sells.sort(key=lambda x: x.price)
        prices = list()
        for x in self.buy_data.values():
            prices += [y.price for y in x if y is not None and y.price != float('inf')]
        for x in self.sell_data.values():
            prices += [y.price for y in x if y is not None and y.price != 0]
        prices = np.unique(prices)
        prices = list(prices)
        prices.sort()
        total_buys_for_price = [0.0 for i in range(len(prices))]
        total_sells_for_price = [0.0 for i in range(len(prices))]
        cur_buyer = 0
        cur_seller = 0
        for i in range(len(prices)):
            if i > 0:
                total_sells_for_price[i] += total_sells_for_price[i - 1]
            while cur_seller < len(sells) and sells[cur_seller].price <= prices[i]:
                total_sells_for_price[i] += sells[cur_seller].quantity
                cur_seller += 1
        prices.reverse()

        for i in range(len(prices)):
            if i > 0:
                total_buys_for_price[i] += total_buys_for_price[i - 1]
            while cur_buyer < len(buys) and buys[cur_buyer].price >= prices[i]:
                total_buys_for_price[i] += buys[cur_buyer].quantity
                cur_buyer += 1
        total_buys_for_price.reverse()
        best_price = None
        best_quantity = None
        prices.reverse()
        left_ind, right_ind = None, None
        for i in range(len(prices)):
            current_quantity = min(total_buys_for_price[i], abs(total_sells_for_price[i]))
            if best_quantity is None:
                best_quantity = current_quantity
                left_ind = 0
                right_ind = 0
            else:
                if current_quantity == best_quantity:
                    right_ind = i
                if current_quantity > best_quantity:
                    best_quantity = current_quantity
                    left_ind = i
                    right_ind = i
        if best_quantity == 0:
            return prev_price, prev_price, prev_price
        best_price = prices[(left_ind + right_ind)//2]
        offer_price = 0
        bid_price = prices[-1] + 1
        for i in range(len(buys)):
            bid_price = buys[i].price
            if buys[i].price < best_price:
                break
        for i in range(len(sells)):
            offer_price = sells[i].price
            if sells[i].price > best_price:
                break
        bid_price = min(bid_price, best_price)
        offer_price = max(offer_price, best_price)
        return best_price, offer_price, bid_price

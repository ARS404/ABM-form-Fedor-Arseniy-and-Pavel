from constants import OperationTypes


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
        def __init__(self, price, quantity, operation_type, trader):
            if operation_type not in OperationTypes:
                raise OrderBookException("`quantity` value should be from `OperationTypes`")
            self.price = price
            self.quantity = quantity
            self.operation_type = operation_type
            self.trader = trader

    def __init__(self):
        self.data = list()

    def clean(self):
        self.data = list()

    def add_order(self, price, quantity, operation_type, trader):
        self.data.append(OrderBook.Order(price, quantity, operation_type, trader))

    def buyers_at_price(self, price):
        return list(filter(lambda x: (x.operation_type == OperationTypes.BUY) and (x.price <= price), self.data))

    def sellers_at_price(self, price):
        return list(filter(lambda x: (x.operation_type == OperationTypes.SELL) and (x.price >= price), self.data))

    def get_price(self):
        buys = list(filter(lambda x: x.operation_type == OperationTypes.BUY, self.data))
        sells = list(filter(lambda x: x.operation_type == OperationTypes.SELL, self.data))
        buys.sort(key=lambda x: x.price)
        sells.sort(key=lambda x: x.price, reverse=True)
        prices = set(map(lambda x: x.price, self.data))
        prices = list(prices)
        prices.sort()
        total_buys_for_price = [0.0 for i in range(len(prices))]
        total_sells_for_price = [0.0 for i in range(len(prices))]
        cur_buyer = 0
        cur_seller = 0
        for i in range(len(prices)):
            if i > 0:
                total_buys_for_price[i] += total_buys_for_price[i - 1]
            while cur_buyer < len(buys) and buys[cur_buyer].price <= prices[i]:
                total_buys_for_price[i] += buys[cur_buyer].quantity
                cur_buyer += 1
        prices.reverse()
        for i in range(len(prices)):
            if i > 0:
                total_sells_for_price[i] += total_sells_for_price[i - 1]
            while cur_seller < len(sells) and sells[cur_seller].price >= prices[i]:
                total_sells_for_price[i] += sells[cur_seller].quantity
                cur_seller += 1
        total_sells_for_price.reverse()
        best_price = None
        best_quantity = None
        prices.reverse()
        for i in range(len(prices)):
            current_quantity = min(total_buys_for_price[i], abs(total_sells_for_price[i]))
            if best_quantity is None:
                best_quantity = current_quantity
                best_price = prices[i]
            else:
                if current_quantity > best_quantity:
                    best_quantity = current_quantity
                    best_price = prices[i]
        offer_price = 0
        bid_price = prices[-1] + 1
        for i in range(len(buys)):
            if buys[i].price >= best_price:
                break
            bid_price = buys[i].price
        for i in range(len(sells)):
            if sells[i].price <= best_price:
                break
            offer_price = sells[i].price
        return best_price, offer_price, bid_price

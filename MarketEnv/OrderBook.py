class OrderBook():

    class Order:
        def __init__(self, price, quantity, trader_id):
            self.price = price
            self.quantity = quantity
            self.trader_id = trader_id

    def __init__(self):
        raise NotImplementedError
    def clean(self):
        self.data = list()

    def get_price(self):
        buys = list(filter(lambda x: x.quantity > 0, self.data))
        sells = list(filter(lambda x: x.quantity < 0, self.data))
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
        for i in range(len(prices)):
            current_quantity = min(total_buys_for_price[i], abs(total_sells_for_price[i]))
            if best_quantity is None:
                best_quantity = current_quantity
            else:
                if current_quantity > best_quantity:
                    best_quantity = current_quantity
                    best_price = prices[i]

        return best_price

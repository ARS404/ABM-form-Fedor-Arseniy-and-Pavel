from .OrderBook import OrderBook
from .MarketHistory import MarketHistory



class MarketEnv(object):
    """
    This class contains params:
        - cur_order_book :OrderBook: current order book (empty at the start of iteration)
        - market_history :MarketHistory:
    This class contains methods:
        - clean_order_book(self) :void: prepare cur_order_book to new iteration
        - add_order(self, price, quantity, trader_id) :void: add order to the order book
        - get_history(self) :MarketHistory: return market history
        - get_price(self) :float: return the price set according to the order book
    """
    def __init__(self):
        self.order_book = OrderBook()
        self.market_history = MarketHistory()

    def add_order(self, price, quantity, trader_id):
        self.order_book.add_order(price, quantity, trader_id)

    def get_history(self):
        return self.market_history

    def clean_order_book(self):
        self.order_book.clean()

    def get_price(self):
        return self.order_book.get_price()














def main():
    m_env = MarketEnv()
    for i in range(4, 6):
        m_env.add_order((i**4 + 234) / (i**3 + 54), 2 * i, i)
    for i in range(3, 5):
        m_env.add_order((i**5 + 235) / (i**4 + 5), -3 * i, i)
    m_env.get_price()


if __name__ == '__main__':
    main()
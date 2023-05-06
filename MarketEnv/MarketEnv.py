from .OrderBook import OrderBook
from .MarketHistory import MarketHistory


class MarketEnv(object):
    """
    This class contains params:
        - cur_order_book :OrderBook: current order book (empty at the start of iteration)
        - market_history :MarketHistory:
    This class contains methods:
        - clean_order_book(self) :viod: prepare cur_order_book to new iteration
    """
    def __init__(self):
        self.order_book = OrderBook()
        self.market_history = MarketHistory()

    def clean_order_book(self):
        self.order_book.clean()

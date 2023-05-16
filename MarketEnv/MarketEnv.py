from .OrderBook import OrderBook
from .MarketHistory import MarketHistory

from utils.AgentMapping import AgentTypes


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

    def add_order(self, price, quantity, operation_type, trader, time, report=False):
        self.order_book.add_order(price, quantity, operation_type, trader, time, report=report)

    def get_history(self):
        return self.market_history

    def clean_order_book(self):
        self.order_book.clean()

    def get_price(self):
        return self.order_book.get_price()

    def clear_order_from_trader(self, agent):
        if type(agent) == AgentTypes.MM_TR:
            self.order_book.sell_data[agent] = [None] * agent.model.p.MM_order_live_time
            self.order_book.buy_data[agent] = [None] * agent.model.p.MM_order_live_time
        else:
            self.order_book.sell_data[agent] = [None]
            self.order_book.buy_data[agent] = [None]

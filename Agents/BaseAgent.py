import agentpy as ap
from utils.Constants import OperationTypes


class BaseAgent(ap.Agent):
    """
    Methods:
        - make_decision(self, market_env) -> void : agent make its decision based on market_env.market_history
            and its state, then write chosen option to market_env.order_book
    """

    def __hash__(self):
        return self.id

    def setup(self):
        raise NotImplementedError

    def make_decision(self):
        raise NotImplementedError

    def change_balance(self, d_money, d_invent):
        self._money += d_money
        self._inventory += d_invent

    def make_deal(self, price, quantity, op_type):
        if op_type is OperationTypes.SELL:
            self._money += price * quantity
            self._inventory -= quantity
        if op_type is OperationTypes.BUY:
            self._money -= price * quantity
            self._inventory += quantity

    def close_deal(self, quantity, op_type):
        pass

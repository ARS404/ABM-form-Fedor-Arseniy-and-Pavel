import BaseAgent
from constants import OperationTypes
from scipy.stats import norm


class HamsterAgent(BaseAgent):
    """
    This class contains params:
        - risk_level : float : can vary from 0 to 1; the bigger risk_level is, the bigger orders agent make
    This class contains methods:
        - make_decision(self, market_env) : void : agent make its decision based on market_env.market_history
        and its state, then write chosen option to market_env.order_book
    """

    def __init__(self, agent_id, money, inventory, risk_level=1):
        self.id = agent_id
        self._money = money
        self._inventory = inventory
        self._risk_level = risk_level

    def make_decision(self, market_env):
        price_history = market_env.get_history().get_prices()
        if len(price_history) < 2:
            return
        order_price = 2 * price_history[-1] - price_history[-2]
        if price_history[-1] >= price_history[-2]:
            order_type = OperationTypes.SELL
            order_size = min(max(norm.rvs(loc=self._inventory * self._risk_level, size=1), 0), self._inventory)
            market_env.add_order(order_price, order_size, order_type, self)
        else:
            order_type = OperationTypes.BUY
            order_size = min(max(norm.rvs(loc=self._money * self._risk_level, size=1), 0), self._money) / order_price
            market_env.add_order(order_price, order_size, order_type, self)
        return

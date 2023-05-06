import BaseAgent
from scipy.stats import uniform
from scipy.stats import bernoulli

from constants import OperationTypes


class ZeroIntelligenceAgent(BaseAgent):
    """
    This class contains params:
        - risk_level : float : can vary from 0 to 1; the bigger risk_level is, the bigger orders agent make
        - min_money, min_inventory : float : the minimum amount of resource to be able to make respective order
    This class contains methods:
        - make_decision(self, market_env) : void : agent make its decision based on market_env.market_history
        and its state, then write chosen option to market_env.order_book
    """

    def __init__(self, agent_id, money, inventory, risk_level=1, min_money=0, min_inventory=0):
        self.id = agent_id
        self._money = money
        self._inventory = inventory
        self._risk_level = risk_level
        self._min_money = min_money
        self._min_inventory = min_inventory

    def make_decision(self, market_env):
        price_history = market_env.get_history().get_prices()
        if self._inventory < self._min_inventory and self._money < self._min_money or len(price_history) == 0:
            return
        order_price = price_history[-1]
        if self._inventory < self._min_inventory:
            order_type = OperationTypes.BUY
            order_size = (self._money ** uniform.rvs(scale=self._risk_level, size=1)) / order_price
            market_env.add_order(order_price, order_size, order_type, self)
            return
        if self._money < self._min_money:
            order_type = OperationTypes.SELL
            order_size = self._inventory ** uniform.rvs(scale=self._risk_level, size=1)
            market_env.add_order(order_price, order_size, order_type, self)
            return
        if bernoulli.rvs(p=0.5) == 1:
            order_type = OperationTypes.BUY
            order_size = (self._money ** uniform.rvs(scale=self._risk_level, size=1)) / order_price
        else:
            order_type = OperationTypes.SELL
            order_size = self._inventory ** uniform.rvs(scale=self._risk_level, size=1)
        market_env.add_order(order_price, order_size, order_type, self)
        return

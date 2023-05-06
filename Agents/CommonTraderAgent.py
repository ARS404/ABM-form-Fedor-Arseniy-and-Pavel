import BaseAgent
from scipy.stats import lognorm
from scipy.stats import bernoulli
from constants import OperationTypes


class CommonTraderAgent(BaseAgent):
    """
    This class contains params:
        - risk_level : float:  can vary from 0 to 1; the bigger risk_level is, the bigger orders agent make
        - sell_probability : float : varies from 0 to 1, agent will make sell order with his sell_probability and a buy
        order with probability of 1 - sell_probability
        - price_variance : float : price forming parameter, the bigger variance, the bigger deviation from the previous
         price
    This class contains methods:
        - make_decision(self, market_env) : void : agent make its decision based on market_env.market_history
        and its state, then write chosen option to market_env.order_book
    """

    def __init__(self, agent_id, money, inventory, risk_level=1, sell_probability=0.5, price_variance=1):
        self.id = agent_id
        self._money = money
        self._inventory = inventory
        self._risk_level = risk_level
        self._sell_probability = sell_probability
        self._price_variance = price_variance

    def make_decision(self, market_env):
        price_history = market_env.get_history().get_prices()
        if len(price_history) == 0:
            return
        order_price = price_history[-1] * lognorm.rvs(s=self._price_variance, size=1)
        if bernoulli.rvs(p=self._sell_probability) == 1:
            order_type = OperationTypes.SELL
            order_size = self._risk_level * self._inventory
        else:
            order_type = OperationTypes.BUY
            order_size = self._risk_level * self._money / order_price
        market_env.add_order(order_price, order_size, order_type, self)
        return

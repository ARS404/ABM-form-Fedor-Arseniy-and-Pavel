from Agents.BaseAgent import BaseAgent
from scipy.stats import lognorm
from scipy.stats import uniform
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

    def setup(self):
        self._money = self.p.Setup['CommonTraderAgent']['start_money']
        self._inventory = self.p.Setup['CommonTraderAgent']['start_inventory']
        self._risk_level = self.p.Setup['CommonTraderAgent']['risk_level']
        self._sell_probability = self.p.Setup['CommonTraderAgent']['sell_probability']
        self._price_variance = self.p.Setup['CommonTraderAgent']['price_variance']

    def make_decision(self):
        market_env = self.model.market_env
        price_history = market_env.get_history().get_prices()
        # order_price = price_history[-1] + uniform.rvs(loc=-0.05, scale=0.1)
        # order_price = lognorm.rvs(s=self._price_variance, scale=1.0) * price_history[-1]
        if (bernoulli.rvs(p=self._sell_probability) == 1 or self._money < 0) and self._inventory > 0:
            order_price = lognorm.rvs(s=self._price_variance, scale=1.1) * price_history[-1]
            order_type = OperationTypes.SELL
            order_size = uniform.rvs(scale=self._risk_level) * self._inventory
        else:
            order_price = lognorm.rvs(s=self._price_variance, scale=0.9) * price_history[-1]
            order_type = OperationTypes.BUY
            order_size = uniform.rvs(scale=self._risk_level) * self._money / order_price
        market_env.add_order(order_price, order_size, order_type, self, report=self.p.report)
        return

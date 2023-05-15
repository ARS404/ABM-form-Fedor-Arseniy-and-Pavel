from Agents.BaseAgent import BaseAgent
from numpy.random import lognormal
from scipy.stats import uniform
from scipy.stats import lognorm
from scipy.stats import bernoulli
from utils.Constants import OperationTypes


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
        self._money = self.p['CommonTraderAgent_start_money']
        self._inventory = self.p['CommonTraderAgent_start_inventory']
        self._risk_level = self.p['CommonTraderAgent_risk_level']
        self._sell_probability = self.p['CommonTraderAgent_sell_probability']
        self._price_variance = self.p['CommonTraderAgent_price_variance']

    def make_decision(self):
        market_env = self.model.market_env
        price_history = market_env.get_history().get_prices()
        # spread = (market_env.get_history().get_offer_prices()[-1] - market_env.get_history().get_bid_prices()[-1]) / price_history[-1]
        # order_price = price_history[-1] + uniform.rvs(loc=-0.05, scale=0.1)
        order_price = lognormal(-0.5, self._price_variance) * price_history[-1]
        if (bernoulli.rvs(p=self._sell_probability) == 1 or self._money < 0) and self._inventory > 0:
            # order_price = lognormal(-spread / 2, self._price_variance) * price_history[-1]
            if order_price == 0:
                return
            order_type = OperationTypes.SELL
            order_size = uniform.rvs(scale=self._risk_level) * self._inventory
        else:
            # order_price = lognormal(spread / 2, self._price_variance) * price_history[-1]
            if order_price == 0:
                return
            order_type = OperationTypes.BUY
            order_size = uniform.rvs(scale=self._risk_level) * self._money / order_price
        market_env.add_order(order_price, order_size, order_type, self, self.model.t, report=self.p.report)
        return

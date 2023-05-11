from Agents.BaseAgent import BaseAgent
from constants import OperationTypes
from scipy.stats import norm
from scipy.stats import uniform
from sklearn.linear_model import LinearRegression
import numpy as np


class HamsterAgent(BaseAgent):
    """
    This class contains params:
        - risk_level : float : can vary from 0 to 1; the bigger risk_level is, the bigger orders agent make
    This class contains methods:
        - make_decision(self, market_env) : void : agent make its decision based on market_env.market_history
        and its state, then write chosen option to market_env.order_book
    """

    def setup(self):
        self._money = self.p.Setup['HamsterAgent']['start_money']
        self._inventory = self.p.Setup['HamsterAgent']["start_inventory"]
        self._risk_level = self.p.Setup['HamsterAgent']['risk_level']
        self._interpolate_degree = self.p.Setup['HamsterAgent']['interpolate_degree']
        self._history_depth = self.p.Setup['HamsterAgent']['history_depth']

    def make_decision(self):
        market_env = self.model.market_env
        price_history = market_env.get_history().get_prices(limit=self._history_depth)
        if len(price_history) < self._history_depth:
            return
        x = np.vander(range(self._history_depth), self._interpolate_degree)
        reg = LinearRegression().fit(x, price_history)
        order_price = reg.predict(np.vander([self._history_depth], self._interpolate_degree))[0]
        if order_price <= 0:
            return
        if order_price >= price_history[-1]:
            order_type = OperationTypes.SELL
            order_size = min(max(norm.rvs(loc=self._inventory * self._risk_level), 0), self._inventory)
            market_env.add_order(order_price, order_size, order_type, self, report=self.p.report)
        else:
            order_type = OperationTypes.BUY
            order_size = min(max(norm.rvs(loc=self._money * self._risk_level), 0), self._money) / order_price
            market_env.add_order(order_price, order_size, order_type, self, report=self.p.report)
        return

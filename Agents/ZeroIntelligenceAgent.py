from Agents.BaseAgent import BaseAgent

from utils.Constants import OperationTypes


class ZeroIntelligenceAgent(BaseAgent):
    """
    This class contains params:
        - risk_level : float : can vary from 0 to 1; the bigger risk_level is, the bigger orders agent make
        - min_money, min_inventory : float : the minimum amount of resource to be able to make respective order
    This class contains methods:
        - make_decision(self, market_env) : void : agent make its decision based on market_env.market_history
        and its state, then write chosen option to market_env.order_book
    """

    def setup(self):
        self._money = self.p['ZeroIntelligenceAgent_start_money']
        self._inventory = self.p['ZeroIntelligenceAgent_start_inventory']
        self._risk_level = self.p['ZeroIntelligenceAgent_risk_level']
        self._min_money = self.p['ZeroIntelligenceAgent_min_money']
        self._min_inventory = self.p['ZeroIntelligenceAgent_min_inventory']
        self._noise = self.p['ZeroIntelligenceAgent_noise']

    def make_decision(self):
        market_env = self.model.market_env
        price_history = market_env.get_history().get_prices()
        if self._inventory < self._min_inventory and self._money < self._min_money or len(price_history) == 0:
            return
        order_price = price_history[-1] * self.model.nprandom.uniform(low=(1 - self._noise), high=(1 + self._noise))
        if order_price == 0:
            return
        if self._inventory < self._min_inventory:
            order_type = OperationTypes.BUY
            order_size = (self._money ** self.model.nprandom.uniform(high=self._risk_level)) / order_price
            market_env.add_order(order_price, order_size, order_type, self, self.model.t, report=self.p.report)
            return
        if self._money < self._min_money:
            order_type = OperationTypes.SELL
            order_size = self._inventory ** self.model.nprandom.uniform(high=self._risk_level)
            market_env.add_order(order_price, order_size, order_type, self, self.model.t, report=self.p.report)
            return
        if self.model.nprandom.binomial(n=1, p=0.5) == 1:
            order_type = OperationTypes.BUY
            order_size = (self._money ** self.model.nprandom.uniform(high=self._risk_level)) / order_price
        else:
            order_type = OperationTypes.SELL
            order_size = self._inventory ** self.model.nprandom.uniform(high=self._risk_level)
        market_env.add_order(order_price, order_size, order_type, self, self.model.t, report=self.p.report)
        return

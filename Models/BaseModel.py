import agentpy as ap

from Agents.BaseAgent import BaseAgent
from MarketEnv.MarketEnv import MarketEnv

from constants import OperationTypes

class BaseModel(ap.Model):
    """
    Methods:
        - step(self) -> void : one step of iteration
        - setup(self) -> void : some shit from ap.Model superclass ...
    """

    def setup(self):
        self.market_env = MarketEnv()
        self.agents = dict()
        for tp, cnt in self.p.agents:
            self.agents[tp] = ap.AgentList(self, cnt, tp)

    def step(self):
        for agent_sublist in self.agents.values():
            agent_sublist.make_dessision()

    def update(self):
        price = self.market_env.get_price()

        sell_offers = list(offer for offer in self.market_env.order_book.data
                           if offer.operration_type == OperationTypes.SELL)
        buy_offers = list(offer for offer in self.market_env.order_book.data
                          if offer.operration_type == OperationTypes.BUY)

    def end(self):
        pass



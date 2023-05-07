from Agents.BaseAgent import BaseAgent
from constants import OperationTypes
from scipy.stats import uniform


def f(x):
    return x


class MarketMakerAgent(BaseAgent):
    """
    This class contains params:
        - risk_level : float : defines the stable interval from -risk_level to risk_level
    This class contains methods:
        - make_decision(self, market_env) : void : agent make its decision based on market_env.market_history
        and its state, then write chosen option to market_env.order_book
    """

    def setup(self):
        self._money = 0
        self._inventory = self.p.Setup['MarketMakerAgent']['start_inventory']
        self._risk_level = self.p.Setup['MarketMakerAgent']['risk_level']

    def make_decision(self):
        market_env = self.model.market_env
        if -self._risk_level <= self._inventory <= self._risk_level:
            new_inventory = self._inventory + uniform.rvs(loc=-5, scale=10)
            if new_inventory > 0:
                bid_size = self._risk_level - self._inventory
                offer_size = -new_inventory + self._risk_level
            else:
                bid_size = self._risk_level + new_inventory
                offer_size = self._inventory + self._risk_level
            best_offer = market_env.get_history().get_offer_prices()[-1]
            best_bid = market_env.get_history().get_bid_prices()[-1]
            offset = (best_offer - best_bid) * f(self._inventory / self._risk_level)
            bid_price = best_bid - offset
            offer_price = best_offer - offset
            market_env.add_order(bid_price, bid_size, OperationTypes.BUY, self)
            market_env.add_order(offer_price, offer_size, OperationTypes.SELL, self)
        else:
            if self._inventory < 0:
                market_env.add_order(1e20, abs(self._inventory) - self._risk_level * 0.99, OperationTypes.BUY, self)
            else:
                market_env.add_order(0, abs(self._inventory) - self._risk_level * 0.99, OperationTypes.SELL, self)
        return

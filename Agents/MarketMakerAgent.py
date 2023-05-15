from Agents.BaseAgent import BaseAgent
from utils.Constants import OperationTypes
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
        self._bids = 0
        self._offers = 0
        self._money = 0
        self._inventory = self.p['MarketMakerAgent_start_inventory']
        self._risk_level = self.p['MarketMakerAgent_risk_level']

    def make_decision(self):
        market_env = self.model.market_env
        # price_history = market_env.get_history().get_prices()
        if -self._risk_level > self._inventory - self._offers:
            market_env.clear_order_from_trader(self)
            self._bids = 0
            self._offers = 0
            market_env.add_order(float('inf'), self._risk_level, OperationTypes.BUY, self, self.model.t,
                                 report=self.p.report)
            self._bids += self._risk_level
            return

        if self._inventory + self._bids > self._risk_level:
            market_env.clear_order_from_trader(self)
            self._bids = 0
            self._offers = 0
            market_env.add_order(0, self._risk_level, OperationTypes.SELL, self, self.model.t,
                                 report=self.p.report)
            self._offers += self._risk_level
            return
        new_inventory = -self._inventory
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
        # bid_size = min(bid_size, 2e8 / bid_price)
        # offer_size = min(offer_size, 2e8 / offer_price)

        if bid_price > 0:
            market_env.add_order(bid_price, bid_size, OperationTypes.BUY, self, self.model.t, report=self.p.report)
            self._bids += bid_size
        if offer_price > 0:
            market_env.add_order(offer_price, offer_size, OperationTypes.SELL, self, self.model.t, report=self.p.report)
            self._offers += offer_size

        return

    def make_deal(self, price, quantity, op_type):
        if op_type is OperationTypes.SELL:
            self._money += price * quantity
            self._inventory -= quantity
            self._offers -= quantity
        if op_type is OperationTypes.BUY:
            self._money -= price * quantity
            self._inventory += quantity
            self._bids -= quantity

    def close_deal(self, quantity, op_type):
        if op_type is OperationTypes.SELL:
            self._offers -= quantity
        if op_type is OperationTypes.BUY:
            self._bids -= quantity

    def get_inv(self):
        return self._inventory, self._inventory + self._bids, self._inventory - self._offers

from Agents.BaseAgent import BaseAgent
from constants import OperationTypes


class TargetWealthAgent(BaseAgent):
    """
    This class contains params:
        - target_level : float : the ratio of inventory value to capital that agent is trying to achieve
    This class contains methods:
        - make_decision(self, market_env) : void : agent make its decision based on market_env.market_history
        and its state, then write chosen option to market_env.order_book
    """

    def setup(self):
        self._money = self.p.Setup['TargetWealthAgent']['start_money']
        self._inventory = self.p.Setup['TargetWealthAgent']['start_inventory']
        self._target_level = self.p.Setup['TargetWealthAgent']['target_level']

    def make_decision(self):
        market_env = self.model.market_env
        price_history = market_env.get_history().deals_prices
        if len(price_history) == 0:
            return
        order_price = price_history[-1]
        inventory_value = self._inventory * price_history[-1]
        new_inventory_value = (inventory_value + self._money) * self._target_level / (self._target_level + 1)
        new_inventory = new_inventory_value / order_price
        if new_inventory == self._inventory:
            return
        if new_inventory > self._inventory:
            order_size = new_inventory - self._inventory
            order_type = OperationTypes.BUY
        else:
            order_size = self._inventory - new_inventory
            order_type = OperationTypes.SELL
        market_env.add_order(order_price, order_size, order_type, self)

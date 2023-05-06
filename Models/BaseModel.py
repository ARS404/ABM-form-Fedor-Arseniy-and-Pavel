import agentpy as ap

from MarketEnv.MarketEnv import MarketEnv


class BaseModel(ap.Model):
    """
    Methods:
        - step(self) -> void : one step of iteration
        - setup(self) -> void : some shit from ap.Model superclass ...
    """

    def setup(self):
        self.market_env = MarketEnv()
        self.agents = dict()
        for tp, cnt in self.p.Agents.items():
            if cnt == 0:
                continue
            self.agents[tp] = ap.AgentList(self, cnt, tp)

    def step(self):
        for agent_sublist in self.agents.values():
            agent_sublist.make_decision()

    def update(self):
        if self.t == 0:
            return
        price, offer_price, bid_price = self.market_env.get_price()
        _, price, _ = self.market_env.get_price()
        self.market_env.market_history.start_new_iter()
        self.market_env.market_history.add_deal_price(price)
        self.market_env.market_history.add_offer_price(offer_price)
        self.market_env.market_history.add_bid_price(bid_price)

        sell_offers = self.market_env.order_book.sellers_at_price(price)
        buy_offers = self.market_env.order_book.buyers_at_price(price)

        sell_ind = 0
        buy_ind = 0
        while sell_ind != len(sell_offers) and buy_ind != len(buy_offers):
            sell_of = sell_offers[sell_ind]
            buy_of = buy_offers[buy_ind]

            if sell_of.quantity >= buy_of.quantity:
                sell_of.quantity -= buy_of.quantity
                total_quantity = buy_of.quantity
                buy_ind += 1
            else:
                buy_of.quantity -= sell_of.quantity
                total_quantity = sell_of.quantity
                sell_ind += 1
            sell_of.trader.change_balance(-1 * total_quantity, total_quantity * price)
            buy_of.trader.change_balance(total_quantity, -1 * total_quantity * price)
            self.market_env.market_history.add_deal(sell_of.trader, buy_of.trader, total_quantity)
        self.market_env.order_book.clean()

    def end(self):
        pass



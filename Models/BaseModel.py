import datetime

import agentpy as ap
import numpy as np

from matplotlib import pyplot as plt

from MarketEnv.MarketEnv import MarketEnv


class BaseModel(ap.Model):
    """
    Methods:
        - step(self) -> void : one step of iteration
        - setup(self) -> void : some shit from ap.Model superclass ...
    """

    def setup(self):
        self.start_time = datetime.datetime.now()
        self.market_env = MarketEnv()
        self.market_env.market_history.add_deal_price(self.p.start_price)
        self.market_env.market_history.add_offer_price(self.p.start_price)
        self.market_env.market_history.add_bid_price(self.p.start_price)
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
            sell_of.trader.change_balance(total_quantity * price, -1 * total_quantity)
            buy_of.trader.change_balance(-1 * total_quantity * price, total_quantity)
            self.market_env.market_history.add_deal(sell_of.trader, buy_of.trader, total_quantity)
        self.market_env.order_book.clean()
        if self.p.print_ETA:
            mean_time = (datetime.datetime.now() - self.start_time) / self.t
            print(f"\rModel with ID {self.id} complete: {self.t} steps \t ETA = {mean_time * (self.p.steps - self.t)}", end='')

    def end(self):
        if self.p.record_results:
            prices = self.market_env.market_history.get_prices(limit=None)
            u = list()
            for i in range(20, len(prices) - 1):
                u.append(np.log(prices[i + 1] / prices[i]))
            figure1 = plt.figure(1, figsize=(20, 10))
            plt.hist(u, 500, density=True)
            plt.savefig(f"run_results/{self.p.model_name}/{self.p.steps}_price_hist.png")
            plt.close(figure1)
            figure2 = plt.figure(1, figsize=(20, 10))
            plt.hist(u, 500, density=True)
            plt.yscale('log')
            plt.savefig(f"run_results/{self.p.model_name}/{self.p.steps}_price_hist_log.png")
            plt.close(figure2)
            figure3 = plt.figure(1, figsize=(max(self.p.steps // 100, 50), 15))
            plt.plot(prices, "bo-")
            plt.savefig(f"run_results/{self.p.model_name}/{self.p.steps}_price_plot.png")
            plt.close(figure3)


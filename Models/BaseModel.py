import datetime
import os.path
import random


import agentpy as ap
import numpy as np

from matplotlib import pyplot as plt
from utils.Constants import OperationTypes
from MarketEnv.MarketEnv import MarketEnv
from utils.AgentMapping import AGENT_NAMES_LIST, AGENT_TYPE_FROM_NAME, AgentTypes


class BaseModelException(Exception):
    def __init__(self, message="You have to send some error message"):
        self.message = message
        super().__init__(self.message)


class BaseModel(ap.Model):
    """
    Methods:
        - step(self) -> void : one step of iteration
        - setup(self) -> void : some shit from ap.Model superclass ...
    """

    def _prepare_agents(self):
        self.agents = {}

        self.used_agent_types = []
        self.used_agent_names = []
        self.agent_names_count = dict()
        self.agent_types_count = dict()

        for agent_name in AGENT_NAMES_LIST:
            try:
                cnt = self.p.__getattr__(f"{agent_name}_count")
            except AttributeError:
                continue
            if cnt == 0:
                continue
            agent_type = AGENT_TYPE_FROM_NAME[agent_name]

            self.used_agent_names.append(agent_name)
            self.used_agent_types.append(agent_type)
            self.agent_names_count[agent_name] = cnt
            self.agent_types_count[agent_type] = cnt

            self.agents[agent_type] = ap.AgentList(self, cnt, agent_type)
            self.agents[agent_type].set_name(agent_name)

    def _prepare_market_env(self):
        self.market_env = MarketEnv()

        self.market_env.market_history.add_deal_price(self.p.start_price)
        self.market_env.market_history.add_offer_price(self.p.start_price)
        self.market_env.market_history.add_bid_price(self.p.start_price)

        for agent_type in self.used_agent_types:
            for agent in self.agents[agent_type]:
                if agent == AgentTypes.MM_TR:
                    self.market_env.order_book.sell_data[agent] = [None] * self.p.MM_order_live_time
                    self.market_env.order_book.buy_data[agent] = [None] * self.p.MM_order_live_time
                else:
                    self.market_env.order_book.sell_data[agent] = [None]
                    self.market_env.order_book.buy_data[agent] = [None]

    # TODO:
    # Add collection of panic state, init of inventory collection, market volume
    def _prepare_statistic_collection(self):
        self.panic_cases = [[]] * self.p.steps

        self.agent_inventories = dict()

        # TODO:
        # Add other stuff

    def _prepare_logging(self):
        log_file_name = '_'.join(map(lambda x: str(self.agent_names_count[x]), self.used_agent_names))
        log_path = os.path.join('run_results', 'logs', self.p.model_name, f"{log_file_name}.log")
        with open(log_path, 'w') as f:
            f.write("Start logging\n"
                    "Model successfully setup\n"
                    "Running configuration:\n")
            f.flush()
        self.__log_file = open(log_path, 'a')
        for agent_name in self.used_agent_names:
            # self.__log_file.write(f"\t {agent_name} count is {self.p.__getattr__(f'{agent_name}_count')}\n")
            self.__log_file.write(f"\t {agent_name} count is {self.agent_names_count[agent_name]}\n")
        self.__log_file.write(f"\t model steps: {self.p.steps}\n")
        self.__log_file.write("Extracted prices:\n")
        self.__log_file.flush()

    def record_panic_state(self, agent):
        self.panic_cases[self.t].append(agent)

    def add_to_inventory(self, agent, value):
        if agent not in self.agent_inventories.keys():
            self.agent_inventories[agent] = []
        self.agent_inventories[agent].append(value)

    def setup(self):
        self.start_time = datetime.datetime.now()
        self._prepare_agents()
        self._prepare_market_env()
        self._prepare_logging()
        self._prepare_statistic_collection()

        self._config_str = ' '.join([f'{agent_name}: {str(self.agent_names_count[agent_name])}'
                                     for agent_name in self.used_agent_names]) + \
                           f' steps: {self.p.steps}'

    def step(self):
        for agent_sublist in self.agents.values():
            agent_sublist.make_decision()

    def update(self):
        if self.t == 0:
            return
        price, offer_price, bid_price = self.market_env.get_price()
        if self.t == 4000:
            price *= 1.2
            bid_price *= 1.2
            offer_price *= 1.2
        self.market_env.market_history.start_new_iter()
        self.market_env.market_history.add_deal_price(price)
        self.market_env.market_history.add_offer_price(offer_price)
        self.market_env.market_history.add_bid_price(bid_price)
        for i in range(self.agent_types_count[AgentTypes.MM_TR]):
            mm_inv = self.agents[AgentTypes.MM_TR][i].get_inv()
            self.add_to_inventory(self.agents[AgentTypes.MM_TR][i], mm_inv)
        sell_offers = self.market_env.order_book.sellers_at_price(price)
        buy_offers = self.market_env.order_book.buyers_at_price(price)
        random.shuffle(sell_offers)
        random.shuffle(buy_offers)
        sell_ind = 0
        buy_ind = 0
        while sell_ind != len(sell_offers) and buy_ind != len(buy_offers):
            sell_of = sell_offers[sell_ind]
            buy_of = buy_offers[buy_ind]

            if sell_of.quantity >= buy_of.quantity:
                sell_of.quantity -= buy_of.quantity
                total_quantity = buy_of.quantity
                ind = self.t - sell_of.time
                self.market_env.order_book.sell_data[sell_of.trader][ind].quantity -= buy_of.quantity
                ind = self.t - buy_of.time
                self.market_env.order_book.buy_data[buy_of.trader][ind] = None
                buy_ind += 1
            else:
                buy_of.quantity -= sell_of.quantity
                total_quantity = sell_of.quantity
                ind = self.t - buy_of.time
                self.market_env.order_book.buy_data[buy_of.trader][ind].quantity -= sell_of.quantity
                ind = self.t - sell_of.time
                self.market_env.order_book.sell_data[sell_of.trader][ind] = None
                sell_ind += 1
            sell_of.trader.make_deal(price, total_quantity, OperationTypes.SELL)
            buy_of.trader.make_deal(price, total_quantity, OperationTypes.BUY)
            self.market_env.market_history.add_deal(buy_of.trader, sell_of.trader, total_quantity)
        self.market_env.order_book.clean()
        if self.p.print_ETA:
            mean_time = (datetime.datetime.now() - self.start_time) / self.t
            print(f"\rModel with ID {self.id} complete: {self.t} steps \t ETA = {mean_time * (self.p.steps - self.t)}",
                  end='')
        if self.p.record_logs:
            self.__log_file.write(f"\titer {self.t}: price = {price}\n")
            self.__log_file.write(f"\titer {self.t}: bid_price = {bid_price}\n")
            self.__log_file.write(f"\titer {self.t}: offer_price = {offer_price}\n")
            for deal in self.market_env.market_history.deals[-1]:
                self.__log_file.write(f"{deal.__str__()}\n")
            self.__log_file.flush()

    def end(self):
        if self.p.draw_hists or self.p.draw_plots:
            prices = self.market_env.market_history.get_prices(limit=None)
            template_file = os.path.join('run_results', self.p.model_name, str(self.p.steps))
            if self.p.draw_hists:
                u = list()
                for i in range(20, len(prices) - 1):
                    u.append(np.log(prices[i + 1] / prices[i]))
                figure1 = plt.figure(1, figsize=(20, 10))
                plt.hist(u, 500, density=True)
                plt.savefig(f"{template_file}_price_hist.png")
                plt.close(figure1)
                figure2 = plt.figure(1, figsize=(20, 10))
                plt.hist(u, 500, density=True)
                plt.yscale('log')
                plt.savefig(f"{template_file}_price_hist_log.png")
                plt.close(figure2)
            if self.p.draw_plots:
                figure3 = plt.figure(1, figsize=(max(self.p.steps // 100, 50), 15))
                if max(prices) > 10000:
                    plt.yscale('log')
                plt.axvline(x=1000, color='r')
                title = self._config_str
                plt.title(title)
                plt.plot(prices, "bo-")
                plt.savefig(f"{template_file}_price_plot.png")
                plt.close(figure3)

                figure4 = plt.figure(1, figsize=(max(self.p.steps // 100, 50), 15))
                title = self._config_str
                plt.title(title)
                for agent in self.agents[AgentTypes.MM_TR]:
                    plt.plot(self.agent_inventories[agent], label=f'inv of {agent.id}')
                plt.axhline(y=self.p.MarketMakerAgent_risk_level, color='r', ls=':')
                plt.axhline(y=-1 * self.p.MarketMakerAgent_risk_level, color='r', ls=':')
                plt.axhline(y=0, color='g', ls=':')
                plt.legend()
                plt.savefig(f"{template_file}_mm_inventory.png")
                plt.close(figure4)
        if self.p.record_logs:
            self.__log_file.write(f"\nModel successfully finished at {(datetime.datetime.now() - self.start_time)}")
            self.__log_file.flush()
            self.__log_file.close()

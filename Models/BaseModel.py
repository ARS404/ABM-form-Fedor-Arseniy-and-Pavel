import datetime
import os.path

import agentpy as ap
import numpy as np

from matplotlib import pyplot as plt

from MarketEnv.MarketEnv import MarketEnv
from utils.AgentMapping import AGENT_FROM_STR, AGENT_NAMES_LIST

# # TODO: fix this shit
# models_total_cnt = (10000 + 11) // 12
# models_inited = 0
# models_finished = 0
# start_time = None


class BaseModel(ap.Model):
    """
    Methods:
        - step(self) -> void : one step of iteration
        - setup(self) -> void : some shit from ap.Model superclass ...
    """

    def setup(self):
        # # TODO: fix this shit
        # global start_time, models_inited, models_total_cnt
        # if models_inited == 0:
        #     start_time = datetime.datetime.now()
        #     # print(f'\rset start_time to {start_time}', end='')
        # models_inited += 1
        # # print(f'\rsetup model number {models_inited} of {models_total_cnt}', end='')

        self.start_time = datetime.datetime.now()
        self.market_env = MarketEnv()
        self.market_env.market_history.add_deal_price(self.p.start_price)
        self.market_env.market_history.add_offer_price(self.p.start_price)
        self.market_env.market_history.add_bid_price(self.p.start_price)
        self.agents = dict()

        self.used_agents = []
        for agent_name in AGENT_NAMES_LIST:
            try:
                cnt = self.p.__getattr__(f"{agent_name}_count")
            except AttributeError:
                continue
            if cnt == 0:
                continue
            self.used_agents.append(agent_name)
        self.used_agents = sorted(self.used_agents)
        self.agents_count = {agent_name: self.p.__getattr__(f"{agent_name}_count") for agent_name in self.used_agents}

        for agent_name in self.used_agents:
            cnt = self.p.__getattr__(f"{agent_name}_count")
            self.agents[AGENT_FROM_STR[agent_name]] = ap.AgentList(self, cnt, AGENT_FROM_STR[agent_name])
        if self.p.record_logs:
            name = '_'.join(map(lambda x: str(self.agents_count[x]), self.used_agents))
            # name = '_'.join(map(lambda x: str(self.p.__getattr__(f"{x}_count")), self.used_agents))
            log_path = os.path.join('run_results', 'logs', self.p.model_name, f"{name}.log")
            with open(log_path, 'w') as f:
                f.write("Start logging\n"
                        "Model successfully setup\n"
                        "Running configuration:\n")
                f.flush()
            self.__log_file = open(log_path, 'a')
            for agent_name in self.used_agents:
                # self.__log_file.write(f"\t {agent_name} count is {self.p.__getattr__(f'{agent_name}_count')}\n")
                self.__log_file.write(f"\t {agent_name} count is {self.agents_count[agent_name]}\n")
            self.__log_file.write(f"\t model steps: {self.p.steps}\n")
            self.__log_file.write("Extracted prices:\n")
            self.__log_file.flush()

    def step(self):
        for agent_sublist in self.agents.values():
            agent_sublist.make_decision()

    def update(self):
        if self.t == 0:
            return
        price, offer_price, bid_price = self.market_env.get_price()
        if self.t == 1000:
            price *= 1.05
            bid_price *= 1.05
            offer_price *= 1.05
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
            print(f"\rModel with ID {self.id} complete: {self.t} steps \t ETA = {mean_time * (self.p.steps - self.t)}",
                  end='')
        if self.p.record_logs:
            self.__log_file.write(f"\titer {self.t}: price = {price}\n")
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
                title = ' '.join([f'{agent}: {str(self.agents_count[agent])}' for agent in self.used_agents]) + \
                        f' steps: {self.p.steps}'
                plt.title(title)
                plt.plot(prices, "bo-")
                plt.show()
                # plt.savefig(f"{template_file}_price_plot.png")
                plt.close(figure3)
        if self.p.record_logs:
            self.__log_file.write(f"\nModel successfully finished at {(datetime.datetime.now() - self.start_time)}")
            self.__log_file.flush()
            self.__log_file.close()
        # # TODO: fix this shit
        # global models_finished, models_total_cnt, start_time
        # models_finished += 1
        # print(f'\rfinish {models_finished} model(s) of {models_total_cnt} \t ETA: '
        #       f'{(datetime.datetime.now() - start_time) / models_finished * (models_total_cnt - models_finished)}',
        #       end='')

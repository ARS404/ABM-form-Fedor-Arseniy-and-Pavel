import datetime
import os.path

import agentpy as ap
import numpy as np
from scipy.stats import norm

from MarketEnv.MarketEnv import MarketEnv
from utils.Constants import OperationTypes
from utils.AgentMapping import AGENT_NAMES_LIST, AGENT_TYPE_FROM_NAME, AgentTypes, AgentNames
from utils.UtilFunctions import draw_plot


class BaseModel(ap.Model):
    """
    Methods:
        - step(self) -> void : one step of iteration
        - setup(self) -> void : some shit from ap.Model superclass ...
    """

    def _prepare_agents(self):
        self.agents = {}

        self._used_agent_types = []
        self._used_agent_names = []
        self._agent_names_count = dict()
        self._agent_types_count = dict()

        sum_inv = 0.0
        sum_money = 0.0

        for agent_name in AGENT_NAMES_LIST:
            if agent_name == AgentNames.MM_TR:
                continue
            try:
                cnt = self.p.__getattr__(f"{agent_name}_count")
            except AttributeError:
                continue
            if cnt == 0:
                continue
            sum_inv += cnt * self.p.__getattr__(f"{agent_name}_start_inventory")
            sum_money += cnt * self.p.__getattr__(f"{agent_name}_start_money")
            agent_type = AGENT_TYPE_FROM_NAME[agent_name]

            self._used_agent_names.append(agent_name)
            self._used_agent_types.append(agent_type)
            self._agent_names_count[agent_name] = cnt
            self._agent_types_count[agent_type] = cnt

            self.agents[agent_type] = ap.AgentList(self, cnt, agent_type)
            self.agents[agent_type].set_name(agent_name)

        self.p.MarketMakerAgent_start_inventory = 0.0
        self.p.MarketMakerAgent_risk_level = sum_inv * self.p.inventory_fraction / self.p.MarketMakerAgent_count
        self.p.start_price = sum_money / sum_inv * self.p.start_price_coefficient
        sum_inv += self.p.MarketMakerAgent_count * 2 * self.p.MarketMakerAgent_risk_level
        agent_name = AgentNames.MM_TR
        try:
            cnt = self.p.__getattr__(f"{agent_name}_count")
        except AttributeError:
            return
        if cnt == 0:
            return
        agent_type = AGENT_TYPE_FROM_NAME[agent_name]

        self._used_agent_names.append(agent_name)
        self._used_agent_types.append(agent_type)
        self._agent_names_count[agent_name] = cnt
        self._agent_types_count[agent_type] = cnt

        self.agents[agent_type] = ap.AgentList(self, cnt, agent_type)
        self.agents[agent_type].set_name(agent_name)
    def _prepare_market_env(self):
        self.market_env = MarketEnv()

        self.market_env.market_history.add_deal_price(self.p.start_price)
        self.market_env.market_history.add_offer_price(self.p.start_price)
        self.market_env.market_history.add_bid_price(self.p.start_price)

        for agent_type in self._used_agent_types:
            for agent in self.agents[agent_type]:
                if agent == AgentTypes.MM_TR:
                    self.market_env.order_book.sell_data[agent] = [None] * self.p.MM_order_live_time
                    self.market_env.order_book.buy_data[agent] = [None] * self.p.MM_order_live_time
                else:
                    self.market_env.order_book.sell_data[agent] = [None]
                    self.market_env.order_book.buy_data[agent] = [None]

    def _prepare_statistic_collection(self):
        self._panic_cases = [[] for i in range(self.p.steps + 1)]
        self._agent_inventories = {}
        self._market_volume_money = []
        self._market_volume_product = []

    def _prepare_logging(self):
        log_file_name = '_'.join(map(lambda x: str(self._agent_names_count[x]), self._used_agent_names))
        log_path = os.path.join('run_results', 'logs', self.p.model_name, f"{log_file_name}.log")
        with open(log_path, 'w') as f:
            f.write("Start logging\n"
                    "Model successfully setup\n"
                    "Running configuration:\n")
            f.flush()
        self.__log_file = open(log_path, 'a')
        for agent_name in self._used_agent_names:
            # self.__log_file.write(f"\t {agent_name} count is {self.p.__getattr__(f'{agent_name}_count')}\n")
            self.__log_file.write(f"\t {agent_name} count is {self._agent_names_count[agent_name]}\n")
        self.__log_file.write(f"\t model steps: {self.p.steps}\n")
        self.__log_file.write("Extracted prices:\n")
        self.__log_file.flush()

    def record_panic_state(self, agent):
        self._panic_cases[self.t].append(agent)

    def add_to_inventory(self, agent, value):
        if agent not in self._agent_inventories.keys():
            self._agent_inventories[agent] = []
        self._agent_inventories[agent].append(value)

    def setup(self):
        if not isinstance(self.p.shock_moments, list):
            self.p.shock_moments = [self.p.shock_moments]
        if not isinstance(self.p.shock_values, list):
            self.p.shock_values = [self.p.shock_values]
        self._start_time = datetime.datetime.now()
        self._prepare_agents()
        self._prepare_market_env()
        if self.p.record_logs:
            self._prepare_logging()
        self._prepare_statistic_collection()
        self._config_str = ' '.join([f'{agent_name}: {str(self._agent_names_count[agent_name])}'
                                     for agent_name in self._used_agent_names]) + \
                           f' steps: {self.p.steps}'

    def step(self):
        for agent_sublist in self.agents.values():
            agent_sublist.make_decision()

    def update(self):
        if self.t == 0:
            return
        price, offer_price, bid_price = self.market_env.get_price()

        if self.p.enable_shock and self.t in self.p.shock_moments:
            shock_number = self.p.shock_moments.index(self.t)
            shock_value = self.p.shock_values[shock_number]
            price *= (1 + shock_value)
            offer_price *= (1 + shock_value)
            bid_price *= (1 + shock_value)

        self.market_env.market_history.start_new_iter()
        self.market_env.market_history.add_deal_price(price)
        self.market_env.market_history.add_offer_price(offer_price)
        self.market_env.market_history.add_bid_price(bid_price)

        sell_offers = self.market_env.order_book.sellers_at_price(price)
        buy_offers = self.market_env.order_book.buyers_at_price(price)
        self.nprandom.shuffle(sell_offers)
        self.nprandom.shuffle(buy_offers)
        sell_ind = 0
        buy_ind = 0

        iter_total_quantity = 0.0
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
            iter_total_quantity += total_quantity
            sell_of.trader.make_deal(price, total_quantity, OperationTypes.SELL)
            buy_of.trader.make_deal(price, total_quantity, OperationTypes.BUY)
            self.market_env.market_history.add_deal(buy_of.trader, sell_of.trader, total_quantity)

        self._market_volume_money.append(price * iter_total_quantity)
        self._market_volume_product.append(iter_total_quantity)

        self.market_env.order_book.clean()

        for agent in self.agents[AgentTypes.MM_TR]:
            self.add_to_inventory(agent, agent.get_inv())

        if self.p.print_ETA:
            mean_time = (datetime.datetime.now() - self._start_time) / self.t
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
        if self.p.draw_plots:
            prices = self.market_env.market_history.get_prices(limit=None)
            # uncomment next line if you want ot save plots
            template_file = os.path.join('run_results', self.p.model_name, str(self.p.steps))
            template_figsize = (max(self.p.steps // 100, 50), 15)
            template_vlines = None
            if self.p.enable_shock:
                template_vlines = [(self.p.shock_moments[i], 'r' if self.p.shock_values[i] > 0.0 else 'g', ':')
                                   for i in range(len(self.p.shock_moments))]

            if max([len(self._panic_cases[i]) for i in range(1000, 1100)]) >= 2 and\
                    max([len(self._panic_cases[i]) for i in range(0, 999)]) == 0:
                log_file_name = '_'.join(map(lambda x: str(self._agent_names_count[x]), self._used_agent_names))
                log_path = os.path.join('run_results', 'logs', f"{self.p.MM_order_live_time}_{log_file_name}.log")
                with open(log_path, 'w') as f:
                    f.write(f'volatility = {self.calculate_volatility()}\n'
                            f'linear_liquidity = {self.calculate_linear_liquidity()}\n'
                            f'log_liquidity = {self.calculate_log_liquidity()}')
                    f.flush()
            # draw_plot(plots_data=prices, title=f'prices with config = {self._config_str}', xlabel=None,
            #           ylabel=None, figsize=template_figsize, vlines=template_vlines,
            #           file=f'{template_file}_{self.p.enable_shock}_{log_file_name}_prices.png', logscale=False)
            #
            # draw_plot(plots_data=[self._agent_inventories[agent] for agent in self.agents[AgentTypes.MM_TR]],
            #           title=f'MM inventories with config = {self._config_str}',
            #           xlabel='model step', ylabel='inventory', figsize=template_figsize,
            #           hlines=[
            #               (self.p.MarketMakerAgent_risk_level, 'r', ':'),
            #               (0, 'g', ':'),
            #               (-self.p.MarketMakerAgent_risk_level, 'r', ':')
            #           ],
            #           labels=[f'inv of {agent.id}' for agent in self.agents[AgentTypes.MM_TR]],
            #           vlines=template_vlines,
            #           multyplot=True, file=f'{template_file}_MM_inventories')
            #
            # draw_plot(plots_data=[len(self._panic_cases[i]) for i in range(self.p.steps + 1)],
            #           title=f'MMs in panic with config = {self._config_str}',
            #           xlabel=None, ylabel=None, figsize=template_figsize,
            #           vlines=template_vlines, file=f'{template_file}_MM_in_panic')
            # draw_plot(plots_data=self._market_volume_money,
            #           title=f'market volume in money with config = {self._config_str}',
            #           xlabel='model step', ylabel='market volume', figsize=template_figsize, vlines=template_vlines,
            #           file=f'{template_file}_volume_money')
            # draw_plot(plots_data=self._market_volume_product,
            #           title=f'market volume in product with config = {self._config_str}',
            #           xlabel='model step', ylabel='market volume', figsize=template_figsize,
            #           vlines=template_vlines, file=f'{template_file}_volume_product')
            # draw_plot(plots_data=self.calculate_vpin(),
            #           title=f'vpin with config = {self._config_str}',
            #           xlabel='model step', ylabel='VPIN', figsize=template_figsize,
            #            file=f'{template_file}_VPIN', hlines=[(0, 'black', '-'), (1, 'black', '-')])
            # draw_plot(plots_data=self.calculate_log_liquidity(),
            #           title=f'log liquidity with config = {self._config_str}',
            #           xlabel='model step', ylabel='log liquidity', figsize=template_figsize,
            #           file=f'{template_file}_log_liquidity')
            # draw_plot(plots_data=self.calculate_linear_liquidity(),
            #           title=f'linear liquidity with config = {self._config_str}',
            #           xlabel='model step', ylabel='linear liquidity', figsize=template_figsize,
            #           file=f'{template_file}_linear_liquidity')
            # draw_plot(plots_data=self.calculate_volatility(),
            #           title=f'volatility with config = {self._config_str}',
            #           xlabel='model step', ylabel='volatility', figsize=template_figsize,
            #           file=f'{template_file}_volatility', logscale=True)

        if self.p.record_logs:
            self.__log_file.write(f"\nModel successfully finished at {(datetime.datetime.now() - self._start_time)}")
            self.__log_file.flush()
            self.__log_file.close()

    def calculate_vpin(self):
        volumes = self._market_volume_product
        volume_in_bucket = sum(volumes) / (self.p.statistics_window * 4)
        price_changes = list()
        oi = list()
        prices = self.market_env.market_history.get_prices(limit=None)
        cur_vol = 0
        bucket_begin = 0
        for i in range(len(volumes)):
            cur_vol += volumes[i]
            if cur_vol < volume_in_bucket:
                price_changes.append(prices[i + 1] - prices[i])
            while cur_vol >= volume_in_bucket:
                z = 0.5
                if len(price_changes) >= 2:
                    price_dev = np.sqrt(np.var(price_changes))
                    total_price_change = prices[i + 1] - prices[bucket_begin]
                    if price_dev != 0:
                        z = norm.cdf(total_price_change / price_dev)
                v_b = volume_in_bucket * z
                v_s = volume_in_bucket - v_b
                oi.append(abs(v_b - v_s) / volume_in_bucket)
                cur_vol = cur_vol - volume_in_bucket
                price_changes = list()
                if cur_vol > 0:
                    bucket_begin = i
                else:
                    bucket_begin = i + 1
        seg_sum = sum(oi[0:self.p.statistics_window])
        vpin = list([seg_sum / self.p.statistics_window])
        for i in range(len(oi) - self.p.statistics_window):
            seg_sum += oi[i + self.p.statistics_window] - oi[i]
            vpin.append(seg_sum / self.p.statistics_window)
        return vpin

    def calculate_log_liquidity(self):
        prices = self.market_env.market_history.get_prices(limit=None)
        volumes = self._market_volume_product
        log_liquidity = list()
        for i in range(self.p.steps - self.p.statistics_window):
            log_liquidity.append(abs(np.log(prices[i + self.p.statistics_window]) - np.log(prices[i])))
            log_liquidity[-1] /= np.log(sum(volumes[i:i + self.p.statistics_window]))
        return log_liquidity

    def calculate_linear_liquidity(self):
        prices = self.market_env.market_history.get_prices(limit=None)
        volumes = self._market_volume_product
        linear_liquidity = list()
        for i in range(self.p.steps - self.p.statistics_window):
            linear_liquidity.append(abs(prices[i + self.p.statistics_window] - prices[i]))
            linear_liquidity[-1] /= sum(volumes[i:i + self.p.statistics_window])
        return linear_liquidity

    def calculate_volatility(self):
        prices = self.market_env.market_history.get_prices(limit=None)
        log_returns = list()
        for i in range(self.p.steps):
            log_returns.append(np.log(prices[i + 1]) - np.log(prices[i]))
        volatility = list()
        for i in range(self.p.steps - self.p.statistics_window):
            volatility.append(np.sqrt(np.var(prices[i:i + self.p.statistics_window])))
        return volatility

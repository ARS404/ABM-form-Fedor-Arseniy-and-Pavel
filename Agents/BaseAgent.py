import agentpy as ap


class BaseAgent(ap.Agent):
    """
    Methods:
        - make_decision(self, market_env) -> void : agent make its decision based on market_env.market_history
            and its state, then write chosen option to market_env.order_book
    """

    def __hash__(self):
        return self.id

    def setup(self):
        self.money = self.p.start_money[BaseAgent]
        self.invent = self.p.start_invent[BaseAgent]

    def make_decision(self, market_env):
        raise NotImplementedError

    def change_balance(self, d_money, d_invent):
        self.money += d_money
        self.invvent += d_invent



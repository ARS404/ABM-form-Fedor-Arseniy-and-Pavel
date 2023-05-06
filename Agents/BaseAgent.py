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
        raise NotImplementedError

    def make_decision(self, market_env):
        raise NotImplementedError




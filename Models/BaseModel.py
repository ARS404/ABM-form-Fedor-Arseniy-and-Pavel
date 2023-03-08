import agentpy as ap



class BaseModel(ap.Model):
    """
    Methods:
        - step(self) -> void : one step of iteration
        - setup(self) -> void : some shit from ap.Model superclass ...
    """

    def __init__(self, agent_list, market_env):
        self.agents = agent_list
        self.market_env = market_env
    def setup(self):
        pass

    def step(self):
        self.market_env.clean_order_book()

        for agent in self.agents:
            agent.make_decision(self.market_env)

        # Here we should write code to make exchange between agents



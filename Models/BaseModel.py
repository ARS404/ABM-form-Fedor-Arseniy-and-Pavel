import agentpy as ap

from Agents.BaseAgent import BaseAgent

class BaseModel(ap.Model):
    """
    Methods:
        - step(self) -> void : one step of iteration
        - setup(self) -> void : some shit from ap.Model superclass ...
    """

    def setup(self):
        self.agents = dict()
        for tp, cnt in self.p.agents:
            self.agents[tp] = ap.AgentList(self, cnt, tp)

    def step(self):
        for agent_sublist in self.agents.values():
            agent_sublist.make_dessision()

    def update(self):
        super().update()
        # Here we should write code to make exchange between agents

    def end(self):
        pass



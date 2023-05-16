from enum import Enum

from Agents.CommonTraderAgent import CommonTraderAgent
from Agents.HamsterAgent import HamsterAgent
from Agents.MarketMakerAgent import MarketMakerAgent
from Agents.TargetWealthAgent import TargetWealthAgent
from Agents.ZeroIntelligenceAgent import ZeroIntelligenceAgent


class AgentNames(object):
    COM_TR = 'CommonTraderAgent'
    HAM_TR = "HamsterAgent"
    MM_TR = "MarketMakerAgent"
    TARG_TR = "TargetWealthAgent"
    ZERO_INT_TR = "ZeroIntelligenceAgent"


class AgentTypes(object):
    COM_TR = CommonTraderAgent
    HAM_TR = HamsterAgent
    MM_TR = MarketMakerAgent
    TARG_TR = TargetWealthAgent
    ZERO_INT_TR = ZeroIntelligenceAgent


AGENT_NAMES_LIST = [
    AgentNames.COM_TR,
    AgentNames.HAM_TR,
    AgentNames.MM_TR,
    AgentNames.TARG_TR,
    AgentNames.ZERO_INT_TR,
]

AGENT_TYPE_FROM_NAME = {
    AgentNames.COM_TR: AgentTypes.COM_TR,
    AgentNames.HAM_TR: AgentTypes.HAM_TR,
    AgentNames.MM_TR: AgentTypes.MM_TR,
    AgentNames.TARG_TR: AgentTypes.TARG_TR,
    AgentNames.ZERO_INT_TR: AgentTypes.ZERO_INT_TR,
}


AGENT_NAME_FROM_TYPE = {
    AgentTypes.COM_TR: AgentNames.COM_TR,
    AgentTypes.HAM_TR: AgentNames.HAM_TR,
    AgentTypes.MM_TR: AgentNames.MM_TR,
    AgentTypes.TARG_TR: AgentNames.TARG_TR,
    AgentTypes.ZERO_INT_TR: AgentNames.ZERO_INT_TR,
}

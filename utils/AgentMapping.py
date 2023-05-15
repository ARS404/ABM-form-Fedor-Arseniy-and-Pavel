import enum

from Agents.CommonTraderAgent import CommonTraderAgent
from Agents.HamsterAgent import HamsterAgent
from Agents.MarketMakerAgent import MarketMakerAgent
from Agents.TargetWealthAgent import TargetWealthAgent
from Agents.ZeroIntelligenceAgent import ZeroIntelligenceAgent


AGENT_FROM_STR = {
    "CommonTraderAgent": CommonTraderAgent,
    "HamsterAgent": HamsterAgent,
    "MarketMakerAgent": MarketMakerAgent,
    "TargetWealthAgent": TargetWealthAgent,
    "ZeroIntelligenceAgent": ZeroIntelligenceAgent,
}

AGENT_NAMES_LIST = sorted([
    "CommonTraderAgent",
    "HamsterAgent",
    "MarketMakerAgent",
    "TargetWealthAgent",
    "ZeroIntelligenceAgent",
])


class AGENT_NAMES(enum):
    COMMON = "CommonTraderAgent"
    HAMSTER = "HamsterAgent"
    MARKET_MAKER = "MarketMakerAgent"
    TARGET_WEALTH = "TargetWealthAgent"
    ZERO_INT = "ZeroIntelligenceAgent"

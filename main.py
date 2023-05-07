import json

from copy import deepcopy

from Models.BaseModel import BaseModel

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


def prepare_configs(params):
    ret = deepcopy(params)
    for name in params['Agents']:
        ret['Agents'].pop(name)
        ret['Agents'][AGENT_FROM_STR[name]] = params['Agents'][name]
    return ret


def main():
    with open('settings.json', 'r') as f:
        params = f.read()
    parameters = json.loads(params)['SecondSetup']
    parameters = prepare_configs(parameters)
    model = BaseModel(parameters=parameters)
    result = model.run()
    print(result)


if __name__ == '__main__':
    main()

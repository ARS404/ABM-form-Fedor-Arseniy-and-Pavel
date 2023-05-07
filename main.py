import json

from copy import deepcopy
from matplotlib import pyplot
import agentpy as ap
import ipysimulate as ips
from ipywidgets import AppLayout

from Models.BaseModel import BaseModel
from Agents.CommonTraderAgent import CommonTraderAgent
from Agents.HamsterAgent import HamsterAgent
from Agents.TargetWealthAgent import TargetWealthAgent
from Agents.ZeroIntelligenceAgent import ZeroIntelligenceAgent


AGENT_FROM_STR = {
    "CommonTraderAgent": CommonTraderAgent,
    "HamsterAgent": HamsterAgent,
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
    parameters = json.loads(params)['FirstSetup']
    parameters = prepare_configs(parameters)
    model = BaseModel(parameters=parameters)
    # control = ips.Control(model, parameters, variables=('t',))
    # lineplot = ips.Lineplot(control, 'gini')
    # AppLayout(
    #     left_sidebar=control,
    #     center=lineplot,
    #     pane_widths=['125px', 1, 1],
    #     height='400px'
    # )
    result = model.run()
    print(model.market_env.market_history.get_prices())
    pyplot.figure(1, figsize=(60, 15))
    pyplot.plot(model.market_env.market_history.get_prices(), "bo-")
    pyplot.savefig("a.png")
    print(result)


if __name__ == '__main__':
    main()

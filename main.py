import json

from copy import deepcopy

import matplotlib.pyplot as plt
from matplotlib import pyplot
import numpy as np
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
    result = model.run()
    prices = model.market_env.market_history.get_prices(limit=None)
    u = list()
    for i in range(20, len(prices) - 1):
        u.append(np.log(prices[i + 1] / prices[i]))
    figure1 = pyplot.figure(1, figsize=(20, 10))
    plt.hist(u, 500, density=True)
    pyplot.savefig("b.png")
    plt.close(figure1)
    figure2 = pyplot.figure(1, figsize=(100, 15))
    plt.plot(prices, "bo-")
    pyplot.savefig("a.png")
    plt.close(figure2)
    print(result)


if __name__ == '__main__':
    main()

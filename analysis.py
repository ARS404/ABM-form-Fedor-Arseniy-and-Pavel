import copy

import matplotlib.pyplot as plt
import re
from utils.UtilFunctions import draw_plot
import os
import numpy as np

def draw_plot_from_log(log_file_name, vol=False, lin_liq=False, log_liq=False):
    with open(log_file_name, 'r') as f:
        data = f.read()
        volatility = re.findall("volatility = \[([^\]]*)\]", data)[0]
        volatility = list(map(lambda x: float(x), volatility.split(", ")))
        template_figsize = (max(5000 // 100, 50), 15)
        template_vlines = [(1000, 'r', ':')]
        template_file = os.path.join('run_results', log_file_name.split('.log')[0].split('/')[-1] + "_5000")
        draw_plot(plots_data=volatility,
                  title=f'volatility with config = {log_file_name}',
                  xlabel='model step', ylabel='volatility', figsize=template_figsize,
                  file=f'{template_file}_volatility.png', vlines=template_vlines)


files = os.listdir("run_results/logs")
volatility_data = [[]]
linear_liquidity_data = [[]]
log_liquidity_data = [[]]
for i in range(14):
    volatility_data.append(list([]))
    linear_liquidity_data.append(list([]))
    log_liquidity_data.append(list([]))

for file in files:
    if file == 'Experiments':
        continue
    data1 = list()
    data2 = list()

    with open(f'run_results/logs/{file}', 'r') as f:
        parameter = int(file.split('_')[0])
        data = f.read()
        volatility = re.findall("volatility = \[([^\]]*)\]", data)[0]
        volatility = list(map(lambda x: float(x), volatility.split(", ")))
        volatility_data[parameter - 2].append(np.mean(volatility[1000:-1]))

        log_liquidity = re.findall("log_liquidity = \[([^\]]*)\]", data)[0]
        log_liquidity = list(map(lambda x: float(x), log_liquidity.split(", ")))
        log_liquidity_data[parameter - 2].append(np.mean(log_liquidity[1000:-1]))

        linear_liquidity = re.findall("linear_liquidity = \[([^\]]*)\]", data)[0]
        linear_liquidity = list(map(lambda x: float(x), linear_liquidity.split(", ")))
        linear_liquidity_data[parameter - 2].append(np.mean(linear_liquidity[1000:-1]))


for x in volatility_data:
    print(np.mean(x))
for x in linear_liquidity_data:
    print(np.mean(x))
for x in log_liquidity_data:
    print(np.mean(x))

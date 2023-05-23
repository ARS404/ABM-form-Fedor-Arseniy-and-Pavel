import re
import os

import matplotlib.pyplot as plt
import numpy as np

from utils.UtilFunctions import draw_plot


def format_data(data, keys):
    # prices=False, volatility=False, log_liquidity=False, linear_liquidity=False):
    ret = dict()
    for key in keys:
        x = re.findall(f"{key} = \[([^\]]*)\]", data)
        if len(x) == 0:
            print("Wrong key")
            exit(1)
        ret[key] = list(map(lambda a: float(a), x[0].split(', ')))
    return ret


def parce_log_folder(folder):
    logs = os.listdir(folder)
    logs = sorted([log for log in logs if '.log' in log])
    ret = dict()
    for log in logs:
        with open(os.path.join(folder, log), 'r') as f:
            data = f.read()
        ret[log.split('/')[-1].split('.')[0]] = format_data(data, ('prices', 'volatility', 'log_liquidity',
                                                                   'linear_liquidity'))
    return ret


def main():
    results = parce_log_folder("run_results/logs")
    # 0
    key = list(results.keys())[18]
    draw_plot(plots_data=results[key]['prices'], title=f'prices with config {key}',
              xlabel=None,
              ylabel=None, figsize=(100, 20), vlines=None,
              file=None, logscale=False)
    # draw_plot(plots_data=[results[list(results.keys())[0]]['prices']], xlabel='step', ylabel='price',
    #           title='price',
    #           file=None, hlines=None, vlines=None)


if __name__ == '__main__':
    main()

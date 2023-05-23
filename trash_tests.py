import re
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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


def parce_log_folder(folder, keys):
    logs = os.listdir(folder)
    logs = sorted([log for log in logs if '.log' in log])
    ret = dict()
    for log in logs:
        with open(os.path.join(folder, log), 'r') as f:
            data = f.read()
        ret[log.split('/')[-1].split('.')[0]] = format_data(data, keys)
    logs_count = len(logs)
    return ret, logs_count


def main():
    keys = ['prices', 'volatility', 'log_liquidity', 'linear_liquidity']
    dct, logs_count = parce_log_folder("run_results/logs", keys)
    for setup in dct.keys():
        dct[setup]['var_var'] = np.var(dct[setup]['volatility'])
        dct[setup]['mean_price'] = np.mean(dct[setup]['prices'])
        dct[setup]['mean_vol'] = np.mean(dct[setup]['volatility'])
        dct[setup]['ham_val'] = int(setup.split('_')[0])
    results = pd.DataFrame.from_dict(dct)
    results = results.T
    # hist_var_var = results.hist(column='var_var', by='ham_val', bins=50, figsize=(30, 30), range=(, 500),
    #                             legend=True, sharex=True, sharey=True)
    # plt.show()
    # hist_var_var = results.hist(column='mean_price', by='ham_val', bins=50, figsize=(30, 30), range=(-1, 500),
    #                             legend=True, sharex=True, sharey=True)
    # plt.show()
    hist_var_var = results.hist(column='mean_vol', by='ham_val', bins=50, figsize=(15, 15), range=[0, 50],
                                grid=True)
    plt.show()


if __name__ == '__main__':
    main()

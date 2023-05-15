import re
import os

import matplotlib.pyplot as plt
import numpy as np

from utils.AgentMapping import AGENT_NAMES_LIST


def parce_log_folder(folder):
    logs = os.listdir(folder)
    logs = [log for log in logs if '.log' in log]
    ret = []
    for log in logs:
        to_append = dict()
        with open(os.path.join(folder, log), 'r') as f:
            data = f.read()
        reg_config = r'\s*([^\s]*) count is (\d*)'
        to_append['configs'] = re.findall(reg_config, data)
        reg_price = r'\s*iter (\d*): price = ([\d.]*[\de+-]*)'
        prs = re.findall(reg_price, data)
        prices = []
        for x in prs:
            prices.append([int(x[0]), float(x[1])])
        to_append['prices'] = prices
        ret.append(to_append)
        print(f'\rParsed {len(ret)} logs', end='')
    print(f'\rFinish parsing, {len(ret)} logs collected')
    return ret


def add_mean_prices(results):
    for result in results:
        result['mean_price'] = sum(x[1] for x in result['prices']) / len(result['prices'])


def main():
    results = parce_log_folder(os.path.join('run_results', 'logs', 'Experiments'))
    add_mean_prices(results)
    results = [result for result in results if 1.0 <= result['mean_price'] <= 200.0]
    print(len(results))
    # figure = plt.figure(figsize=(30, 15))
    # plt.hist([result['mean_price'] for result in results], 100)
    # plt.show()
    # plt.close(figure)
    for result in results[13::361]:
        figure = plt.figure(figsize=(30, 15))
        x = [p[0] for p in result['prices']]
        y = [p[1] for p in result['prices']]
        plt.plot(x, y, 'bo-')
        plt.show()
        plt.close(figure)


if __name__ == '__main__':
    main()

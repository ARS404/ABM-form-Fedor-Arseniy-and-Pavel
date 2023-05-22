import matplotlib.pyplot as plt
import re
from utils.UtilFunctions import draw_plot
import os

os.listdir("run_results")
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

draw_plot_from_log("run_results/old_logs/0.8_3_2_8_3.log")

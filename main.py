import argparse
import copy
import json
import multiprocessing

import agentpy as ap

from Models.BaseModel import BaseModel
from utils.AgentMapping import AGENT_NAMES_LIST


def get_parameters(setup_name):
    with open('settings.json', 'r') as f:
        params = f.read()
    parameters = json.loads(params)[setup_name]
    return parameters


def run_setup(setup_name, display=False):
    parameters = get_parameters(setup_name)
    model = BaseModel(parameters=parameters)
    model.run(display=display)
    print(f"\nFinish model run with setup {setup_name}")


def run_experiment(setup_name, v_min, v_max, n_jobs, display=False):
    def prepare_samples():
        sample = copy.deepcopy(init_parameters)
        for agent in AGENT_NAMES_LIST:
            if f"{agent}_count" in init_parameters.keys():
                sample[f"{agent}_count"] = ap.IntRange(vmin=v_min, vmax=v_max)
        return ap.Sample(sample, n=(v_max - v_min + 1))

    init_parameters = get_parameters(setup_name)
    samples = prepare_samples()
    experiment = ap.Experiment(BaseModel, sample=samples, iterations=1)
    experiment.run(n_jobs=n_jobs, display=display)
    print(f"\nFinish experiment run with setup {setup_name}")


def run_diff_shock(setup_name, display=False):
    def start_proc(params):
        model = BaseModel(parameters=params)
        model.run(display=display)

    parameters1 = get_parameters(setup_name)
    parameters2 = copy.deepcopy(parameters1)
    parameters2['enable_shock'] = parameters2['enable_shock'] ^ True
    p1 = multiprocessing.Process(target=start_proc, args=(parameters1,))
    p1.start()
    p2 = multiprocessing.Process(target=start_proc, args=(parameters2,))
    p2.start()


def main():
    # TODO: make normal parser
    parser = argparse.ArgumentParser(prog='ABM form simple market')
    parser.add_argument('--setup-name', '-stp', type=str, required=True,
                        help="This is required argument. Type name if setup from setting.json, you want to run")
    parser.add_argument('--mode', '-m', choices=['run_experiment', 'run_setup', 'diff_shock'], required=True,
                        help='This is required argument. Choose run_experiment or run_setup')
    parser.add_argument('--min-val', type=int, default=1,
                        help='Use only if you are running experiment to set min_val to agents count')
    parser.add_argument('--max-val', type=int, default=10,
                        help='Use only if you are running experiment to set max_val to agents count')
    parser.add_argument('--njobs', type=int, default=-1,
                        help='use only if you are running experiment. This argument passed as "n_jobs" Experiment.run. '
                             'By default set to -1')
    parser.add_argument('--no-display', '-nd', action='store_false', default=True,
                        help='If set, pass display=False to Experiment.run() or Model.run() *MAY BE BROKEN*')

    args = parser.parse_args()
    if args.mode == 'run_setup':
        run_setup(args.setup_name, args.no_display)
    if args.mode == 'run_experiment':
        if args.min_val > args.max_val:
            print(f"Bad range: {(args.min_val, args.max_val)}")
            exit(1)
        run_experiment(args.setup_name, args.min_val, args.max_val, args.njobs, args.no_display)
    if args.mode == 'diff_shock':
        run_diff_shock(args.setup_name, args.no_display)


if __name__ == '__main__':
    main()

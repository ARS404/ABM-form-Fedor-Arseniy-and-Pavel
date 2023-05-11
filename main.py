import argparse
import copy
import itertools
import json

from copy import deepcopy

from agentpy import Experiment

from Models.BaseModel import BaseModel
from utils.AgentMapping import AGENT_FROM_STR


def prepare_configs(params):
    ret = deepcopy(params)
    for name in params['Agents']:
        ret['Agents'].pop(name)
        ret['Agents'][AGENT_FROM_STR[name]] = params['Agents'][name]
    return ret


def get_parameters(setup_name):
    with open('settings.json', 'r') as f:
        params = f.read()
    parameters = json.loads(params)[setup_name]
    parameters = prepare_configs(parameters)
    return parameters


def run_setup(setup_name, display=False):
    parameters = get_parameters(setup_name)
    model = BaseModel(parameters=parameters)
    model.run(display=display)
    print(f"Finish model.run with setup {setup_name}")


def run_experiment(setup_name, v_min, v_max, n_jobs, display=False):
    def replace_with_new_config(new_config):
        ret = copy.deepcopy(init_parameters)
        for ind, cnt in enumerate(new_config):
            ret['Agents'][AGENT_FROM_STR[used_agents[ind]]] = cnt
        return ret

    def prepare_samples():
        possible_configs = itertools.product(range(v_min, v_max + 1), repeat=len(used_agents))
        possible_parameters = list(map(replace_with_new_config, possible_configs))
        return possible_parameters

    init_parameters = get_parameters(setup_name)
    used_agents = sorted(init_parameters['Setup'].keys())
    samples = prepare_samples()
    experiment = Experiment(BaseModel, sample=samples, iterations=1)
    # TODO: try different backends
    experiment.run(n_jobs=n_jobs, display=display)


def main():
    # TODO: make normal parser
    parser = argparse.ArgumentParser(prog='ABM form simple market')
    parser.add_argument('--setup-name', '-stp', type=str, required=True,
                        help="This is required argument. Type name if setup from setting.json, you want to run")
    parser.add_argument('--mode', '-m', choices=['run_experiment', 'run_setup'], required=True,
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
        run_setup(args.setup_name, args.display)
        exit(0)
    if args.mode == 'run_experiment':
        if args.min_val > args.max_val:
            print(f"Bad range: {(args.min_val, args.max_val)}")
            exit(1)
        run_experiment(args.setup_name, args.min_val, args.max_val, args.njobs, args.no_display)


if __name__ == '__main__':
    main()

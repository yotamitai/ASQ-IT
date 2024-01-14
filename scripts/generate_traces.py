import argparse
import json
from datetime import datetime
from pathlib import Path
from os.path import join, abspath
from queries.get_agent import get_agent, get_config
from queries.common import make_clean_dirs, pickle_save


def by_interface(args):
    if args.interface == "Highway":
        params = {"config": args.config, "load_path": args.load_path,
                  "output_dir": args.output_dir}
        env, agent = get_agent(args.interface, params)
        evaluation = agent.interface.evaluation(env, agent)
        env.args = args
        env.predicate_env = HighwayKinematicEnvWithSpeed() #TODO added for speed
        traces, states = env.predicate_env.get_traces(env, agent, args.n_traces, args.verbose)
        env.close()
        evaluation.close()
    return traces, states


def generate_traces(args):
    args.output_dir = join(abspath('../queries/results'), '_'.join(
        [datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(' ', '_'), args.agent]))
    make_clean_dirs(args.output_dir)
    with Path(join(args.output_dir, 'metadata.json')).open('w') as f:
        json.dump(vars(args), f, sort_keys=True, indent=4)

    args.config = get_config(args.load_path, args.config_filename, changes=args.config_changes)
    traces, states = by_interface(args)

    for dir in [args.results_dir, args.output_dir]:
        pickle_save(traces, join(dir, f'Traces{args.data_name}.pkl'))
        pickle_save(states, join(dir, f'States{args.data_name}.pkl'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HIGHLIGHTS')
    parser.add_argument('-a', '--agent', help='agent name', type=str, default="Expert")
    parser.add_argument('-n', '--n_traces', help='number of traces to obtain', type=int,
                        default=2)
    parser.add_argument('-v', '--verbose', help='print information to the console',
                        action='store_true', default=True)
    parser.add_argument('-results', '--results_dir', help='results directory',
                        default=abspath('../results'))
    parser.add_argument('-steps', '--max_trace_steps', help='max trace steps',
                        default=200)
    args = parser.parse_args()

    "RUN"
    args.interface = "Highway"

    if args.interface == "Highway":
        from interfaces.Highway.highway_interface import highway_config, HighwayKinematicEnv, \
            HighwayKinematicEnvWithSpeed

        args.agent = 'Plain'
        lane_configs = [4]  # [2, 3, 4]
        args = highway_config(args)
        args.n_traces = 10
        args.config_changes['env']["lanes_count"] = 4
        args.config_changes['env']['vehicles_density'] = 1


    args.data_name = ""
    generate_traces(args)

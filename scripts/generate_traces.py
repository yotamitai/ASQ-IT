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
    elif args.interface == "Frogger":
        params = {"config_path": args.config_path, "config": args.config,
                  "load_path": args.load_path, "output_dir": args.output_dir,
                  "n_traces": args.n_traces, "fps": args.fps}
        env, agent = get_agent(args.interface, params)
        env.args = args
        env.predicate_env = FroggerEnv()
        traces, states = env.predicate_env.get_traces(env, agent, args.n_traces, args.verbose)
        env.close()
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
                        default=abspath('../queries/results'))
    parser.add_argument('-steps', '--max_trace_steps', help='max trace steps',
                        default=200)
    args = parser.parse_args()

    args.interface = "Highway"

    if args.interface == "Highway":
        from interfaces.Highway.highway_interface import highway_config, HighwayKinematicEnv, \
        HighwayKinematicEnvWithSpeed
        args.agent = 'Plain'
        lane_configs = [4]  # [2, 3, 4]

        args = highway_config(args)
        args.n_traces = 200
        args.config_changes['env']["lanes_count"] = 4
        args.config_changes['env']['vehicles_density'] = 1


        # """get multiple data sets"""
        # trace_multiplier = 10
        # for n_lanes in lane_configs:
        #     args.n_traces = n_lanes * trace_multiplier
        #     args.config_changes['env']["lanes_count"] = n_lanes
        #     for density in [1, 2]:
        #         args.config_changes['env']['vehicles_density'] = density
        #         args.data_name = f"_Lanes-{n_lanes}_Density-{density}_N-{args.n_traces}"
        #         print(f"Generating - {args.data_name}")
        #         generate_traces(args)


    elif args.interface == "Frogger":
        from interfaces.Frogger.frogger_interface import frogger_config, FroggerEnv
        args.agent = 'NoLeft'
        args = frogger_config(args)
        args.n_traces = 50
        #TODO deal with changes in predicate vector due to change in action spaces (No left , Yes Idle)

    "RUN"
    args.data_name = ""
    generate_traces(args)

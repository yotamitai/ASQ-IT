import argparse
import json
from datetime import datetime
from pathlib import Path
from os.path import join, abspath
from queries.get_agent import get_agent, get_config
from queries.common import make_clean_dirs, pickle_save, log_msg
from interfaces.Highway.highway_interface import HighwayKinematicEnv, HighwayInterface, \
    AP_Highway, HighwayKinematicEnvWithSpeed


def get_conditional_agent(args, config, load_path):
    interface = HighwayInterface(config, args.output_dir, load_path)
    env, agent = interface.initiate()
    evaluation = interface.evaluation(env, agent)
    agent.interface = interface
    env.seed(0)
    return env, agent, evaluation


def check_condition(condition, predicate_vector):
    """check if the predicates in the desired locations of the vector are true"""
    for idx in condition:
        if not predicate_vector[idx]: return False
    return True


def conditional_traces(args):
    """Compare two agents running online, search for disagreements"""
    ap_dict = AP_Highway
    condition = [ap_dict[predicate] for predicate in args.condition]

    """get agents and environments"""
    env1, a1, evaluation1 = get_conditional_agent(args, args.config1, args.load_path1)
    env2, a2, evaluation2 = get_conditional_agent(args, args.config2, args.load_path2)
    env1.args = env2.args = args
    # env1.predicate_env = env2.predicate_env = HighwayKinematicEnv()
    env1.predicate_env = env2.predicate_env = HighwayKinematicEnvWithSpeed() #TODO added for speed

    """Run"""
    traces, states_dict = [], {}
    for e in range(args.n_traces):
        log_msg(f'Running Episode number: {e}', args.verbose)
        trace = []
        """initial state"""
        obs, _ = env1.reset(), env2.reset()
        assert obs.tolist() == _.tolist(), f'Nonidentical environment'
        trace_length, r, done, infos = 0, 0, False, {}
        a1.previous_state = a2.previous_state = obs  # required
        state = a1.interface.get_state_from_obs(a1, obs, r, done, infos)
        params = a1.interface.get_features(env1, a1, obs, state, None)
        state_id = (e, trace_length)
        state_img = env1.render(mode='rgb_array')
        predicate_vector = env1.predicate_env.obs_to_preds(obs, state, params)
        condition_flag = check_condition(condition, predicate_vector)
        action_values = a2.interface.get_state_action_values(a2, state) if condition_flag else \
            a1.interface.get_state_action_values(a1, state)
        states_dict[state_id] = [obs, state_img, params, action_values]
        trace.append([predicate_vector, state_id])
        trace_length += 1

        # for _ in range(20):  # for testing
        while not done:
            """check which agent to follow"""
            current_agent, current_env, other_env = \
                (a1, env1, env2) if not condition_flag else (a2, env2, env1)
            a = current_agent.interface.get_next_action(current_agent, obs, state)
            obs, r, done, infos = current_env.step(a)
            _ = other_env.step(a)
            """sanity test"""
            assert obs.tolist() == _[0].tolist(), f'Nonidentical environment transition'
            """state"""
            state = current_agent.interface.get_state_from_obs(current_agent, obs, r, done, infos)
            params = current_agent.interface.get_features(
                current_env, current_agent, obs, state, a)
            action_values = current_agent.interface.get_state_action_values(current_agent, state)
            # action_values = a1.interface.get_state_action_values(a1, state)
            state_img = current_env.render(mode='rgb_array')
            state_id = (e, trace_length)
            states_dict[state_id] = [obs, state_img, params, action_values]
            predicate_vector = current_env.predicate_env.obs_to_preds(obs, state, params)
            trace.append([predicate_vector, state_id])
            if not condition_flag:
                condition_flag = check_condition(condition, predicate_vector)
                if condition_flag: log_msg(f"Condition occurred at {state_id}")
            """Add step to trace"""
            trace_length += 1

        """end of episode"""
        traces.append(trace)

    """close environments"""
    env1.close()
    env2.close()
    evaluation1.close()
    evaluation2.close()
    return traces, states_dict


def generate_conditional_traces(args):
    args.output_dir = join(abspath(args.results_dir), '_'.join(
        [datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(' ', '_'), args.agent1,
         args.agent2]))
    make_clean_dirs(args.output_dir)
    with Path(join(args.output_dir, 'metadata.json')).open('w') as f:
        json.dump(vars(args), f, sort_keys=True, indent=4)
    args.config1 = get_config(args.load_path1, args.config_filename, changes=args.config_changes)
    args.config2 = get_config(args.load_path2, args.config_filename, changes=args.config_changes)

    traces, states = conditional_traces(args)

    for dir in [args.results_dir, args.output_dir]:
        pickle_save(traces, join(dir, f'Traces{args.data_name}.pkl'))
        pickle_save(states, join(dir, f'States{args.data_name}.pkl'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HIGHLIGHTS')
    parser.add_argument('-v', '--verbose', help='print information to the console',
                        action='store_true', default=True)
    parser.add_argument('-results', '--results_dir', help='results directory',
                        default=abspath('../queries/results'))
    args = parser.parse_args()

    args.interface = "Highway"
    args.agent1 = 'SecondLane'
    args.agent2 = 'BumperCar'
    args.load_path1 = abspath(f'../agents/Trained/{args.interface}/{args.agent1}')
    args.load_path2 = abspath(f'../agents/Trained/{args.interface}/{args.agent2}')
    # args.load_path1 = abspath(f'agents/Testing/{args.agent1}')
    # args.load_path2 = abspath(f'agents/Testing/{args.agent2}')
    args.config_filename = "metadata"
    args.config_changes = {
        "env": {
            "ego_spacing": 1, "vehicles_density": 1,
            # "simulation_frequency": 15, "policy_frequency": 5,
            # "lanes_count": 4,  "duration": 150
        },
        "agent": {}
    }
    args.config1 = get_config(args.load_path1, args.config_filename, changes=args.config_changes)
    args.config2 = get_config(args.load_path2, args.config_filename, changes=args.config_changes)
    args.n_traces = 20
    args.condition = ["lane2", "above"]
    args.data_name = ""

    generate_conditional_traces(args)

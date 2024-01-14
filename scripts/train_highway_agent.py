import argparse
from json import load
from os import listdir
from os.path import join, abspath
from pathlib import Path

import gym

from interfaces.Highway.highway_interface import MyEvaluation
from rl_agents.agents.common.exploration.abstract import exploration_factory
from rl_agents.agents.common.factory import agent_factory
import agents.configs.reward_functions


def config(env_config, agent_config):
    env = gym.make(env_config["env_id"])
    env.configure(env_config)
    env.define_spaces()
    agent = agent_factory(env, agent_config)
    return env, agent


def train_agent(config_path):
    """train agent"""
    configuration = load(open(config_path))
    env_config, agent_config = configuration["env"], configuration["agent"]
    env, agent = config(env_config, agent_config)
    return env, agent


def load_agent(load_path, num_episodes):
    """load agent"""
    config_filename = [x for x in listdir(load_path) if "metadata" in x][0]
    f = open(join(load_path, config_filename))
    config_dict = load(f)
    env_config, agent_config, = config_dict['env'], config_dict['agent']
    env, agent = config(env_config, agent_config)
    agent.exploration_policy = exploration_factory({'method': 'Greedy'}, env.action_space)
    return env, agent


def test_agent(evaluation):
    evaluation.test()


def main(args):
    print(f"Training: {not bool(args.load_path)}")
    print(f"Evaluating: {bool(args.eval)}")
    env, agent = load_agent(args.load_path, args.num_episodes) if args.load_path \
        else train_agent(args.config)

    print(f"Environment: {env.config['env_id']}")
    print(f"Environment Configuration: {env.config}")
    print(f"Agent Configuration: {agent.config}")
    print(f"Logging results to: {abspath(args.output_dir)}")

    evaluation = MyEvaluation(env, agent, num_episodes=args.num_episodes,
                              display_env=args.display_env, output_dir=args.output_dir)
    if args.load_path:
        evaluation.load_agent_model(Path(join(args.load_path, 'checkpoint-final.tar')))
    else:
        evaluation.train()

    if args.eval: test_agent(evaluation)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RL Agent Comparisons')
    parser.add_argument('-load', '--load_path', help='path to pre-trained agent', default=None)
    parser.add_argument('-a_cnfg', '--agent_config', help='path to env config file', default=None)
    parser.add_argument('-e_cnfg', '--env_config', help='path to env config file', default=None)
    parser.add_argument('-n_ep', '--num_episodes',
                        help='number of episodes to run for Expert or train', default=3, type=int)
    parser.add_argument('-eval', '--eval', help='run evaluation', default=False)
    parser.add_argument('--display_env', help='display environment', default=True)
    parser.add_argument('--output_dir', help='output dir', default='../agents/Testing')
    parser.add_argument('--observation_config', help='observation type', default=None)
    args = parser.parse_args()

    args.config = "Plain"
    args.num_episodes = 2

    """train"""
    args.config = abspath(f'../agents/configs/full_configs/{args.config}.json')

    """load"""
    # args.load_path = abspath(f'../agents/Trained/Highway/{args.config}')
    # args.num_episodes = 6

    """evaluate"""
    args.eval = True

    main(args)


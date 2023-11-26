import argparse
from os.path import join, abspath
import gym
import numpy as np

from interfaces.Frogger.explorations import GreedyExploration
from interfaces.abstract_interface import AbstractInterface, AbstractPredicateEnv
from interestingness_xrl.learning.agents import QValueBasedAgent
from interestingness_xrl.learning.behavior_tracker import BehaviorTracker
from interestingness_xrl.scenarios import EnvironmentConfiguration, create_helper

ACTION_DICT = {0: 'LEFT', 1: 'RIGHT', 2: 'UP', 3: 'DOWN'}


class FroggerInterface(AbstractInterface):
    def __init__(self, config_file, config, load_path, output_dir, num_episodes, fps, seed=0):
        super().__init__(config, output_dir)
        self.config_file = config_file
        self.num_episodes = num_episodes
        self.seed = seed
        self.fps = fps
        self.load_path = load_path

    def initiate(self):
        config_file, output_dir = self.config_file, self.output_dir
        config = EnvironmentConfiguration.load_json(config_file)
        config.num_episodes = self.num_episodes
        agent_rng = np.random.RandomState(self.seed)
        helper = create_helper(config)
        config.save_json(join(output_dir, 'config.json'))
        helper.save_state_features(join(output_dir, 'state_features.csv'))
        env_id = '{}-{}-v0'.format(config.gym_env_id, 0)
        helper.register_gym_environment(env_id, False, self.fps, False)
        env = gym.make(env_id)
        video_callable = (lambda e: True)
        exploration_strategy = GreedyExploration(config.min_temp, agent_rng)
        agent = QValueBasedAgent(config.num_states, config.num_actions,
                                 action_names=config.get_action_names(),
                                 exploration_strategy=exploration_strategy)
        agent.load(self.load_path)
        behavior_tracker = BehaviorTracker(config.num_episodes)
        agent_args = {"helper": helper, "behavior_tracker": behavior_tracker,
                      "video_callable": video_callable}
        agent.agent_args = agent_args
        return env, agent

    def get_state_from_obs(self, agent, obs, reward, done, infos):
        return agent.agent_args["helper"].get_state_from_observation(obs, reward, done)

    def get_next_action(self, agent, obs, state):
        return agent.act(state)

    def get_features(self, env, agent, obs, state, action):
        position = [round(x) for x in env.env.game_state.game.frog.position]
        surroundings = agent.agent_args["helper"].get_features_from_observation(obs)
        timeout = not (env.env.game_state.game.game.steps)
        prev_action = ACTION_DICT[action] if action is not None else None
        return {"coords": position, "surroundings": surroundings,
                "timeout": timeout, "action": prev_action}

    def get_state_action_values(self, agent, state):
        return agent.q[state]

    # def update_interface(self, agent,trace_idx, step, old_obs, new_obs, r, done, a, prev_state, old_state, new_state):
    #     r = agent.agent_args['helper'].get_reward(prev_state, a, r, new_state, done)
    #     agent.update(old_state, a, r, new_state)
    #     agent.agent_args['helper'].update_stats(trace_idx, step, old_obs, new_obs, prev_state, a, r, new_state)
    #     return r


"""Atomic Propositions"""
area = ['beforeroad', 'onroad', 'onriver']
positions = []
for d in ['left', 'right', 'up', 'down']:
    for e in ['clear', 'water', 'car', 'log', 'lilypad', 'boundary']:
        positions.append(d[0] + '_' + e)
death = ['runover', 'drown', 'timeout']
# area = ['atstartalocation', 'atroadstart', 'afterroadstart',
#         'atroadend_riverstart', 'afterroadend', 'beforeriverstart',
#         'afterriverstart']
# side = ['left', 'right', 'middle']
win = ['win']
actions_occur = ['l_occurs', 'r_occurs', 'u_occurs', 'd_occurs', 'None']
predicates = area + positions + death + win + actions_occur
AP_Frogger = dict(zip(predicates, range(len(predicates))))


class FroggerEnv(AbstractPredicateEnv):
    def __init__(self):  # n_lanes
        super().__init__()
        self.execution_traces = []
        self.predicates = predicates
        self.predicate_tests = {

        }

    def obs_to_preds(self, obs, state, params):
        """
        vector:
        0-2    Area-    [before road, on road, on river]
        3-8    left-    [clear,water,car,log,lilypad,boundary]
        9-14   right-   [clear,water,car,log,lilypad,boundary]
        15-20  up-      [clear,water,car,log,lilypad,boundary]
        21-26  down-    [clear,water,car,log,lilypad,boundary]
        27-29  death    [runover, drown, timeout]
        30     win      lilypad
        31-35  action   [left,right,up,down, None]
        """
        x_coord = params["coords"][0]
        y_coord = params["coords"][1]
        surroundings = params['surroundings']
        timeout = params["timeout"]
        prev_action = params['action']
        on_road = (475 >= y_coord >= 241)
        on_river = (y_coord < 241)
        # on_grass = y_coord in [475, 241]
        before_road = (y_coord == 475)

        predicate_vector = []
        """on"""
        predicate_vector.append(1 if before_road else 0)  # on grass
        predicate_vector.append(1 if on_road else 0)  # on road
        predicate_vector.append(1 if on_river else 0)  # on log(river)
        """get type of area for each surrounding position"""
        for direction in surroundings:
            direction_vec = [0] * 6
            direction_vec[direction] = 1
            predicate_vector += direction_vec
        """death"""
        predicate_vector.append(
            1 if surroundings == [5, 5, 5, 5] and on_road else 0)  # death runover
        predicate_vector.append(
            1 if surroundings == [5, 5, 5, 5] and on_river else 0)  # death drowning
        predicate_vector.append(
            1 if surroundings == [5, 5, 5, 5] and timeout else 0)  # death timeout
        """areas"""
        # predicate_vector.append(1 if [x_coord, y_coord] == [200, 475] else 0)  # start location
        # predicate_vector.append(1 if y_coord == 475 else 0)  # At road start
        # predicate_vector.append(1 if y_coord < 475 else 0)  # After road start
        # predicate_vector.append(1 if y_coord == 241 else 0)  # At road end/River start
        # predicate_vector.append(1 if y_coord <= 241 else 0)  # After road end
        # predicate_vector.append(1 if y_coord >= 241 else 0)  # Before river start
        # predicate_vector.append(1 if y_coord < 241 else 0)  # After river start
        "screen side"
        # predicate_vector.append(1 if x_coord < 200 else 0)  # left side of screen
        # predicate_vector.append(1 if x_coord > 200 else 0)  # right side of screen
        # predicate_vector.append(1 if x_coord == 200 else 0)  # middle of screen
        """win (lilypad)"""
        predicate_vector.append(1 if state == 1036 else 0)  # win state
        """previous action"""
        for action in ACTION_DICT.values():
            predicate_vector.append(1 if action == prev_action else 0)
        predicate_vector.append(1 if not prev_action else 0)

        assert len(predicate_vector) == len(self.predicates), "predicate vector is too small"
        return predicate_vector


def frogger_ltlf_params(query_data):
    parser = argparse.ArgumentParser(description='HIGHLIGHTS')
    args, unknown = parser.parse_known_args()
    args.pause = 3
    args.predicates = predicates
    args.max_len = 20
    args.fps = 5
    args.fade_duration = 2
    args.num_trajectories = 4
    args.query_data = query_data
    args.seq_min_len = args.fps*3
    args.domain = "frogger"
    args.seq_max_len = None
    args.trace_constrains = []
    return args


def frogger_data2query(data):
    query = {}
    """turn data into states and constraints"""
    query["start"] = (
        data['start_area'],
        data['start_left'] if not data['start_left'] else "l_" + data['start_left'],
        data['start_right'] if not data['start_right'] else "r_" + data['start_right'],
        data['start_up'] if not data['start_up'] else "u_" + data['start_up'],
        data['start_down'] if not data['start_down'] else "d_" + data['start_down']
    )
    query["end"] = (
        data['end_area'], data['end_terminal'],
        data['end_left'] if not data['end_left'] else "l_" + data['end_left'],
        data['end_right'] if not data['end_right'] else "r_" + data['end_right'],
        data['end_up'] if not data['end_up'] else "u_" + data['end_up'],
        data['end_down'] if not data['end_down'] else "d_" + data['end_down'],
    )

    query['constraints'] = []
    for c in ['act_left', 'act_right', 'act_up', 'act_down']:
        if data[c] == 'occurs':
            query['constraints'].append(("occurs", c.split('_')[1][0] + '_occurs'))
        elif data[c] == 'notoccurs':
            query['constraints'].append(("notoccurs", c.split('_')[1][0] + '_occurs'))
    if data['area_constraint']:
        query['constraints'].append((data['area_constraint'], data['start_area']))
    return query


def frogger_config(args):
    """frogger configuration"""
    args.interface = "Frogger"
    args.config_filename = "config"
    args.load_path = abspath(f'../agents/Trained/{args.interface}/{args.agent}')
    """Highlight parameters"""
    args.config_changes = None
    args.config_path = join(args.load_path, args.config_filename + '.json')
    args.fps = 2
    return args


"""
obs - [steps, level, points, deaths, lives, arrived frogs *5 lilipads, 
        frog: x,y,width,height,direction pointing, 
        cars: [x,y,width,height,direction pointing] * #cars
        separator element, 
        logs: [x,y,width,height,direction pointing] * #logs
        ] 
        
state - [Left, Right, Up, Down] - values between 0-5
        0- EMPTY_IDX
        1- WATER_IDX
        2- CAR_IDX
        3-LOG_IDX
        4-LILYPAD_IDX
        5- OUT_OF_BOUNDS_IDX

DEATH_OBS_VEC = [5,5,5,5]
MAX_GRASS_Y_POS - 241
MAX_Y_POS - 475


[276, 275, 273, 274]
"""

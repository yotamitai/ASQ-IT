import argparse
from os.path import abspath, join
from highway_env.vehicle.controller import MDPVehicle
from pathlib import Path
import gym
from rl_agents.agents.common.exploration.abstract import exploration_factory
from rl_agents.agents.common.factory import agent_factory
from interfaces.abstract_interface import AbstractInterface, AbstractPredicateEnv
from rl_agents.trainer.evaluation import Evaluation
from agents import configs

# ACTION_DICT = {0: 'LANE_LEFT', 1: 'IDLE', 2: 'LANE_RIGHT', 3: 'FASTER', 4: 'SLOWER'}

class MyEvaluation(Evaluation):
    def __init__(self, env, agent, output_dir='../agents', num_episodes=1000, display_env=False):
        self.OUTPUT_FOLDER = output_dir
        super(MyEvaluation, self).__init__(env, agent, num_episodes=num_episodes,
                                           display_env=display_env)


class HighwayInterface(AbstractInterface):
    def __init__(self, config, output_dir, load_path):
        super().__init__(config, output_dir)
        self.load_path = load_path

    def initiate(self, seed=0, evaluation_reset=False):
        config, output_dir = self.config, self.output_dir
        env_config, agent_config = config['env'], config['agent']
        env = gym.make(env_config["env_id"])
        env.seed(seed)
        # env_config.update()
        env.configure(env_config)
        env.define_spaces()
        agent = agent_factory(env, agent_config)
        agent.exploration_policy = exploration_factory({'method': 'Greedy'}, env.action_space)
        if evaluation_reset:
            evaluation_reset.training = False
            evaluation_reset.close()
        return env, agent

    def evaluation(self, env, agent):
        evaluation = MyEvaluation(env, agent, display_env=False, output_dir=self.output_dir)
        agent_path = Path(join(self.load_path, 'checkpoint-final.tar'))
        evaluation.load_agent_model(agent_path)
        return evaluation

    def get_state_action_values(self, agent, state):
        return agent.get_state_action_values(state)

    def get_next_action(self, agent, obs, state):
        return agent.act(state)

    def get_state_from_obs(self, agent, obs, reward, done, infos):
        return obs

    def get_features(self, env, agent, obs, state, action):
        lane = env.controlled_vehicles[0].lane_index[2]
        crashed = env.vehicle.crashed
        Speed = env.vehicle.speed #TODO added for speed
        # q_vals = self.get_state_action_values(agent, state)
        return {"lane": lane, "crashed": crashed, "Speed": Speed}  # , "q_vals": q_vals}


positions = ['behind', 'infrontof', 'above', 'below']
lanes = ['lane1', 'lane2', 'lane3', 'lane4']
collision = ['collision']
speed = ["slow", "fast"] #TODO added for speed
# predicates = positions + lanes + collision
predicates = positions + lanes + speed + collision #TODO added for speed
AP_Highway = dict(zip(predicates, range(len(predicates))))




class HighwayKinematicEnv(AbstractPredicateEnv):
    def __init__(self):
        super().__init__()
        # self.max_speed = MDPVehicle.DEFAULT_TARGET_SPEEDS.max()
        # self.min_speed = MDPVehicle.DEFAULT_TARGET_SPEEDS.min()
        self.positions = positions
        self.lanes = lanes
        self.execution_traces = []
        self.predicates = predicates
        self.predicate_tests = {
            'behind': self.test_predicate_before,
            'infrontof': self.test_predicate_after,
            'above': self.test_predicate_above,
            'below': self.test_predicate_below,
        }
        self.threshold_same_lane = 0.05
        self.threshold_same_verticle = 0.01
        self.threshold_x_dist = 0.1

    def test_predicate_before(self, obs):
        return int(any([1 for x in obs[1:] if self.threshold_x_dist > x[1] > 0
                        and abs(x[2]) < self.threshold_same_lane]))

    def test_predicate_after(self, obs):
        return int(any([1 for x in obs[1:] if (-2 * self.threshold_x_dist) < x[1] < 0
                        and abs(x[2]) < self.threshold_same_lane]))

    def test_predicate_above(self, obs):
        return int(
            any([1 for x in obs[1:] if abs(x[1]) < self.threshold_same_verticle and x[2] > 0]))

    def test_predicate_below(self, obs):
        return int(
            any([1 for x in obs[1:] if abs(x[1]) < self.threshold_same_verticle and x[2] < 0]))

    def obs_to_preds(self, obs, state, params):
        """translate the observation (occupancy grid) to predicates for querying
        vector:
        0-3         Position-   [behind, infrontof, above, below]
        4-5/6/7     Lane-       [lane1,lane2,lane3,lane4...]
        8           Crashed-    crashed
        """
        lane, crashed = params["lane"], params["crashed"]
        predicate_vector = []  # [0] * len(self.predicates)
        for p in self.positions:
            predicate_vector.append(self.predicate_tests[p](obs))
        predicate_vector += [(1 if l == lane else 0) for l in range(len(self.lanes))]
        predicate_vector += [1] if crashed else [0]
        assert len(predicate_vector) == len(self.predicates), "predicate vector is too small"
        return tuple(predicate_vector)


class HighwayKinematicEnvWithSpeed(HighwayKinematicEnv):  #TODO added for speed
    def __init__(self):
        super().__init__()

    def obs_to_preds(self, obs, state, params):
        """translate the observation (occupancy grid) to predicates for querying
                vector:
                0-3         Position-   [behind, infrontof, above, below]
                4-5/6/7     Lane-       [lane1,lane2,lane3,lane4...]
                8-9         Speed -     [slow, fast]
                10          Crashed-    crashed
                """
        lane, crashed, speed = params["lane"], params["crashed"], params["Speed"]
        predicate_vector = []  # [0] * len(self.predicates)
        for p in self.positions:
            predicate_vector.append(self.predicate_tests[p](obs))
        predicate_vector += [(1 if l == lane else 0) for l in range(len(self.lanes))]
        """speed"""
        predicate_vector += [1] if 20<=speed<=23 else [0]
        predicate_vector += [1] if 27<=speed<=30 else [0]
        predicate_vector += [1] if crashed else [0]
        assert len(predicate_vector) == len(self.predicates), "predicate vector is too small"
        return tuple(predicate_vector)


def highway_ltlf_params(query_data):
    parser = argparse.ArgumentParser(description='HIGHLIGHTS')
    args, unknown = parser.parse_known_args()
    args.pause = 0
    args.predicates = predicates
    # args.max_len = 20
    args.fps = 7
    # args.fade_duration = 2
    args.num_trajectories = 4
    args.query_data = query_data
    args.seq_min_len = int(args.fps*2.5)
    args.seq_max_len = None
    args.domain = "highway"
    args.trace_constrains = {  # manual constraints on specific elements
        # "lane4": ["Lanes-4"],
        # "lane3": ["Lanes-4", "Lanes-3"],
        # "lane2": ["Lanes-4", "Lanes-3", "Lanes-2"]
    }
    return args


def highway_data2query(data):
    query = {}

    #removing speed
    """turn data into states and constraints"""
    query["start"] = (data['start_pos'], data['start_lane'], data['start_speed']) #TODO added for speed
    query["end"] = (data['end_pos'], data['end_lane'], data['end_speed']) #TODO added for speed

    query['constraints'] = []
    if data['constraint_s_e']:
        if data['constraint_s_e'] == "changesinto":
            query['constraints'].append((data['constraint_s_e'], data['constraint_s_e_p1'],
                                         data['constraint_s_e_p2']))
        else:
            query['constraints'].append((data['constraint_s_e'], data['constraint_s_e_p1']))

    return query


def highway_config(args):
    """highway"""
    args.config_filename = "metadata"
    """Highlight parameters"""
    args.config_changes = {"env": {"simulation_frequency": 15, "policy_frequency": 5},
                           "agent": {}}
    args.load_path = abspath(f'../agents/Trained/{args.interface}/{args.agent}')
    return args

    """get multiple data sets"""
    # for n_lanes in [2, 3, 4]:
    #     args.n_traces = n_lanes * 25
    #     args.config_changes['env']["lanes_count"] = n_lanes
    #     for density in [1, 2]:
    #         args.config_changes['env']['vehicles_density'] = density
    #         args.data_name = f"_Lanes-{n_lanes}_Density-{density}_N-{args.n_traces}"
    #         print(f"Generating - {args.data_name}")
    #         get_highlights(args)

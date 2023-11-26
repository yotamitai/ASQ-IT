import math

import numpy as np

from highway_env.envs import HighwayEnv, Action
from gym.envs.registration import register

from highway_env.utils import lmap
from highway_env.vehicle.controller import ControlledVehicle


class Plain(HighwayEnv):
    """rewarded for driving in parallel to a car"""

    def _reward(self, action: Action) -> float:
        obs = self.observation_type.observe()
        other_cars = obs[1:]
        dist_closest_car_in_lane = [x[1] for x in other_cars if x[1] > 0 and abs(x[2]) <= 0.05]
        scaled_speed = lmap(self.vehicle.speed, self.config["reward_speed_range"], [0, 1])

        # safety distance from car in same lane
        if not dist_closest_car_in_lane or dist_closest_car_in_lane[0] > 0.02:
            keeping_distance = 1
        else:
            keeping_distance = -1

        reward = \
            + self.config["keep_distance_reward"] * keeping_distance \
            + self.config["high_speed_reward"] * np.clip(scaled_speed, 0, 1) \
            + self.config["collision_reward"] * self.vehicle.crashed

        reward = -10 if not self.vehicle.on_road else reward
        return reward


register(
    id='Plain-v0',
    entry_point='agents.configs.reward_functions:Plain',
)


class FastRight(HighwayEnv):

    def _reward(self, action: Action) -> float:
        """
        The reward is defined to foster driving at high speed, on the rightmost lanes, and to avoid collisions.
        :param action: the last action performed
        :return: the corresponding reward
        """
        obs = self.observation_type.observe()
        lanes = self.road.network.all_side_lanes(self.vehicle.lane_index)
        current_lane = self.vehicle.target_lane_index[2] if \
            isinstance(self.vehicle, ControlledVehicle) else self.vehicle.lane_index[2]
        scaled_speed = lmap(self.vehicle.speed, self.config["reward_speed_range"], [0, 1])

        # safety distance from car in same lane
        if self.config['observation']['type'] == "OccupancyGrid":
            mid_grid = len(obs[0][0]) // 2
            ego_car_coords = (mid_grid, mid_grid)
            cars_y_coords, cars_x_coords = np.where(obs[0])
            other_cars = [(cars_y_coords[i], cars_x_coords[i]) for i in range(len(cars_y_coords))]
            other_cars.remove(ego_car_coords)
            dist_closest_car_in_lane = [x[1] - mid_grid for x in other_cars if
                                        x[0] == mid_grid and abs(x[1]) > mid_grid]
            min_dist = 1
        else:  # kinematics
            other_cars = obs[1:]
            dist_closest_car_in_lane = [x[1] for x in other_cars if
                                        x[1] > 0 and abs(x[2]) <= 0.05]
            min_dist = 0.01

        if not dist_closest_car_in_lane or dist_closest_car_in_lane[0] > min_dist:
            keeping_distance = 1
        else:
            keeping_distance = -1

        reward = \
            + self.config["collision_reward"] * self.vehicle.crashed \
            + self.config["right_lane_reward"] * current_lane / max(len(lanes) - 1, 1) \
            + self.config["high_speed_reward"] * np.clip(scaled_speed, 0, 1) \
            + self.config["keep_distance_reward"] * keeping_distance

        # reward_rng = [self.config["collision_reward"], self.config["right_lane_reward"]
        #               +self.config["high_speed_reward"]+self.config["keep_distance_reward"]]
        # scaled_reward = lmap(reward, reward_rng, [0, 1])
        reward = -10 if not self.vehicle.on_road else reward
        return reward


register(
    id='FastRight-v0',
    entry_point='agents.configs.reward_functions:FastRight',
)


class FastFastRight(HighwayEnv):

    def _reward(self, action: Action) -> float:
        """
        Prioritize fast and right
        """
        lanes = self.road.network.all_side_lanes(self.vehicle.lane_index)
        current_lane = self.vehicle.target_lane_index[2] if \
            isinstance(self.vehicle, ControlledVehicle) else self.vehicle.lane_index[2]
        scaled_speed = lmap(self.vehicle.speed, self.config["reward_speed_range"], [0, 1])

        reward = \
            + self.config["collision_reward"] * self.vehicle.crashed \
            + self.config["right_lane_reward"] * current_lane / max(len(lanes) - 1, 1) \
            + self.config["high_speed_reward"] * scaled_speed

        reward = -10 if not self.vehicle.on_road else reward
        return reward


register(
    id='FastFastRight-v0',
    entry_point='agents.configs.reward_functions:FastFastRight',
)


class FirstLane(HighwayEnv):

    def _reward(self, action: Action) -> float:
        """
        Prioritize second lane
        """
        current_lane = self.vehicle.target_lane_index[2] if \
            isinstance(self.vehicle, ControlledVehicle) else self.vehicle.lane_index[2]

        lane_reward = 1 if current_lane == 0 else (-1 * current_lane)

        reward = \
            + self.config["collision_reward"] * self.vehicle.crashed \
            + self.config["right_lane_reward"] * lane_reward

        reward = -10 if not self.vehicle.on_road else reward
        return reward


register(
    id='FirstLane-v0',
    entry_point='agents.configs.reward_functions:FirstLane',
)


class SecondLane(HighwayEnv):

    def _reward(self, action: Action) -> float:
        """
        Prioritize second lane
        """
        current_lane = self.vehicle.target_lane_index[2] if \
            isinstance(self.vehicle, ControlledVehicle) else self.vehicle.lane_index[2]

        lane_reward = 1 if current_lane == 1 else (-1 * abs(current_lane - 1))

        reward = \
            + self.config["collision_reward"] * self.vehicle.crashed \
            + self.config["right_lane_reward"] * lane_reward

        reward = -10 if not self.vehicle.on_road else reward
        return reward


register(
    id='SecondLane-v0',
    entry_point='agents.configs.reward_functions:SecondLane',
)


class Slow(HighwayEnv):

    def _reward(self, action: Action) -> float:
        """
        Prioritize driving slow
        """
        scaled_speed = lmap(self.vehicle.speed, self.config["reward_speed_range"], [1, 0])

        reward = \
            + self.config["collision_reward"] * self.vehicle.crashed \
            + self.config["speed_reward"] * scaled_speed

        reward = -10 if not self.vehicle.on_road else reward
        return reward


register(
    id='Slow-v0',
    entry_point='agents.configs.reward_functions:Slow',
)


class BumperCar(HighwayEnv):

    def _reward(self, action: Action) -> float:
        """
        Prioritize colliding
        """
        reward = self.config["collision_reward"] * self.vehicle.crashed if self.vehicle.crashed \
            else -1
        return reward


register(
    id='BumperCar-v0',
    entry_point='agents.configs.reward_functions:BumperCar',
)


class ParallelDriver(HighwayEnv):
    """rewarded for driving in parallel to a car"""

    def _reward(self, action: Action) -> float:
        obs = self.observation_type.observe()
        other_cars = obs[1:]
        # closest car in front that is not in same lane
        cars_x_dist = [car[1] for car in other_cars if car[1] > 0 and abs(car[2]) > 0.2]
        closest_car = lmap(cars_x_dist[0], [0, 0.3], [0, 1]) if cars_x_dist \
            else 0

        # safety distance from car in same lane
        dist_closest_car_in_lane = [x[1] for x in other_cars if x[1] > 0 and abs(x[2]) <= 0.05]
        if not dist_closest_car_in_lane or dist_closest_car_in_lane[0] > 0.01:
            keeping_distance = 0
        else:
            keeping_distance = -1

        reward = \
            + self.config["parallel_distance_reward"] * (1 - np.clip(closest_car, 0, 1)) \
            + self.config["collision_reward"] * self.vehicle.crashed \
            + self.config["keep_distance_reward"] * keeping_distance
        reward = -1 if not self.vehicle.on_road else reward
        return reward


register(
    id='ParallelDriver-v0',
    entry_point='agents.configs.reward_functions:ParallelDriver',
)


class SocialDistance(HighwayEnv):
    """rewarded for keeping as much distance from all cars"""

    def _reward(self, action: Action) -> float:
        other_cars = self.observation_type.observe()[1:]
        # distance from all cars
        dist = 0
        max_dist = len(other_cars) * math.sqrt(
            0.4 ** 2 + 0.75 ** 2)  # max in x and y coords relative to agent
        for i, car in enumerate(other_cars):
            dist += math.sqrt(abs(car[1]) ** 2 + abs(car[2]) ** 2)
        scaled_dist = lmap(dist, [0, 4 * max_dist], [0, 1])

        # safety distance from car in same lane
        dist_closest_car_in_lane = [x[1] for x in other_cars if x[1] > 0 and abs(x[2]) <= 0.05]
        if not dist_closest_car_in_lane or dist_closest_car_in_lane[0] > 0.01:
            keeping_distance = 1
        else:
            keeping_distance = -1

        reward = \
            + self.config['distance_reward'] * np.clip(scaled_dist, 0, 1) \
            + self.config['keep_distance_reward'] * keeping_distance \
            + self.config["collision_reward"] * self.vehicle.crashed
        reward = -1 if not self.vehicle.on_road else reward
        return reward


register(
    id='SocialDistance-v0',
    entry_point='agents.configs.reward_functions:SocialDistance',
)


class NoLaneChange(HighwayEnv):
    """penalized for changing lanes, otherwise rewarded for speed"""

    def _reward(self, action: Action) -> float:
        obs = self.observation_type.observe()
        other_cars = obs[1:]
        # punish for changing lanes
        lane_change = action == 0 or action == 2
        # safety distance from car in same lane
        dist_closest_car_in_lane = [x[1] for x in other_cars if x[1] > 0 and abs(x[2]) <= 0.05]
        if not dist_closest_car_in_lane or dist_closest_car_in_lane[0] > 0.01:
            keeping_distance = 1
        else:
            keeping_distance = -1

        reward = \
            + self.config["collision_reward"] * self.vehicle.crashed \
            + self.config["keep_distance_reward"] * keeping_distance \
            + self.config["lane_change_reward"] * lane_change
        reward = -1 if not self.vehicle.on_road else reward
        return reward


register(
    id='NoLaneChange-v0',
    entry_point='agents.configs.reward_functions:NoLaneChange',
)


class ClearLane(HighwayEnv):

    def _reward(self, action: Action) -> float:
        """ if no cars in your lane - max reward,
         else reward based on how close agent is to a car in it's lane"""
        obs = self.observation_type.observe()
        other_cars = obs[1:]
        dist_closest_car_in_lane = [x[1] for x in other_cars if x[1] > 0 and abs(x[2]) <= 0.05]
        closest_car = lmap(dist_closest_car_in_lane[0], [0, 0.4], [0, 1]) \
            if dist_closest_car_in_lane else 1

        # safety distance from car in same lane
        if not dist_closest_car_in_lane or dist_closest_car_in_lane[0] > 0.01:
            keeping_distance = 0
        else:
            keeping_distance = -1

        reward = \
            + self.config["distance_reward"] * (1 - np.clip(closest_car, 0, 1)) \
            + self.config["keep_distance_reward"] * keeping_distance \
            + self.config["collision_reward"] * self.vehicle.crashed
        reward = -1 if not self.vehicle.on_road else reward
        return reward


register(
    id='ClearLane-v0',
    entry_point='agents.configs.reward_functions:ClearLane',
)

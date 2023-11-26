import json
from os import listdir
from os.path import join


def get_agent(interface, params):
    """Implement here for specific agent and environment loading scheme"""

    if interface == "Frogger":
        from interfaces.Frogger.frogger_interface import FroggerInterface
        interface = FroggerInterface(params["config_path"], params["config"], params["load_path"],
                                     params["output_dir"], params["n_traces"], params["fps"])
    # elif args.interface == "gym":
    #     from queries.interfaces.gym_interface import GymInterface
    #     interface = GymInterface(args.config, args.output_dir)
    else:
        from interfaces.Highway.highway_interface import HighwayInterface
        interface = HighwayInterface(params["config"], params["output_dir"], params["load_path"])
    env, agent = interface.initiate()
    agent.interface = interface
    env.seed(0)
    return env, agent


def get_config(load_path, filename, changes=None):
    config_filename = [x for x in listdir(load_path) if filename in x][0]
    f = open(join(load_path, config_filename))
    config = json.load(f)

    if changes:
        for section in changes:
            for k, v in changes[section].items():
                config[section][k] = v

    return config

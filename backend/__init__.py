from collections import defaultdict
from os import listdir
from os.path import join, abspath
from flask import Flask
from queries.common import pickle_load
from load_agents import AGENTS
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fc1ebdc2c345372884f9d1263ac3cece'
app.config['TEMPLATES_AUTO_RELOAD'] = True

GLOBAL_VARS = {
    "vector_state_counter": 0,
    "count_queries": defaultdict(int),
    # "count_load_more": defaultdict(int),
    "traces_ds": {},
    "states_ds": {},
    "seen": defaultdict(list),
    "videos": defaultdict(list),
    "sequences": defaultdict(list),
    "unseen": defaultdict(list),
    "args": defaultdict(),
    "done": defaultdict(lambda: False),
    "static_videos": {k:[join(f"videos/{k}", x) for x in listdir(abspath(f"backend/static/videos/{k}"))]
                      for k in listdir(abspath("backend/static/videos"))},  # queries
    # "data": {
    #         "frogger": "data/Frogger/Expert",
    #         "highway": "data/Highway/Plain"
    #     },
}

import backend.routes
# import backend.routes_Both


def initial_load():
    print("LOADING TRACES - start")
    for agent in AGENTS:
        s = time.time()
        path = AGENTS[agent]
        files = listdir(path)
        traces_files = [file for file in files if file.startswith("Traces")]
        states_files = [file for file in files if file.startswith("States")]
        traces, states = {}, {}
        if agent == 'highway':
            print(f"\tFILES: {[x.replace('.pkl', '').replace('Traces_', '') for x in traces_files]}")
            traces = {k.replace(".pkl", '').replace("Traces_", ''):
                          pickle_load(join(path, k)) for k in traces_files}
            for k in states_files:
                print(k)
                states[k.replace(".pkl", '').replace("States_", '')] = pickle_load(join(path, k))
        else:
            traces["all"] = pickle_load(join(path, traces_files[0]))
            states["all"] = pickle_load(join(path, states_files[0]))

        GLOBAL_VARS["traces_ds"][agent] = traces
        GLOBAL_VARS["states_ds"][agent] = states
        print(f"LOADING TRACES - {agent} - done \tTime: {time.time() - s}")

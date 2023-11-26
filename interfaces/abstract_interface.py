from collections import defaultdict


class AbstractInterface(object):
    def __init__(self, config, output_dir):
        self.output_dir = output_dir
        self.config = config

    def initiate(self):
        return


class AbstractPredicateEnv(object):
    def __init__(self):
        self.predicates = []
        self.predicate_tests = {}
        self.execution_traces = defaultdict(list)
        self.states_dict = {}


    def obs_to_preds(self, obs, state, params):
        raise NotImplementedError("Translation from observation to domain predicates")

    def get_features(self, env, agent, obs, state, action):
        return

    def get_state_action_values(self, agent, state):
        return

    def get_state_from_obs(self, agent, obs, reward, done, infos):
        return

    def get_next_action(self, agent, obs, state):
        return

    def get_traces(self, environment, agent, n_traces, verbose):
        """Obtain traces and state dictionary"""
        for i in range(n_traces):
            self.get_single_trace(environment, agent, i)
            if verbose: print(f"\tTrace {i} {15 * '-' + '>'} Obtained")
        """save to results dir"""
        if verbose: print(f"Highlights {15 * '-' + '>'} Traces & States Generated")
        return self.execution_traces, self.states_dict

    def get_single_trace(self, env, agent, trace_idx):
        """Implement a single trace while using the Trace and State classes"""
        trace = []
        done, r, infos = False, 0, {}
        obs = env.reset()
        state = agent.interface.get_state_from_obs(agent, obs,  r, done, infos)
        params = agent.interface.get_features(env, agent, obs, state, None)
        trace_length = 0
        state_id = (trace_idx, trace_length)
        state_img = env.render(mode='rgb_array')
        action_values = agent.interface.get_state_action_values(agent, state)
        self.states_dict[state_id] = [obs, state_img, params, action_values]
        trace.append([env.predicate_env.obs_to_preds(obs, state, params), state_id])
        # self.execution_traces[self.obs_to_preds(obs[0])] += [state_id]
        trace_length += 1
        done = False
        while not done:
            a = agent.interface.get_next_action(agent, obs, state)
            obs, r, done, infos = env.step(a)
            state = agent.interface.get_state_from_obs(agent, obs, r, done, infos)
            """state"""
            params = agent.interface.get_features(env, agent, obs, state, a)
            state_img = env.render(mode='rgb_array')
            state_id = (trace_idx, trace_length)
            action_values = agent.interface.get_state_action_values(agent, state)
            self.states_dict[state_id] = [obs, state_img, params, action_values]
            trace.append([env.predicate_env.obs_to_preds(obs, state, params), state_id])
            # self.execution_traces[self.obs_to_preds(obs[0])] += [state_id]
            """Add step to trace"""
            trace_length += 1
        self.execution_traces.append(trace)
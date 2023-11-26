import random
import pandas as pd
from os.path import join

from highlights.utils import pickle_save, pickle_load
from highlights.highlights_state_selection import compute_states_importance, highlights, \
    highlights_div
from highlights.get_trajectories import states_to_trajectories, trajectories_by_importance


def get_highlights(args):
    """Load traces and state dictionary"""
    traces = pickle_load(join(args.load_dir, 'Traces.pkl'))
    states = pickle_load(join(args.load_dir, 'States.pkl'))
    if args.verbose: print(f"Highlights {15 * '-' + '>'} Traces & States Loaded")

    """Save data used for this run in output dir"""
    pickle_save(traces, join(args.output_dir, 'Traces.pkl'))
    pickle_save(states, join(args.output_dir, 'States.pkl'))

    """highlights algorithm"""
    a, b, c = states[(0, 0)][1].shape
    reshape = a * b * c
    data = {'state': list(states.keys()),
            'q_values': [x[3] for x in states.values()],
            'features': [x[1].reshape(reshape) for x in states.values()]}
    q_values_df = pd.DataFrame(data)

    """importance by state"""
    q_values_df = compute_states_importance(q_values_df, compare_to=args.state_importance)
    highlights_df = q_values_df
    state_importance_dict = dict(zip(highlights_df["state"], highlights_df["importance"]))

    """get highlights"""
    if args.importance_type == "single_state":
        """highlights importance by single state importance"""
        trace_lengths = {k: len(v) for k, v in enumerate(traces)}
        if args.highlights_div:
            """threshold for divergence based on middle state of first trace"""
            i = trace_lengths[0] // 2
            threshold = args.div_coefficient * (
                sum(states[(0, i)][1].reshape(reshape) - states[(0, i + 1)][1].reshape(reshape)))
            """get highlights"""
            summary_states = highlights_div(highlights_df, trace_lengths, args.num_trajectories,
                                            args.trajectory_length, args.minimum_gap,
                                            threshold=threshold)
        else:
            summary_states = highlights(highlights_df, trace_lengths, args.num_trajectories,
                                        args.trajectory_length, args.minimum_gap)
        all_trajectories = states_to_trajectories(summary_states, state_importance_dict)
        summary_trajectories = all_trajectories

    else:
        """highlights importance by trajectory"""
        all_trajectories, summary_trajectories = \
            trajectories_by_importance(traces, state_importance_dict, args)

    # if args.random_highlights:
    #     summary_states = random.choices(list(state_importance_dict.keys()), k=args.num_trajectories)
    #     summary_states = {k:state_importance_dict[k] for k in summary_states}
    #     all_trajectories = states_to_trajectories(summary_states, state_importance_dict)
    #     summary_trajectories = all_trajectories

    # random order
    if args.randomized: random.shuffle(summary_trajectories)
    """Save trajectories used for this run in output dir"""
    pickle_save(all_trajectories, join(args.output_dir, 'Trajectories.pkl'))

    return states, summary_trajectories

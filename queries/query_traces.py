import shutil

import logging

import time

import argparse
import collections
import json
from datetime import datetime
from os import makedirs, getpid, listdir, unlink
from os.path import join, abspath, basename
from pathlib import Path
from random import sample, randint
from backend import GLOBAL_VARS
from queries.ltlf import LTLfQuery
from queries.common import pickle_load, create_highlights_videos, save_frames, log_msg, \
    make_clean_dirs


def output_and_metadata(args):
    log_name = f'run_{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}_uid:{args.user_id}'
    args.output_dir = join(abspath('backend/static'), log_name)
    args.videos_dir = join(args.output_dir, "Conditional3")
    args.frames_dir = join(args.output_dir, 'Highlight_Frames')
    makedirs(args.output_dir)
    with Path(join(args.output_dir, 'metadata.json')).open('w') as f:
        json.dump(vars(args), f, sort_keys=True, indent=4)


def get_frames_and_state_vectors(sequences, states, traces):
    frames, state_vectors = [], {}
    for s, e, ds in sequences:
        frames.append([states[ds][(s[0], x)][1] for x in range(s[1], e[1] + 1)])
        state_vectors[ds, s, e] = [traces[ds][s[0]][x][0] for x in range(s[1], e[1] + 1)]
    return frames, state_vectors


def log_query_info(query, args):
    with Path(join(args.output_dir, 'user_query.txt')).open('w') as f:
        [f.write(f"{k}: {v}\n") for k, v in query.query.items()]

    with Path(join(args.output_dir, 'LTLf_Formula.txt')).open('w') as f:
        f.write(query.formula_str)


def log_vector_states(state_vectors, args):
    """Save state vectors of sequences"""
    i = GLOBAL_VARS['vector_state_counter']
    with Path(join(args.output_dir, f'vector_states_{str(i)}.txt')).open('w') as f:
        for k, v in state_vectors.items():
            f.write(f"{k}:\n")
            [f.write(f"\t{v}\n") for v in state_vectors[k]]
    GLOBAL_VARS['vector_state_counter'] += 1


def save_highlights(img_shape, n_videos, args):
    """Save Highlight videos"""

    height, width, layers = img_shape
    img_size = (width, height)
    create_highlights_videos(args.frames_dir, args.videos_dir, n_videos,
                            img_size, args.fps, pause=args.pause)


    """OLD:"""
    # rand_temp_id = str(randint(1000000, 9999999))
    # temp_vid_dir = join(abspath('backend/static/temp'), rand_temp_id)
    # create_highlights_videos(args.frames_dir, temp_vid_dir, n_videos,
    #                          img_size, args.fps, pause=args.pause)
    # log_msg(f"\tVIDEOS - mid, \t TIME: {time.time() - s_time},\t {args.user_id}")
    # ffmpeg_highlights_seperated(temp_vid_dir, n_videos)
    #
    # make_clean_dirs(args.videos_dir)
    # for file in listdir(temp_vid_dir):
    #     if file.endswith("reformatted.mp4") or file.endswith(".sh"):
    #         shutil.move(join(temp_vid_dir, file), join(args.videos_dir, file))
    # shutil.rmtree(temp_vid_dir)



def partition_on_index(it, indices):
    l1, l2 = [], []
    l_append = (l1.append, l2.append)
    for idx, element in enumerate(it):
        l_append[idx in indices](element)
    return l1, l2


def pick_n_sequences(n_sequences, domain):
    # pick randomly
    datasets, important_seqs, pick = [], [], []
    GLOBAL_VARS['sequences'][domain], _ = partition_on_index(GLOBAL_VARS['sequences'][domain],
                                                             GLOBAL_VARS['seen'][domain])
    sequences = GLOBAL_VARS['sequences'][domain]
    if sequences:
        pick = sample(sequences, min(n_sequences, len(sequences)))
        if len(pick) == 1:
            important_seqs = [0]
        else:
            important_seqs = [sequences.index(i) for i in pick]
        datasets = set([sequences[i][2] for i in important_seqs])
        GLOBAL_VARS['seen'][domain] = important_seqs
    GLOBAL_VARS["unseen"][domain] = len(sequences) - len(pick)
    return pick, datasets


def load_data(path, file_str, limited_set=None):
    file_dict = {}
    files = listdir(path)
    relevant_files = [file for file in files if file.startswith(file_str)]
    for i in range(len(relevant_files)):
        suffix = relevant_files[i].replace(file_str, '').replace(".pkl", '')
        if limited_set:
            if suffix in limited_set:
                file_dict[suffix] = pickle_load(join(path, relevant_files[i]))
        else:
            file_dict[suffix] = pickle_load(join(path, relevant_files[i]))
    return file_dict


def load_more_videos(args):
    s = time.time()
    log_msg(f"LOAD MORE ------------------------- START")
    agent, user_id = args.agent, args.user_id
    summary_sequences, datasets = pick_n_sequences(args.num_trajectories, user_id)
    if summary_sequences:
        [unlink(join(args.videos_dir, x)) for x in listdir(args.videos_dir)]
        GLOBAL_VARS['videos'][user_id] = []
        log_msg(f"\tUNLINK VIDEOS - done, \t TIME: {time.time() - s}, \t{user_id}")
        states_datasets = GLOBAL_VARS['states_ds'][agent]
        frames, state_vectors = get_frames_and_state_vectors(summary_sequences, states_datasets,
                                                             GLOBAL_VARS['traces_ds'][agent])
        log_msg(f"\tFRAMES - obtained, \t TIME: {time.time() - s}, \t{user_id}")
        save_frames(frames, args.frames_dir)
        log_msg(f"\tFRAMES - saved, \t TIME: {time.time() - s}, \t{user_id}")
        img_shape = frames[0][0].shape
        save_highlights(img_shape, len(summary_sequences), args)
        log_msg(f"\tVIDEOS - obtained, \t TIME: {time.time() - s}, \t{user_id}")
        base_name = args.videos_dir[args.videos_dir.index('/static/') + len("/static/"):]
        GLOBAL_VARS['videos'][user_id] = [join(base_name, x) for x in listdir(args.videos_dir) if
                                          x.endswith(".mp4")]
        log_vector_states(state_vectors, args)
    else:
        GLOBAL_VARS['videos'][user_id] = []
    log_msg(f"video retrieval completed, \t TIME: {time.time() - s}, \t{user_id}")


def get_query_highlights(args):
    s = time.time()
    log_msg(f"GET QUERY ------------------------- START")
    output_and_metadata(args)
    agent, user_id = args.agent, args.user_id
    query = LTLfQuery(args.query_data, args.seq_min_len, args.seq_max_len, args.domain, s,
                      user_id)  # , args.predicates)
    log_msg(f"\tLTLf - obtained, \t TIME: {time.time() - s} , \t{user_id}")
    GLOBAL_VARS['sequences'][user_id] = query.search_traces(GLOBAL_VARS['traces_ds'][agent],
                                                            args.trace_constrains)
    log_msg(f"\tSEARCH - complete, \t TIME: {time.time() - s} , \t{user_id}")
    if GLOBAL_VARS['sequences'][user_id]:
        summary_sequences, datasets = pick_n_sequences(args.num_trajectories, user_id)
        states_datasets = {k: GLOBAL_VARS['states_ds'][agent][k] for k in datasets}
        frames, state_vectors = get_frames_and_state_vectors(summary_sequences, states_datasets,
                                                             GLOBAL_VARS['traces_ds'][agent])
        log_msg(f"\tFRAMES - obtained, \t TIME: {time.time() - s} , \t{user_id}")
        save_frames(frames, args.frames_dir)
        log_msg(f"\tFRAMES - saved, \t TIME: {time.time() - s} , \t{user_id}")
        img_shape = frames[0][0].shape
        save_highlights(img_shape, len(summary_sequences), args)
        log_msg(f"\tVIDEOS - obtained, \t TIME: {time.time() - s} , \t{user_id}")
        base_name = args.videos_dir[args.videos_dir.index('/static/') + len("/static/"):]
        GLOBAL_VARS['videos'][user_id] = [join(base_name, x) for x in listdir(args.videos_dir) if
                                          x.endswith(".mp4")]
        log_vector_states(state_vectors, args)
        GLOBAL_VARS['count_queries'][user_id] += 1
    else:
        GLOBAL_VARS['videos'][user_id] = []
    if user_id != 'free_hand_ltlf': log_query_info(query, args)
    log_msg(f"video retrieval completed, \t TIME: {time.time() - s} , \t{user_id}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Queries')
    parser.add_argument('--load-path', help='path to existing traces', default='../data')
    parser.add_argument('--query', help='query')
    parser.add_argument('--max-len', help='max length of trajectory', default=20)
    parser.add_argument('--fps', help='summary video fps', type=int, default=3)
    parser.add_argument('--fade-duration', help='fade-in fade-out duration', type=int, default=2)
    parser.add_argument('--num-trajectories', default=5)

    args = parser.parse_args()

    """Highlight parameters"""
    # args.load_path = '../data'
    args.query = {
        "start": (0, 0, 0, 0),
        "end": (0, 0, 1, 0),
        "intermediate": None
    }

    args.pause = 3

    get_query_highlights(args)

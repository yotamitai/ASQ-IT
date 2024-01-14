from os.path import abspath

import argparse

from highlights.main import main

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HIGHLIGHTS')
    parser.add_argument('-a', '--name', help='agent name', type=str, default="Agent-0")
    parser.add_argument('--agent_path', help='path to existing agent', type=str)
    parser.add_argument('--load_dir', help='path to existing traces', type=str)
    parser.add_argument('--seed', help='path to existing traces', type=int, default=0)
    parser.add_argument('-fps', '--fps', help='summary video fps', type=int, default=1)
    parser.add_argument('-n', '--n_traces', help='number of traces to obtain', type=int,
                        default=10)
    parser.add_argument('-k', '--num_trajectories',
                        help='number of highlights trajectories to obtain', type=int, default=5)
    parser.add_argument('-l', '--trajectory_length',
                        help='length of highlights trajectories ', type=int, default=10)
    parser.add_argument('-v', '--verbose', help='print information to the console',
                        action='store_true')
    parser.add_argument('-overlapLim', '--overlay_limit', help='# overlaping', type=int,
                        default=3)
    parser.add_argument('-minGap', '--minimum_gap', help='minimum gap between trajectories',
                        type=int, default=0)
    parser.add_argument('-rand', '--randomized', help='randomize order of summary trajectories',
                        type=bool, default=True)
    parser.add_argument('-impMeth', '--importance_type',
                        help='importance by state or trajectory', default='single_state')
    parser.add_argument('-impState', '--state_importance',
                        help='method calculating state importance', default='second')
    parser.add_argument('--highlights_div',
                        help='use diversity measures', type=bool, default=False)
    parser.add_argument('--div_coefficient',
                        help='diversity coefficient', type=int, default=2)
    args = parser.parse_args()

    # RUN

    args.load_dir = abspath("../data/Highway/Plain")
    args.fps = 7
    args.trajectory_length = 14
    args.highlights_div = True
    # args.random_highlights = True
    args.num_trajectories = 40
    args.pause = 0

    main(args)

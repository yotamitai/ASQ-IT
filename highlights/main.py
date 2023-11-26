import glob

import av
import cv2
from PIL import Image
from random import randint

import json
from datetime import datetime
from os import makedirs
from os.path import join, abspath
from pathlib import Path

from highlights.get_highlights import get_highlights
from highlights.utils import make_clean_dirs


def save_videos(states, summary_trajectories, args):
    """Save Highlight videos"""
    frames_dir = join(args.output_dir, 'Highlight_Frames')
    videos_dir = join(args.output_dir, "Highlight_Videos")
    height, width, layers = list(states.values())[0][1].shape
    img_size = (width, height)
    get_trajectory_images(summary_trajectories, states, frames_dir)

    make_clean_dirs(videos_dir)
    for hl in range(args.num_trajectories):
        hl_str = str(hl) if hl > 9 else "0" + str(hl)
        img_array = []
        file_list = sorted(
            [x for x in glob.glob(frames_dir + "/*.png") if
             x.split('/')[-1].startswith(hl_str)])
        for i, f in enumerate(file_list):
            img = cv2.imread(f)
            img_array.append(img)
            if args.pause and i in [0,
                                    len(file_list) - 1]:  # adds pause to start and end of video
                [img_array.append(img) for _ in range(args.pause)]

        output = av.open(join(videos_dir, f'HL_{hl}.mp4'), 'w')
        stream = output.add_stream('h264', str(args.fps))
        stream.bit_rate = 8000000
        stream.height = img_size[1]
        stream.width = img_size[0]
        for i, img in enumerate(img_array):
            frame = av.VideoFrame.from_ndarray(img, format='bgr24')
            packet = stream.encode(frame)
            output.mux(packet)
        # flush
        packet = stream.encode(None)
        output.mux(packet)
        output.close()


def get_trajectory_images(trajectories, states_dict, path):
    make_clean_dirs(path)
    trajectory_idx = 0
    for trajectory in trajectories:
        counter = 0
        for state in trajectory.states:
            trajectory_str = str(trajectory_idx) if trajectory_idx > 9 else "0" + str(
                trajectory_idx)
            counter_str = str(counter) if counter > 9 else "0" + str(counter)
            img_name = "_".join([trajectory_str, counter_str])
            counter += 1
            save_image(path, img_name, states_dict[state][1])
        trajectory_idx += 1


def save_image(path, name, array):
    img = Image.fromarray(array)
    img.save(path + '/' + name + '.png')


def output_and_metadata(args):
    log_name = f'run_{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}_{randint(100000, 900000)}'
    args.output_dir = join(abspath('highlights/results'), log_name)
    makedirs(args.output_dir)
    with Path(join(args.output_dir, 'metadata.json')).open('w') as f:
        json.dump(vars(args), f, sort_keys=True, indent=4)


def main(args):
    output_and_metadata(args)
    states, summary_trajectories = get_highlights(args)
    save_videos(states, summary_trajectories, args)

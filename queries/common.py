import random

import av as av
import logging
import codecs
import json
import os
import glob
import pickle
from os.path import join

import cv2
import matplotlib.pyplot as plt
import imageio
import numpy as np
from PIL import Image
from skimage import img_as_ubyte


class Trace(object):
    def __init__(self):
        # self.obs = []
        # self.actions = []
        # self.rewards = []
        # self.dones = []
        # self.infos = []
        # self.reward_sum = 0
        # self.game_score = None
        self.length = 0
        self.states = []

    def update(self, obs, r, done, infos, a, state_id):
        # self.obs.append(obs)
        # self.rewards.append(r)
        # self.dones.append(done)
        # self.infos.append(infos)
        # self.actions.append(a)
        # self.reward_sum += r
        self.states.append(state_id)
        self.length += 1


class State(object):
    def __init__(self, name, obs, img):  # action_vector, feature_vector):
        self.observation = obs
        self.image = img
        # self.observed_actions = action_vector
        self.name = name
        # self.features = feature_vector

    def plot_image(self):
        plt.imshow(self.image)
        plt.show()

    def save_image(self, path, name):
        imageio.imwrite(path + '/' + name + '.png', self.image)


def pickle_load(filename):
    return pickle.load(open(filename, "rb"))


def pickle_save(obj, path):
    with open(path, "wb") as file:
        pickle.dump(obj, file)


def make_clean_dirs(path, no_clean=False, file_type=''):
    try:
        os.makedirs(path)
    except:
        if not no_clean: clean_dir(path, file_type)


def clean_dir(path, file_type=''):
    files = glob.glob(path + "/*" + file_type)
    for f in files:
        os.remove(f)


def create_video(frames_dir, output_dir, n_HLs, size, fps):
    make_clean_dirs(output_dir)
    for hl in range(n_HLs):
        hl_str = str(hl) if hl > 9 else "0" + str(hl)
        img_array = []
        file_list = sorted(
            [x for x in glob.glob(frames_dir + "/*.png") if x.split('/')[-1].startswith(hl_str)])
        for f in file_list:
            img = cv2.imread(f)
            img_array.append(img)
        out = cv2.VideoWriter(join(output_dir, f'HL_{hl}.mp4'), cv2.VideoWriter_fourcc(*'mp4v'),
                              fps, size)
        for i in range(len(img_array)):
            out.write(img_array[i])
        out.release()


def save_image(path, name, array):
    # imageio.imsave(path + '/' + name + '.png', img_as_ubyte(array))
    img = Image.fromarray(array)
    img.save(path + '/' + name + '.png')


def save_frames(trajectories, path):
    make_clean_dirs(path)
    for i, frames in enumerate(trajectories):
        for j, frame in enumerate(frames):
            vid_num = str(i) if i > 9 else "0" + str(i)
            frame_num = str(j) if j > 9 else "0" + str(j)
            img_name = f"{vid_num}_{frame_num}"
            save_image(path, img_name, frame)


def create_highlights_videos(frames_dir, video_dir, n_HLs, size, fps, pause=None):
    make_clean_dirs(video_dir)
    for hl in range(n_HLs):
        vid_rand_name = random.randint(100000000,999999999)
        hl_str = str(hl) if hl > 9 else "0" + str(hl)
        img_array = []
        file_list = sorted(
            [x for x in glob.glob(frames_dir + "/*.png") if x.split('/')[-1].startswith(hl_str)])
        for i, f in enumerate(file_list):
            img = cv2.imread(f)
            img_array.append(img)
            if pause and i in [0,len(file_list) - 1]:  # adds pause to start and end of video
                [img_array.append(img) for _ in range(pause)]

        output = av.open(join(video_dir, f'{vid_rand_name}.mp4'), 'w')
        stream = output.add_stream('h264', str(fps))
        stream.bit_rate = 8000000
        stream.height = size[1]
        stream.width = size[0]
        for i, img in enumerate(img_array):
            frame = av.VideoFrame.from_ndarray(img, format='bgr24')
            packet = stream.encode(frame)
            output.mux(packet)
        # flush
        packet = stream.encode(None)
        output.mux(packet)
        output.close()


def jasonify(np_array):
    lst = np_array.tolist()  # nested lists with same data, indices
    file_path = "/path.json"  ## your path variable
    json.dump(lst, codecs.open(file_path, 'w', encoding='utf-8'), separators=(',', ':'),
              sort_keys=True, indent=4)  ### this saves the array in .json format


def unjasonify(file_path):
    obj_text = codecs.open(file_path, 'r', encoding='utf-8').read()
    lst = json.loads(obj_text)
    return np.array(lst)


def log_msg(msg, verbose=True):
    logging.info(msg)
    if verbose: print(msg)

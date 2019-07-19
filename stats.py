from converter import mrp2conllu
from utils import read_conllu, read_mrp
import pickle
from copy import deepcopy
from tqdm import tqdm
import pandas as pd


def DM_frame_stats(mrp):
    """
    :param mrp: json mrp content
    :return: DM frame vocab
    """

    frame_dict = {}
    for i in tqdm(mrp):
        nodes = i['nodes']
        for node in nodes:
            properties = node['properties']
            if 'frame' in properties:
                frame = node['values'][properties.index('frame')]
                if frame in frame_dict:
                    frame_dict[frame] += 1
                else:
                    frame_dict[frame] = 1

    return frame_dict

def DM_frame_stats_split(mrp):
    frame_dict = DM_frame_stats(mrp)
    keys = frame_dict.keys()
    left = set(k.split(':')[0] for k in keys)
    frame_stats = {}
    for l in tqdm(left):
        frame_stats[l] = []
        for k, v in frame_dict.items():
            ll, rr = k.split(':')
            if ll == l:
                frame_stats[l].append({rr: v})

    return frame_stats

def PSD_frame_stats(mrp):
    return DM_frame_stats(mrp)

def PSD_frame_stats_split(mrp):
    frame_dict = PSD_frame_stats(mrp)
    keys = frame_dict.keys()
    left = set(k.split('-')[0] for k in keys)
    frame_stats = {}
    strange_pattern = 0
    for l in tqdm(left):
        frame_stats[l] = []
        for k, v in frame_dict.items():
            try:
                ll, rr = k.split('-')
            except ValueError:
                ll, rr = k.split('-')[0], '-'.join(k.split('-')[1:])
                strange_pattern += 1
                print(k)

            if ll == l:
                frame_stats[l].append({rr: v})

    print(strange_pattern)
    return frame_stats

if __name__ == '__main__':

    ## DM
    # with open('../mrp/2019/training/dm/wsj.mrp', 'r', encoding='utf-8') as fin:
    #     mrps = read_mrp(fin)
    #
    # frame_dict = DM_frame_stats(mrps)
    # frame_stats = DM_frame_stats_split(mrps)
    #
    # pd.DataFrame.from_dict(frame_dict, orient='index').to_csv('../processed_data/dm/dm_frame.csv')
    # pd.DataFrame.from_dict(frame_stats, orient='index').to_csv('../processed_data/dm/dm_frame_splits.csv')

    # PSD
    with open('../mrp/2019/training/psd/wsj.mrp', 'r', encoding='utf-8') as fin:
        mrps = read_mrp(fin)

    frame_dict = PSD_frame_stats(mrps)
    frame_stats = PSD_frame_stats_split(mrps)

    pd.DataFrame.from_dict(frame_dict, orient='index').to_csv('../processed_data/psd/psd_frame.csv')
    pd.DataFrame.from_dict(frame_stats, orient='index').transpose().to_csv('../processed_data/psd/psd_frame_splits.csv')
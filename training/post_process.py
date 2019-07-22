import pickle
# from ..utils import *
import json
from graph_reduction import conpanion_read
from tqdm import tqdm
import pickle

def delete_by_id(key_string, node):
    if key_string in node:
        del node[key_string]

if __name__ == '__main__':

    wsj = conpanion_read()

    with open('eds_dict.pkl', 'rb') as fin:
        eds_dict = pickle.load(fin)
    for i in tqdm(range(len(eds_dict))):
        eds_dict[i]['nodes'] = [node for node_id, node in eds_dict[i]['nodes'].items()]
        for node in eds_dict[i]['nodes']:
            # node['edges'] = '|'.join([':'.join([str(k) for k in i]) for i in node['edges']])
            delete_by_id('complex_word', node)
            delete_by_id('removed_info', node)
            delete_by_id('parents', node)
            delete_by_id('children', node)
            delete_by_id('edges', node)
            delete_by_id('align_id', node)
            delete_by_id('word', node)
            delete_by_id('complex_word', node)


    # with open('eds_small.json', 'w') as fout:
    #     json.dump(eds_dict, fout)
    with open('eds_small.pkl', 'wb') as fout:
        pickle.dump(eds_dict, fout)
    with open('eds_small.pkl', 'rb') as fin:
        eds_dict = pickle.load(fin)


    assert len(eds_dict) == len(wsj)
    for i in tqdm(range(len(eds_dict))):
        eds = eds_dict[i]
        id = eds['id']
        conllu = wsj[id]
        conllu_token_range = [c[-1][11:].split(':') for c in conllu.values()]
        conllu_token_end = [int(c[1]) for c in conllu_token_range]
        conllu_token_start = [int(c[0]) for c in conllu_token_range]

        for node in eds['nodes']:
            temp = []
            _from = node['anchors'][0]['from']
            _to = node['anchors'][0]['to']
            try:
                _from_id = conllu_token_start.index(_from) + 1
            except ValueError:
                print('WRONG FROM ANCHOR!')

            try:
                _to_id = conllu_token_end.index(_to) + 1
            except ValueError:
                print('WRONG TO ANCHOR!')

            node['anchors'] = [_from_id, _to_id]

    with open('eds_change_anchor.pkl', 'wb') as fout:
        pickle.dump(eds_dict, fout)





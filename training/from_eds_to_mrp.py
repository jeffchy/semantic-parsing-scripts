import json
import pickle
from graph_reduction import single_list, double_list, entity_list, conpanion_read
from tqdm import tqdm
import sys
sys.path.append('../')
from utils import write_mrp

def assign_single_edge_label(node_label):
    # needs some stats
    return 'BV' # temp

def assign_double_edge_label(node_label):
    # needs some stats
    return 'ARG1', 'ARG2' # temp src, temp tgt

def get_node_by_id(nodes, id):
    for node in nodes:
        if node['id'] == id:
            return node

def recover_eds_to_mrp(eds, conllu):

    # anchor preprocess
    conllu_token_range = [c[-1][11:].split(':') for c in conllu.values()]
    conllu_token_end = [int(c[1]) for c in conllu_token_range]
    conllu_token_start = [int(c[0]) for c in conllu_token_range]

    # recover nodes / edges / tops / anchors
    nodes_eds = eds['nodes']
    eds['edges'] = [{
        'source': k[0],
        'target': k[1],
        'label': v[0]
    } for k, v in eds['edges'].items()]

    # get id in serve
    node_ids = [int(node['id']) for node in nodes_eds]
    min_id = min(node_ids)
    max_id = max(node_ids)
    # a queue for unassigned ids
    id_in_serve = [i for i in range(min_id + 1, max_id) if i not in node_ids] + [i for i in range(max_id+1, max_id+100)]

    # first recover graph
    new_nodes = []
    new_edges = []
    for _node in nodes_eds:

        # single recover
        if 'attributes' in _node:
            attrs = _node['attributes']
            for attr in attrs:
                assert attr in single_list
                # pop id from queue list
                # create new list
                new_node = {}
                new_node['id'] = id_in_serve.pop(0)
                new_node['label'] = attr
                new_node['anchors'] = _node['anchors']
                new_nodes.append(new_node)
                new_edges.append({
                    'source': new_node['id'],
                    'target': _node['id'],
                    'label': assign_single_edge_label(_node['label'])
                })

    # double recover
    for _edge in eds['edges']:
        edge_label = _edge['label']
        if edge_label in double_list:

            new_node = {}
            new_node['id'] = id_in_serve.pop(0)
            new_node['label'] = edge_label
            node_src = get_node_by_id(nodes_eds, _edge['source'])
            node_tgt = get_node_by_id(nodes_eds, _edge['target'])
            if node_src['anchors'][1] <= node_tgt['anchors'][1]:
                new_node['anchors'] = [node_src['anchors'][0], node_tgt['anchors'][1]]
            else:
                new_node['anchors'] = [node_tgt['anchors'][0], node_src['anchors'][1]]
            new_nodes.append(new_node)

            label_src, label_tgt = assign_double_edge_label(edge_label)
            new_edges.append({
                'source': new_node['id'],
                'target': _edge['source'],
                'label': label_src
            })
            new_edges.append({
                'source': new_node['id'],
                'target': _edge['target'],
                'label': label_tgt
            })


    eds['nodes'] += new_nodes
    eds['edges'] += new_edges


    for _node in eds['nodes']:
        node_anchor = _node['anchors']
        anchor_dict = {
            'from': conllu_token_start[node_anchor[0]-1],
            'to': conllu_token_end[node_anchor[1]-1]
        }
        _node['anchors'] = [anchor_dict]

        if 'values' in _node:
            node_values  = _node['values']
            # recover entity list
            if node_values[0] in entity_list:
                temp = _node['label']
                _node['label'] = node_values[0]
                _node['values'] = [temp]


    mrp = eds
    return mrp


if __name__ == '__main__':

    with open('eds_change_anchor.pkl', 'rb') as fin:
        eds_all = pickle.load(fin)
    companion = conpanion_read()

    mrp_all = []
    for eds in tqdm(eds_all):
        conllu = companion[eds['id']]
        mrp_all.append(recover_eds_to_mrp(eds, conllu))

    with open('eds_recover.pkl', 'wb') as fout:
        # write_mrp(mrp_all, fout)
        pickle.dump(mrp_all, fout)


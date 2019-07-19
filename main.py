from utils import read_conllu, read_mrp, write_to_conllu
import pickle
from copy import deepcopy
from tqdm import tqdm

def check_equal(mrp_node, conllu_word, conllu_range):
    conllu_range = conllu_range[11:].split(':')
    assert len(mrp_node['anchors']) == 1
    return (mrp_node['anchors'][0]['from'] == int(conllu_range[0]) and
            mrp_node['anchors'][0]['to'] == int(conllu_range[1]))

def get_heads(node, edges):
    node_id = node['id']
    infos = []
    for e in edges:
        if e['target'] == node_id:
            infos.append([e['source'] ,e['label']])
    return infos

def get_node_by_id(nodes, id):
    for node in nodes:
        if node['id'] == id:
            return node

def get_conllu_id(conllu, node):
    for j in range(1, len(conllu)):
        conllu_id, conllu_word, conllu_range = conllu[j][0], conllu[j][1], conllu[j][-1]
        if check_equal(node, conllu_word, conllu_range):
            return int(conllu[j][0])




if __name__ == '__main__':

    # conllus = []
    # for i in range(5):
    #     with open('../mrp/2019/companion/dm/wsj0{}.conllu'.format(i), 'r', encoding='utf-8') as fin:
    #         conllus += read_conllu(fin)
    # conllus = sorted(conllus, key=lambda x: x[0])
    # pickle.dump(conllus, open('../processed_data/dm/sorted_conllu.pkl', 'wb'))

    conllus = pickle.load(open('../processed_data/dm/sorted_conllu.pkl', 'rb'))
    fout = open('../processed_data/psd/psd.conllu', 'w', encoding='utf-8')

    with open('../mrp/2019/training/psd/wsj.mrp', 'r', encoding='utf-8') as fin:
        mrps = read_mrp(fin)

    # check aligned
    for i in range(len(conllus)):
        assert conllus[i][0][1:] == mrps[i]['id']

    count_same_word = 0
    count_same_lemma = 0
    count_node = 0

    # start processing:
    for i in tqdm(range(len(conllus))):
        mrp = mrps[i]
        conllu = [k.split('\t') for k in conllus[i]]
        new_conllu = deepcopy(conllu)
        top_id = None
        top_nodes = None
        try:
            top_ids = mrp['tops']
            # print(mrp['tops'])
            # assert len(mrp['tops']) == 1
            top_nodes = [get_node_by_id(mrp['nodes'], top_id) for top_id in top_ids]
            if len(top_nodes) > 1:
                temp = top_nodes
        except KeyError:
            pass

        for j in range(1, len(conllu)):
            conllu_id, conllu_word, conllu_range, conllu_lemma = conllu[j][0], conllu[j][1], conllu[j][-1], conllu[j][2]
            mrp_edges = mrp['edges']
            frame = '_'
            pos = '_'

            for node in mrp['nodes']:
                if check_equal(node, conllu_word, conllu_range):

                    # some stats
                    if conllu_word == node['label']:
                        count_same_word += 1
                    if conllu_lemma == node['label']:
                        count_same_lemma += 1
                    count_node += 1

                    # change lemma to the node label
                    new_conllu[j][2] = node['label']

                    properties = node['properties']
                    if 'pos' in properties:
                        pos = node['values'][properties.index('pos')]
                    if 'frame' in properties:
                        frame = node['values'][properties.index('frame')]

                    infos = get_heads(node, mrp_edges)
                    heads_info = []
                    for info in infos:
                        mrp_id, edge_label = info
                        node_mrp = get_node_by_id(mrp['nodes'], mrp_id)
                        conllu_id = get_conllu_id(conllu, node_mrp)
                        # assert conllu_id == mrp_id + 1
                        heads_info.append('{}:{}'.format(conllu_id ,edge_label))

                    new_conllu[j][-2] = '|'.join(heads_info) if heads_info else '_'
                    break


            if top_nodes != None:
                for top_node in top_nodes:
                    if check_equal(top_node, conllu_word, conllu_range):
                        if new_conllu[j][-2] == '_':
                            new_conllu[j][-2] = '0:root'
                        else:
                            new_conllu[j][-2] = '0:root|'+ new_conllu[j][-2]


            new_conllu[j][5] = frame


        write_to_conllu(new_conllu, fout)


    print('all_nodes: {}, all node label same as word: {}, all node label same as lemma: {}'.format(count_node, count_same_word, count_same_lemma))
    fout.close()
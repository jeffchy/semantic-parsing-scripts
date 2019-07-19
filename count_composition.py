from utils import *
import pickle

def count_composition(mrps):
    composition_word = {}
    for mrp in mrps:
        for node in mrp['nodes']:
            node_lab = node['label']
            if '+' in node_lab:
                # print(node_lab)
                if node_lab in composition_word:
                    composition_word[node_lab] += 1
                else:
                    composition_word[node_lab] = 1

    return composition_word

def correct_mrp_by_composition(mrps, compositions):
    def composition_in_mrp(mrp, composition):
        input_str = mrp['input']
        comp_list = composition.split('+')
        comp_str = ' '.join(comp_list)
        if comp_str in input_str:
            return True, (input_str.index(comp_str), input_str.index(comp_str) + len(comp_str))
        elif comp_str.capitalize() in input_str:
            return True, (input_str.index(comp_str.capitalize()), input_str.index(comp_str.capitalize()) + len(comp_str))
        return False, None

    def generalize_composition(composition):
        comp_list = composition.split('+')
        comp_cap_list = [i.capitalize() for i in comp_list]
        return comp_list + comp_cap_list

    def in_range(node, range):
        if node['anchors'][0]['from'] >= range[0] and node['anchors'][0]['to'] <= range[1]:
            return True
        return False

    for mrp in mrps:
        for composition, count in compositions.items():
            flag, range = composition_in_mrp(mrp, composition)
            if flag:
                for node in mrp['nodes']:
                    if node['label'] in generalize_composition(composition) and in_range(node, range):
                        node['label'] = composition
    return mrps



if __name__ == '__main__':
    with open('../mrp/2019/training/dm/wsj.mrp', 'r', encoding='utf-8') as fin:
        mrps = read_mrp(fin)
    # res_dict = count_composition(mrps)
    # with open('../processed_data/dm/composition_dict.pkl', 'wb') as fout:
    #     pickle.dump(res_dict, fout)
    with open('../processed_data/dm/composition_dict.pkl', 'rb') as fin:
        res_dict = pickle.load(fin)
    with open('../processed_data/dm/dev.en.dm.conllu.sdp.mrp', 'r', encoding='utf-8') as fin:
        mrps_parse = read_mrp(fin)

    new_mrps = correct_mrp_by_composition(mrps_parse, res_dict)

    with open('../processed_data/dm/dev.en.dm.conllu.sdp.composition_correction.mrp', 'w', encoding='utf-8') as fout:
        write_mrp(new_mrps, fout)
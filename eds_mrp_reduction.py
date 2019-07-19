from utils import *

#'_am_x', '_pm_x' also have 'carg', but they can be found in the text, do not modify these nodes is good
entity_list=set(['numbered_hour', 'named_n', 'excl', 'year_range', 'timezone_p', 'named', 'card', 'mofy', 'yofc', 'ord', 'meas_np', 'season', 'holiday', 'fraction', 'dofw', 'dofm', 'polite'])
resdict=[]
#single_list=json.load(open('single_list.json','r'))
write_dict=[]

replace_list=set(['pron', 'pronoun_q', 'poss', 'much-many_a', 'little-few_a', 'free_relative_q', 'comp_so', 'eventuality', 'with_p', 'comp_enough', 'temp_loc_x', 'comp_too', 'recip_pro', 'every_q', 'unspec_manner', 'manner', 'abstr_deg', 'temp', 'refl_mod', 'free_relative_ever_q', 'comp_not+so', 'unspec_adj', 'property', 'prpstn_to_prop'])

# single_list is for implicit nodes for only one child
single_list=set(['proper_q','udef_q','def_explicit_q','def_implicit_q','nominalization','part_of','superl','idiom_q_i','neg','relative_mod', 'which_q', 'ellipsis_ref', 'not_x_deg','unknown','number_q'])

# double_list is for implicit nodes for two children
double_list=set(['measure','compound','loc_nonsp','of_p','appos','times','implicit_conj','subord', 'discourse', 'parenthetical', 'cop_id', 'id','addressee','num_seq','comp_equal', 'comp_less','comp','plus'])

non_list=set(['time_n','place_n','person','reason','thing','ellipsis','elliptical_n','ellipsis_expl','interval','v_event','generic_entity'])

#check_list=set(['comp_equal', 'id', 'interval_p_end', 'interval_p_start', 'addressee', 'num_seq'])
check_list=set(['time_n','place_n'])
#check_list=set(['time_n', 'generic_entity', 'place_n', 'person', 'reason', 'thing'])

#check_list=set(['interval_p_start','interval_p_end','interval','elliptical_n'])

#determined_remove_list=set([])

removed_list=set(['cop_id', 'recip_pro', 'ellipsis', 'ellipsis_expl', 'addressee', 'refl_mod', 'fw_seq', 'generic_verb', 'free_relative_ever_q', 'not_x_deg', 'num_seq', 'v_event', 'comp_not+so', 'unspec_adj', 'property', 'prpstn_to_prop'])

labels_list=set(['proper_q', 'compound', 'named', 'measure', 'udef_q', 'card', 'loc_nonsp',
'mofy', 'def_explicit_q', 'of_p', 'def_implicit_q', 'dofm', 'appos',
'nominalization', 'pron', 'pronoun_q', 'time_n', 'comp', 'poss', 'yofc',
'generic_entity', 'year_range', 'times', 'implicit_conj', 'unknown', 'much-many_a', 'part_of', 'subord', 'superl', 'idiom_q_i', 'named_n', 'little-few_a',
'neg', 'free_relative_q', 'place_n', 'dofw', 'relative_mod', 'numbered_hour',
'number_q', 'season', 'ord', 'comp_so', 'comp_equal', 'person', 'which_q',
'comp_less', 'plus', 'fraction', 'ellipsis_ref', 'reason', 'id', 'thing',
'eventuality', 'with_p', 'comp_enough', 'temp_loc_x', 'excl', 'discourse',
'comp_too', 'parenthetical', 'cop_id', 'recip_pro', 'ellipsis', 'every_q',
'interval_p_end', 'interval_p_start', 'elliptical_n', 'interval',
'unspec_manner', 'manner', 'ellipsis_expl', 'abstr_deg', 'temp', 'addressee',
'refl_mod', 'fw_seq', 'generic_verb', 'free_relative_ever_q', 'holiday',
'timezone_p', 'not_x_deg', 'polite', 'num_seq', 'meas_np', 'v_event',
'comp_not+so', 'unspec_adj', 'property', 'prpstn_to_prop'])

#remained_labels=set({'ellipsis', 'thing', 'v_event', 'time_n', 'elliptical_n', 'reason', 'place_n', 'person', 'ellipsis_expl'})
remained_labels=set(['time_n', 'generic_entity', 'place_n', 'person', 'reason', 'thing'])
#index_list={'ARG0':0,'ARG2':1,'ARG3':2,'ARG1':3,'L-HNDL':4,'L-INDEX':5,'R-INDEX':6,'R-HNDL':7}
index_list=['ARG0', 'ARG2', 'others', 'ARG3', 'ARG1', 'L-HNDL', 'L-INDEX', 'R-INDEX', 'R-HNDL']
index_list={x:i for i,x in enumerate(index_list)}

protected_symbols=set(['%', '2', '8', '1', '–', '7', 'F', '5', '9', '6', 'B', '3', 'l', '4', 'D', 'H', 'E', 'Z', 'L', '0', 'U']+\
	['a', 'A', '&', 'I', ':', 'X', 'b', 'G', '…', 'N', 'W', 'c', 'C', 'K', 'e', 'f', 'z', 'd', 'r', 'x', 'J', 'i', 'M', 'S', '?'])

def reduce_single(mrp):
    pass

def reduce_double(mrp):
    pass

def check_anchor_single(node, mrp):
    pass

def check_anchor_double(node, mrp):
    pass

def find_parent(node, edges):
    """
    :param node:
    :param edges:
    :return node :
    """

def recude(mrps):
    for mrp in mrps:
        id = mrp['id']
        input = mrp['input']
        tops = mrp['tops']
        nodes = mrp['nodes']
        edges = mrp['edges']





if __name__ == '__main__':
    with open('../mrp/2019/training/eds/wsj.mrp', 'r', encoding='utf-8') as fin:
        eds_mrp = read_mrp(fin)
    with open('../processed_data/amr/amr_sample.json', 'r', encoding='utf-8') as fin:
        sample_json = read_mrp(fin)
    c = eds_mrp
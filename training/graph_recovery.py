
import math
import numpy as np
import json
import bisect
from string import punctuation
import collections
import pdb
import jsonlines
from copy import deepcopy
# import Levenshtein


#'_am_x', '_pm_x' also have 'carg', but they can be found in the text, do not modify these nodes is good
entity_list=set(['numbered_hour', 'named_n', 'excl', 'year_range', 'timezone_p', 'named', 'card', 'mofy', 'yofc', 'ord', 'meas_np', 'season', 'holiday', 'fraction', 'dofw', 'dofm', 'polite'])
resdict=[]
#single_list=json.load(open('single_list.json','r'))
write_dict=[]
writer=jsonlines.open('eds_wsj.mrp','w')
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


def conpanion_read(filename='wsj.conllu',anchor_based=True):
	wsj={}
	with open(filename, 'r', encoding='utf-8') as reader:
		for current_line in reader:
			current_line=current_line.strip()
			if current_line:
				if current_line.startswith('#'):
					lineid=current_line[1:]
					wsj[lineid]={}
				else:
					data=current_line.split('\t')
					if anchor_based:
						anchor_pos=data[-1].split('=')[-1].split(':')
						wsj[lineid][anchor_pos[0]]=data
						# if lineid=='20446029':
						# 	pdb.set_trace()
					else:
						wsj[lineid][data[0]]=data
	#pdb.set_trace()
	return wsj

def create_node(data,wsj_data):
	node={}
	node['id']=int(data[0])
	node['label']=data[5]
	node['attributes']=data[9].split('|') if data[9]!='_' else []
	# parents_head_id, edge_label
	node['parents']=[(int(x.split(':')[0]),x.split(':')[1]) for x in data[8].split('|')] if data[8]!='_' else []
	node['children']=[]
	anchor = anchor_prediction(data,wsj_data)
	node['anchors'] = {'from':anchor[0],'to':anchor[1]}
	attribute = check_properties(node['attributes'])
	if attribute:
		node['properties']=['carg']
		# node['values']=['attributes']
		# node values will always be the corresponding word
		node['values'] = data[1]

		while attribute in node['attributes']:
			node['attributes'].remove(attribute)

		node['label'] = attribute

	return node

def check_properties(attributes):
	for attribute in attributes:
		if attribute in entity_list:
			return attribute
	return False

def anchor_prediction(data,wsj_data):
	anchors=wsj_data[9].strip('TokenRange=').split(':')
	return anchors

def edge_recovery(data,wsj_data,edges,special_edge_collection=[]):
	heads=[(int(x.split(':')[0]),x.split(':')[1]) for x in data[8].split('|')] if data[8]!='_' else []
	current_id=int(data[0])
	for head in heads:
		if head[0]==0:
			continue
		if head[1] in labels_list:
			special_edge_collection.append((head[0],current_id,head[1]))
		edges[(head[0],current_id)]=head[1]
	return

def create_node_single(
		id=None, label=None, attributes=[], parents=[], children=[], anchors=[]
):
	return {
		'id': int(id),
		'label': label,
		'attribites': attributes,
		'parents': parents,
		'children': children,
		'anchors': anchors,
	}


def graph_recovery_type1(nodes):
	max_id = max(list(nodes.keys()))
	new_nodes = deepcopy(nodes)
	# type 1, proper_q, udef_q
	for node_id, node in nodes.items():
		attribites = node['attributes']
		for attr in attribites:
			if attr in single_list:
				max_id += 1
				# add new node to new_nodes
				new_nodes[max_id] = create_node_single(
					id = max_id,
					label = attr,
					anchors = node['anchors'],
					children = [(node['id'], 'BV')]
				)
				# add another parent to the original node
				new_nodes[node_id]['parents'].append((max_id, 'BV'))
				# remove used single label attributes
				new_nodes[node_id]['attributes'].remove(attr)

	return new_nodes

def graph_recovery_type2(nodes):
	max_id = max(list(nodes.keys()))
	new_nodes = deepcopy(nodes)
	# type 2, measure
	for node_id, node in nodes.items():
		parents = node['parents']
		for par in parents:
			label = par[1]
			if label in double_list:
				max_id += 1
				head = par[0]
				dep = node_id

				new_nodes[max_id] = create_node_single(
					id = max_id,
					label = label,
					anchors = node['anchors'], # TODO: need change
					children = [(head, 'ARG2'), (dep, 'ARG1')]
				)

				# add another parent to the original node
				new_nodes[node_id]['parents'].append((max_id, 'ARG1'))
				new_nodes[head]['parents'].append((max_id, 'ARG2'))

				# remove used single label attributes
				new_nodes[node_id]['parents'].remove((head, label))

	return new_nodes


def extract_edge_from_graph(nodes):
	edges = []
	for node_id, node in nodes.items():
		par = node['parents']
		if par:
			for p in par:
				head, label = p
				dep = node_id

				edges.append((head, label, dep))

	return edges

def from_conllu_to_jsonlines(target_file,wsj):
	for sentence_id in target_file:
		sentence={}
		nodes={}
		edges={}
		tops=[]
		sentence['id']=sentence_id
		wsj_val=wsj[sentence['id']]
		current_data=target_file[sentence_id]
		for lineid in current_data:
			data=current_data[lineid]
			# this kind of nodes will not appear in mrp
			if data[5]=='_' and data[8]=='_' and data[9]=='_':
				continue
			# pdb.set_trace()
			nodes[int(lineid)]=create_node(data,wsj_val[lineid])
			# node=nodes[int(lineid)]

		for node_id, node in nodes.items():
			if (0,'root') in node['parents']:
				tops.append(node['id'])
				node['parents'].remove((0,'root'))

		nodes = graph_recovery_type1(nodes)
		nodes = graph_recovery_type2(nodes)
		edges = extract_edge_from_graph(nodes)


		# recovery part
		# if len(node['parents'])>0:
		# 	edge_recovery(data,wsj_val[lineid],edges)

			




		sentence['edges']=nodes
		sentence['nodes']=edges
		sentence['tops']=tops


if __name__ == '__main__':

	wsj=conpanion_read(anchor_based=False)
	target=conpanion_read(filename='mrp_eds.conllu',anchor_based=False)
	from_conllu_to_jsonlines(target,wsj)

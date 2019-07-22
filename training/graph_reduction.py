import math
import numpy as np
import json
import bisect
from string import punctuation
import collections
import pdb
import jsonlines
# import Levenshtein
import pickle

def range_check(p_label, p_from, p_to, curr, children, not_covered, checked):
	if curr['id'] in checked:
		return
	else:
		checked.append(curr['id'])
	if curr['anchors'][0]['from'] < p_from or curr['anchors'][0]['to'] > p_to:
		not_covered.append(p_label)
		return
	for child in children[curr['id']]:
		range_check(p_label, p_from, p_to, child, children, not_covered, checked)
	return

alldicts=[]
with open('eds/wsj.mrp', encoding='utf-8') as f:
	for line in f:
		alldicts.append(json.loads(line))
		# break

def type_switch(node_type):
	if node_type=='implicit':
		return 'explicit'
	else:
		return 'implicit'

def entity_reduction(node):
	assert 'properties' in node, 'current node has no properties!'
	label=node['label']
	value=node['values'][0]
	node['label']=value
	node['values']=[label]
	node['type']=type_switch(node['type'])
	return node

def assign_type(node, type):
	node['type']=type
	return node

def preprocess_nodes(sentence,counter={}):
	parents,children,parents_ids,children_ids=collect_edges_info(sentence)
	nodes=sentence['nodes']
	newnode={}
	for idx, node in enumerate(nodes):
		assert len(parents_ids)==len(nodes), 'not equal!'
		assert len(children_ids)==len(nodes), 'not equal!'
		if node['label'][0]=='_':
			nodes[idx]=assign_type(node,'explicit')
		else:
			nodes[idx]=assign_type(node,'implicit')
			if 'count' not in counter:
				counter['count']=0
			if node['label'] not in counter:
				counter[node['label']]=0
			counter[node['label']]+=1
			counter['count']+=1
		if node['label'] in entity_list:
			nodes[idx]=entity_reduction(node)
		nodes[idx]['parents']=parents_ids[idx]
		nodes[idx]['children']=children_ids[idx]
		newnode[idx]=nodes[idx]
	return newnode

def collect_edges_info(sentence):
	nodes=sentence['nodes']
	ids = [node['id'] for node in nodes]
	parents = [[] for i in range(0, len(ids))]
	children = [[] for i in range(0,len(ids))]
	parents_ids = [[] for i in range(0, len(ids))]
	children_ids = [[] for i in range(0,len(ids))]
	for edge in sentence['edges']:
		if edge['source'] in ids:
			tar = sentence['nodes'][edge['target']]
			children[edge['source']].append(tar['label'])
			children_ids[edge['source']].append(tar['id'])
		if edge['target'] in ids:
			src = sentence['nodes'][edge['source']]
			parents[edge['target']].append(src['label'])
			parents_ids[edge['target']].append(src['id'])
	return parents,children,parents_ids,children_ids

def conpanion_read(filename='wsj.conllu',anchor_based=True):
	wsj={}
	with open('wsj.conllu', 'r', encoding='utf-8') as reader:
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
	#pdb.set_trace()
	return wsj

def assign_wsj_node(node,wsj_node):
	node['word']=wsj_node[1]
	# align_id is the id in companion data
	node['align_id']=wsj_node[0]



def wsj_align(node,wsj_val,collect={},lev_dict={},simple_mode=True):
	node_anchor=str(node['anchors'][0]['from'])
	#node_anchor_end=str(node['anchors'][0]['to'])
	word_span=node['anchors'][0]['to']-node['anchors'][0]['from']
	current_span=9999
	anchor_list=list(wsj_val.keys())[list(wsj_val.keys()).index(node_anchor):]
	if simple_mode:
		# for the anchor span is only larger than two, but the from span is the punct label, we just choose the next label for the node label
		assigned=False
		for wordidx, node_anchor in enumerate(anchor_list):
			if int(node_anchor)>node['anchors'][0]['to']:
				break
			current_word=wsj_val[node_anchor][1]

			# detect symbols like ", ', (, {
			if len(current_word)==1 and current_word not in protected_symbols:
				continue
			else:
				label=node['label']
				if '+' in label:
					node['complex_word']=True
				else:
					node['complex_word']=False
				assign_wsj_node(node,wsj_val[node_anchor])
				assigned=True
				break
		if not assigned:
			if wsj_val[str(node['anchors'][0]['from'])][1] not in collect:
				collect[wsj_val[str(node['anchors'][0]['from'])][1]]=set()	
			collect[wsj_val[str(node['anchors'][0]['from'])][1]].add(node['label'])
			assign_wsj_node(node,wsj_val[node_anchor])
			#pdb.set_trace()
			# if word_span-len(wsj_val[node_anchor][1])>1:
			# 	if wsj_val[node_anchor][1] not in collect:
			# 		collect[wsj_val[node_anchor][1]]={}
			# 		collect[wsj_val[node_anchor][1]]['count']=0
			# 		collect[wsj_val[node_anchor][1]]['next_node']=[]
			# 	collect[wsj_val[node_anchor][1]]['count']+=1
			# 	#pdb.set_trace()
			# 	try:
			# 		next_anchor=list(wsj_val.keys())[list(wsj_val.keys()).index(node_anchor)+1]
			# 		#collect[wsj_val[node_anchor][1]]['next_node'].append(wsj_val[next_anchor][1])
			# 		if len(wsj_val[next_anchor][1])==1:
			# 			pdb.set_trace()
			# 		collect[wsj_val[node_anchor][1]]['next_node'].append(node['label'])
			# 	except:
			# 		#pdb.set_trace()
			# 		print(wsj_val[node_anchor][1])
			# if word_span-len(wsj_val[node_anchor][1])==1:
			# 	if wsj_val[node_anchor][1] not in collect:
			# 		collect[wsj_val[node_anchor][1]]={}
			# 		collect[wsj_val[node_anchor][1]]['count']=0
			# 		collect[wsj_val[node_anchor][1]]['next_node']=set()
			# 	collect[wsj_val[node_anchor][1]]['count']+=1
			# 	#pdb.set_trace()
			# 	try:
			# 		next_anchor=list(wsj_val.keys())[list(wsj_val.keys()).index(node_anchor)+1]
			# 		#collect[wsj_val[node_anchor][1]]['next_node'].append(wsj_val[next_anchor][1])
			# 		collect[wsj_val[node_anchor][1]]['next_node'].add(node['label'])
			# 	except:
			# 		#pdb.set_trace()
			# 		print(wsj_val[node_anchor][1])

	else:
		for wordidx, node_anchor in enumerate(anchor_list):
			if int(node_anchor)>node['anchors'][0]['to']:
				break
			# for complex word, we choose longest one, and avoid PUNCT words
			if abs(word_span-len(wsj_val[node_anchor][1]))<current_span:
				if abs(node['anchors'][0]['to']-node['anchors'][0]['from']-len(wsj_val[node_anchor][1]))>0:
					#pdb.set_trace()
					pass
				current_span=abs(word_span-len(wsj_val[node_anchor][1]))
				# if 'properties' not in node:
				# 	label=node['label'].split('_')[1]
				# else:
				# 	label=node['label']
				label=node['label']
				if '+' in label:
					node['complex_word']=True
				else:
					node['complex_word']=False
				assign_wsj_node(node,wsj_val[node_anchor])
	# some collections
	# if '+' in label:
	# 	if label.lower() not in collect:
	# 		collect[label.lower()]=1
	# 	else:
	# 		collect[label.lower()]+=1
	# elif Levenshtein.distance(node['word'].lower(),label.lower())>1:
	# 	if node['word'] in lev_dict:
	# 		lev_dict[node['word']].add(label)
	# 	else:
	# 		lev_dict[node['word']]=set()
	# 		lev_dict[node['word']].add(label)
	#return node

def explict_alignment(sentence,wsj,collect={},lev_dict={}):
	nodes=sentence['nodes']
	wsj_val=wsj[sentence['id']]
	for idx in nodes:
		node=nodes[idx]
		if node['type']=='explicit':
			#pdb.set_trace()
			wsj_align(node,wsj_val,collect,lev_dict,simple_mode=True)
	#pdb.set_trace()
	return nodes

def count_correspond_words(sentence,wsj,rel_dict={}):
	nodes=sentence['nodes']
	wsj_val=wsj[sentence['id']]
	for idx in nodes:
		node=nodes[idx]
		if node['type']=='implicit' and node['label'] not in entity_list:
			#pdb.set_trace()
			anchor=node['anchors'][0]['from']
			word=wsj_val[str(anchor)][1]
			if 'total_count' not in rel_dict:
				rel_dict['total_count']=0
			if node['label'] not in rel_dict:
				rel_dict[node['label']]={}
				rel_dict[node['label']]['count']=0
			if word.lower() not in rel_dict[node['label']]:
				rel_dict[node['label']][word.lower()]=0	
			rel_dict[node['label']][word.lower()]+=1
			rel_dict[node['label']]['count']+=1
			rel_dict['total_count']+=1


def count_implicit_anchors(sentence,rel_dict={}):
	nodes=sentence['nodes']
	anchor_dict={}
	# first find anchors in explicit nodes
	for idx in nodes:
		node=nodes[idx]
		if node['type']=='explicit':
			#pdb.set_trace()
			anchor=node['anchors'][0]['from']
			# first, we see whether explicit nodes have coupled
			#anchor=node['anchors'][0]['to']
			if anchor not in anchor_dict:
				anchor_dict[anchor]=[]
			else:
				pass
			anchor_dict[anchor].append(node)
	# then check the anchors of implicit nodes have coincidence with explicit nodes anchors
	for idx in nodes:
		node=nodes[idx]
		if node['type']=='implicit':
			anchor=node['anchors'][0]['from']
			if node['label'] not in rel_dict:
				rel_dict[node['label']]={}
				rel_dict[node['label']]['total']=0
				rel_dict[node['label']]['success']=0
			if anchor not in anchor_dict:
				rel_dict[node['label']]['success']+=1
			rel_dict[node['label']]['total']+=1

def node_change(sentence):
	pass

def remove_edge(nodes,edge_tupl,edge_dict):
	assert 0,'not implemented'

def edge_change(sentence,labels={}):
	edge_dict={}
	edges=sentence['edges']
	nodes=sentence['nodes']
	for edge in edges:
		edge_tupl=(edge['source'],edge['target'])
		if edge_tupl in edge_dict:
			if nodes[edge_tupl[0]]['label']=='compound':
				#fix misaligned nodes 
				for idx in nodes:
					node=nodes[idx]
					if node['anchors']==nodes[edge_tupl[0]]['anchors'] and node['type']=='explicit':
						nodes[edge_tupl[0]]['children'][0]=node['id']
						nodes[edge_tupl[1]]['parents'].remove(edge_tupl[0])
						node['parents'].append(edge_tupl[0])
						break
				#pdb.set_trace()
				nodes[edge_tupl[0]]['anchors'][0]['from']=min(nodes[edge_tupl[1]]['anchors'][0]['from'],node['anchors'][0]['from'])
				nodes[edge_tupl[0]]['anchors'][0]['to']=max(nodes[edge_tupl[1]]['anchors'][0]['to'],node['anchors'][0]['to'])
				edge_tupl=(edge_tupl[0],node['id'])
				# while edge_tupl[0] in nodes[edge_tupl[1]]['parents']:
				# 	nodes[edge_tupl[1]]['parents'].remove(edge_tupl[0])
				# del edge_dict[edge_tupl]
				# del nodes[edge_tupl[0]]
				if edge_tupl in edge_dict:
					pdb.set_trace()
				else:
					edge_dict[edge_tupl]=[]
				edge_dict[edge_tupl].append(edge['label'])
				#sentence['nodes'].remove(sentence['nodes'][edge_tupl[0]])
			else:
				edge_dict[edge_tupl].append(edge['label'])
		else:
			edge_dict[edge_tupl]=[]
			edge_dict[edge_tupl].append(edge['label'])
	return edge_dict

#def reduce(,parent_node):

def count_explicit_parents(sentence,rel_dict={}):
	#we need to count how many implicit parents are directly connecting to the explicit nodes, how many are not, and the relationships between parents and grand parents of explicit words

	nodes=sentence['nodes']
	for idx in nodes:
		node=nodes[idx]
		if node['type']=='explicit':
			for parent in node['parents']:
				if nodes[parent]['type']=='explicit':
					continue
				#pdb.set_trace()
				impl_node=nodes[parent]
				if impl_node['label'] not in rel_dict:
					rel_dict[impl_node['label']]={}
					rel_dict[impl_node['label']]['val_count']=0
				rel_dict[impl_node['label']]['val_count']+=1

				#count grand parent appearence
				for grandparent in impl_node['parents']:
					#pdb.set_trace()
					if nodes[grandparent]['type']=='explicit':
						continue
					gp_node=nodes[grandparent]
					if gp_node['label'] not in rel_dict[impl_node['label']]:
						rel_dict[impl_node['label']][gp_node['label']]=0
					rel_dict[impl_node['label']][gp_node['label']]+=1

def count_children(sentence,rel_dict={}):
	#we need to count how many implicit parents are directly connecting to the explicit nodes, how many are not, and the relationships between parents and grand parents of explicit words

	nodes=sentence['nodes']
	edges=sentence['edges']
	for idx in nodes:
		node=nodes[idx]
		if node['type']=='implicit':
			if node['label'] not in rel_dict:
				rel_dict[node['label']]={}
				rel_dict[node['label']]['val_count']=0
				rel_dict[node['label']]['explicit']=0
				rel_dict[node['label']]['implicit']=0
				rel_dict[node['label']]['children_len']=[]
				rel_dict[node['label']]['children_edge_label']={}
				rel_dict[node['label']]['children']={}
			rel_dict[node['label']]['val_count']+=1
			rel_dict[node['label']]['children_len'].append(len(set(node['children'])))
			#pdb.set_trace()
			try:
				for child in node['children']:
					if nodes[child]['type']=='explicit':
						rel_dict[node['label']]['explicit']+=1
					else:
						rel_dict[node['label']]['implicit']+=1
						if nodes[child]['label'] not in rel_dict[node['label']]['children']:
							rel_dict[node['label']]['children'][nodes[child]['label']]=0
						rel_dict[node['label']]['children'][nodes[child]['label']]+=1

					edgelabels=edges[(idx,child)]
					for edgelabel in edgelabels:
						if edgelabel not in rel_dict[node['label']]['children_edge_label']:
							rel_dict[node['label']]['children_edge_label'][edgelabel]=0
						rel_dict[node['label']]['children_edge_label'][edgelabel]+=1
			except:
				pdb.set_trace()


def count_parents(sentence,rel_dict={}):
	#we need to count how many implicit parents are directly connecting to the explicit nodes, how many are not, and the relationships between parents and grand parents of explicit words

	nodes=sentence['nodes']
	edges=sentence['edges']
	for idx in nodes:
		node=nodes[idx]
		if node['type']=='implicit':
			if node['label'] not in rel_dict:
				rel_dict[node['label']]={}
				rel_dict[node['label']]['val_count']=0
				rel_dict[node['label']]['explicit']=0
				rel_dict[node['label']]['implicit']=0
				rel_dict[node['label']]['parents_len']=[]
				rel_dict[node['label']]['parents_edge_label']={}
				rel_dict[node['label']]['parents']={}
			rel_dict[node['label']]['val_count']+=1
			rel_dict[node['label']]['parents_len'].append(len(set(node['parents'])))
			#pdb.set_trace()
			for parent in node['parents']:
				if nodes[parent]['type']=='explicit':
					rel_dict[node['label']]['explicit']+=1
				else:
					rel_dict[node['label']]['implicit']+=1
					if nodes[parent]['label'] not in rel_dict[node['label']]['parents']:
						rel_dict[node['label']]['parents'][nodes[parent]['label']]=0
					rel_dict[node['label']]['parents'][nodes[parent]['label']]+=1

				edgelabels=edges[(parent,idx)]
				for edgelabel in edgelabels:
					if edgelabel not in rel_dict[node['label']]['parents_edge_label']:
						rel_dict[node['label']]['parents_edge_label'][edgelabel]=0
					rel_dict[node['label']]['parents_edge_label'][edgelabel]+=1

def add_extra_edge(node1,node2,label,edges):
	source=node1['id']
	target=node2['id']
	if (source,target) not in edges:
		edges[(source,target)]=[]
	edges[(source,target)]+=[label]
	node1['children'].append(target)
	node2['parents'].append(source)

def create_wsj_end_anchor_dict(wsj_val):
	wsj_end_dict={}
	for index,idx in enumerate(wsj_val):
		val=wsj_val[idx]
		wsj_end_dict[int(val[-1].split(':')[-1])]=val[-1].split('=')[-1].split(':')[0]
	return wsj_end_dict

def create_new_node(label,nodes,wsj_node):
	new_id=len(nodes)+10
	if new_id in nodes:
		assert 0, 'wrong node id!'
	newnode={}
	newnode['id']=new_id
	newnode['label']=label
	anchors=wsj_node[-1].split('=')[-1].split(':')
	newnode['anchors']=[{'from':int(anchors[0]),'to':int(anchors[-1])}]
	newnode['type']='explicit'
	newnode['parents']=[]
	newnode['children']=[]
	assign_wsj_node(newnode,wsj_node)
	#nodes[new_id]=newnode
	return newnode

def single_align(node,nodes,edges,wsj_val):
	anchor=node['anchors'][0]['from']
	anchor_end=node['anchors'][0]['to']
	wsj_align(node,wsj_val)
	node=assign_type(node,'explicit')
	# if the word length is longer than the anchor_node, set it to be an edge
	if abs(len(node['word'])-(anchor_end-anchor))>1:
		for idx in node['children']:
			#child=nodes[idx]
			edges[node['id'],idx]=[node['label']]
	else:
		# otherwise set is as an attribute
		if 'attributes' not in node:
			node['attributes']=[]
		node['attributes'].append(node['label'])	
	node['label']='nonnode'
	nodes[node['id']]=node

def single_implicit_reduction(sentence,wsj,stats_single=collections.Counter()):

	# target: reduce all explicit target nodes' implicit parents with single child into the explicit node for special properties
	nodes=sentence['nodes']
	anchor_dict={}
	anchor_dict_end={}
	edges=sentence['edges']
	wsj_val=wsj[sentence['id']]
	orig=sentence.copy()
	# then check the anchors of implicit nodes have coincidence with explicit nodes anchors
	wsj_end_dict=create_wsj_end_anchor_dict(wsj_val)

	for idx in nodes:
		node=nodes[idx]
		if node['type']=='explicit':
			anchor=node['anchors'][0]['from']
			anchor_end=node['anchors'][0]['to']
			if anchor_end not in anchor_dict_end:
				anchor_dict_end[anchor_end]=[]
			if anchor not in anchor_dict:
				anchor_dict[anchor]=[]
			else:
				#pdb.set_trace()
				pass
			anchor_dict[anchor].append(idx)
			anchor_dict_end[anchor_end].append(idx)
	to_del=[]
	to_add=[]
	# if sentence['id']=='20009001':
	# 	pdb.set_trace()
	for idx in nodes:
		node=nodes[idx]
		if node['label'] in single_list:
			anchor=node['anchors'][0]['from']
			anchor_end=node['anchors'][0]['to']
			# if sentence['id']=='20250023' and node['id']==2:
			# 		pdb.set_trace()
			if anchor in anchor_dict:
				# 	pdb.set_trace()
				target_node=nodes[anchor_dict[anchor][0]]
				anchor_equal=(node['anchors'][0]['from'],node['anchors'][0]['to'])==(target_node['anchors'][0]['from'],target_node['anchors'][0]['to'])
				#if node and target node have the same anchor, we set the node to be an attribute of target node, other wise we set is as an edge bettween target node and children of node
				if (anchor_equal and len(node['children'])==1 and node['children'][0]==target_node['id'] and len(node['parents'])==0 and node['id'] not in sentence['tops']):
					set_edge_label=False
					temp = edges[(node['id'], target_node['id'])][0]
					stats_single[(node['label'], temp)] += 1

					newnode = combine_nodes([target_node, node], nodes, edges, set_edge_label=set_edge_label)


					to_add.append(newnode)
					to_del.append(idx)
			# else:
			# 	single_align(node,nodes,edges,wsj_val)
	for idx in to_del:
		del nodes[idx]
	for newnode in to_add:
		nodes[newnode['id']]=newnode

def break_connection(parent,child,edges):
	while parent['id'] in child['parents']:
		child['parents'].remove(parent['id'])
	while child['id'] in parent['children']:
		parent['children'].remove(child['id'])
	del edges[(parent['id'],child['id'])]

def gen_connection(parent,child,label,edges):
	parent['children'].append(child['id'])
	child['parents'].append(parent['id'])
	if (parent['id'],child['id']) not in edges:
		edges[(parent['id'],child['id'])]=[]
	edges[(parent['id'],child['id'])]+=label

def join_two_nodes(node1_id,node2_id,decomp_node_id,nodes,edges,reverse=False):
	if reverse:
		edge1=edges[node1_id,decomp_node_id][0]
		edge2=edges[node2_id,decomp_node_id][0]	
	else:
		edge1=edges[decomp_node_id,node1_id][0]
		edge2=edges[decomp_node_id,node2_id][0]
	if edge1 not in index_list:
		edge1='others'
	if edge2 not in index_list:
		edge2='others'
	edge_index1=index_list[edge1]
	edge_index2=index_list[edge2]
	decomp_node=nodes[decomp_node_id]
	# head have smaller idx
	if edge_index1<edge_index2:
		headid=node1_id
		depid=node2_id
	elif edge_index2<edge_index1:
		headid=node2_id
		depid=node1_id
	else:
		# set left node to be head
		if nodes[node1_id]['anchors'][0]['from']<nodes[node2_id]['anchors'][0]['from']:
			headid=node1_id
			depid=node2_id
		else:
			headid=node2_id
			depid=node1_id
	headnode=nodes[headid]
	depnode=nodes[depid]

	# if repeated edge, cancel
	if (headnode['id'], depnode['id']) in edges:
		return

	#pdb.set_trace()
	if not reverse:
		if len(decomp_node['parents'])>0:
			parlist=set(decomp_node['parents'].copy())
			for parent in parlist:
				try:
					label=edges[parent,decomp_node_id]
				except:
					# pdb.set_trace()
					pass
				if parent not in headnode['parents']:
					#pdb.set_trace()
					gen_connection(nodes[parent],headnode,label,edges)
				break_connection(nodes[parent],decomp_node,edges)
	else:
		if len(decomp_node['children'])>0:
			childlist=set(decomp_node['children'].copy())
			for child in childlist:
				break_connection(decomp_node,nodes[child],edges)

	if (headid,depid) not in edges:
		edges[(headid,depid)]=[]
	edges[(headid,depid)]+=[decomp_node['label']]
	#try: 
	if reverse:
		break_connection(depnode,decomp_node,edges)
		break_connection(headnode,decomp_node,edges)	
	else:
		break_connection(decomp_node,depnode,edges)
		break_connection(decomp_node,headnode,edges)
	if depid not in headnode['children']:
		headnode['children'].append(depid)
	if headid not in depnode['parents']:
		depnode['parents'].append(headid)
	# except:

def remove_node(node,nodes,edges):
	for idx in node['children']:
		child=nodes[idx]
		while node['id'] in child['parents']:
			child['parents'].remove(node['id'])
		if (node['id'],child['id']) in edges:
			del edges[(node['id'],child['id'])]
	for idx in node['parents']:
		parent=nodes[idx]
		while node['id'] in parent['children']:
			parent['children'].remove(node['id'])
		if (parent['id'],node['id']) in edges:
			del edges[(parent['id'],node['id'])]

def double_implicit_reduction(sentence,wsj,stats_double):
	# target: reduce all explicit target nodes' implicit parents with two children into an edge with label of node label
	nodes=sentence['nodes']
	anchor_dict={}
	anchor_dict_end={}
	edges=sentence['edges']
	wsj_val=wsj[sentence['id']]

	anchor_dict,anchor_dict_end=anchor_dict_generation(nodes)
	to_del=[]
	for idx in nodes:
		node=nodes[idx]
		# if there are two children, then just join these two nodes, and the anchor is determined by each label,
		# if there is only one children, then set it into the anchored node, and set the edge label to the node label
		# if there are over two children, find two highest priority edges in the node
		if node['label'] in double_list and node['type']=='implicit':
			# if sentence['id']=='20109040' and node['label']=='implicit_conj':
			# 	pdb.set_trace()

			children=node['children']

			if len(children)==2:
				if children[0]==children[1]:
					#pdb.set_trace()
					remove_node(node,nodes,edges)
					to_del.append(idx)

				else:
					anchor_ch_0 = nodes[children[0]]['anchors'][0]
					anchor_ch_1 = nodes[children[1]]['anchors'][0]
					anchor_self = node['anchors'][0]
					# check anchor valid
					if (((anchor_ch_0['to'] + 1 == anchor_ch_1['from']) and (anchor_ch_0['from'] == anchor_self['from']) and  (anchor_ch_1['to'] == anchor_self['to'])) or \
							((anchor_ch_0['from'] == anchor_ch_1['to'] + 1) and (anchor_ch_1['from'] == anchor_self['from']) and  (anchor_ch_0['to'] == anchor_self['to']) )) and \
							node['id'] not in sentence['tops']:
						temp0 = edges[(node['id'], children[0])][0]
						temp1 = edges[(node['id'], children[1])][0]
						stats_double[(node['label'], temp0, temp1)] += 1
						join_two_nodes(children[0],children[1],node['id'],nodes,edges)
						to_del.append(idx)

	for idx in to_del:
		del nodes[idx]

def remove_redundant_node(node,nodes,edges):
	parents=node['parents'].copy()
	children=node['children'].copy()
	for parent in parents:
		break_connection(nodes[parent],node,edges)
	for child in children:
		break_connection(node,nodes[child],edges)

def remove_few_implicits(sentence):
	nodes=sentence['nodes']
	edges=sentence['edges']
	to_del=[]
	for idx in nodes:
		node=nodes[idx]
		#pdb.set_trace()
		if node['label'] in removed_list and node['type']=='implicit':
			remove_redundant_node(node,nodes,edges)
			to_del.append(idx)
	for val in to_del:
		del nodes[val]

def align_top_nodes(sentence,wsj):
	nodes=sentence['nodes']
	wsj_val=wsj[sentence['id']]
	new_top=[]
	for top in sentence['tops']:
		if nodes[top]['type']=='explicit':
			align_id=nodes[top]['align_id']
			align_word=nodes[top]['word']
		else:
			nodecopy=nodes[top].copy()
			wsj_align(nodecopy,wsj_val)
			align_id=nodecopy['align_id']
			align_word=nodecopy['word']
		new_top.append({'word':align_word,'align_id':align_id})
	#pdb.set_trace()
	sentence['tops']=new_top

def no_child_implicit_reduction(sentence,wsj):
	# target: reduce all explicit target nodes' implicit children with no child into the explicit node for special properties
	pdb.set_trace()

def other_reduction(sentence,wsj):
	# process for other special cases
	pdb.set_trace()

def combine_two_nodes(node1,node2):
	#combine informations of two nodes
	node1['parents']=node1['parents']+node2['parents']
	node1['children']=node1['children']+node2['children']
	return node1

def update_edge_connection(target_id,nodeid,nodes,edges,set_edge_label=False,reverse=False):
	# here we want to combine node into target, so the connection between these two nodes should be removed, the parent and children should be merged in these two nodes
	node=nodes[nodeid]
	target=nodes[target_id]
	if reverse:
		parent_sent='children'
		children_sent='parents'	
	else:
		parent_sent='parents'
		children_sent='children'
	#pdb.set_trace()
	if 'attributes' not in target:
		target['attributes']=[]
	if 'removed_info' not in target:
		target['removed_info']=[]
		
	removed_info={}
	removed_info['node']=node
	removed_info['edges']=[]
	#removed_info['edges'].append({(nodeid,target_id):edges[(nodeid,target_id)]})
	#del edges[(nodeid,target_id)]
	if target['id'] in target[parent_sent]:
		while target['id'] in target[parent_sent]:
			target[parent_sent].remove(target['id'])

	if target['id'] in target[children_sent]:
		while target['id'] in target[children_sent]:
			target[children_sent].remove(target['id'])

	if node['id'] in target[parent_sent]:
		# use while loop to avoid repeat edges
		while node['id'] in target[parent_sent]:
			# if node is target's parent
			target[parent_sent].remove(node['id'])
		if reverse:
			removed_info['edges'].append({(target_id,nodeid):edges[(target_id,nodeid)]})
			del edges[(target_id,nodeid)]
		else:
			removed_info['edges'].append({(nodeid,target_id):edges[(nodeid,target_id)]})
			del edges[(nodeid,target_id)]

	if node['id'] in target[children_sent]:
		# use while loop to avoid repeat edges
		while node['id'] in target[children_sent]:
			# if node is target's child
			target[children_sent].remove(node['id'])
		if reverse:
			removed_info['edges'].append({(nodeid,target_id):edges[(nodeid,target_id)]})
			del edges[(nodeid,target_id)]
		else:
			removed_info['edges'].append({(target_id,nodeid):edges[(target_id,nodeid)]})
			del edges[(target_id,nodeid)]
		
	
	for idx in node[parent_sent]:
		#pdb.set_trace()
		if idx==target_id:
			continue
		parent=nodes[idx]
		# remove parent's child
		parent[children_sent].remove(nodeid)
		# add new child
		parent[children_sent].append(target_id)
		# remove child's parent
		
		# add new parent
		target[parent_sent].append(idx)
		# set new edge
		if reverse:
			edge_tupl=(target_id,parent['id'])
			edge_tupl2=(nodeid,parent['id'])
		else:
			edge_tupl=(parent['id'],target_id)
			edge_tupl2=(parent['id'],nodeid)
		if edge_tupl not in edges:
			edges[edge_tupl]=[]
		else:
			pass
			#pdb.set_trace()
			

		if edge_tupl2 in edges:
			edges[edge_tupl]+=edges[edge_tupl2]
			#remove old edge
			removed_info['edges'].append({edge_tupl2:edges[edge_tupl2]})
			del edges[edge_tupl2]

	for idx in node[children_sent]:
		if idx==target_id:
			continue
		#pdb.set_trace()
		child=nodes[idx]
		# remove parent's child
		child[parent_sent].remove(nodeid)
		# add new child
		child[parent_sent].append(target_id)
		# remove child's parent
		
		# add new parent
		target[children_sent].append(idx)
		# set new edge
		if reverse:
			edge_tupl=(child['id'],target_id)
			edge_tupl2=(child['id'],nodeid)
		else:
			edge_tupl=(target_id,child['id'])
			edge_tupl2=(nodeid,child['id'])
		if edge_tupl not in edges:
			edges[edge_tupl]=[]
		else:
			pass
			#pdb.set_trace()	
		try:
			if set_edge_label:
				edges[edge_tupl]+=[node['label']]
			else:
				edges[edge_tupl]+=edges[edge_tupl2]
		except:
			# pdb.set_trace()
			pass
		#remove old edge
		removed_info['edges'].append({edge_tupl2:edges[edge_tupl2]})
		del edges[edge_tupl2]
	target['removed_info'].append(removed_info)
	if not set_edge_label:
		target['attributes'].append(nodes[nodeid]['label'])
	#return nodeid

def combine_nodes(anchor_nodes,nodes,edges,set_edge_label=False,reverse=False):
	newnode=anchor_nodes[0]
	if len(anchor_nodes)==1:
		return anchor_nodes[0]
	if len(anchor_nodes)>3:
		assert 0, 'not implemented!'
	for idx in range(1,len(anchor_nodes)):
		update_edge_connection(newnode['id'],anchor_nodes[idx]['id'],nodes,edges,set_edge_label=set_edge_label,reverse=reverse)
	return newnode


def replacable_implicit_anchor_reduction(sentence,wsj):
	#for replacable implicits, we only reduce these node into their anchors, and remove the edges between the node and it's anchor node
	nodes=sentence['nodes']
	anchor_dict={}
	edges=sentence['edges']
	wsj_val=wsj[sentence['id']]
	# then check the anchors of implicit nodes have coincidence with explicit nodes anchors
	for idx in nodes:
		node=nodes[idx]
		if node['label'] in replace_list:
			anchor=node['anchors'][0]['from']
			if anchor not in anchor_dict:
				anchor_dict[anchor]=[]
			anchor_dict[anchor].append(node)
	# if sentence['id']=='20004004':
	# 	pdb.set_trace()
	for anchor in anchor_dict:
		# only 1,2,3
		if len(anchor_dict[anchor])>=4:
			pdb.set_trace()
		new_node=combine_nodes(anchor_dict[anchor],nodes,edges)
		new_node=new_node.copy()
		for anchor_node in anchor_dict[anchor]:
			del nodes[anchor_node['id']]
		wsj_align(new_node,wsj_val)
		new_node=assign_type(new_node, 'explicit')
		nodes[new_node['id']]=new_node

		#wsj_check()
		#...
		#del_nodes...
		#del_edges...
		#


def complex_word_breaking(sentence,wsj):
	pass

def check_implicit_anchor_conincide(sentence,rel_dict={},replace_list=None):
	nodes=sentence['nodes']
	anchor_dict={}
	edges=sentence['edges']
	# then check the anchors of implicit nodes have coincidence with explicit nodes anchors
	for idx in nodes:
		node=nodes[idx]
		if node['label'] in replace_list:
			anchor=node['anchors'][0]['from']
			if node['label'] not in rel_dict:
				rel_dict[node['label']]={}
				rel_dict[node['label']]['total']=0
				rel_dict[node['label']]['success']=0
				rel_dict[node['label']]['coincidence']={}
				rel_dict[node['label']]['edge_coincidence']={}
			if anchor not in anchor_dict:
				anchor_dict[anchor]=[]
				#rel_dict[node['label']]['success']+=1
			# else:
			# 	#pdb.set_trace()
			# 	for val in anchor_dict[anchor]:
			# 		rel_dict[val['label']]['success']-=1
			rel_dict[node['label']]['total']+=1
			anchor_dict[anchor].append(node)
	for anchor in anchor_dict:
		if len(anchor_dict[anchor])==1:
			rel_dict[anchor_dict[anchor][0]['label']]['success']+=1
		else:
			for node1 in anchor_dict[anchor]:
				for node2 in anchor_dict[anchor]:
					if node1['label']==node2['label']:
						continue
					if 'anchor_check' not in rel_dict:
						rel_dict['anchor_check']={}
						rel_dict['anchor_check']['success']=0
						rel_dict['anchor_check']['total']=0
						rel_dict['anchor_check']['failed_list']={}
					if node1['anchors'][0]['to']==node2['anchors'][0]['to'] and node1['anchors'][0]['to']==node2['anchors'][0]['to']:
						rel_dict['anchor_check']['success']+=1
					else:
						if (node1['label'],node2['label']) not in rel_dict['anchor_check']['failed_list']:
							rel_dict['anchor_check']['failed_list'][(node1['label'],node2['label'])]=0
						rel_dict['anchor_check']['failed_list'][(node1['label'],node2['label'])]+=1
					rel_dict['anchor_check']['total']+=1
					
					if node2['label'] not in rel_dict[node1['label']]['coincidence']:
						rel_dict[node1['label']]['coincidence'][node2['label']]=0
						rel_dict[node1['label']]['edge_coincidence'][node2['label']]={}
						rel_dict[node1['label']]['edge_coincidence'][node2['label']]['count']=0
						rel_dict[node1['label']]['edge_coincidence'][node2['label']]['edges']={}
					# if node1['label'] not in rel_dict[node2['label']]['coincidence']:
					# 	rel_dict[node2['label']]['coincidence'][node1['label']]=0
					rel_dict[node1['label']]['coincidence'][node2['label']]+=1
					#rel_dict[node2['label']]['coincidence'][node1['label']]+=1
					#rel_dict[node1['label']]['coincidence'][node2['label']]={}
					set1=set(node1['parents'])&set(node2['parents'])
					set2=set(node1['children'])&set(node2['children'])
					if len(set1)!=0 or len(set2)!=0:
						#pdb.set_trace()
						rel_dict[node1['label']]['edge_coincidence'][node2['label']]['count']+=len(set1)+len(set2)

						for idx in set1:
							node=nodes[idx]
							# count which label have conincidence with another (which label both node1 and node2 pointing to/from)
							if node['label'] not in rel_dict[node1['label']]['edge_coincidence'][node2['label']]:
								rel_dict[node1['label']]['edge_coincidence'][node2['label']][node['label']]=0
							rel_dict[node1['label']]['edge_coincidence'][node2['label']][node['label']]+=1
							# count the conincidenced label groups
							edge_label1=edges[(node['id'],node1['id'])]
							edge_label2=edges[(node['id'],node2['id'])]
							if len(edge_label1)>1 or len(edge_label2)>1:
								#pdb.set_trace()
								pass
							edge_tupl=str((edge_label1[0],edge_label2[0]))
							if edge_tupl not in rel_dict[node1['label']]['edge_coincidence'][node2['label']]['edges']:
								rel_dict[node1['label']]['edge_coincidence'][node2['label']]['edges'][edge_tupl]=0
							rel_dict[node1['label']]['edge_coincidence'][node2['label']]['edges'][edge_tupl]+=1

						for idx in set2:
							node=nodes[idx]
							if node['label'] not in rel_dict[node1['label']]['edge_coincidence'][node2['label']]:
								rel_dict[node1['label']]['edge_coincidence'][node2['label']][node['label']]=0
							rel_dict[node1['label']]['edge_coincidence'][node2['label']][node['label']]+=1
							# count the conincidenced label groups
							edge_label1=edges[(node1['id'],node['id'])]
							edge_label2=edges[(node2['id'],node['id'])]
							if len(edge_label1)>1 or len(edge_label2)>1:
								#pdb.set_trace()
								pass
							edge_tupl=str((edge_label1[0],edge_label2[0]))
							if edge_tupl not in rel_dict[node1['label']]['edge_coincidence'][node2['label']]['edges']:
								rel_dict[node1['label']]['edge_coincidence'][node2['label']]['edges'][edge_tupl]=0
							rel_dict[node1['label']]['edge_coincidence'][node2['label']]['edges'][edge_tupl]+=1
						#rel_dict[node1['label']]['edge_coincidence'][node2['label']]=rel_dict[node1['label']]['edge_coincidence'][node2['label']]


def POS_implicit_rel(sentence,wsj, rel_dict={}):
	# count the relationships between POS tagging and parent implicit node labels
	nodes=sentence['nodes']
	wsj_val=wsj[sentence['id']]
	wsj_ids=list(wsj_val.keys())
	for node in nodes:
		if node['type']=='explicit':
			current_xpos=wsj_val[wsj_ids[int(node['align_id'])-1]][4]
			#pdb.set_trace()
			for parent in node['parents']:
				if nodes[parent]['type']=='explicit':
					continue
				if current_xpos not in rel_dict:
					rel_dict[current_xpos]={}
					rel_dict[current_xpos]['val_counts']=0
				if nodes[parent]['label'] not in rel_dict[current_xpos]:
					rel_dict[current_xpos][nodes[parent]['label']]=0	
				rel_dict[current_xpos][nodes[parent]['label']]+=1
				rel_dict[current_xpos]['val_counts']+=1
	#pdb.set_trace()
	return nodes

def special_case_check(sentence,collect={}):

	nodes=sentence['nodes']
	anchor_dict={}
	wsj_val=wsj[sentence['id']]
	edges=sentence['edges']
	special_label_count={'interval':0,'interval_p_start':0,'interval_p_end':0,'elliptical_n':0}
	intervalnodes=[]
	start_nodes=[]
	end_nodes=[]
	elliptical_nodes=[]
	interval_type=[]
	for idx in nodes:
		node=nodes[idx]
		if node['label'] in special_label_count:
			special_label_count[node['label']]+=1
		if node['label']=='interval':
			intervalnodes.append(node['id'])
			it_type=1
			for parent in node['parents']:
				if nodes[parent]['label'] in ['interval_p_start','interval_p_end']:
					for child in nodes[parent]['children']:
						if nodes[child]['label']=='elliptical_n':
							it_type=2
			interval_type.append(it_type)
		if node['label']=='interval_p_start':
			start_nodes.append(node['id'])
		if node['label']=='interval_p_end':
			end_nodes.append(node['id'])
		if node['label']=='elliptical_n':
			elliptical_nodes.append(node['id'])
		if node['type']=='explicit' :
			anchor=node['anchors'][0]['from']
			if anchor not in anchor_dict:
				anchor_dict[anchor]=[]
			anchor_dict[anchor].append(node['id'])
	reduce_node=[]
	for index,idx in enumerate(intervalnodes):
		interval=nodes[idx]
		anchor=interval['anchors'][0]['from']
		if anchor in anchor_dict:
			target_id=anchor_dict[anchor][0]
			if len(anchor_dict[anchor])>0:
				#pdb.set_trace()
				pass
		else:
			wsj_align(interval,wsj_val)
			assign_type(interval,'explicit')
			target_id=interval['id']
		if interval_type[index]==1:
			start=None
			end=None
			udef_q=None
			for parent_id in interval['parents']:
				if parent_id in start_nodes:
					start=parent_id
				if parent_id in end_nodes:
					end=parent_id
				if nodes[parent_id]['label']=='udef_q':
					udef_q=parent_id
			#pdb.set_trace()
			if start==None or end==None:
				remove_node(nodes[idx],nodes,edges)
				remove_node(nodes[udef_q],nodes,edges)
				del nodes[udef_q]
				del nodes[idx]
				continue
			#try:
			break_connection(nodes[start],nodes[idx],edges)
			break_connection(nodes[end],nodes[idx],edges)
			if udef_q==None:
				pass
			else:
				break_connection(nodes[udef_q],nodes[idx],edges)
			combine_nodes([nodes[target_id],nodes[start]],nodes,edges,set_edge_label=True)
			combine_nodes([nodes[target_id],nodes[end]],nodes,edges,set_edge_label=True)
			nodes[target_id]['attributes'].append('interval')
			if udef_q!=None:
				remove_node(nodes[udef_q],nodes,edges)
				del nodes[udef_q]
			remove_node(nodes[start],nodes,edges)
			del nodes[start]
			remove_node(nodes[end],nodes,edges)
			del nodes[end]
			if len(nodes[idx]['parents'])>0:
				#pdb.set_trace()
				parent_list=nodes[idx]['parents'].copy()
				for parent in parent_list:
					break_connection(nodes[parent],nodes[idx],edges)
			if target_id!=idx:
				remove_node(nodes[idx],nodes,edges)
				del nodes[idx]
		elif interval_type[index]==2:
			for parent_id in interval['parents']:
				if parent_id in start_nodes:
					start=parent_id
					for child_id in nodes[start]['children']:
						if child_id in elliptical_nodes:
							elli_start=child_id
							parent_temp=nodes[elli_start]['parents'].copy()
							for elli_parent in parent_temp:
								break_connection(nodes[elli_parent],nodes[elli_start],edges)
								if nodes[elli_parent]['label']=='udef_q':
									remove_node(nodes[elli_parent],nodes,edges)
									del nodes[elli_parent]
				if parent_id in end_nodes:
					end=parent_id
					for child_id in nodes[end]['children']:
						if child_id in elliptical_nodes:
							elli_end=child_id
							parent_temp=nodes[elli_end]['parents'].copy()
							for elli_parent in parent_temp:
								break_connection(nodes[elli_parent],nodes[elli_end],edges)
								if nodes[elli_parent]['label']=='udef_q':
									remove_node(nodes[elli_parent],nodes,edges)
									del nodes[elli_parent]
				if nodes[parent_id]['label']=='udef_q':
					udef_q=parent_id
			break_connection(nodes[start],nodes[idx],edges)
			break_connection(nodes[end],nodes[idx],edges)
			break_connection(nodes[udef_q],nodes[idx],edges)
			#combine_nodes([nodes[target_id],nodes[start]],nodes,edges,set_edge_label=True)
			#combine_nodes([nodes[target_id],nodes[end]],nodes,edges,set_edge_label=True)
			if 'attributes' not in nodes[target_id]:
				nodes[target_id]['attributes']=[]
			nodes[target_id]['attributes'].append('interval_elliptical')
			
			remove_node(nodes[end],nodes,edges)
			remove_node(nodes[start],nodes,edges)
			remove_node(nodes[udef_q],nodes,edges)
			del nodes[udef_q]
			del nodes[start]
			del nodes[end]
			try:
				remove_node(nodes[elli_start],nodes,edges)
				del nodes[elli_start]
			except:
				pdb.set_trace()
			remove_node(nodes[elli_end],nodes,edges)
			del nodes[elli_end]
			if target_id!=idx:
				if len(nodes[idx]['parents'])>0:
					combine_nodes([nodes[target_id],nodes[idx]],nodes,edges,set_edge_label=True)
				remove_node(nodes[idx],nodes,edges)
				del nodes[idx]

def anchor_dict_generation(nodes):
	anchor_dict={}
	anchor_dict_end={}
	for idx in nodes:
		node=nodes[idx]
		if node['type']=='explicit':
			anchor=node['anchors'][0]['from']
			anchor_end=node['anchors'][0]['to']
			if anchor_end not in anchor_dict_end:
				anchor_dict_end[anchor_end]=[]
			if anchor not in anchor_dict:
				anchor_dict[anchor]=[]
			else:
				#pdb.set_trace()
				pass
			anchor_dict[anchor].append(idx)
			anchor_dict_end[anchor_end].append(idx)
	return anchor_dict,anchor_dict_end

def special_case_reduce(sentence):
	nodes=sentence['nodes']
	anchor_dict={}
	wsj_val=wsj[sentence['id']]
	edges=sentence['edges']
	special_label_count={'interval':0,'interval_p_start':0,'interval_p_end':0,'elliptical_n':0}
	for idx in nodes:
		node=nodes[idx]
		if node['label'] in special_label_count:
			special_label_count[node['label']]+=1
	if str(special_label_count) not in collect:
		collect[str(special_label_count)]=0
	collect[str(special_label_count)]+=1

def anchor_node_extra_children_check(sentence,collect={}):
	nodes=sentence['nodes']
	edges=sentence['edges']
	wsj_val=wsj[sentence['id']]
	anchor_dict,anchor_dict_end=anchor_dict_generation(nodes)
	for idx in nodes:
		node=nodes[idx]
		if node['label'] in check_list:
			if node['label'] not in collect:
				collect[node['label']]={}
				collect[node['label']]['total']=0
				collect[node['label']]['not_match']=0
				collect[node['label']]['match']=0
			anchor=node['anchors'][0]['from']
			collect[node['label']]['total']+=1
			if anchor not in anchor_dict:
				collect[node['label']]['match']+=1
				continue
			target_node=None
			for index in anchor_dict[anchor]:
				if node['anchors'][0]['to']==nodes[index]['anchors'][0]['to']:
					target_node=nodes[index]
				
			if target_node==None:
				#pdb.set_trace()
				collect[node['label']]['not_match']+=1
				continue
			if len(set(target_node['children']))==1:
				collect[node['label']]['match']+=1
			else:
				collect[node['label']]['not_match']+=1
				#pdb.set_trace()
				pass
			
# cleaning repeat parents/children in nodes
def clean_node_representation(sentence):
	nodes=sentence['nodes']
	for idx in nodes:
		node=nodes[idx]
		node['parents']=list(set(node['parents']))
		node['children']=list(set(node['children']))

def remain_labels_reduction(sentence,wsj):
	nodes=sentence['nodes']
	edges=sentence['edges']
	wsj_val=wsj[sentence['id']]
	anchor_dict,anchor_dict_end=anchor_dict_generation(nodes)
	to_del=[]
	for idx in nodes:
		node=nodes[idx]
		#pdb.set_trace()
		if node['label'] in remained_labels:
			if node['label']!='generic_entity' or (node['label']=='generic_entity' and len(node['parents'])==1):
				anchor=node['anchors'][0]['from']
				if anchor not in anchor_dict:
					#pdb.set_trace()
					single_align(node,nodes,edges,wsj_val)
				else:
					target_node=None
					for index in anchor_dict[anchor]:
						if node['anchors'][0]['to']==nodes[index]['anchors'][0]['to']:
							target_node=nodes[index]

					if target_node==None:
						#pdb.set_trace()
						#combine_nodes()
						target_node=nodes[node['parents'][0]]
						newnode=combine_nodes([target_node,node],nodes,edges,set_edge_label=False,reverse=True)
						pass
					else:
						if target_node['type']=='implicit':
							pdb.set_trace()
						#pdb.set_trace()
						newnode=combine_nodes([target_node,node],nodes,edges,set_edge_label=False,reverse=True)
					to_del.append(idx)
			else:
				pass
				#pdb.set_trace()
				parents=node['parents']
				if len(parents)==1:
					pdb.set_trace()
				elif len(parents)==2:
					if parents[0]==parents[1]:
						remove_node(node,nodes,edges)
					join_two_nodes(parents[0],parents[1],node['id'],nodes,edges,reverse=True)
				elif len(parents)==0:
					remove_node(node,nodes,edges)
				else:
					#pdb.set_trace()
					max_index=-1
					target_parent=-1
					if len(set(parents))<len(parents):
						remove_node(node,nodes,edges)
					else:
						num_targets=len(set(parents))-2
						target_list=[]
						for parent in parents:
							label=edges[parent,node['id']][0]
							if label not in index_list:
								label='others'
							target_list.append(index_list[label])
							# if index_list[label]>max_index:
							# 	max_index=index_list[label]
							# 	target_parent=parent
						sorted_list=np.argsort(target_list)[::-1]
						to_break=parents.copy()
						for i in range(num_targets):
							target_parent=to_break[sorted_list[i]]
							break_connection(nodes[target_parent],node,edges)

						try:
							join_two_nodes(parents[0],parents[1],node['id'],nodes,edges,reverse=True)
						except:
							pdb.set_trace()
					#pdb.set_trace()
					pass
				to_del.append(idx)
				#pdb.set_trace()

	for idx in to_del:
		del nodes[idx]

def anchor_edge_label_check(sentence,wsj,collect={}):
	#check the implicit nodes that with two children, whether their anchor are aligned with their children
	nodes=sentence['nodes']
	anchor_dict={}
	wsj_val=wsj[sentence['id']]
	edges=sentence['edges']
	for idx in nodes:
		node=nodes[idx]
		if node['label'] in check_list:
			if node['label'] not in collect:
				collect[node['label']]={}
				collect[node['label']]['total']=0
				collect[node['label']]['not_match']=0
			
			anchor=(node['anchors'][0]['from'],node['anchors'][0]['to'])
			collect[node['label']]['total']+=1
			children=set(node['children'])
			pdb.set_trace()
			if len(set(node['parents']))>1:
				pdb.set_trace()
			if len(children)==2:
				child1=nodes[children[0]]
				child2=nodes[children[1]]
				child1_anchor=(child1['anchors'][0]['from'],child1['anchors'][0]['to'])
				child2_anchor=(child2['anchors'][0]['from'],child2['anchors'][0]['to'])
				if child1_anchor!=anchor and child2_anchor!=anchor:
					collect[node['label']]['not_match']+=1
					#pdb.set_trace()
				else:
					pass
					#pdb.set_trace()
			elif len(children)==1:
				child1=nodes[children[0]]
				child1_anchor=(child1['anchors'][0]['from'],child1['anchors'][0]['to'])
				if child1_anchor!=anchor:
					#pdb.set_trace()
					collect[node['label']]['not_match']+=1
			else:
				pass
				#pdb.set_trace()

def convert_current_wsj_to_id_dict(wsj_val):
	new_wsj_val={}
	for key in wsj_val:
		new_wsj_val[wsj_val[key][0]]=wsj_val[key]
	return new_wsj_val

def convert_to_conllu(sentence,wsj):
	nodes=sentence['nodes']
	anchor_dict={}
	wsj_val=wsj[sentence['id']]
	wsj_val=convert_current_wsj_to_id_dict(wsj_val)
	edges=sentence['edges']
	wsj_keys=list(wsj_val.keys())
	attribute_dict={}
	label_dict={}
	node_to_align_id={}
	edge_dict={}
	for idx in nodes:
		node=nodes[idx]
		try:
			node_to_align_id[node['id']]=node['align_id']
		except:
			pdb.set_trace()
		current_wsj_val=wsj_val[node['align_id']]
		assert current_wsj_val[0]==node['align_id'], 'wrong aligned'
		if node['align_id'] not in attribute_dict:
			attribute_dict[node['align_id']]=[]
		if 'attributes' in node:
			attribute_dict[node['align_id']]=attribute_dict[node['align_id']]+node['attributes']
		if 'properties' in node:
			attribute_dict[node['align_id']]=attribute_dict[node['align_id']]+node['values']
		
		if node['align_id'] not in label_dict:
			label_dict[node['align_id']]=[]
		if node['label'] in labels_list or node['label']=='nonnode':
			#pdb.set_trace()
			attribute_dict[node['align_id']]=attribute_dict[node['align_id']]+[node['label']]
		label_dict[node['align_id']].append(node['label'])

	for parent,child in edges:
		try:
			align_id=node_to_align_id[child]
		except:
			pdb.set_trace()
		edge_labels=edges[parent,child]
		if len(edge_labels)>1:
			#pdb.set_trace()
			pass
		if align_id not in edge_dict:
			edge_dict[align_id]=[]
		try:
			edge_dict[align_id].append(node_to_align_id[parent]+':'+edge_labels[0])
		except:
			pdb.set_trace()
	new_wsj_val=wsj_val.copy()
	#pdb.set_trace()
	#TODO: add label dict
	for aligned_id in new_wsj_val:
		if aligned_id not in attribute_dict:
			new_wsj_val[aligned_id][9]='_'
		else:
			if len(attribute_dict[aligned_id])==0:
				new_wsj_val[aligned_id][9]='_'
			else:
				new_wsj_val[aligned_id][9]='|'.join(attribute_dict[aligned_id])
		#pdb.set_trace()
		if aligned_id not in label_dict:
			new_wsj_val[aligned_id][5]='_'
		else:
			#Problem
			if label_dict[aligned_id][0] in labels_list:
				new_wsj_val[aligned_id][5]='_'
			else:
				target_label=label_dict[aligned_id][0]
				# if '_' in target_label:
				# 	target_label=target_label.split('_')[1]
				new_wsj_val[aligned_id][5]=target_label

		if aligned_id not in edge_dict:
			new_wsj_val[aligned_id][8]='_'
		else:
			if len(edge_dict[aligned_id])==0:
				new_wsj_val[aligned_id][8]='_'
			else:
				new_wsj_val[aligned_id][8]='|'.join(edge_dict[aligned_id])
	for top in sentence['tops']:
		if new_wsj_val[top['align_id']][8]=='_':
			new_wsj_val[top['align_id']][8]='0:root'
		else:
			new_wsj_val[top['align_id']][8]+='|0:root'
	#pdb.set_trace()
	new_wsj_val['id']=sentence['id']
	return new_wsj_val

repeated_edges = 0
def convert_to_dict(sentence):
	global repeated_edges
	nodes = sentence['nodes']
	id = sentence['id']
	edges = sentence['edges']
	tops = sentence['tops']
	input = sentence['input']
	res_dict = {}

	for node_id, _ in nodes.items():
		nodes[node_id]['edges'] = []

	# for (source, target), label in edges.items():
	# 	if len(label) != 1:
	# 		repeated_edges += 1
	# 	label = label[0]
	# 	nodes[target]['edges'].append((source, label))
	#
	# for top in tops:
	# 	nodes[top]['edges'] = [(0, 'root')] + nodes[top]['edges']

	res_dict['id'] = id
	res_dict['nodes'] = nodes
	res_dict['edges'] = edges
	res_dict['tops'] = tops
	res_dict['input'] = input

	return res_dict



# node_edges dictionary above is of the format:
# 'udef_q':[['BV'],['BV'],['ARG1','ARG2'],...]
# length of the list: number of nodes of type 'udef_q'
# every entry(also a list) of this list: edge labels of each node of type 'udef_q'
count={'count':0,'total':0}
properlist=set()
explicit_proper=set()
valuelist=set()
falselist=set()
node_deprel={}
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

wsj=conpanion_read()

if __name__ == '__main__':

	collect={}
	lev_dict={}
	reldict={}
	reldict2={}
	all_count={}
	stats_single = collections.Counter()
	stats_double = collections.Counter()
	for sentence in alldicts:

		# ---- Recording each word's starting index ----
		string = sentence['input']
		# print(string)
		words = string.split(' ')
		ids = []
		explicit = []
		implicit = []
		# TODO: preprocess top nodes
		#sentence['nodes']=top_preprocess(sentence)
		# assign nodes with explicit, implicit type, convert label node with properties to corresponding value
		sentence['nodes']=preprocess_nodes(sentence,all_count)

		# align words for explicit words
		# TODO: add decomposed word type into alignment
		sentence['nodes']=explict_alignment(sentence,wsj,collect=collect,lev_dict=lev_dict)

		# reset the edge data to a faster dictionary
		sentence['edges']=edge_change(sentence,labels=reldict)
		#pdb.set_trace()
		# if sentence['id']=='21273038':
		# 	pdb.set_trace()

		# align_top_nodes(sentence,wsj)
		# remove?
		# remove_few_implicits(sentence)
		# special_case_check(sentence,collect)
		# we can now reduce these replacable nodes into a single node
		# replacable_implicit_anchor_reduction(sentence,wsj)

		# implicit nodes reduction

		single_implicit_reduction(sentence,wsj,stats_single=stats_single)
		double_implicit_reduction(sentence,wsj,stats_double=stats_double)
		# clean_node_representation(sentence)
		# anchor_node_extra_children_check(sentence,collect)
		# remain_labels_reduction(sentence,wsj)


		# res_sent=convert_to_conllu(sentence,wsj)
		res_dict = convert_to_dict(sentence)

		write_dict.append(res_dict)

	pickle.dump(write_dict, open('eds_dict.pkl', 'wb'))
	print(stats_single)
	print(stats_double)

# import codecs
	# fout = open('mrp_eds.conllu', 'wb')
# writer = codecs.getwriter('utf-8')(fout)
# for data in write_dict:
# 	num=len(data)
# 	writer.write('#'+data['id']+'\n')
# 	for i in range(1,num):
# 		try:
# 			writer.write('\t'.join(data[str(i)])+'\n')
# 		except:
# 			pdb.set_trace()
# 	writer.write('\n')
# # writer.write_all(write_dict)
# writer.close()
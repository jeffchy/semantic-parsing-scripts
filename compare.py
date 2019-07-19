import utils
def compare_len(conllu_dm_new, conllu_dm_old):
    assert len(conllu_dm_new) == len(conllu_dm_old)
    print('Same # of sent')
    l = len(conllu_dm_new)
    for i in range(l):
        con_n = conllu_dm_new[i]
        con_o = conllu_dm_old[i]
        assert con_n[0] == con_o[0]
    print('Same sent ids')

    same_len_sent = 0
    all_sent = 0
    for i in range(l):
        all_sent += 1
        con_n = conllu_dm_new[i]
        con_o = conllu_dm_old[i]
        if len(con_n) == len(con_o):
            same_len_sent += 1
    print('Same len sent: {}, all sent: {}, ratio: {}%'.format(same_len_sent, all_sent, same_len_sent/all_sent))
    return

def compare_single_field(conllu_dm_new, conllu_dm_old, idx):

    same = 0
    all = 0
    l = len(conllu_dm_new)
    for i in range(l):
        con_n = conllu_dm_new[i]
        con_o = conllu_dm_old[i]
        for j in range(1, len(con_o)):
            all += 1
            if con_n[j][idx] == con_o[j][idx]:
                same += 1
    return same, all

def same_edge(list1, list2):
    if len(list1) != len(list2):
        return False
    else:
        sorted_list1 = sorted(list1)
        sorted_list2 = sorted(list2)
        for i in range(len(sorted_list1)):
            if sorted_list1[i] != sorted_list2[i]:
                return False
    return True

def compare_edge(conllu_dm_new, conllu_dm_old):
    same = 0
    all = 0
    l = len(conllu_dm_new)
    for i in range(l):
        con_n = conllu_dm_new[i]
        con_o = conllu_dm_old[i]
        for j in range(1, len(con_o)):
            all += 1
            con_n_edge = con_n[j][-2].split('|')
            con_o_edge = con_o[j][-2].split('|')
            if same_edge(con_n_edge, con_o_edge):
                same += 1
            else:
                print(con_n[0])
                print(j, con_n_edge, con_o_edge)

    return same, all

if __name__ == '__main__':
    with open('../processed_data/dm/train.en.dm.conllu', 'r', encoding='utf-8') as fin:
        conllu_dm_new = utils.read_conllu_2(fin)
    with open('../processed_data/dm/train.en.dm_modified.conllu', 'r', encoding='utf-8') as fin:
        conllu_dm_old = utils.read_conllu_2(fin)
    compare_len(conllu_dm_new, conllu_dm_old)
    same, all = compare_single_field(conllu_dm_new, conllu_dm_old, 1)
    print('Field: {}, Same: {}, All: {}, Ratio: {}'.format('Word', same, all, same / all))
    same, all = compare_single_field(conllu_dm_new, conllu_dm_old, 2)
    print('Field: {}, Same: {}, All: {}, Ratio: {}'.format('LEMMA', same, all, same / all))
    same, all = compare_single_field(conllu_dm_new, conllu_dm_old, 4)
    print('Field: {}, Same: {}, All: {}, Ratio: {}'.format('POS', same, all, same / all))
    same, all = compare_edge(conllu_dm_new, conllu_dm_old)
    print('Field: {}, Same: {}, All: {}, Ratio: {}'.format('EDGE', same, all, same / all))
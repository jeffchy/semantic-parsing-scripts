from utils import *
import re
import Levenshtein

def fill_in_lemma_and_compare(conllu_ner, conllu_new, conllu_old):

    assert len(conllu_ner) == len(conllu_new)

    def find_from_idx(conllu, idx, string):
        flag = False
        for k in range(idx, len(conllu)):
            if conllu[k][1] ==  string \
                or ('Inc' in string and 'Inc' in conllu[k][1]) \
                or (string+'.' == conllu[k][1]) \
                or (string == conllu[k][1]+'.') \
                or (string + ',' == conllu[k][1]) \
                or (string == conllu[k][1] + ','):
                flag = True
                break
        if flag == False:
            return idx, flag

        return k, flag

    def fill_in(ner, conllu):
        conllu_idx = 0
        for match in re.finditer(r'\[.+?\]', ner):
            temp = match[0]
            temp = temp.replace('[','')
            temp = temp.replace(']','')
            temp = temp.split()
            if not temp:
                continue
            tag = temp[0]
            strings = temp[1:]
            for string in strings:
                if '??' in string:
                    continue
                if len(string) < 3:
                    continue

                conllu_idx, find = find_from_idx(conllu, conllu_idx + 1, string)
                if find:
                    conllu[conllu_idx][2] = tag

        return


    def fill_in_1(ner, conllu):
        conllu_idx = 0
        for kk in range(1, len(conllu)):
            conllu[kk][2] = '_'
        for match in re.finditer(r'\[.+?\]', ner):
            temp = match[0]
            temp = temp.replace('[','')
            temp = temp.replace(']','')
            temp = temp.split()
            if not temp:
                continue
            tag = temp[0]
            strings = temp[1:]
            for string in strings:
                if '??' in string:
                    continue
                if len(string) < 3:
                    continue

                conllu_idx, find = find_from_idx(conllu, conllu_idx + 1, string)
                if find:
                    conllu[conllu_idx][2] = tag

        return

    def fill_in_amr(ner, conllu):
        conllu_idx = 0
        for kk in range(1, len(conllu)):
            conllu[kk][-1] = '_'

        for match in re.finditer(r'\[.+?\]', ner):
            temp = match[0]
            temp = temp.replace('[','')
            temp = temp.replace(']','')
            temp = temp.split()
            if not temp:
                continue
            tag = temp[0]
            strings = temp[1:]
            for string in strings:
                if '??' in string:
                    continue
                if len(string) < 3:
                    continue

                conllu_idx, find = find_from_idx(conllu, conllu_idx + 1, string)
                if find:
                    conllu[conllu_idx][-1] = tag

        return

    def fill_in_2(ner, conllu):
        conllu_idx = 0
        for kk in range(1, len(conllu)):
            conllu[kk][3] = '_'

        for match in re.finditer(r'\[.+?\]', ner):
            temp = match[0]
            temp = temp.replace('[','')
            temp = temp.replace(']','')
            temp = temp.split()
            if not temp:
                continue
            tag = temp[0]
            strings = temp[1:]
            for string in strings:
                if '??' in string:
                    continue
                if len(string) < 3:
                    continue

                conllu_idx, find = find_from_idx(conllu, conllu_idx + 1, string)
                if find:
                    conllu[conllu_idx][3] = tag

        return


    l = len(conllu_ner)
    for i in range(l):
        conllu_ner_i = conllu_ner[i]
        conllu_new_i = conllu_new[i]
        # conllu_old_i = conllu_old[i]
        fill_in_2(conllu_ner_i, conllu_new_i)


    return



if __name__ == '__main__':
    with open('../processed_data/dm/train.en.dm.conllu', 'r', encoding='utf-8') as fin:
        conllu_dm_new = read_conllu_2(fin)
    # with open('../processed_data/dm/dev.en.dm_modified.conllu', 'r', encoding='utf-8') as fin:
    #     conllu_dm_old = read_conllu_2(fin)
    with open('../../illinois-ner/output/train.en.dm.txt', 'r', encoding='utf-8') as fin:
        conllu_dm_ner = read_txt(fin).split('<SENT_SPLIT>')
        conllu_dm_ner = [i for i in conllu_dm_ner if i.strip()]

    fill_in_lemma_and_compare(conllu_dm_ner, conllu_dm_new, None)
    with open('../processed_data/dm/train.dm.ner+lemma.conllu', 'w', encoding='utf-8') as fout:
        for conllu in conllu_dm_new:
            write_to_conllu(conllu, fout)

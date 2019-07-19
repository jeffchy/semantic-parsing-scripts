from utils import *
import re
import Levenshtein
import pickle

def fill_in_lemma_and_compare(conllu_ner, conllu_new, conllu_old):

    assert len(conllu_ner) == len(conllu_new)

    def find_from_idx(conllu, idx, string):
        flag = False
        for k in range(idx, len(conllu)):
            if conllu[k] ==  string \
                or ('Inc' in string and 'Inc' in conllu[k]) \
                or (string + '.' == conllu[k]) \
                or (string == conllu[k]+'.') \
                or (string == conllu[k] + ',') \
                or (string + ','== conllu[k]):
                flag = True
                break
        if flag == False:
            return idx, flag
        return k, flag

    def fill_in(ner, conllu):
        conllu_idx = -1
        new_conllu = len(conllu) * ['O']
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
                if len(string) < 2:
                    continue
                if ':' in string:
                    continue

                conllu_idx, find = find_from_idx(conllu, conllu_idx + 1, string)
                # assert find == True
                if find:
                    new_conllu[conllu_idx] = tag

        return new_conllu

    all = []
    l = len(conllu_ner)
    for i in range(l):
        conllu_ner_i = conllu_ner[i]
        conllu_new_i = conllu_new[i]
        # conllu_old_i = conllu_old[i]
        filled_conllu = fill_in(conllu_ner_i, conllu_new_i)
        all.append(filled_conllu)

    return all



if __name__ == '__main__':

    with open('../processed_data/amr/train_sentence.tagged.txt', 'r', encoding='utf-8') as fin:
        amr_ner = read_txt(fin).split('<SENT_SPLIT>')
        amr_ner = [i for i in amr_ner if i.strip()]

    with open('../processed_data/amr/train_sentence.txt', 'r', encoding='utf-8') as fin:
        amr_origin = read_txt(fin).split('\n')
        amr_origin = [i.split() for i in amr_origin if i.strip()]

    all = fill_in_lemma_and_compare(amr_ner, amr_origin, None)
    assert len(all) == len(amr_origin)

    with open('../processed_data/amr/sentence.tagged.pkl', 'wb') as fout:
        pickle.dump(all, fout)

from utils import *


if __name__ == '__main__':

    with open('../processed_data/amr/amr.conllu', 'r', encoding='utf-8') as fin:
        conllu_dm = read_conllu_2(fin)
    lines = conllu_to_txt(conllu_dm)
    with open('../processed_data/amr/amr.txt', 'w', encoding='utf-8') as fout:
        write_to_lines(lines, fout)



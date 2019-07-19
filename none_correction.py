from utils import *



if __name__ == '__main__':
    with open('../processed_data/psd/psd.conllu', 'r', encoding='utf-8') as fin:
        dm_conllu = read_conllu(fin)

    with open('../mrp/2019/training/psd/wsj.mrp', 'r', encoding='utf-8') as fin:
        dm_mrps = read_mrp(fin)

    for dm_data in dm_conllu:
        id = dm_data[0]
        c = 0
        for line in dm_data:
            c += 1
            if 'None:' in line:
                print(id, c)



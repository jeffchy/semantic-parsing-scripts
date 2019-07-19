from utils import *


if __name__ == '__main__':

    with open('../processed_data/dm/dm.conllu', 'r', encoding='utf-8') as fin_dm:
        train_dm, dev_dm = train_dev_split(fin_dm)

    with open('../processed_data/dm/train.en.dm.conllu', 'w', encoding='utf-8') as fout_dm_train:
        write_to_conllu_1(train_dm, fout_dm_train)

    with open('../processed_data/dm/dev.en.dm.conllu', 'w', encoding='utf-8') as fout_dm_dev:
        write_to_conllu_1(dev_dm, fout_dm_dev, dev=True)

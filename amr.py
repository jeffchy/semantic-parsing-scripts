import glob
from utils import *
import pickle

if __name__ == '__main__':
    # conllus = []
    # files = glob.glob('../mrp/2019/companion/amr/*.conllu')
    # for f in files:
    #     with open(f, 'r', encoding='utf-8') as fin:
    #         conllus += read_conllu(fin)
    # conllus = sorted(conllus, key=lambda x: x[0])
    # pickle.dump(conllus, open('../processed_data/amr/sorted_conllu.pkl', 'wb'))
    conllus = pickle.load(open('../processed_data/amr/sorted_conllu.pkl', 'rb'))
    with open('../processed_data/amr/amr.conllu', 'w', encoding='utf-8') as fout:
        write_to_conllu_1(conllus, fout, True)

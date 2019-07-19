import json

def read_mrp(fin):
    """
    :param fin:
    :return: mrp - list of graphs in mrp
    """

    mrp = []
    for line in fin:
        mrp.append(json.loads(line))

    return mrp

def read_conllu(fin):
    """
    :param fin:
    :return: mrp - list of graphs in mrp
    """

    s = fin.read()
    conllus = s.split('\n\n')
    conllus = [i.split('\n') for i in conllus if i]

    return conllus

def read_conllu_2(fin):
    """
    :param fin:
    :return: mrp - list of graphs in mrp
    """

    s = fin.read()
    conllus = s.split('\n\n')
    conllus = [[j.split('\t') for j in i.split('\n')] for i in conllus if i]

    return conllus

def read_txt(fin):
    """
    :param fin:
    :return: mrp - list of graphs in mrp
    """

    s = fin.read()

    return s

def write_to_conllu(new_conllu, fout):
    for line in new_conllu:
        fout.write('\t'.join(line))
        fout.write('\n')
    fout.write('\n')

def write_to_lines(lines, fout):
    for line in lines:
        fout.write(line)
        fout.write('\t')
        fout.write('<SENT_SPLIT>')
        fout.write('\n')

def write_to_conllu_1(new_conllu, fout, dev=False):


    for conllu in new_conllu:
        if len(conllu) < 61 or dev:
            for line in conllu:
                fout.write(line)
                fout.write('\n')
            fout.write('\n')


def train_dev_split(fin):
    """
    :param fin: file in conllu form
    :return: train, dev: data list in conllu form
    """

    conllus = read_conllu(fin)
    train_conllus = []
    dev_conllus = []
    for conllu in conllus:
        sent_id = conllu[0]
        if sent_id[1:3] == '22':
            dev_conllus.append(conllu)
        else:
            train_conllus.append(conllu)
    return train_conllus, dev_conllus

def conllu_to_txt(conllu):
    lines = []
    for i in conllu:
        line = ' '.join([i[l][1] for l in range(1, len(i))])
        lines.append(line)
    return lines

def mrp_to_txt(mrps):
    all = []
    for mrp in mrps:
        all.append(mrp['input'])
    return all

def write_mrp(mrps, fout):
    for mrp in mrps:
        # fout.write(str(mrp))
        # fout.write('\n')
        json.dump(mrp, fout)
        fout.write('\n')

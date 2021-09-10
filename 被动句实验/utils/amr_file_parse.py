import re
from tqdm import tqdm
import time

# 获得每个句子的信息
def get_amr_data(filepath):
    """
    :param filepath: AMR文件名
    :return: amr_parsed_data = {
        amr_id: 句子索引
        amr_snt： 句子的分词表示
        amr_wid： 句子token下标
        amr_graph： 句子的语义依存图
    }
    """
    amr_parsed_data = []
    file = open(filepath, "r", encoding="utf8")
    _ = file.readline()  # 前两行不含句子信息，跳过
    _ = file.readline()
    temp_str = ""  # 每个句子的所有信息，后面进行细分
    amr_data = []
    stn_id = []
    while True:
        line = file.readline()
        if not line:
            break
        if "::id" in line:
            if len(temp_str) > 1:
                amr_data.append(temp_str)
                temp_str = ""
        temp_str += line
    amr_data.append(temp_str)

    for i in tqdm(range(0, len(amr_data))):
        amr_stn = amr_data[i]
        stn_detail = {}
        graph_info = ""
        for line in amr_stn.strip().split("\n"):
            if "#" in line:
                # 解析id snt wid
                tokens = line.strip().split()
                if "::id" in tokens:
                    idx = tokens[2].split('.')
                    stn_detail["amr_id"] = int(idx[1])
                elif "::snt" in tokens:
                    stn_detail["amr_snt"] = tokens[2:]
                elif "::wid" in tokens:
                    temp_tks = []
                    for tk in tokens[2:]:
                        temp_tks.append(tk.split('_')[0])
                    stn_detail["amr_wid"] = temp_tks
            else:
                # 分析amr依存关系图
                graph_info += line
        parse_input = graph_info.strip().replace('\n', ' ')
        if parse_input == "":
            stn_detail["amr_graph"] = None
            stn_detail["verb_list"] = None
        else:
            parse_output, verb_list = amr_graph_parse(parse_input)
            stn_detail["amr_graph"] = parse_output
            # 删除不在句子中的父节点，得到动词
            token_ids = stn_detail["amr_wid"]
            for vb in verb_list:
                if vb[0] not in token_ids:
                    verb_list.remove(vb)
            stn_detail["verb_list"] = verb_list
        amr_parsed_data.append(stn_detail)
    return amr_parsed_data


# 解析单个句子的语义依存图
def amr_graph_parse(data_info):
    parse_res = []
    graph_root = {}
    graph_lines = data_info.split(" :")
    verb_list = []
    level = 0
    for line in graph_lines:
        line = line.strip()
        n1 = count_of_char('(', line)
        n2 = count_of_char(')', line)
        diff = n1 - n2

        if level in graph_root.keys():
            graph_root[level].append(line)
        else:
            graph_root[level] = [line]

        if diff > 0:
            # 提取动词
            tks = line.split('/')
            reg_verb_idx = r'x[0-9]{1,3}'
            verb_idx = re.search(reg_verb_idx, tks[0]).group()
            verb_name = tks[-1].strip()
            verb_list.append((verb_idx, verb_name))
        if diff < 0:
            cur_level = level
            tag_level = cur_level + diff
            for i in range(cur_level, tag_level - 1, -1):
                while len(graph_root[i]) > 0:
                    son_node = graph_root[i].pop()
                    if i == 0:
                        father_node = "ROOT"
                    else:
                        father_node = graph_root[i - 1][-1]
                    triple_tuple = get_triple(father_node, son_node)
                    parse_res.append(triple_tuple)

        level += diff

    return parse_res, verb_list


# 字符在该字符串中出现的次数
def count_of_char(ch, string):
    """
    :param ch: 字符
    :param string:字符串
    :return count: 字符在该字符串中出现的次数
    """
    count = 0
    for i in string:
        if i == ch:
            count += 1
    return count


# 根据两个节点抽取三元组
def get_triple(father_node, son_node):
    reg_idx = r'([x,_,0-9]{1,20})\s\/'  # :op1()  (x5 / 有-03  匹配：x5
    reg_idx2 = r'([x,_,0-9]{1,20})\/'  # :op1() x3/北京城  匹配: x3
    reg_idx3 = r'\((\S+)\)'  # :source(x4/从)  (x5 / 远处  匹配: x4/从

    reg_rela = r'[a-z,0-9,-]{1,10}\('
    reg_rela2 = r'[a-z,0-9,-]{1,10}\s[x0-9]'

    index1 = None
    index2 = None
    relation = None
    rela_word = None

    if father_node == "ROOT":
        index2 = re.search(reg_idx, son_node).group()
        index2 = index2[:-2]
        relation = "ROOT"
    else:
        left = son_node.find('(')
        right = son_node.find(')')
        if left > 0 and right > 0 and right - left > 1:
            rela_word = son_node[left + 1: right]  # 依存关系中附带的词如：:arg0-of(x2/的)  中的： x2/的

        if count_of_char('(', father_node) == 0:  # :op1() x3/北京城
            match_res = re.search(reg_idx2, father_node)
            if match_res is not None:
                index1 = (match_res.group())[:-1]
        else:
            index1 = re.search(reg_idx, father_node).group()
            index1 = index1[:-2]

        if count_of_char('(', son_node) == 0:
            match_res2 = re.search(reg_idx2, son_node)
            if match_res2 is not None:
                index2 = (match_res2.group())[:-1]
            relation = re.search(reg_rela2, son_node).group()
            relation = relation[:-2]
        else:
            index2 = re.search(reg_idx, son_node).group()
            relation = re.search(reg_rela, son_node).group()
            relation = relation[:-1]
            index2 = index2[:-2]
    son_instance = son_node.split('/')[-1]
    relation_tuple = (index1, index2, relation, rela_word, son_instance.strip(')').strip())
    return relation_tuple


# 根据父节点下标提取
def parse_wid(word_ids, stn_tokens):
    stn_len = len(stn_tokens)
    ids = word_ids.split('_')
    temp_word = []
    last_order = 0
    if len(ids) > 1:
        temp_char = []
        for i in ids:
            if 'x' in i:
                word_order = int(i.split('x')[1])
                if word_order > stn_len:
                    continue
                last_order = word_order
                temp_word.append(stn_tokens[word_order - 1])
            else:
                word_inner_order = int(i)
                if word_inner_order >= len(temp_word[-1]):
                    continue
                temp_char.append(temp_word[-1][word_inner_order - 1])
        if len(temp_char) > 0:
            temp_word[-1] = ''.join(temp_char)
    else:
        last_order = int(ids[0].split('x')[1])
        if last_order >= stn_len:
            return None, None
        temp_word = stn_tokens[last_order - 1]
    return last_order, temp_word


def judge_passive_sentence(sentence_amr_data):
    passive_flag = False
    v_arg1 = None
    stn_tokens = sentence_amr_data["amr_snt"]
    amr_graph = sentence_amr_data["amr_graph"]
    verbs = sentence_amr_data["verb_list"]
    if amr_graph is None:
        return passive_flag, v_arg1
    v_idx = []
    for v in verbs:
        v_idx.append(v[0])
    for rel in amr_graph:
        if rel[0] in v_idx and rel[2] == "arg1":
            if rel[3] is not None and "把" in rel[3]:
                continue
            father_word_order, father_word = parse_wid(rel[0], stn_tokens)
            son_word_order, son_word = parse_wid(rel[1], stn_tokens)
            if son_word is not None and father_word is not None and son_word_order < father_word_order:
                passive_flag = True
                v_arg1 = {"V": father_word, "Arg1": son_word}
    return passive_flag, v_arg1


if __name__ == '__main__':
    amr_file = "../data/base/amr小学语文全.txt"
    save_file = "../data/res/amr小学语文被动句.txt"
    f = open(save_file, "w+", encoding="utf8")
    res = get_amr_data(amr_file)
    stn_num = len(res)
    print("AMR句子依存图解析完毕！共{}个句子".format(stn_num))
    time.sleep(1)
    passive_count = 0
    for i in tqdm(range(0, stn_num)):

        stn_amr_data = res[i]
        sentence = ''.join(stn_amr_data["amr_snt"])
        passive_stn, passive_action = judge_passive_sentence(stn_amr_data)
        if passive_stn:
            passive_count += 1
        write_info = str(passive_stn) + "|||" + str(passive_action) + "|||" + sentence + '\n'
        f.write(write_info)
    print("被动句判定完毕！共{}个被动句".format(passive_count))
    f.close()

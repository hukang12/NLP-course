import re
from tqdm import tqdm


# 获得每个句子的信息
def get_amr_data(filepath):
    file = open(filepath, "r", encoding="utf8")
    _ = file.readline()
    _ = file.readline()
    temp_str = ""
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
            tk = line.strip().split()
            idx = tk[2].split('.')
            stn_id.append(idx[1])
        temp_str += line
    amr_data.append(temp_str)
    return amr_data, stn_id


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
    index1 = None
    index2 = None
    relation = None
    rela_word = None
    son_instance = None
    father_instance = None

    father_info = father_node.strip('(').strip(')').split(' ')
    son_info = son_node.strip('(').strip(')').split(' ')
    if '' in father_info:
        father_info.remove('')
    if '' in son_info:
        son_info.remove('')
    if father_node == "ROOT":
        index1 = son_info[0]
        son_instance = son_info[-1]
        relation = "ROOT"
    else:
        if len(father_info) == 3 or len(father_info) == 2:
            index1 = father_info[0].strip('(')
        elif len(father_info) == 4:
            index1 = father_info[1].strip('(')
        father_instance = father_info[-1]

        if len(son_info) == 2:
            index2 = son_info[1].strip('(')
        elif len(son_info) == 4:
            index2 = son_info[1].strip('(')

        son_instance = son_info[-1]
        relation = son_info[0]
    relation_tuple = (index1, index2, relation, rela_word, son_instance, father_instance)
    return relation_tuple

# 解析单个句子的语义依存图
def amr_graph_parse(data_info):
    parse_res = []
    graph_root = {}
    graph_lines = data_info.split(" :")
    verb_list = []
    level = 0
    content = ""
    for line in graph_lines:
        line = line.strip()
        n1 = count_of_char('(', line)
        n2 = count_of_char(')', line)
        diff = n1 - n2
        content = "\t" * level + ":" + line + "\n"

        if level in graph_root.keys():
            graph_root[level].append(line)
        else:
            graph_root[level] = [line]

        if diff > 0:
            # 提取动词
            tks = line.split('/')
            reg_verb_idx = r'[xc][0-9]{1,3}'
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

    return parse_res, verb_list, content


# 解析每个句子的标点符号下标
def amr_wid_parse(stn_wid_list):
    punc_idx = []
    for it in stn_wid_list:
        tj = it.split('_')
        if tj[-1] in ['，', ',', '。', '.', ' :', '!', '？', '?'] or "”" in tj[-1]:
            punc_idx.append(tj[0])
    return punc_idx


def parse_amr_data(amr_data):
    amr_detail = []
    for i in tqdm(range(len(amr_data))):
        amr_stn = amr_data[i]
        stn_detail = {}
        graph_info = ""
        for line in amr_stn.strip().split("\n"):
            if "#" in line:
                tokens = line.strip().split()

                if "::id" in tokens:
                    idx = tokens[2].split('.')
                    stn_detail["amr_id"] = int(idx[1])
                elif "::snt" in tokens:
                    stn_detail["amr_snt"] = tokens[2:]
                else:
                    stn_detail["amr_wid"] = tokens[2:]
                    stn_detail["puc_idx"] = amr_wid_parse(tokens[2:])
            else:
                graph_info += line
        parse_input = graph_info.strip().replace('\n', ' ')
        if parse_input == "":
            stn_detail["amr_graph"] = None
            # print(stn_detail["amr_id"], "缺少graph")
        else:
            parse_output, verb_list, content = amr_graph_parse(parse_input)
            stn_detail["amr_graph"] = parse_output
            stn_detail["graph_info"] = content
            stn_detail["verb_list"] = verb_list

        amr_detail.append(stn_detail)

    return amr_detail


if __name__ == '__main__':
    amr_path = "data/amr/amr小学语文全.txt"
    data, ids = get_amr_data(amr_path)
    amr_detail = parse_amr_data(data)

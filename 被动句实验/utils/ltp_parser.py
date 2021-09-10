from ltp import LTP
from tqdm import tqdm

ltp = LTP()


def open_news_txt(filepath):
    news_data = []
    ff = open(filepath, "r", encoding="utf8")
    while True:
        line = ff.readline()
        if not line:
            break
        if len(line.strip()) == 0 or line == '\n':
            continue
        tokens = line.strip().split()[1:]
        for i, tk in enumerate(tokens):
            tokens[i] = (tk.split('/'))[0]
        sentence = ''.join(tokens)
        single_sentence_list = sentence.strip('。').split('。')
        news_data.extend(single_sentence_list)
    ff.close()
    return news_data



def data_parser(sent_list):
    sent_seg_list, hidden = ltp.seg(sent_list)  # 分词
    sent_srl_list = ltp.srl(hidden)  # 语义角色标注
    sent_pos_tag = ltp.pos(hidden)  # 词性标注
    sent_dep_tag = ltp.dep(hidden)    # 依存句法分析
    sent_sdp_graph = ltp.sdp(hidden, mode="graph")  # 语义依存图
    return {"seg": sent_seg_list, "dep": sent_dep_tag, "pos": sent_pos_tag, "srl": sent_srl_list, "sdp": sent_sdp_graph}


def extract_info(sent_ltp_data, save_file_path):
    f = open(save_file_path, "a+", encoding="utf8")
    seg_list = sent_ltp_data["seg"]
    pos_list = sent_ltp_data["pos"]
    dep_list = sent_ltp_data["dep"]
    srl_list = sent_ltp_data["srl"]
    sdp_list = sent_ltp_data["sdp"]
    sentences_num = len(seg_list)
    # 处理句子的ltp解析结果
    for i in range(sentences_num):
        no_flag = False
        verb_arg1 = []
        sent_tokens = seg_list[i]
        # 找出动词所在索引
        verb_set = find_verb(seg_list[i], pos_list[i])

        # 找出充当角色的部分
        srl_idx_set = find_role(srl_list[i])
        # print(srl_idx_set)

        # 找出不充当角色（名词性成分）的动词
        real_verb = {}
        for verb_idx in verb_set.keys():
            if verb_idx not in srl_idx_set:
                real_verb[verb_idx] = verb_set[verb_idx]
        # print(real_verb)

        # 通过句法依存分析进一步筛选
        wait_pop = []
        has_fob_idx = []
        for v_idx in real_verb.keys():
            has_att = False
            temp = v_idx + 1
            for edge in dep_list[i]:
                if edge[1] == temp and edge[2] == "ATT":
                    has_att = True
                    break
                if edge[1] == temp and edge[2] == "ADV" and sent_tokens[edge[0]-1] in ["被", "把", "将", "给", "由", "用"]:
                    has_att = True
                    break
                # if edge[1] == temp and edge[2] == "FOB":
                #     has_fob_idx.append(v_idx)
            if has_att:
                wait_pop.append(v_idx)
        for idx in wait_pop:
            real_verb.pop(idx)


        # 找出动词相关联的语义依存边
        for v_id in real_verb.keys():
            flag = False
            arg1_idx = []
            temp_idx = v_id + 1
            for edge in sdp_list[i]:
                # 动词为父节点的边
                if edge[1] == temp_idx:
                    if "AGT" in edge[2] or "EXP" in edge[2]:
                        flag = False
                        break
                    if ("PAT" in edge[2] or "CONT" in edge[2]) and edge[0] < edge[1]:
                        flag = True
                        arg1_idx.append(edge[0])
            if flag:
                no_flag = True
                for idx in arg1_idx:
                    verb_arg1.append({"verb": sent_tokens[v_id], "arg1": sent_tokens[idx-1]})
        if no_flag:
            # 写入文件
            f.write(''.join(sent_tokens) + ' # ' + str(verb_arg1) + '\n')
        # print(verb_arg1)
    f.close()


def find_verb(token_list, pos_tag_list):
    verb_set = {}
    for i, pos in enumerate(pos_tag_list):
        if pos == 'v':
            verb_set[i] = token_list[i]
    return verb_set


def find_role(srl_list):
    role_idx_set = set()
    for srl in srl_list:
        if len(srl) > 0:
            for tp in srl:
                if tp[0] in ['A0', 'A1', 'A2', 'A3', 'A4']:
                    temp_list = []
                    for j in range(tp[1], tp[2] + 1):
                        temp_list.append(j)
                    role_idx_set = set(temp_list) | role_idx_set
    return role_idx_set



def get_amr_data(filepath):
    snts_data = []
    f = open(filepath, "r", encoding="utf-8")
    for line in f.readlines():
        words = line.strip().split()
        if "::snt" in words:
            words = words[2:]
            if len(words) > 0 and "\ue5f1" not in words[0]:
                strr = "".join(words)
                snts_data.append(strr)
    return snts_data


def test():
    st = ["以色列人控制了渡口。", "从此，古典经济学日益被庸俗化。", "自从７０年代末中国社会学重建以来，实证研究方法和技术迅速大量地传入中国，这是一件好事。。"]
    test_file = "res/无标记测试文件0816.txt"
    for s in st:
        test_data = data_parser([s])
        extract_info(test_data, test_file)


def main():
    save_file = "res/无标记被动句（最新0817再不改了）.txt"
    TH_data = []
    with open("data/THTreeBank(抽取原句子).txt", "r", encoding="gb18030") as f:
        count = 0
        for line in f.readlines():
            if len(line) > 0 and "\ue5f1" not in line:
                count += 1
                TH_data.append(line)
    print("句子数：", len(TH_data))

    for i in tqdm(range(len(TH_data))):
        s = TH_data[i]
        ltp_data = data_parser([s])
        extract_info(ltp_data, save_file)

def newsmain():
    newsdata = open_news_txt("../data/base/199801.txt")
    savefile = "../data/res/人民日报199801抽取结果(FOB).txt"
    for i in tqdm(range(len(newsdata))):
        s = newsdata[i]
        ltp_data = data_parser([s])
        extract_info(ltp_data, savefile)

if __name__ == '__main__':

    # test()
    # main()
    newsmain()
    # newsdata = open_news_txt("../data/base/199801.txt")











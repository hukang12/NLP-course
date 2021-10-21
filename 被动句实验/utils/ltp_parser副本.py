# -*- coding: utf-8 -*
from ltp import LTP
from tqdm import tqdm
import os

ltp = LTP()
# os.environ["CUDA_VISIBLE_DEVICES"] = 2

def open_amr_txt(filepath):
    news_data = []
    ff = open(filepath, "r", encoding="utf8")
    while True:
        line = ff.readline()
        if not line:
            break
        if len(line.strip()) == 0 or line == '\n':
            continue
        if "::snt" in line:
            tokens = line.strip().split()
            if len(tokens) > 2:
                news_data.append(''.join(tokens[2:]))
    return news_data


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
    sent_dep_tag = ltp.dep(hidden)  # 依存句法分析
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
    sentence_core_is_verb = False   # 句子核心是否为动词
    sentence_core_idx = -1  #句子核心词索引

    for i in range(sentences_num):
        sentence_is_positive = False
        sentence_is_negative = False
        for sdp in sdp_list[i]:
            # 判断句子核心是否为动词
            if 'Root' in sdp[2] and pos_list[i][int(sdp[0]-1)] is 'v':
                sentence_core_is_verb = True
                sentence_core_idx = sdp[0]
        if not sentence_core_is_verb:
            f.write("其他" + ' # ' + ''.join(seg_list[i]) + ' # \n')
            continue

        for sdp in sdp_list[i]:
            if sdp[1] == sentence_core_idx:
                # 如果含有施事或当事，则为主动句
                if "AGT" in sdp[2] or "EXP" in sdp[2]:
                    sentence_is_positive = True
                    break
                elif "PAT" in sdp[2] or "CONT" in sdp[2]:
                    sentence_is_negative = True

        if sentence_is_positive:
            # print("主动句" + ' # ' + ''.join(seg_list[i]) + ' # ' + str(seg_list[i][sentence_core_idx-1]))
            f.write("主动句" + ' # ' + ''.join(seg_list[i]) + ' # ' + str(seg_list[i][sentence_core_idx-1]) + '\n')
        if sentence_is_negative:
            if "被" in seg_list[i]:
                f.write("被字句" + ' # ' + ''.join(seg_list[i]) + ' # ' + str(seg_list[i][sentence_core_idx - 1]) + '\n')
            else:
                f.write("被动句" + ' # ' + ''.join(seg_list[i]) + ' # ' + str(seg_list[i][sentence_core_idx - 1]) + '\n')
            # f.write(''.join(sent_tokens) + ' # ' + str(verb_arg1) + '\n')
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
    st = ["棉花姑娘说:“请你帮我捉害虫吧!”", "人类的命运掌握在自己的手中。", "小柳树看看自己，什么也没结。","李铁映等向第一批获得资格证书的代表颁证。"]
    test_file = "../data/res/1013实验结果/test.txt"
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


def newsmain(news_file):
    newsdata = open_news_txt(news_file)
    savefile = "../data/res/1013实验结果/人民日报199801抽取结果(5~6).txt"
    for i in tqdm(range(len(newsdata))):
        s = newsdata[i]
        ltp_data = data_parser([s])
        extract_info(ltp_data, savefile)


def amr_main():
    amr_file_data = open_amr_txt("../data/base/amr小学语文全.txt")
    save_file = "../data/res/1013实验结果/amr语文.txt"
    for i in tqdm(range(251, len(amr_file_data))):  # 321
        s = amr_file_data[i]
        ltp_data = data_parser([s])
        extract_info(ltp_data, save_file)


if __name__ == '__main__':
    # test()
    # main()
    # newsmain('../data/base/199801.txt')
    # amr_main()
    for i in range(5, 7):
        filename = "19980" + str(i) + ".txt"
        filepath = "../data/base/199801/" + filename
        newsmain(filepath)

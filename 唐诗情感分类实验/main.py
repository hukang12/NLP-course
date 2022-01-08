from preDo import *
import pandas as pd
from FileReadWrite import read_txt_file, read_seed_excel
import xlwt
from tqdm import tqdm


def tokenize():
    klm_filename = "jiayan_tokenizer/jiayan/jiayan.klm"
    df = pd.read_csv("data/未标注的全唐诗.csv", encoding="gb18030")
    data = df["内容"].tolist()
    tks = tokenize_data(data_list=data, mode="hmm", klm_file=klm_filename, remove_punc=False)
    save_token2txt(tks, "data/res/20211118/未标注唐诗分词文本2.txt")


def find_puc(tokens):
    punctuation = ['。', '！', '？', '；', '.', '!', ';', ':', '?', '、']    # , '，', ','
    for p in punctuation:
        if p in tokens:
            return tokens.index(p)
    return -1


def get_poem_with_target_words(poem_list, seed_list):
    res = {}
    for poem_id in tqdm(range(0, len(poem_list))):
        poem = poem_list[poem_id]
        poem_with_target_words = {}     # 诗歌含各类别种子词情况
        poem2wordlist = poem.split()     # 诗歌内容
        for seeds in seed_list:     # 大类或小类的种子词信息
            for key, seeds_value in seeds.items():  # 类别，种子词列表
                wl = []
                for w in seeds_value:
                    wl.append(w[0])     # 取出种子词列表
                target_words = list(set(poem2wordlist).intersection(set(wl)))
                if len(target_words) > 0:
                    target_words2sentence = []
                    for tw in target_words:
                        tw_idx = poem2wordlist.index(tw)
                        start_idx = find_puc(poem2wordlist[:tw_idx]) + 1
                        sentence_span = find_puc(poem2wordlist[tw_idx:]) + 1
                        if tw_idx + sentence_span - start_idx > 20:
                            continue
                        sentence_with_tw = poem2wordlist[start_idx:tw_idx+sentence_span]
                        sentence_with_tw = ''.join(sentence_with_tw)
                        target_words2sentence.append((tw, sentence_with_tw))

                    poem_with_target_words[key] = target_words2sentence
        res[poem] = poem_with_target_words
    return res


def save_res(res_data, save_path):
    workbook = xlwt.Workbook(encoding='utf-8')
    sheet = workbook.add_sheet("sheet0")
    sheet.write_merge(0, 0, 1, 7, "大类")
    sheet.write_merge(0, 0, 8, 28, "小类")
    row = ["诗歌内容", "哀", "恶", "惧", "好", '惊', '乐', '怒',
           '悲伤', '贬责', '恐惧', '赞扬', '惊奇', '尊敬', '快乐',
           '思', '安心', '相信', '喜爱', '愤怒', '烦闷', '憎恶',
           '怀疑', '失望', '慌', '疚', '羞', '妒忌'
           ]
    for i in range(0, len(row)):
        sheet.write(1, i, row[i])

    row_idx = 2
    for k, v in res_data.items():
        sheet.write(row_idx, 0, k)
        for label, word_list in v.items():
            if len(word_list) == 0:
                continue
            label_in_cols_idx = row.index(label)
            write_txt = str(word_list[0])
            for w_s in word_list:
                write_txt = '\n' + str(w_s)
            sheet.write(row_idx, label_in_cols_idx, write_txt)
        row_idx += 1
    workbook.save(save_path)


if __name__ == '__main__':
    tokens_file = "data/res/20211118/未标注唐诗分词文本2.txt"
    seeds_file = "data/res/seed/反选诗歌种子词.xlsx"
    save_file = "data/res/20211118/全唐诗分类候选1121.xlsx"
    # tokenize()

    data = read_txt_file(tokens_file)
    seeds_list = read_seed_excel(seeds_file)
    res = get_poem_with_target_words(data, seeds_list)
    save_res(res, save_file)
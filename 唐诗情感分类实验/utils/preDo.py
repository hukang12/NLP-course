import re
from tqdm import tqdm
import pandas as pd

from jiayan import load_lm
from jiayan import WordNgramTokenizer
from jiayan import CharHMMTokenizer

punctuation = '，。！？；：:,.!,;:?、"\''


# 去除标点符号
def remove_punctuation(text):
    text = re.sub(r'[{}]+'.format(punctuation), '', text)
    return text.strip()


# 甲言ngram分词
def ngram_tokenize(text):
    tokenizer = WordNgramTokenizer()
    return list(tokenizer.tokenize(text))


# 甲言hmm分词
def hmm_tokenize(text, klm_file):
    lm = load_lm(klm_file)
    tokenizer = CharHMMTokenizer(lm)
    return list(tokenizer.tokenize(text))


# 封装分词函数
def tokenize_data(data_list, mode=None, klm_file=None):
    tokens_list = []
    if mode is None:
        for data in data_list:
            sentence_token = list(data)
            tokens_list.append(remove_punctuation(' '.join(sentence_token)))
    elif mode == "ngram":
        for i in tqdm(range(len(data_list))):
            data = data_list[i]
            # 分词
            sentence_token = ngram_tokenize(data)
            tokens_list.append(remove_punctuation(' '.join(sentence_token)))
    elif mode == 'hmm':
        for i in tqdm(range(len(data_list))):
            data = data_list[i]
            # 分词
            sentence_token = hmm_tokenize(data, klm_file)
            tokens_list.append(remove_punctuation(' '.join(sentence_token)))
    else:
        print("get_tokens（）参数错误！")

    return tokens_list


# 保存分词结果到文本
def save_token2txt(tokens_list, save_file):
    f = open(save_file, 'w+', encoding="utf8")
    for tokens in tokens_list:
        f.write(str(tokens) + '\n')
    f.close()


def tokenize_1600():
    data_file = "../data/1600/1600标注唐诗.csv"
    klm_file = "../data/jiayan/jiayan.klm"
    df = pd.read_csv(data_file)
    sentence_list = df["内容"].tolist()
    tokens = tokenize_data(sentence_list, "hmm", klm_file)
    save_token2txt(tokens, "../data/res/1600分词(hmm).txt")


if __name__ == '__main__':
    tokenize_1600()
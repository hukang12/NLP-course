import re
import operator
from tqdm import tqdm
import pandas as pd
from collections import Counter
from jiayan import load_lm
from jiayan import WordNgramTokenizer
from jiayan import CharHMMTokenizer

punctuation = '，。！？；：:,.!,;:?、"\''


# 读取txt
def read_txt_file(filename):
    data_list = []
    f = open(filename, 'r', encoding="utf8")
    lines = f.readlines()
    for line in lines:
        data_list.append(line.strip())

    f.close()
    return data_list


# 构建词表、统计词频
def construct_vocab(lexicon, save_csv_file, stop_word_file):
    stopwords = read_txt_file(stop_word_file)
    all_words = []

    for poem in lexicon:
        all_words.extend(poem.split())

    res = Counter(all_words)
    vocab = dict(res)
    vocab = sorted(vocab.items(), key=operator.itemgetter(1), reverse=True)
    vocab_list = []
    for i in vocab:
        if i[0] in stopwords:
            continue
        vocab_list.append([i[0], i[1]])
    df = pd.DataFrame(columns=['单词', '词频'], data=vocab_list)
    df.to_csv(save_csv_file)


# 去除标点符号
def remove_punctuation(text):
    text = re.sub(r'[{}]+'.format(punctuation), '', text)
    return text.strip()


# 甲言ngram分词
def ngram_tokenize(text):
    tokenizer = WordNgramTokenizer()
    return list(tokenizer.tokenize(text))


# 甲言hmm分词（分词效果更好）
def hmm_tokenize(text, klm_file):
    lm = load_lm(klm_file)
    tokenizer = CharHMMTokenizer(lm)
    return list(tokenizer.tokenize(text))


# 封装分词函数
def tokenize_data(data_list, mode=None, klm_file=None, remove_punc=False):
    tokens_list = []
    if mode is None:
        for data in data_list:
            sentence_token = list(data)
            sentence_token = ' '.join(sentence_token)
            if remove_punc:
                sentence_token = remove_punctuation(sentence_token)

            tokens_list.append(sentence_token)
    elif mode == "ngram":
        for i in tqdm(range(len(data_list))):
            data = data_list[i]
            # 分词
            sentence_token = ngram_tokenize(data)
            sentence_token = ' '.join(sentence_token)
            if remove_punc:
                sentence_token = remove_punctuation(sentence_token)

            tokens_list.append(sentence_token)
    elif mode == 'hmm':
        for i in tqdm(range(len(data_list))):
            data = data_list[i]
            # 分词
            sentence_token = hmm_tokenize(data, klm_file)
            sentence_token = ' '.join(sentence_token)
            if remove_punc:
                sentence_token = remove_punctuation(sentence_token)

            tokens_list.append(sentence_token)
    else:
        print("get_tokens（）参数错误！")

    return tokens_list


# 保存分词结果到文本
def save_token2txt(tokens_list, save_file):
    f = open(save_file, 'w+', encoding="utf8")
    for tokens in tokens_list:
        f.write(str(tokens) + '\n')
    f.close()


# 对需分词的文本进行分词并统计词频
def my_tokenize(data_file, save_tokenized_file, save_vocab_file, stop_words, remove_punc=False, ):
    klm_file = "jiayan/jiayan.klm"
    df = pd.read_csv(data_file, encoding='gbk')
    sentence_list = df["内容"].tolist()
    tokens = tokenize_data(sentence_list, "hmm", klm_file, remove_punc)
    save_token2txt(tokens, save_tokenized_file)
    construct_vocab(tokens, save_vocab_file, stop_words)


if __name__ == '__main__':
    stop_words = "data/stopword(标点).txt"
    data_file_lb = "data/李白.csv"
    data_file_df = "data/杜甫.csv"

    save_tokenized_file_lb = "res/李白_分词.txt"
    save_tokenized_file_df = "res/杜甫_分词.txt"

    save_file_lb = "res/词频_李白(只去除标点).csv"
    save_file_df = "res/词频_杜甫(只去除标点).csv"

    my_tokenize(data_file=data_file_lb,
                save_tokenized_file=save_tokenized_file_lb,
                save_vocab_file=save_file_lb,
                stop_words=stop_words)

    my_tokenize(data_file=data_file_df,
                save_tokenized_file=save_tokenized_file_df,
                save_vocab_file=save_file_df,
                stop_words=stop_words)

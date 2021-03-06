import re
import operator
from tqdm import tqdm
import pandas as pd
from collections import Counter
from FileReadWrite import read_csv_file, read_txt_file
from jiayan import load_lm
from jiayan import WordNgramTokenizer
from jiayan import CharHMMTokenizer
from jiayan import PMIEntropyLexiconConstructor

punctuation = '，。！？；：:,.!,;:?、"\''


# 构建词库
def construct_vocab(lexicon, save_csv_file):
    constructor = PMIEntropyLexiconConstructor()
    constructor.MIN_WORD_FREQ = 2
    lexicon = constructor.construct_lexicon(lexicon)
    constructor.save(lexicon, save_csv_file)


# 构建词库2
def construct_vocab_2(lexicon, save_csv_file, stop_word_file):
    stopwords = read_txt_file(stop_word_file)
    data = read_csv_file(filename=lexcion, column_name=['分词'])['分词']
    all_words = []

    for poem in data:
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


# 甲言hmm分词
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


# 对CSV文本进行分词
def tokenize_1600(remove_punc=False):
    data_file = "../data/1600/1600标注唐诗.csv"
    klm_file = "../jiayan_tokenizer/jiayan/jiayan.klm"
    df = pd.read_csv(data_file)
    sentence_list = df["内容"].tolist()
    tokens = tokenize_data(sentence_list, "hmm", klm_file, remove_punc)
    save_token2txt(tokens, "../data/res/1600分词(不去标点).txt")


if __name__ == '__main__':
    # tokenize_1600(remove_punc=False)
    lexcion = "../data/1600/1600标注唐诗.csv"
    df_save_file = "词频_杜甫.csv"
    lb_save_file = "词频_李白.csv"
    stop_words = "../data/stopword.txt"
    construct_vocab_2(lexcion, save_file, stop_words)
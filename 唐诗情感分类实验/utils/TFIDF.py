from collections import defaultdict
import math
import operator
import xlrd
import xlwt
from xlutils.copy import copy

from FileReadWrite import *



# 使用词表过滤
def who_in_vocab(vocab, words):
    real_word = []
    for word in words:
        if word in vocab:
            real_word.append(word)
    return real_word


# 去除单音节词
def danyinjie(word_list):
    new_words = []
    for word in word_list:
        if len(word) > 1:
            new_words.append(word)
    return new_words


# 加载唐诗三百首数据
def data_load(tokenized_file, vocab_file=None):
    vocab_words = read_excel_file(filename=vocab_file, sheet_id=0, column_id_list=[0])
    print(len(vocab_words))

    tang1600 = read_csv_file(tokenized_file, ["分词", "小类", "大类"])
    tokenized_poems = tang1600["分词"]
    poem_tiny_label = tang1600["小类"]
    poem_big_label = tang1600["大类"]
    poem_num = len(tokenized_poems)

    big_label_docs = dict()
    tiny_label_docs = dict()

    for i in range(poem_num):
        content = tokenized_poems[i].split()
        content = who_in_vocab(vocab_words, content)
        # content = danyinjie(content)
        tiny_label = poem_tiny_label[i]
        big_label = poem_big_label[i]

        # 相同类别的诗歌写入同一个文档
        if tiny_label not in tiny_label_docs.keys():
            tiny_label_docs[tiny_label] = list()

        tiny_label_docs[tiny_label].extend(content)

        if big_label not in big_label_docs.keys():
            big_label_docs[big_label] = list()

        big_label_docs[big_label].extend(content)

    '''
       # 每个文档的词表
        if label not in doc_vocab.keys():
            doc_vocab[label] = set()
        temp_set = set(content)
        doc_vocab[label] = doc_vocab[label] | temp_set
    return doc_data, doc_vocab
       '''
    return big_label_docs, tiny_label_docs


# 统计一篇文档中每个词的词频
def get_word_freq(doc_data):
    word_freq = {}
    # words_num = len(doc_data)
    # if words_num <= 0:
    #     print("诗歌长度为0！")
    #     return None

    for word in doc_data:
        if str(word) in word_freq.keys():
            count = word_freq[str(word)]
            word_freq[str(word)] = count + 1
        else:
            word_freq[str(word)] = 1
    # for k, v in word_freq.items():
    #     word_freq[k] = v/words_num
    return word_freq


# 统计某单词出现的文档数
def doc_freq(word, docs):
    count = 0
    for doc in docs:
        if word in doc:
            count += 1

    return count


# 计算tfidf
def get_tf_idf(doc_list):
    final_res = {}
    doc_num = len(doc_list.keys())  # 语料库总数
    for cls, doc in doc_list.items():
        word_tf_idf = {}    # 该文档中的词的TFIDF值
        words_freq = get_word_freq(doc)
        words_num = len(doc)
        for i, v in words_freq.items():
            word_tf = v/words_num
            doc_have_word = doc_freq(i, doc_list.values())
            word_idf = math.log(doc_num / doc_have_word + 1)
            tf_idf = word_tf * word_idf
            word_tf_idf[i] = [tf_idf, words_freq[i], doc_have_word]
        top_of_tfidf = select_top(word_tf_idf, 50)
        final_res[cls] = top_of_tfidf
    return final_res


# 选择tfidf值最高的n个
def select_top(tfidf_dict, top_num):
    top_tfidf = []
    word_of_doc = sorted(tfidf_dict.items(), key=operator.itemgetter(1), reverse=True)
    count = 0
    for i in range(len(word_of_doc)):
        top_tfidf.append(word_of_doc[i])
        count += 1
        if count == top_num:
            break
    return top_tfidf


# 保存结果至Excel
def save2excel(save_data, save_path):
    try:
        old_excel = xlrd.open_workbook(save_path, formatting_info=True)
        sheet_num = len(old_excel.sheets())
        workbook = copy(old_excel)
        sheet = workbook.add_sheet("sheet" + str(sheet_num))
    except FileNotFoundError:
        workbook = xlwt.Workbook(encoding='utf-8')
        sheet = workbook.add_sheet("sheet0")


    class_idx = 0
    for k, v in save_data.items():
        class_idx += 1
        sheet.write_merge(0, 0, 4 * class_idx - 4, 4 * class_idx - 1, k)
        row = ["单词", "tf-idf值", "词频", "含此词的类别数"]
        for i in range(0, len(row)):
            sheet.write(1, 4 * class_idx - 4 + i, row[i])

        num = 2
        for tp in v:
            sheet.write(num, 4 * class_idx - 4, tp[0])
            sheet.write(num, 4 * class_idx - 3, tp[1][0])
            sheet.write(num, 4 * class_idx - 2, tp[1][1])
            sheet.write(num, 4 * class_idx - 1, tp[1][2])
            num += 1

    workbook.save(save_path)


def parse_res(doc_vocab, word_features):
    ress = {}
    for k, v in doc_vocab.items():
        # print("大类类型：", k)
        top30 = []
        word_of_doc = {}
        for word in v:
            word_of_doc[word] = word_features[word]
        word_of_doc = sorted(word_of_doc.items(), key=operator.itemgetter(1), reverse=True)
        count = 0
        for i in range(len(word_of_doc)):
            top30.append(word_of_doc[i])
            count += 1
            if count == 30:
                break
        ress[k] = top30
    return ress


if __name__ == '__main__':
    data_set = data_load("data/1600/1600标注唐诗.csv")
    print("文档数目:", len(data_set))
    features = get_tf_idf(data_set)  # 所有词的TF-IDF值
    # res = parse_res(label_set, features)
    save_path = '../data/res/唐诗三百首TF-IDF.xls'
    save2excel(features, save_path)

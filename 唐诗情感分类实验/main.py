from TFIDF import *

vocab_file = "data/1600/全唐诗词表.xlsx"
# vocab_words = read_excel_file(filename=vocab_file, sheet_id=0, column_id_list=[0])
# print(len(vocab_words))

tokenized_file = "data/1600/1600标注唐诗.csv"
tang1600_big, tang1600_tiny = data_load(tokenized_file, vocab_file=vocab_file)
features_big = get_tf_idf(tang1600_big)  # 所有词的TF-IDF值
features_tiny = get_tf_idf(tang1600_tiny)  # 所有词的TF-IDF值
save_path = 'data/res/唐诗三百首TF-IDF(全音节).xls'
save2excel(features_big, save_path)
save2excel(features_tiny, save_path)
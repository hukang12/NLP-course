import random
import os
import xlrd
import xlwt


def get_bei_data(bei_file):
    data = {}
    f = xlrd.open_workbook(bei_file)
    for i in range(3):
        sheet = f.sheets()[i]
        sent_list = []
        for j in range(1, sheet.nrows):
            sentence = sheet.row_values(j)[1]
            sent_list.append(sentence)
        data[i] = sent_list
    return data


def data_split(raw_data, val_size=2, test_size=2):
    train_data = []
    val_data = []
    test_data = []
    for label, data_list in raw_data.items():
        data_len = len(data_list)
        train_size = round(data_len/10) * (10-test_size-val_size)
        val_data_size = round(data_len/10) * val_size
        for i in range(0, train_size):
            train_data.append(data_list[i]+'\t'+str(label))
        for j in range(train_size, train_size + val_data_size):
            val_data.append(data_list[j] + '\t' + str(label))
        for k in range(train_size + val_data_size, data_len):
            test_data.append(data_list[k]+'\t'+str(label))
    random.shuffle(train_data)
    random.shuffle(val_data)
    random.shuffle(test_data)
    return train_data, val_data, test_data


def save2txt(data, save_file):
    f = open(save_file, "w+", encoding="utf8")
    for line in data:
        f.write(line+'\n')
        # f.write(line + '\t-1\n')
    f.close()


def main():
    data_dir = "../data/bdj/data"
    split_file = "../data/bdj/无标记、有标记、主动句数据集1014.xlsx"
    data = get_bei_data(split_file)
    train_data, val_data, test_data = data_split(data, 2, 2)
    save2txt(train_data, os.path.join(data_dir, "train.txt"))
    save2txt(val_data, os.path.join(data_dir, "dev.txt"))
    save2txt(test_data, os.path.join(data_dir, "test.txt"))


if __name__ == '__main__':
    main()
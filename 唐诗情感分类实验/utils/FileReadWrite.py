import pandas as pd
import xlrd
import xlwt


# 读取csv
def read_csv_file(filename, column_name):
    data_dict = {}
    df = pd.read_csv(filename)
    for col in column_name:
        data_dict[col] = df[col].tolist()
    return data_dict


# 读取Excel文件
def read_excel_file(filename, sheet_id, column_id_list):
    data_list = []
    xl = xlrd.open_workbook(filename)
    sheet = xl.sheets()[sheet_id]
    for i in range(1, sheet.nrows):
        for column_id in column_id_list:
            data_list.append(sheet.row_values(i)[column_id])
    return data_list


# 读取txt
def read_txt_file(filename):
    data_list = []
    f = open(filename)
    lines = f.readlines()
    for line in lines:
        data_list.append(line.strip())

    f.close()
    return data_list


# list写入文本
def list2txt(datalist, txt_filename):
    f = open(txt_filename, 'w+', encoding="utf8")
    for line in datalist:
        f.write(str(line) + '\n')
    f.close()


if __name__ == '__main__':
    pass
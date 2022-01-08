# -*- coding: utf-8 -*-
import pandas as pd
import xlrd
import xlwt


# 读取csv
def read_csv_file(filename, column_name):
    data_dict = {}
    df = pd.read_csv(filename , encoding='GB18030') #
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


# 读取种子候选词文件
def read_seed_excel(filename):
    """
    :param filename:种子候选词文件
    :return: all_sheet_seeds
    """
    all_sheet_seeds = []
    xl = xlrd.open_workbook(filename)  # , formatting_info=True
    for sheet in xl.sheets():
        # sheet = xl.sheets()[0]
        total_rows = sheet.nrows    # 表格总数据行数
        data_content = {}
        # 获取表格中所有合并单元格位置，以列表形式返回 （起始行，结束行，起始列，结束列）
        merged_cell = sheet.merged_cells

        for (min_row, max_row, min_col, max_col) in merged_cell:
            word_list = []
            merge_cell_value = sheet.cell_value(min_row, min_col)   # 合并单元格的内容
            at_last_line = False
            for row_idx in range(max_row + 1, total_rows):
                item_content = []
                for col_idx in range(min_col, max_col):
                    cell_txt = sheet.cell_value(row_idx, col_idx)
                    if cell_txt is '':
                        at_last_line = True
                        break
                    item_content.append(cell_txt)
                if at_last_line:
                    break
                word_list.append(item_content)

            data_content[merge_cell_value] = word_list
        all_sheet_seeds.append(data_content)
    return all_sheet_seeds


# 读取txt
def read_txt_file(filename):
    data_list = []
    f = open(filename, 'r', encoding="utf8")
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
    read_seed_excel("../data/res/唐诗1600全类多音节TF-IDF.xlsx")
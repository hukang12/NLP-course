import re

stn = ["南京", "师范", "大学"]
wid = []

str1 = ["x1_x2_x3", "x1_1_x2_2", "x1"]

for str in str1:
    a = str.split('_')
    if len(a) > 1:
        temp_word = []
        for i in a:
            if 'x' in i:
                word_order = int(i.split('x')[1])
                last_order = word_order
                temp_word.append(stn[word_order-1])
            else:
                word_inner_order = int(i)
                temp_word[-1] = temp_word[-1][word_inner_order-1]
        print(temp_word, last_order)
    else:
        last_order = int(a[0].split('x')[1])
        print(stn[last_order-1])

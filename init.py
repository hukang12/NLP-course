import re
'''


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
'''


def maxEvents(events):
    events = sorted(events, key=lambda x: (x[1], x[0]))  # 按最晚时间，最早时间两种元素进行排列
    arr2 = [False]
    count = 0
    for i in range(len(events)):
        for j in range(events[i][0], events[i][1] + 1):
            while len(arr2) <= j:
                arr2.append(False)  # 如果天数数组不够大，动态增加天数数组大小
            if arr2[j] == False:  # 判定在j天是否已经有会议安排
                arr2[j] = True
                count += 1
                break
    return count

events= [[1,2],[2,3],[3,4]]
print(maxEvents(events))


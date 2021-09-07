import numpy as np
import torch
import torch.nn as nn
from torch.autograd import Variable


# 自定义
import drr.models as DrrModels
import drr.utils as DrrUtils

# Hyper Parameters
EPOCH = 4  # 练整批数据多少次, 为了节约时间, 我们只训练一次
BATCH_SIZE = 50  # 把数据集分批 每批80个句子
LR = 1e-3  # 学习率


class RunRnnatt17:
    def __init__(self, opts):
        self.train_path = opts['train_path']
        self.test_path = opts['test_path']
        # self.dev_path = opts['dev_path']
        self.model_path = opts['model_path']

    def runTrain(self):
        # 传给DrrUtils.Utils的参数：train_path:data/train.raw.txt
        #                         path:data/train.raw.txt
        sentences, dict = (DrrUtils.Utils({
            'train_path': self.train_path,
            'path': self.train_path,
            'batch_size': BATCH_SIZE
        })).getRnnAtt17SentencesAndDict()

        RNNAtt17Model = DrrModels.RNNAtt17({
            'vocab_size': len(dict['word2id'])
        })
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(RNNAtt17Model.parameters(), lr=LR)
        print("-----训练-----------")
        for epoch in range(EPOCH):
            print('epoch: {}'.format(epoch + 1))
            print('****************************')
            running_loss = 0
            # sentenceArr:一个（80,256）的矩阵
            sentenceArr = np.zeros((BATCH_SIZE, 256))
            # labelArr:一个（80,1）的矩阵
            labelArr = np.zeros((BATCH_SIZE, 1))
            typelabelArr = np.zeros((BATCH_SIZE, 1))
            data_count_train=0
            step = 0

            for data in sentences:
                sentence, label, type_label = data
                labelArr[step] = np.array([label])
                typelabelArr[step] = np.array([type_label])
                sentenceArr[step] = sentence

                if ((step + 1) % BATCH_SIZE == 0):
                    sentenceArr = Variable(torch.LongTensor(sentenceArr))
                    labelArr = Variable(torch.LongTensor(labelArr))


                    out = RNNAtt17Model(sentenceArr)

                    _, predict_label_train = torch.max(out, 1)
                    # print('predict_label_train')
                    # print(predict_label_train)
                    # print("实际：",labelArr.squeeze_())
                    loss = criterion(out, labelArr.squeeze_())
                    # print('sentence',sentence)
                    running_loss += loss.data.item()

                    print('loss')
                    print(loss.data.item())

                    # backward
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()
                    sentenceArr = np.zeros((BATCH_SIZE, 256))
                    labelArr = np.zeros((BATCH_SIZE, 1))
                    step = -1

                step += 1
                data_count_train+=1
            print('Loss: {:.6f}'.format(running_loss / len(sentences)))
            torch.save(RNNAtt17Model, 'saved_models/'+str(epoch)+'.pkl')

    def runTest(self):
        # 预测
        TP=0
        FP=0
        FN=0
        TN=0
        fw=open('result/judge_result_sun3.txt','w',encoding='UTF-8')
        '''
        sentences, dict = (DrrUtils.Utils({
            'train_path': self.train_path,
            'path': self.test_path,
            'batch_size': BATCH_SIZE
        })).getSentencesAndDict()

        '''

        sentences, dict = (DrrUtils.Utils({

            'train_path': self.train_path,
            # 'test_path':self.test_path,
            'path': self.test_path,
            'batch_size': BATCH_SIZE
        })).getRnnAtt17SentencesAndDict()

        id2label = dict['id2label']
        id2typelabel=dict['id2type_label']
        id2word=dict['id2word']
        # print(id2label)

        # 加载模型
        RNNAtt17Model = torch.load(self.model_path)


        sentenceArr = np.zeros((BATCH_SIZE, 256))
        labelArr = np.zeros((BATCH_SIZE, 1))
        type_labelArr=np.zeros((BATCH_SIZE, 1))
        labelArr1=[0 for _ in range(BATCH_SIZE)]

        step = 0
        true_count = 0
        data_count_test=0
        for data in sentences:
            sentence, label ,type_label= data

            labelArr1[step]=label
            type_labelArr[step]=type_label
            labelArr[step] = np.array([label])
            sentence = np.array(sentence)
            sentence.resize((256,))
            # print(type(sentenceArr))
            sentenceArr[step] = sentence

            if ((step + 1) % BATCH_SIZE == 0):
                print('标签',labelArr1)
                # print('labelArr')
                # print(labelArr)
                sentenceArr = Variable(torch.LongTensor(sentenceArr))

                out = RNNAtt17Model(sentenceArr)#预测结果

                # axis = 0 按列 axis = 1 按行
                # print(55555555555)
                # print(out)
                _, predict_label = torch.max(out, 1)

                print('预测',predict_label)

                j=0



                for i in predict_label.numpy():

                    # id2label[i]预测的标签m

                    if (i == labelArr1[j]):
                        true_count += 1
                    else:
                        sentence_list = []
                        for id_word in sentenceArr[j]:
                            if id_word!=0:
                                sentence_list.append(id2word[int(id_word)])
                        sentence = ' '.join(sentence_list)
                        fw.write('预测：' + id2label[predict_label.numpy().tolist()[j]] + '|||' + id2label[
                            labelArr1[j]] + '|||' +
                                 id2typelabel[int(type_labelArr[j])] + '|||' + sentence + '\n')
                    if labelArr1[j]==1 and i==1:
                        TP+=1
                    if labelArr1[j]==1 and i==0:
                        FN+=1
                    if labelArr1[j]==0 and i==0:
                        TN+=1
                    if labelArr1[j]==0 and i==1:
                        FP+=1

                    # 预测-真实
                    # print(id2label[i] + '-' + id2label[labelArr1[j]])
                    # print(id2label[i] )
                    # print(id2label[labelArr1[j]])

                    # sentence_list=[]
                    # for id_word in sentenceArr[j]:
                    #     if id_word!=0:
                    #         sentence_list.append(id2word[int(id_word)])

                    #sentence=' '.join(sentence_list)
                    # print(id2label[i])
                    # print(id2typelabel[int(type_labelArr[j])])
                    j+=1
                # print(true_count)
                sentenceArr = np.zeros((BATCH_SIZE, 256))
                labelArr = np.zeros((BATCH_SIZE, 1))
                step = -1

            elif data_count_test == sentences.shape[0] - 1:#这里是剩下的
                sentenceArr_dev1 = Variable(torch.LongTensor(sentenceArr))
                out = RNNAtt17Model(sentenceArr_dev1)
                _, predict_label = torch.max(out, 1)
                # j = 0
                for c in range(sentences.shape[0] % BATCH_SIZE):
                    # print(type(predict_label.numpy().tolist()))
                    if predict_label.numpy().tolist()[c] == labelArr1[c]:
                        true_count += 1
                    else:
                        sentence_list = []
                        for id_word in sentenceArr[c]:
                            if id_word != 0:
                                sentence_list.append(id2word[int(id_word)])
                        sentence = ' '.join(sentence_list)
                        fw.write(
                            '预测：' + id2label[predict_label.numpy().tolist()[c]] + '|||' + id2label[labelArr1[c]] + '|||' +
                            id2typelabel[int(type_labelArr[c])] + '|||' + sentence + '\n')
                    if predict_label.numpy().tolist()[c] == 1 and labelArr1[c]==1:
                            TP += 1
                    if labelArr1[c] == 1 and predict_label.numpy().tolist()[c] == 0:
                            FN += 1
                    if labelArr1[c] == 0 and predict_label.numpy().tolist()[c] == 0:
                            TN += 1
                    if labelArr1[c] == 0 and predict_label.numpy().tolist()[c] == 1:
                            FP += 1

            #         sentence_list = []
            #         for id_word in sentenceArr[c]:
            #             if id_word != 0:
            #                 sentence_list.append(id2word[int(id_word)])
            #         sentence = ' '.join(sentence_list)
            #         fw.write('预测：' + id2label[predict_label.numpy().tolist()[c]] + '|||' + id2label[labelArr1[c]] +'|||'+ id2typelabel[int(type_labelArr[c])] + '|||' + sentence + '\n')
            data_count_test+=1
            step += 1
        print(TP)
        print(FP)
        print(TN)
        print(FN)
        p=TP/(TP+FP)
        r=TP/(TP+FN)
        f=2*p*r/(p+r)
        fw.write('p:'+str(p))
        fw.write('\n')
        fw.write('r'+str(r))
        fw.write('\n')
        fw.write('f1:'+str(f))
        fw.write('\n')
        print(p)
        print(r)
        print(f)
        print('正确率：{:.4f}%'.format((true_count / len(sentences)) * 100))

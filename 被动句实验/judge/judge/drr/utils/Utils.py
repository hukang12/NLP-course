import torch
import numpy as np

from torch.autograd import Variable
from drr.utils.BuildDict import BuildDict
from drr.utils.DataSet import DataSet


class Utils:
    def __init__(self, opts):
        self.batch_size = opts['batch_size']

        self.train_path = opts['train_path']
        # self.test_path = opts['test_path']
        self.path = opts['path']

    def getRnnAtt17SentencesAndDict(self):
        # 将train_path传给BuildDict
        # 然后跑里面的run函数
        # dict中包含四个内容
        # id2label:每个标签的id作为key,标签作为label
        # id2word:每个词的id作为key,词作为label
        # label2id:每个标签作为key,标签的id作为label
        # word2id:每个词作为key,词的id作为label
        dict = (BuildDict({
            'path': self.train_path
        })).run()

        sentences = (DataSet({
            'path': self.path,
            'dict_dict': dict,
            'batch_size': self.batch_size
        })).getRnnAtt17Sentences()

        return (sentences, dict)

    def getGrn16SentencesAndDict(self):
        dict = (BuildDict({
            'path': self.train_path
        })).run()

        DataSetModel = DataSet({
            'path': self.path,
            'dict_dict': dict,
            'batch_size': self.batch_size
        })

        arg1List, arg2List,labelList = DataSetModel.getGrn16Sentences()

        loader = DataSetModel.getGrn16TensorDataset({
            'arg1List': Variable(torch.from_numpy(np.array(arg1List))),
            'arg2List': Variable(torch.from_numpy(np.array(arg2List))),
            'labelList': Variable(torch.from_numpy(np.array(labelList))),
        })

        return (loader, dict)

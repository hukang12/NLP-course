import sys
import run
actions=['train', 'test']
# actions = ['test']
if __name__ == '__main__':

    # action = sys.argv[1]  # Choose action from cmd line. Options: train or test
    for action in actions:
        if action == 'train':
            print('训练')
            # 将train_path,test_path,model_path传给Runrnnatt17
            # 然后跑runTrain函数
            (run.RunRnnatt17({
                'train_path': 'data/train.txt',
                'test_path': 'data/test.txt',
                'model_path': 'saved_models/RNNAttMode.pkl'
            })).runTrain()
        else:
            print('测试')
            (run.RunRnnatt17({
                'train_path': 'data/train.txt',
                'test_path': 'data/test.txt',
                'model_path': 'saved_models/3.pkl'
            })).runTest()

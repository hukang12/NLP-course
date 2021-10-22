import gensim
from gensim.models import word2vec

sentences=word2vec.Text8Corpus('data/all_corpus.txt')
model=word2vec.Word2Vec(sentences,min_count=3, size=300, window=5, workers=6)
model.save('saved_models/new_model_big.txt')

#
# models = gensim.models.Word2Vec.load('saved_models/new_model_big.txt')
#
# print(models.most_similar(['school']))


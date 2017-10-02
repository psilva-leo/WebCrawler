import logging
# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
from optparse import OptionParser
from gensim import corpora, models, similarities
from collections import defaultdict
from pprint import pprint  # pretty-printer
import os
import json
import argparse


class Corpus(object):
    dictionary = None
    json_file = None

    def __init__(self, json_file, train=False):
        self.json_file = json_file
        self.load_dictionary(train)

    def preprocess_data(self):
        documents = []
        replace = ['(', ')', ',', ':', '.', ';', '?', '!', '"']
        content = open(self.json_file, 'r')
        for line in content:
            line = json.loads(line)['text']
            if line != '':
                for r in replace:
                    line = line.replace(r, '')
                documents.append(line)

        return documents

    def proccess_text(self, documents):
        stoplist = set('é o a e ao da das de des do dos na nas no nos em que um uma para'.split())
        texts = [[word for word in document.lower().split() if word not in stoplist]
                 for document in documents]
        frequency = defaultdict(int)
        for text in texts:
            for token in text:
                frequency[token] += 1

        texts = [[token for token in text if frequency[token] > 1]
                 for text in texts]

        return texts

    def load_dictionary(self, train):
        if os.path.isfile('./storage/deerwester.dict') and not train:
            self.dictionary = corpora.Dictionary.load('/tmp/deerwester.dict')
        else:
            if self.json_file is None:
                raise ValueError('Missing text input file (.json file)')

            documents = self.preprocess_data()
            texts = self.proccess_text(documents)
            self.dictionary = corpora.Dictionary(texts)
            self.dictionary.save('./storage/deerwester.dict')

    # Generator to make it memory efficient, it's basically iguals to preproccess_data, though
    def __iter__(self):
        if self.json_file is None:
            raise ValueError('Missing text input file (.json file)')

        replace = ['(', ')', ',', ':', '.', ';', '?', '!', '"']
        content = open(self.json_file, 'r')
        for line in content:
            line = json.loads(line)['text']
            if line != '':
                for r in replace:
                    line = line.replace(r, '')
                yield self.dictionary.doc2bow(line.lower().split())

def check_models():
    return (os.path.isfile('./storage/deerwester.mm')
        and os.path.isfile('./storage/deerwester.dict')
        and os.path.isfile('./storage/model.lsi'))

def train(train_file, n_topics):
    corpus = Corpus(train_file, train=True)
    dictionary = corpus.dictionary
    # for vector in corpus:
    #     print(vector)
    corpora.MmCorpus.serialize('./storage/deerwester.mm', corpus)

    tfidf = models.TfidfModel(list(corpus))
    corpus_tfidf = tfidf[corpus]

    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary,
                          num_topics=n_topics)  # initialize an LSI transformation
    # corpus_lsi = lsi[corpus_tfidf]
    lsi.save('./storage/model.lsi')

    index = similarities.MatrixSimilarity(lsi[list(corpus)])  # transform corpus to LSI space and index it
    index.save('./storage/deerwester.index')

def predict(predict_file):
    dictionary = corpora.Dictionary.load('./storage/deerwester.dict')
    corpus = corpora.MmCorpus('./storage/deerwester.mm')
    lsi = models.LsiModel.load('./storage/model.lsi')
    index = similarities.MatrixSimilarity.load('./storage/deerwester.index')

    for doc in process_file(predict_file):
        vec_bow = dictionary.doc2bow(doc.lower().split())
        vec_lsi = lsi[vec_bow]  # convert the query to LSI space
        vec_lsi = sorted(vec_lsi, key=lambda tup: -tup[1])

        sims = index[vec_lsi]  # perform a similarity query against the corpus
        sims = sorted(enumerate(sims), key=lambda item: -item[1])

        print('Predicted text\n' + '-'*50)
        print(doc)
        print('-'*50)
        print('Top five more similar')
        for i in range(5):
            info = json.loads(get_title_by_index(sims[i][0]))
            print("[{}] Similarity: {} Title: {}\nAbstract: {}".format(i+1, sims[i][1], info['title'], info['abstract']))

def get_title_by_index(index):
    content = open('text.jl', 'r')
    for i, line in enumerate(content):
        if i == index:
            return line

def process_file(file):
    replace = ['(', ')', ',', ':', '.', ';', '?', '!', '"']
    content = open(file, 'r')
    for line in content:
        line = json.loads(line)['text']
        if line != '':
            for r in replace:
                line = line.replace(r, '')
            yield line

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--train",
                  dest="train",
                  default=False,
                  help="Set to True to train the model.")
    parser.add_argument("--topics",
                  dest="n_topics",
                  default=5,
                  help="Number of topics.")

    parser.add_argument("--train_file",
                  dest="train_file",
                  default='text.jl',
                  help="Input file for training")

    parser.add_argument("--predict_file",
                  dest="predict_file",
                  default='predict.jl',
                  help="Input file for prediction")
    args = parser.parse_args()

    if args.train:
        train(args.train_file, args.n_topics)
    else:
        predict(args.predict_file)





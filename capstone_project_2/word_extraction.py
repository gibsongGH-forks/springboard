# -*- coding: utf-8 -*-
"""word_extraction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18dy5NDw4OdR_PWnj5enxPCaXnQccDZs1
"""

import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import time
import string
import spacy
from collections import Counter
import tensorflow as tf
import os
import matplotlib.pylab as plt
import spacy
from nltk.stem import PorterStemmer
from spacy.lang.en import STOP_WORDS
from sklearn.feature_extraction.text import TfidfVectorizer
#   from word2vec import W2VModelDownload
#  from word2vec import Word2Vec

class text_cleaning:
  #Cleaning the texts
  
  def __init__(self, df):
    self.df = df
    
  def remove_nonalpha(self):
    # lower the words, remove non-alphabetic words and extra blanks
    self.df['abstract'] = self.df['abstract'].str.replace("[^A-Za-z]", " ").str.lower()
    self.df['abstract'] = self.df['abstract'].str.replace("\\s+", " ")
    return self.df
  
  def remove_stopword(self):
    # remove the stopwords
    
    spacy_stopwords = STOP_WORDS
    self.df = self.remove_nonalpha()
    self.df['abstract'] = self.df['abstract'].apply(lambda x: ' '.join([word for word in x.split() if word not in spacy_stopwords]))
    return self.df

  
  def lemma_word(self):
    # lemmatize the words
    nlp = spacy.load('en_core_web_sm')
    self.df = self.remove_stopword()
    self.df['lemma_abstract'] = self.df['clean_abstract'].apply(lambda x: ' '.join([token.lemma_ for token in nlp(x)]))
    return self.df
  
  def stem_word(self):
    # stem the words 
    stemmer = PorterStemmer()
    self.df = self.lemma_word()
    self.df['stem_abstract'] = self.df['lemma_abstract'].apply(lambda x: ' '.join([stemmer.stem(token) for token in x.split()]))
    return self.df

  def key_words_tfidf(self, column):
    # Extract the key words by using tfidf and bigram
    # Use the tfidf to find top 10 words appearing in the seed patents. 
    # We assume those patents would include more synonyms to "purify water" or "filter water"
    tfidf = TfidfVectorizer(ngram_range=(1, 2))
    weights = tfidf.fit_transform(self.df[column])
    score = zip(tfidf.get_feature_names(),
              np.asarray(weights.sum(axis=0)).ravel())
    df_score = pd.DataFrame(score, columns=['feature', 'weight'])
    
    df_score['length'] = df_score['feature'].apply(lambda x: len(x.split()))
    top_feature = df_score[df_score['length'] == 2][['feature', 'weight']].sort_values(by='weight', ascending=False).head(10)
    return top_feature['feature'].tolist()

  def key_words_word2vec(self, bq_project, string, top_number=10):
    # extract the key words by using Word2Vec trained by Google Patents. 
    # Before running this program,  please include word2vec.py in your folder. 
    # You can download here: https://github.com/google/patents-public-data/blob/master/models/landscaping/word2vec.py
    # the model is stored here: https://console.cloud.google.com/storage/browser/patent_landscapes
    # use the pretrained model with 5.9 million pretrained model 
    model_name = '5.9m'
    model_download = W2VModelDownload(bq_project)
    model_download.download_w2v_model('patent_landscapes', model_name)
    word2vec5_9m = Word2Vec('5.9m')
    w2v_runtime = word2vec5_9m.restore_runtime()
    return w2v_runtime.find_similar(string, top_number)

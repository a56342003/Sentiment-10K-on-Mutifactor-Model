import os
import re
import time
import pickle
from collections import Counter
import numpy as np
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

####################################
###            VADER            ####              
####################################
def clean_mda(mda):
    mda = re.sub(r'[(),&/:; ]+',' ', mda)
    return re.sub(r'[^A-Za-z!?. ]+', '', mda)
    return mda

def vader_score(mda):
    senti_dict = {}
    mda = clean_mda(mda)
    tic = time.time()
    result_list = []
    n_pos = 0
    n_neg = 0
    n_neu = 0
    n_total_words = 0
    for sentence in mda.split('.'):
        n_words = len(sentence.split())
        if n_words < 3:
            continue
        n_total_words = n_total_words + n_words
        sentence_score = sia.polarity_scores(sentence)
        if sentence_score['compound'] > 0.05:
            n_pos = n_pos+1
        elif sentence_score['compound'] < -0.05:
            n_neg = n_neg+1
        else:
            n_neu = n_neu+1
        result_list.append((sentence_score, n_words))

    p_pos = 0
    p_neg = 0
    p_neu = 0
    senti_avg = 0
    n_sentence = 0
    for result in result_list:
        p_pos = p_pos + (result[0]['pos']*result[1]/n_total_words)
        p_neg = p_neg + (result[0]['neg']*result[1]/n_total_words)
        p_neu = p_neu + (result[0]['neu']*result[1]/n_total_words)
        senti_avg = senti_avg + result[0]['compound']
        n_sentence = n_sentence + 1
    if n_sentence != 0:
        senti_avg=senti_avg/n_sentence
    else:
        senti_avg=np.nan
        
    senti_dict['avg'] = senti_avg
    senti_dict['p_pos'] = p_pos
    senti_dict['p_neg'] = p_neg
    senti_dict['p_neu'] = p_neu
    senti_dict['n_pos'] = n_pos
    senti_dict['n_neg'] = n_neg
    senti_dict['n_neu'] = n_neu
    senti_dict['n_sentence'] = n_sentence
    senti_dict['n_words'] = n_total_words
    senti_dict['full sentence scores'] = result_list
    '''
    toc = time.time()
    print('Time used: {}'.format(toc-tic))
    print('Amount of words: {}'.format(n_total_words))
    print('Proportion:')
    print('    pos: {}\n    neg: {}\n    neu: {}'.format(p_pos,p_neg,p_neu))
    print('Number of ___ sentence:')
    print('    pos: {}\n    neg: {}\n    neu: {}'.format(n_pos,n_neg,n_neu))
    '''
    return senti_dict
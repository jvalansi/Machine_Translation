'''
Created on Aug 26, 2014

@author: jordan_weizmann
'''
import math
import nltk

def calc_precision(n,translation, reference):
    tra_ngrams = nltk.ngrams(translation, n)
    ref_ngrams = nltk.ngrams(reference, n)
    correct = set(tra_ngrams) & set(ref_ngrams)
    precision = float(len(correct))/min(len(ref_ngrams),len(tra_ngrams))
    return(precision)
    
def calc_bleu(translation, reference):
    bleu = {}
    for n in range(1,5):
        bleu[n] = calc_precision(n,translation, reference)
        if(bleu[n] == 0):
            return 0
    if (len(translation) < len(reference)):
        brevity_penalty = math.exp(1-float(len(reference))/len(translation));
    else:
        brevity_penalty = 1
    score = brevity_penalty * \
            math.exp((math.log( bleu[1] ) + \
                      math.log( bleu[2] ) + \
                      math.log( bleu[3] ) + \
                      math.log( bleu[4] ) ) / 4) ;
    return((score,brevity_penalty,bleu[1],bleu[2],bleu[3],bleu[4]))


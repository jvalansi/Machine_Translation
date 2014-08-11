'''
Created on Aug 8, 2014

@author: jordan_weizmann
'''
import nltk
import argparse
import time
from itertools import permutations

def lm2dict(lm, e):
    e = set(e.split())
    p = permutations(e,3)
    lm_dict = {}
    cnt = 0
    for i in p:
        cnt += 1
        if(cnt%1000000==0):
            print("cnt " + str(cnt) + ": " + time.strftime('%X'))
        lm_dict[i] = lm.logprob(i[2], [i[0],i[1]])
    return(lm_dict)

def get_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-e','--english_text', type=argparse.FileType('r+'), 
                       help='File containing the english text.')
    return(parser.parse_args())

if __name__ == '__main__':

    args = get_args()
    e = args.english_text.read();

    tokens = list(nltk.corpus.genesis.words('english-kjv.txt')) #TODO: use different corpuses 
    estimator = lambda fdist, bins: nltk.probability.LidstoneProbDist(fdist, 0.2)
    lm = nltk.model.ngram.NgramModel(3,tokens,True,False,estimator)
    lm_dict = lm2dict(lm, e)

    f = open('lm', 'w')
    s = ""
    for l in lm_dict:
        s += str(l)+ " => " + str(lm_dict[l]) + "\n"
    f.write(s)
    f.close()


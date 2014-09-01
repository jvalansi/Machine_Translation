'''
Created on Aug 26, 2014

@author: jordan_weizmann
'''
import math
import nltk

def calc_precision(n,translation, reference):
    total = 0
    correct = 0
    for i in range(len(translation)):
        tra_ngrams = nltk.ngrams(translation[i].split(), n)
        ref_ngrams = nltk.ngrams(reference[i].split(), n)
        total += min(len(ref_ngrams),len(tra_ngrams))
        for ng in tra_ngrams:
            if(ng in ref_ngrams):
                correct += 1
    print("total:" + str(total)+ ", correct: "+ str(correct))
    if(total == 0):
        return(0)
    precision = float(correct)/total
    return(precision)

def calc_brev(translation, reference):
    tra_len = 0
    ref_len = 0
    for i in range(len(translation)):
        tra_len += len(translation[i].split())
        ref_len += len(reference[i].split())
    return(min(1,math.exp(1-float(ref_len)/tra_len)))
    
def calc_bleu(translation, reference):
    bleu = {}
    for n in range(1,5):
        bleu[n] = calc_precision(n,translation, reference)
        if(bleu[n] == 0):
            return 0
    brevity_penalty = calc_brev(translation, reference)
    score = brevity_penalty * \
            math.exp((math.log( bleu[1] ) + \
                      math.log( bleu[2] ) + \
                      math.log( bleu[3] ) + \
                      math.log( bleu[4] ) ) / 4) ;
    return((score,brevity_penalty,bleu[1],bleu[2],bleu[3],bleu[4]))

if __name__ == '__main__':
    rf = open('test set/text.eng', 'r')
    references = rf.readlines()
    tf = open('translation', 'r')
    translations = tf.readlines()
    print(calc_bleu(translations, references))
    for i in range(len(translations)):
        print(str(i)+': '+str(calc_bleu([translations[i]], [references[i]])))
    rf.close()

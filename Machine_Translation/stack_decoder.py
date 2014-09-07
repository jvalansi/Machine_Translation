'''
Created on Aug 4, 2014

@author: jordan_weizmann
'''
import argparse
import re
import time
import nltk
import heapq
import os
import logging
import math
import numpy
import sys

logger_dict = {}


def lines2lattice(ll,lm,lm_dict):
    ln=0
    ng = args.n_gram
#     lattice += str(i) + "-" + str(j-1) + ": " + " ".join(phrase) +"\n"
    f_pattern = "^(\d+)-(\d+):((?:\s\S+)*)$"
#     lattice += " ".join(p) + " " + phrases[phrase][p] + "\n"
    e_pattern = "^((?:\S+\s)*)(-?\d+(?:\.\d+)?)$"
    lattice = []
    for l in ll:
            m = re.match(f_pattern,l)
            if(m):
                f = tuple(range(int(m.group(1)),int(m.group(2))+1))
                ln = max(max(f)+1,ln)
            m = re.match(e_pattern, l)
            if(m):
                e = tuple(m.group(1).split())
                p_LM = 0
                for i in range(len(e)-(ng-1)):
#                     p_LM -= lm.logprob(e[i+2],[e[i],e[i+1]])
                    p_LM += get_prob(lm[ng],lm_dict,e[i:i+ng])
                phi = float(m.group(2))
                d = 0
                p = numpy.dot(args.lambda_value, [phi,p_LM,d])
                lattice.append((p,phi,p_LM,d,f,e))
    lattice.sort(reverse=True)
    return(ln, lattice)

def get_lm(ng):
    f = open('res/AV1611Bible.txt')
    words = f.read().split()
#     tokens = list(nltk.corpus.genesis.words('english-kjv.txt')) #TODO: use different corpuses
    tokens = list(words) #TODO: use different corpuses
    cfd = nltk.probability.ConditionalFreqDist()
    for t in nltk.ngrams(words, ng):
        condition = tuple(t[:-1])
        word = t[-1]
        cfd[condition][word] +=1
#     lm = nltk.probability.ConditionalProbDist(cfd, nltk.probability.LidstoneProbDist, 0.2)
    lm = nltk.probability.ConditionalProbDist(cfd, nltk.probability.WittenBellProbDist, len(words))
    return(lm)
    
def get_prob(lm,lm_dict,t):
    if t not in lm_dict:
        lm_dict[t] = lm[t[:-1]].logprob(t[-1]) 
        logger_dict['lm'].debug(str(t)+" : "+ str(lm_dict[t]))
    return(lm_dict[t])
#     return(lm[t[:-1]].logprob(t[-1]) )

def get_missing_ngram_prob(lm,lm_dict,e,e_):
    prob = 0
    ng = args.n_gram
    if(args.small_lm):
        e__ = e+e_
        for i in range(2,ng):
            prob += get_prob(lm[i],lm_dict,e__[:i])
    for i in range(1,ng):
        if(len(e) >= i and len(e_) >= ng-i):
            t = e[-i:]+e_[:ng-i]
            prob += get_prob(lm[ng],lm_dict,t)
    return(prob)

def decode(lattice,ln,lm,lm_dict):
#         print("decoding")
        stacks = {}
        uniques = {}
        for i in range(ln+1):
            stacks[i] = []
            uniques[i] = {}
        heapq.heappush(stacks[0], (0,0,0,0,(0,),('SOS',)))
        for s in stacks:
#             logger.debug(s)
            i=0
            for (p,q,r,d,f,e) in stacks[s]:
                for (p_,q_,r_,d_,f_,e_) in lattice:
#                     if not i%100000:
#                         logger.debug("sentence " + str(i) + ": " + time.strftime('%X'))
#                     i += 1
                    if len(set(f).intersection(set(f_))) == 0:
                        r_ += args.lambda_value[1]*get_missing_ngram_prob(lm,lm_dict,e,e_)
                        d_ += args.lambda_value[2]*math.log(math.pow(0.5,abs(len(f) - f_[0])))
                        (p__,q__,r__,d__,f__,e__) = (q+r+d+q_+r_+d_,q+q_,r+r_,d+d_,f+f_,e+e_)
#                     recombine with existing hypothesis if possible
                        if (e__ in uniques[len(f__)]) and (uniques[len(f__)][e__] > p__):
                            continue
                        uniques[len(f__)][e__] = p__
#                     prune(stacks[s])
                        if(len(stacks[len(f__)]) > args.stack_size):
                            heapq.heappushpop(stacks[len(f__)],(p__,q__,r__,d__,f__,e__))
                        else:
                            heapq.heappush(stacks[len(f__)],(p__,q__,r__,d__,f__,e__))
#                         hyp_logger.debug((p__,q__,r__,d__,f__,e__))
            if(len(stacks[s]) > 0):
                    largest = map(lambda x: str(x),heapq.nlargest(args.stack_size, stacks[s]))
                    logger_dict['log'].debug(str(s))
                    for l in largest:
                        logger_dict['log'].debug(str(largest.index(l))+' : '+l)
                    translation = heapq.nlargest(1, stacks[s])[0]
        return(translation)    

# def rec_dec(translation, hypothesis):
#     translation_ = (0,translation[-2]+hypothesis[-2],translation[-1]+hypothesis[-1])
#     print(translation_)
#     if(translation_[-2] == range(ln)):
#         return translation_
#     for i in range(ln):
#         if(i in translation_[-2]):
#             continue
#         part = filter(lambda x: x[-2][0] == i, lattice)
#         for l in part:
#             if(get_missing_ngram_prob(translation_[-1],l[-1]) < args.threshold):
# #                 print(l[-1])
#                 continue
#             translation_ = rec_dec(translation_,l)
#     return(translation)

# def alt_decode():
# # stop condition: all words translated
# #     insert most probable translation
# #     add most probable continuation
# #     if no possible continuation go back
#     translation = (0,(),())
#     for i in range(ln):
#         part = filter(lambda x: x[-2][0] == i, lattice)
#         for l in part:
#             translation = rec_dec(translation,l)
#     return(translation)
                
def add_handler(filename,logname,numeric_level):
        file_handler = logging.FileHandler(filename+'.'+logname, 'w')
        file_handler.setLevel(numeric_level)
#         formatter = logging.Formatter("%(asctime)s %(filename)s, %(lineno)d, %(funcName)s: %(message)s")
#         file_handler.setFormatter(formatter)
        logger = logging.getLogger(logname)
        logger.setLevel(numeric_level)
        logger.addHandler(file_handler)
        return logger

def remove_handler(logger, name):
        logger.handlers[0].stream.close()
        logger.removeHandler(logger.handlers[0])

def add_heuristic(lattice):
    max_prob = {}
    for (p,q,r,d,f,e) in lattice:
        for i in f:
            if(i not in max_prob):
                max_prob[i] = float(q)/len(f)
            max_prob[i] = max(max_prob[i],float(q)/len(f))
    new_lattice = []
    for (p,q,r,d,f,e) in lattice:
        for i in f:
            q -= max_prob[i]
        p = numpy.dot(args.lambda_value, [q,r,d])
        new_lattice.append((p,q,r,d,f,e))
    new_lattice.sort(reverse=True)
    return new_lattice

def get_args():
    parser = argparse.ArgumentParser(description='stack decodeer.')
    parser.add_argument('-lat','--lattice', nargs='*', 
                       help='file/s generated by the lattice generator')
    parser.add_argument('-lm','--language_model', type=argparse.FileType('r+'),
                       help='File containing the language model.')
    parser.add_argument('-lmbd','--lambda_value', type=float, nargs=3, default=[0.5,0.5,0],
                       help='lambda value for calculating p')
    parser.add_argument('--translation', type=argparse.FileType('w'),default='translations/translations',
                       help='translations file')
    parser.add_argument('-s','--stack_size', type=int, default=1000, help='stack size')
    parser.add_argument('-ng','--n_gram', type=int, default=3, help='n gram size')
    parser.add_argument('-log','--log_level', default='debug', help='log level')
    parser.add_argument('-t','--threshold', default=-10, help='probability threshold for adding phrase')
    parser.add_argument('-l','--limit', default=15, help='max sentences to translate')    
    parser.add_argument('--heuristic', action='store_true',help="consider heuristic function")
    parser.add_argument('--small_lm', action='store_true',help="add language model of smaller ngrams for the beginning of the sentence")
    return(parser.parse_args())

def main(args):
    ng = args.n_gram

    lm={}
    if(args.language_model):
        lm[ng] = args.language_model.read()
    else:
        for i in range(2,ng+1):
            lm[i] = get_lm(i)

    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.log_level)
    logger = logging.getLogger('stream')
    logger.setLevel(numeric_level)
    if(len(logger.handlers) == 0):
        handler = logging.StreamHandler()
        logger.addHandler(handler)
    
    translation_file = args.translation
    translations = []    
    
    print("started @ "+ time.strftime('%X'))

    if args.lattice:
        folder = ''
        files = args.lattice
    else:
        folder = 'lattices/'
        files = sorted(os.listdir(folder))
    for fn in files:
        if not fn.endswith("lattice"):
            continue

        logger_dict['log'] = add_handler(folder+fn,'log',numeric_level)
        logger_dict['lm'] = add_handler(folder+fn,'lm',numeric_level)
#         add_logger(fn,'hyp',numeric_level)

        logger.info(fn +" @ "+ time.strftime('%X'))
        lf = open(folder+fn, 'r')
        lattice_lines = lf.readlines()
        lf.close();
        
        lm_dict = {}
        (ln,lattice) = lines2lattice(lattice_lines, lm, lm_dict)
        if(args.heuristic):
            lattice = add_heuristic(lattice)

        logger.debug("hypotheses:" + str(len(lattice)) + " words: " + str(ln))
                
        translation = decode(lattice,ln,lm,lm_dict)      
        translations.append(' '.join(translation[-1]))

        remove_handler(logger_dict['log'],'log')
        remove_handler(logger_dict['lm'],'lm')
#         remove_logger('hyp')

        translation_file = open(translation_file.name,'a')
        translation_file.write(' '.join(translation[-1])+'\n')
        translation_file.close()
        
        if(len(translations)>args.limit):
            break
        
    print("finished @ "+ time.strftime('%X'))

if __name__ == '__main__':
    args = get_args()
    for i in range(11):
        args.lambda_value = [i*0.1,1-(i*0.1),0]
        for j in range(1,4):
            args.stack_size = j*500
            fn = 'translations/translation.'+str(i)+'.'+str(j)
            args.translation = open(fn,'w')
            print(fn)
            main(args)
            args.heuristic = True
            fn = 'translations/translation.'+str(i)+'.'+str(j)+'.h'
            args.translation = open(fn,'w')
            print(fn)
            main(args)
            args.small_lm = True
            fn = 'translations/translation.'+str(i)+'.'+str(j)+'.h.s'
            args.translation = open(fn,'w')
            print(fn)
            main(args)
            args.heuristic = False
            fn = 'translations/translation.'+str(i)+'.'+str(j)+'.s'
            args.translation = open(fn,'w')
            print(fn)
            main(args)
            args.small_lm = False


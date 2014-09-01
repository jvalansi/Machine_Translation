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
import sys

def lines2lattice(ll):
    ln=0
#     lattice += str(i) + "-" + str(j-1) + ": " + " ".join(phrase) +"\n"
    f_pattern = "(\d+)-(\d+):((?:\s\S+)*)"
#     lattice += " ".join(p) + " " + phrases[phrase][p] + "\n"
    e_pattern = "((?:\S+\s)*)(-?\d+\.\d+)"
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
                for i in range(len(e)-2):
#                     p_LM -= lm.logprob(e[i+2],[e[i],e[i+1]])
                    p_LM += lm[e[i],e[i+1]].logprob(e[i+2])
                phi = float(m.group(2))
                d = 0
                p = lmbd[0]*phi + lmbd[1]*p_LM + lmbd[2]*d
                heapq.heappush(lattice,(p,phi,p_LM,f,e))
    lattice.sort(reverse=True)
    return(ln, lattice)

def get_lm():
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
    
def get_prob(t):
    if t not in lm_dict:
        lm_dict[t] = lm[t[:-1]].logprob(t[-1]) 
        lm_logger.debug(str(t)+" : "+ str(lm_dict[t]))
    return(lm_dict[t])
#     return(lm[t[:-1]].logprob(t[-1]) )

def get_missing_ngram_prob(e,e_):
    prob = 0
    for i in range(1,ng):
        if(len(e) >= i and len(e_) >= ng-i):
            t = e[-i:]+e_[:ng-i]
            prob += get_prob(t)
    return(prob)

def decode(lattice,ln):
#         print("decoding")
        stacks = {}
        uniques = {}
        for i in range(ln+1):
            stacks[i] = []
            uniques[i] = {}
        heapq.heappush(stacks[0], (0,0,0,(0,),('SOS',)))
        for s in stacks:
#             logger.info(s)
#             logger.debug(sys.getsizeof(stacks))
#             i=0
            for (p,q,r,f,e) in stacks[s]:
                for (p_,q_,r_,f_,e_) in lattice:
#                     if not i%100000:
#                         logger.info("sentence " + str(i) + ": " + time.strftime('%X'))
#                         logger.info("sentence " + str(lattice.index((p_,q_,r_,f_,e_))))
#                         logger.info("sentence " + str(stacks[s].index((p,q,r,f,e))))                        
#                     i += 1
                    if len(set(f).intersection(set(f_))) == 0:
                        f__ = f+f_
                        e__ = e+e_
#                         if(abs(len(e) - f_[0]) > 0):
#                             d_ = math.log(float(1)/abs(len(e) - f_[0]))
#                         else:
#                             d_ = 0
#                         d__ = d+d_                        
                        p__ = p+p_
                        q__ = q+q_
                        r__ = r+r_
#                         p__ += lmbd*get_missing_ngram_prob(e,e_,ng,lm,lm_dict)
                        r__ += get_missing_ngram_prob(e,e_)
                        p__ = lmbd[0]*q__+lmbd[1]*r__
#                     recombine with existing hypothesis if possible
                        if (e__ in uniques[len(f__)]) and (uniques[len(f__)][e__] > p__):
                            continue
                        uniques[len(f__)][e__] = p__
#                     prune(stacks[s])
                        if(len(stacks[len(f__)]) > stack_size):
                            heapq.heappushpop(stacks[len(f__)],(p__,q__,r__,f__,e__))
                        else:
                            heapq.heappush(stacks[len(f__)],(p__,q__,r__,f__,e__))
                        hyp_logger.debug((p__,q__,r__,f__,e__))
            if(len(stacks[s]) > 0):
                    largest = map(lambda x: str(x),heapq.nlargest(stack_size, stacks[s]))
                    largest_logger.debug(str(s))
                    for l in largest:
                        largest_logger.debug(str(largest.index(l))+' : '+l)
                    translation = heapq.nlargest(1, stacks[s])[0]
        return(translation)    

def rec_dec(translation, hypothesis):
    translation_ = (0,translation[-2]+hypothesis[-2],translation[-1]+hypothesis[-1])
    print(translation_)
    if(translation_[-2] == range(ln)):
        return translation_
    for i in range(ln):
        if(i in translation_[-2]):
            continue
        part = filter(lambda x: x[-2][0] == i, lattice)
        for l in part:
            if(get_missing_ngram_prob(translation_[-1],l[-1]) < args.threshold):
#                 print(l[-1])
                continue
            translation_ = rec_dec(translation_,l)
    return(translation)

def alt_decode():
# stop condition: all words translated
#     insert most probable translation
#     add most probable continuation
#     if no possible continuation go back
    translation = (0,(),())
    for i in range(ln):
        part = filter(lambda x: x[-2][0] == i, lattice)
        for l in part:
            translation = rec_dec(translation,l)
    return(translation)
                
def get_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-lf','--lattice_file', type=argparse.FileType('r+'),
                       help='generated by the lattice generator')
    parser.add_argument('-lm','--language_model', type=argparse.FileType('r+'),
                       help='File containing the language model.')
    parser.add_argument('-lmbd','--lambda_value', type=float, nargs=3, default=[0.5,0.5,0],
                       help='lambda value for calculating p')
    parser.add_argument('-s','--stack_size', type=int, default=1000,
                       help='stack size')
    parser.add_argument('-ng','--n_gram', type=int, default=3,
                       help='n gram size')
    parser.add_argument('-ll','--log_level', default='debug',
                       help='log level')
    parser.add_argument('-t','--threshold', default=-10,
                       help='probability threshold for adding phrase')
    return(parser.parse_args())

if __name__ == '__main__':

    args = get_args()
    if(args.lattice_file):
        lattice_lines = args.lattice_file.readlines()
    if(args.language_model):
        language_model = args.language_model.read()
    lmbd = args.lambda_value
    stack_size = args.stack_size
    ng = args.n_gram
    lm = get_lm()
    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.log_level)
    handler = logging.StreamHandler()
    logger = logging.getLogger('stream')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)


    translations = []    
    open('translation', 'w').close()
    
    print("started @ "+ time.strftime('%X'))

    listdir = os.listdir("lattices")
    listdir = sorted(listdir)
    for fn in listdir:
        if not fn.endswith(".lattice"):
            continue

        print(fn +" @ "+ time.strftime('%X'))
        lf = open("lattices/"+fn, 'r')
        lattice_lines = lf.readlines()
        lf.close();
        
        (ln,lattice) = lines2lattice(lattice_lines)
#         e_dict = []
#         num_lattice = []
#         for l in lattice:
#             if l[-1] not in e_dict:
#                 e_dict.append(l[-1])
#             num_lattice.append(l[:-1]+(e_dict.index(l[-1]),))
#         lattice = num_lattice
        lm_dict = {}
        logger.debug(len(lattice))
        
        file_handler = logging.FileHandler("lattices/"+fn+'.log', 'w')
        file_handler.setLevel(logging.DEBUG)
#         formatter = logging.Formatter("%(asctime)s %(filename)s, %(lineno)d, %(funcName)s: %(message)s")
#         file_handler.setFormatter(formatter)
        largest_logger = logging.getLogger('largest')
        largest_logger.setLevel(logging.DEBUG)
        largest_logger.addHandler(file_handler)
        file_handler = logging.FileHandler("lattices/"+fn+'.lm', 'w')
        file_handler.setLevel(logging.DEBUG)
        lm_logger = logging.getLogger('lm')
        lm_logger.setLevel(logging.DEBUG)
        lm_logger.addHandler(file_handler)
        file_handler = logging.FileHandler("lattices/"+fn+'.hyp', 'w')
        file_handler.setLevel(logging.DEBUG)
        hyp_logger = logging.getLogger('hypothsis')
        hyp_logger.setLevel(logging.DEBUG)
        hyp_logger.addHandler(file_handler)
        
        translation = decode(lattice,ln)      
        translations.append(' '.join(translation[-1]))

        largest_logger.handlers[0].stream.close()
        largest_logger.removeHandler(largest_logger.handlers[0])
        lm_logger.handlers[0].stream.close()
        lm_logger.removeHandler(lm_logger.handlers[0])
        hyp_logger.handlers[0].stream.close()
        hyp_logger.removeHandler(hyp_logger.handlers[0])

        tf = open('translation', 'a')
        tf.write(' '.join(translation[-1])+'\n')
        tf.close()
        
    print("finished @ "+ time.strftime('%X'))


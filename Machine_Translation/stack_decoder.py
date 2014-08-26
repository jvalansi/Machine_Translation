'''
Created on Aug 4, 2014

@author: jordan_weizmann
'''
import itertools
import argparse
import re
import time
import nltk
import heapq
import os
import bleu

def lines2lattice(ll,lm, lmbd):
    n=0
#     lattice += str(i) + "-" + str(j-1) + ": " + " ".join(phrase) +"\n"
    f_pattern = "(\d+)-(\d+):((?:\s\S+)*)"
#     lattice += " ".join(p) + " " + phrases[phrase][p] + "\n"
    e_pattern = "((?:\S+\s)*)(-?\d+\.\d+)"
    lattice = []
    for l in ll:
            m = re.match(f_pattern,l)
            if(m):
                f = tuple(range(int(m.group(1)),int(m.group(2))+1))
                n = max(max(f)+1,n)
            m = re.match(e_pattern, l)
            if(m):
                e = tuple(m.group(1).split())
                p_LM = 0
                for i in range(len(e)-2):
#                     p_LM -= lm.logprob(e[i+2],[e[i],e[i+1]])
                    p_LM += lm[e[i],e[i+1]].logprob(e[i+2])
                phi = float(m.group(2))
                p = (1-lmbd)*phi + lmbd*p_LM
                lattice.append((p,e,f))
    return(n, lattice)

def lm2dict(lm, e):
    lm_dict = {}

#     words = set(itertools.chain(*e))
#     print("sentences: "+str(len(e)))
#     print("words: "+str(len(words)))
#     for i in words:
#         for j in words:
#             for k in words:
#                 lm_dict[(i,j,k)] = lm[i,j].logprob(k)
                
#     for i in e:
#         for j in e:
#             if(len(i) > 1):
#                 e__ = (i[-2],i[-1],j[0])
#                 lm_dict[e__] = lm[e__[0],e__[1]].logprob(e__[2])
#             if(len(j) > 1):
#                 e__ = (i[-1],j[0],j[1])
#                 lm_dict[e__] = lm[e__[0],e__[1]].logprob(e__[2])
#             else:
#                 for k in e:
#                     e__ = (i[-1],j[0],k[0])
#                     lm_dict[e__] = lm[e__[0],e__[1]].logprob(e__[2])
                    
                
    es2 = set()
    ef2 = set()
    e1 = set()
    es1 = set()
    ef1 = set()
    for i in e:
        es1.add(i[0])
        ef1.add(i[-1])
        if len(i)>1:
            es2.add(i[:2])
            ef2.add(i[-2:])
        else:
            e1.add(i[0])
      
    print("1 words: "+str(len(e1)))
    print("end words: "+str(len(ef1)))
    print("start words: "+str(len(es1)))
    for i in ef1:
        for j in e1:
            for k in es1:
                e__ = (i,j,k)
#                 lm_dict[e__] = lm.logprob(e__[2],[e__[0],e__[1]])
                lm_dict[e__] = lm[e__[0],e__[1]].logprob(e__[2])
    for i in ef1:
        for j in es2:
            e__ = (i,j[0],j[1])
#             lm_dict[e__] = lm.logprob(e__[2],[e__[0],e__[1]])
            lm_dict[e__] = lm[e__[0],e__[1]].logprob(e__[2])
    for i in ef2:
        for j in es1:
            e__ = (i[0],i[1],j)
#             lm_dict[e__] = lm.logprob(e__[2],[e__[0],e__[1]])
            lm_dict[e__] = lm[e__[0],e__[1]].logprob(e__[2])
    return(lm_dict)

def get_lm():
    tokens = list(nltk.corpus.genesis.words('english-kjv.txt')) #TODO: use different corpuses
    cfd = nltk.probability.ConditionalFreqDist()
    for t in nltk.ngrams(tokens, 3):
        condition = tuple(t[:-1])
        word = t[-1]
        cfd[condition][word] +=1
#     lm = nltk.probability.ConditionalProbDist(cfd, nltk.probability.LidstoneProbDist, 0.2)
    lm = nltk.probability.ConditionalProbDist(cfd, nltk.probability.WittenBellProbDist, 1000)
    return(lm)
    
def write_lm(lm_dict):
    f = open('lm', 'w')
    s = ""
    print(len(lm_dict))
    i=0
    for l in lm_dict:
        i+=1
#         if(not i%100000):
#             print(i)
#         s += str(l)+"\n"
        s += str(l)+ " => " + str(lm_dict[l]) + "\n"
    f.write(s)
    f.close()
    

def get_prob((i,j,k),lm,lm_dict):
    if (i,j,k) not in lm_dict:
        lm_dict[(i,j,k)] = lm[i,j].logprob(k) 
    return(lm_dict[(i,j,k)])


def decode(lattice,lm,lm_dict,lmbd,n,l):
#         print("decoding")
        stacks = {}
        uniques = {}
        for i in range(n+1):
            stacks[i] = []
            uniques[i] = {}
        heapq.heappush(stacks[0], (0,(),()))
        for s in stacks:
            print(s)
            for (p,e,f) in stacks[s]:
                i = stacks[s].index((p,e,f))
                if not i%10000:
                    print("sentence " + str(i) + ": " + time.strftime('%X'))
                for (p_,e_,f_) in lattice:
                    if len(set(f).intersection(set(f_))) == 0:
#                         f__ = f.union(f_)
                        f__ = f+f_
                        e__ = e+e_
                        p__ = p+p_
                        if len(e)>1:
                            p__ += lmbd*lm_dict[(e[-2],e[-1],e_[0])]
#                             p__ += lmbd*lm[e[-2],e[-1]].logprob(e_[0])
#                             p__ += lmbd*get_prob((e[-2],e[-1],e_[0]),lm,lm_dict)
                        if len(e)>0 and len(e_)>1:
                            p__ += lmbd*lm_dict[(e[-1],e_[0],e_[1])]
#                             p__ += lmbd*lm[e[-1],e_[0]].logprob(e_[1])
#                             p__ += lmbd*get_prob((e[-1],e_[0],e_[1]),lm,lm_dict)
#                     recombine with existing hypothesis if possible
                        if (e__ in uniques[len(f__)]) and (uniques[len(f__)][e__] > p__):
                            continue
                        uniques[len(f__)][e__] = p__
#                     prune(stacks[s])
                        if(len(stacks[len(f__)]) > l):
                            heapq.heappushpop(stacks[len(f__)],(p__,e__,f__))
                        else:
                            heapq.heappush(stacks[len(f__)],(p__,e__,f__))
#             print(heapq.nlargest(50, stacks[s]))
        translation = heapq.nlargest(1, stacks[n])[0]
        return(translation)

def get_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-l','--lattice_file', type=argparse.FileType('r+'),
                       help='generated by the lattice generator')
    parser.add_argument('-lm','--language_model', type=argparse.FileType('r+'),
                       help='File containing the language model.')
    parser.add_argument('-lmbd','--lambda_value', type=float, default=0.1,
                       help='lambda value for calculating p')
    parser.add_argument('-s','--stack_size', type=int, default=1000,
                       help='stack size')
    return(parser.parse_args())

if __name__ == '__main__':


    args = get_args()
    lattice_lines = args.lattice_file.readlines()
    language_model = args.language_model.read()
    lmbd = args.lambda_value
    lm = get_lm()
    l = args.stack_size

    translations = []    
    tf = open('translation', 'w')
    print("started @ "+ time.strftime('%X'))

#     listdir = os.listdir("lattices")
#     listdir = sorted(listdir)
#     for fn in listdir:
#         print(fn +" @ "+ time.strftime('%X'))
#         lf = open("lattices/"+fn, 'r')
#         lattice_lines = lf.readlines()
#         lf.close()
        
    (n,lattice) = lines2lattice(lattice_lines, lm, lmbd)
  
    e = zip(*lattice)[1]
    lm_dict = lm2dict(lm, e)
#     write_lm(lm_dict)
    
#     lm_dict = {}

    
    translation = decode(lattice, lm, lm_dict, lmbd, n, l)      
    translations.append(' '.join(translation[1]))
        
    print("finished @ "+ time.strftime('%X'))
    rf = open('original_translation', 'r')
    references = rf.readlines()
    for i in range(len(translations)):
        print(bleu.calc_bleu(translations[i].split(), references[i].split()))
        tf.write(translations[i] +'\n')
    tf.close()

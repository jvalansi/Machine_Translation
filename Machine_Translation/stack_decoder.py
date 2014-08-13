'''
Created on Aug 4, 2014

@author: jordan_weizmann
'''
import argparse
import re
import time
import nltk
import heapq


def lines2lattice(ll,lm):
#     lattice += str(i) + "-" + str(j-1) + ": " + " ".join(phrase) +"\n"
    f_pattern = "(\d+)-(\d+):((?:\s\S+)*)"
#     lattice += " ".join(p) + " " + phrases[phrase][p] + "\n"
    e_pattern = "((?:\S+\s)*)(-?\d+\.\d+)"
    lattice = []
    for l in ll:
            m = re.match(f_pattern,l)
            if(m):
                f = range(int(m.group(1)),int(m.group(2))+1) 
            m = re.match(e_pattern, l)
            if(m):
                e = tuple(m.group(1).split())
                p_LM = 0
                for i in range(len(e)-2):
                    p_LM -= lm.logprob(e[i+2],[e[i],e[i+1]])
                phi = float(m.group(2))
                lattice.append((phi + p_LM,e,f))
    return(lattice)

def lm2dict(lm, e):
    lm_dict = {}
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
    for i in ef1:
        for j in e1:
            for k in es1:
                e__ = (i,j,k)
                lm_dict[e__] = lm.logprob(e__[2],[e__[0],e__[1]])
    for i in ef1:
        for j in es2:
            e__ = (i,j[0],j[1])
            lm_dict[e__] = lm.logprob(e__[2],[e__[0],e__[1]])
    for i in ef2:
        for j in es1:
            e__ = (i[0],i[1],j)
            lm_dict[e__] = lm.logprob(e__[2],[e__[0],e__[1]])        
    return(lm_dict)

def get_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-l','--lattice_file', type=argparse.FileType('r+'), 
                       help='generated by the lattice generator')
    parser.add_argument('-lm','--language_model', type=argparse.FileType('r+'), 
                       help='File containing the language model.')
    return(parser.parse_args())
    

if __name__ == '__main__':
    
    
    args = get_args()
    lattice_lines = args.lattice_file.readlines()
    language_model = args.language_model.read();

    tokens = list(nltk.corpus.genesis.words('english-kjv.txt')) #TODO: use different corpuses 
    estimator = lambda fdist, bins: nltk.probability.LidstoneProbDist(fdist, 0.2)
    lm = nltk.model.ngram.NgramModel(3,tokens,True,False,estimator)
    
    lattice = lines2lattice(lattice_lines, lm)
    n=0
    for l in lattice:
        n = max(max(l[2]),n)
    print(n)

    e = zip(*lattice)[1]
    lm_dict = lm2dict(lm, e)

#     e = set([i for t in e for i in t])
#     e_dict = {}
#     for ind,val in enumerate(e):
#         e_dict[val] = ind
# 
#     new_lattice = []
#     for (p,e,f) in lattice:
#         new_e = tuple()
#         for i in e:
#             new_e += (e_dict[i],)
#         new_lattice.append((p,new_e,f))
#     lattice = new_lattice
# 
#     new_lm_dict = {}
#     for l in lm_dict:
#         new_l = (e_dict[l[0]],e_dict[l[1]],e_dict[l[2]])
#         new_lm_dict[new_l] = lm_dict[l]
#     lm_dict = new_lm_dict

    stacks = {}
    for i in range(n+1):
        stacks[i] = []  
    for (p,e,f) in lattice:
#         stacks[len(f)].append((p,e,f))
        heapq.heappush(stacks[len(f)],(p,e,f))
    for s in stacks:
        print(s)
#         stacks[s] = sorted(stacks[s],key = lambda l:(l[2]))
#         stacks[s] = stacks[s][-10000:]
        i=0
        for (p,e,f) in stacks[s]:
            i+=1
            if not i%1000:
                print("sentence " + str(i) + ": " + time.strftime('%X'))
            for (p_,e_,f_) in lattice:
                if len(set(f).intersection(set(f_))) == 0:
#                     f__ = f.union(f_)
                    f__ = f+f_
                    e__ = e+e_
                    if len(e)>1:
                        p -= lm_dict[(e[-2],e[-1],e_[0])]
                    if len(e_)>1:
                        p -= lm_dict[(e[-1],e_[0],e_[1])]
#                     stacks[len(f__)].append((p+p_,e__,f__))
                    heapq.heappush(stacks[len(f__)],(p+p_,e__,f__))
                    if(len(stacks[len(f__)])>10000):
                        heapq.heappop(stacks[len(f__)])
    #                     recombine with existing hypothesis if possible
    #                     prune(stacks[s])

    print(heapq.nlargest(1, stacks[n]))
#     print(stacks[n][-1])     
'''
Created on Jul 28, 2014

@author: jordan_weizmann
'''
import argparse
import numpy
import re
import time
import collections
import math

def sentence2marix(sentence):
# input:
# Sentence pair (1)
# il s' agit de la m\EAme soci\E9t\E9 qui a chang\E9 de propri\E9taires
# NULL ({ }) UNK ({ }) UNK ({ }) this ({ 4 11 }) is ({ }) the ({ }) same ({ 6 }) agency ({ }) which ({ 8 }) has ({ }) undergone ({ 1 2 3 7 9 10 12 }) a ({ }) change ({ 5 }) of ({ }) UNK ({ })
# output:
# f = (il, s', agit, de, la, m\EAme, soci\E9t\E9, qui, a, chang\E9, de, propri\E9taires)
# e = (NULL,UNK,UNK,this,is,the,same,agency,which,has,undergone,a,change,of,UNK)
# A = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#      [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0],
#      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#      [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
#       ...
    f = sentence[1].split()
    pattern = "\s\(\{\s(?:\d+\s)*\}\)\s"
    g = re.findall(pattern, sentence[2])
    g = g[1:]
    e = re.split(pattern, sentence[2])
    e = e[1:]
    A = numpy.zeros((len(g), len(f)))
    for i in range(len(g)):
        h = re.findall("\d+", g[i])
        for j in h:
            A[i,(int(j)-1)] = 1 
    return {"e":e, "f":f, "A":A}
    

def quasi_consecutive(x,aligned):
#tests whether the set of words TP is consecutive, with the possible exception of words that are not aligned.
#     if x.size:
#         d = set(x).difference(range(min(x),max(x)+1))
#         return((not d) | (d not in aligned))
#     else:
#         return False
    return (x.size > 0) #faster
    

def matrix2phrase(M):
    if(not M):
        return None
    e = M["e"]
    f = M["f"]
    A = M["A"]
    BP = []
    aligned = numpy.nonzero(A)
    for i1 in range(len(e)):
        for i2 in range(i1+1,min(i1+8,len(e))): #TODO: limit size
            TP = numpy.nonzero(A[i1:i2,:])[1]
            if quasi_consecutive(TP,aligned[1]):
                j1 = min(TP)
                j2 = max(TP)+1
                SP = numpy.nonzero(A[:,j1:j2])[0]
                if (set(SP) <= set(range(i1,i2))):
                    BP.append((tuple(e[i1:i2]), tuple(f[j1:j2])))
                    j1_ = j1-1
                    while (j1_ > 0) & (len(numpy.nonzero(A[:,j1_])) == 0):
                        j2_ = j2+1
                        while (j2_ <= len(f)) & (len(numpy.nonzero(A[:, j2_])) == 0):
                            BP.append((tuple(f[j1_:j2_]),tuple(e[i1:i2])))
                            j2_ = j2_ + 1
                        j1_ = j1_-1

    return BP

def join_matrices(M1,M2):
    if(M1["A"].shape != M2["A"].T.shape):
        return None
    matrix = M1
    matrix["A"] = M1["A"] + M2["A"].T
    matrix["A"] = (matrix["A"]).astype(bool)*1
    return matrix

def get_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-e2f','--e2ffile', type=argparse.FileType('r+'), 
                       help='english to foreign file to align')
    parser.add_argument('-f2e','--f2efile', type=argparse.FileType('r+'), 
                       help='foreign to english file to align')
    parser.add_argument('-p','--pfile', type=argparse.FileType('w'), 
                       help='aligned phrases file')
    return(parser.parse_args())


if __name__ == '__main__':

    args = get_args()

    e2f = args.e2ffile.readlines()
    f2e = args.f2efile.readlines()
    l = min(len(e2f),len(f2e))
    print("sentences: " +str(l/3))
    phrases = []
#    for i in sentences:
    for i in range(l/3): 
        if(not i%1000):
            print("sentence " + str(i) + ": " + time.strftime('%X'))
#        get matrix1 from first direction
        sentence = [f2e[i*3],f2e[i*3+1],f2e[i*3+2]]
        matrix1 = sentence2marix(sentence)
#        get matrix2 from second direction
        sentence = [e2f[i*3],e2f[i*3+1],e2f[i*3+2]]
        matrix2 = sentence2marix(sentence)        
#        join matrices #TODO: something better
        matrix = join_matrices(matrix1,matrix2)
        if(not matrix):
            print(i)
            print(sentence)
            continue
#        get aligned phrases from matrix
        phrases.extend(matrix2phrase(matrix)) 

    l = len(phrases)
    print("phrases: " +str(l))
    phrases_ = zip(*phrases)
    count_ef = collections.Counter(phrases)
    count_f = collections.Counter(phrases_[1])
#    for i in phrases
    for i in range(len(phrases)):
#        get translation score
        N_ef = count_ef[phrases[i]]
        N_f = count_f[phrases_[1][i]] #TODO: if too small (less than 3) disregard
        score = math.log(float(N_ef)/float(N_f))
#       "e => f p"  
        args.pfile.write(' '.join(phrases[i][1]) + " => " + ' '.join(phrases[i][0]) + ' ' + str(score)  + '\n')
        
'''
Created on Aug 3, 2014

@author: jordan_weizmann
'''
import argparse
import re

def line2tuple(line):
#     (' '.join(phrases[i][0]) + " => " + ' '.join(phrases[i][1]) + ' ' + str(score)  + '\n')
    pattern = "((?:\S+\s)*)=>\s((?:\S+\s)*)(-?\d+\.\d+)"
    t = re.match(pattern,line)
    f = t.group(1).split()
    e = t.group(2).split()
    p = t.group(3)
    t = (tuple(f),tuple(e),p)
    return(t)
    

def parse_sentence(s,phrases):
    s = s.split()
    lattice = ""
    for i in range(len(s)):
        for j in range(i+1,min(i+8,len(s)+1)):
            f = tuple(s[i:j])
            lattice += str(i) + "-" + str(j-1) + ": " + " ".join(f) +"\n"
            if f in phrases:
                for e in phrases[f]:
                    lattice += " ".join(e) + " " + phrases[f][e] + "\n"
            lattice += "\n"
    return(lattice)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-s','--sentences_file', type=argparse.FileType('r+'), 
                       help='File of Hebrew sentences to be translated by the system. Each sentence should be provided in a single line.')
    parser.add_argument('-p','--phrase_table', type=argparse.FileType('r+'), 
                       help='File containing the phrase table.')
    args = parser.parse_args()

    sentences = args.sentences_file.readlines()
    phrase_file = args.phrase_table.readlines();
    
    phrases = {}
    print("phrases to tuples")
    for p in phrase_file:
        (f,e,p) = line2tuple(p)
        if f not in phrases:
            phrases[f] = {}            
        phrases[f][e] = p
    
    print("writing to file")
    for s in sentences:
        lattice = parse_sentence(s,phrases)
        name = str(sentences.index(s))+'_'+'_'.join(s.split())+'.lattice'
        f = open('lattices/'+name, 'w')
        f.write(lattice)
        f.close()
    

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
        for j in range(i+1,min(i+args.phrase_size,len(s)+1)):
            f = tuple(s[i:j])
            lattice += str(i) + "-" + str(j-1) + ": " + " ".join(f) +"\n"
            if f in phrases:
                phrases_dict = sorted(phrases[f].items(), key=lambda x: float(x[1]), reverse = True)
                phrases_dict = phrases_dict[:args.max_translations]
                for (e,p) in phrases_dict:
                    lattice += " ".join(e) + " " + p + "\n"
            elif(i == j-1):
                lattice += "NaW" + " " + str(0) + "\n"
            lattice += "\n"
    return(lattice)

def get_args():
    parser = argparse.ArgumentParser(description='Generate lattice.')
    parser.add_argument('sentences_file', type=argparse.FileType('r+'), 
                       help='File of Hebrew sentences to be translated by the system. Each sentence should be provided in a single line.')
    parser.add_argument('phrase_table', type=argparse.FileType('r+'), 
                       help='File containing the phrase table.')
    parser.add_argument('-ps','--phrase_size', type=int, default=8,
                       help='phrase_size')
    parser.add_argument('-mp','--max_translations', type=int, default=8,
                       help='max allowed translations for phrase')
    return(parser.parse_args())


if __name__ == '__main__':

    args = get_args()
    sentences = args.sentences_file.readlines()
    phrase_file = args.phrase_table.readlines()
    
    phrases = {}
    print("phrases to tuples")
    for phrase in phrase_file:
        (f,e,p) = line2tuple(phrase)
        if f not in phrases:
            phrases[f] = {}
        phrases[f][e] = p
    
    print("writing to file")
    for s in sentences:
        lattice = parse_sentence(s,phrases)
#         name = str(sentences.index(s))+'_'+'_'.join(s.split())+'.lattice'
        name = '{:05}'.format(sentences.index(s))+'.lattice'
        f = open('lattices/'+name, 'w')
        f.write(lattice)
        f.close()
    

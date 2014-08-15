'''
Created on Aug 14, 2014

@author: jordan_weizmann
'''
import argparse
import math

def get_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-e','--efile', type=argparse.FileType('r+'), 
                       help='english file')
    parser.add_argument('-f','--ffile', type=argparse.FileType('r+'), 
                       help='foreign file')
    parser.add_argument('-fo','--forigfile', type=argparse.FileType('r+'), 
                       help='foreign file')
    return(parser.parse_args())

def is_aligned(i,j):
    print("i: "+str(i) + ", jump: " + str(i/j) + ", jump size: " + str(j))
    print(e[i]+fo[i]+f[i])
    return(raw_input('is aligned? (Y)'))
    

def find_boundry(i,j,lower):
        j_ = j/2
        i_ = i-j_ if lower else i+j_
        while(j_ > 1):
            j_ = j_/2
            if(is_aligned(i_,j_) != 'N'):
                i_ = i_+j_ if lower else i_-j_
            else:
                i_ = i_-j_ if lower else i_+j_
        return(i_)
    

if __name__ == '__main__':
    args = get_args()
    e = args.efile.readlines()
    f = args.ffile.readlines()
    fo = args.forigfile.readlines()

    args.efile.close()
    args.ffile.close()

    pf = open('problems', 'a')

    l = min(len(e),len(f),len(fo))
    print(l)
    i = 0 
    j = int(math.sqrt(l))
    problems = []
    while i < l:
        ans = is_aligned(i,j)
        if(ans == 'B'):
            i -= j
        elif(ans == 'N'):
            i_ = find_boundry(i, j, True)
            i__ = find_boundry(i, j, False)
            problems.append((i_,i__))
            pf.write(str((i_,i__))+"\n")
            i += j
        else:
            i += j
    
    print(problems)
    pf.close()


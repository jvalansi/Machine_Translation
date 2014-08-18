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
    parser.add_argument('-fref','--freffile', type=argparse.FileType('r+'), 
                       help='foreign reference file')
    return(parser.parse_args())

def is_aligned(i,j):
    print("i: "+str(i) + ", jump: " + str(i/j) + ", jump size: " + str(j))
    print(e[i]+fref[i]+f[i])
    return(raw_input('is aligned? (Y)'))
    

def find_boundry(i,j,lower):
# binary search: if not aligned go further else go back each time with half size of jump         
# i = 10 j = 5
# i = 5 j = 2
    i_ = i
    while(j > 1):
        ans = is_aligned(i,j) 
        j = j/2
        if(ans == 'B'):
            j = j*4
            i = i_
        elif(ans == 'N'):
            i_ = i
            i = i-j if lower else i+j
        else:
            i_ = i
            i = i+j if lower else i-j
    return(i)
    

if __name__ == '__main__':
    args = get_args()
    e = args.efile.readlines()
    f = args.ffile.readlines()
    fref = args.freffile.readlines()

    args.efile.close()
    args.ffile.close()
    args.freffile.close()

    pf = open('problems', 'a')
    l = min(len(e),len(f),len(fref))
    print(l)
    i = 0 
    j = int(math.sqrt(l))
    problems = []
    
    while i < l:
        ans = is_aligned(i,j)
        if(ans == 'B'):
            i -= j
        elif(ans == 'N'):
            i_ = find_boundry(i-j/2, j/2, True)
            i__ = find_boundry(i+j/2, j/2, False)
            problems.append((i_,i__))
            pf.write(str((i_,i__))+"\n")
            i += j
        else:
            i += j
    
    print(problems)
    pf.close()


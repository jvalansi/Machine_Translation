'''
Created on Jul 27, 2014

@author: jordan_weizmann
'''
import argparse

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-i','--files', type=argparse.FileType('r+'), nargs=2, 
                       help='files to clean')
    parser.add_argument('-t','--threshold', type=int, default=60,
                       help='threshold for sentences')
    
    args = parser.parse_args()
    content1 = args.files[0].readlines()
    content2 = args.files[1].readlines()
    args.files[0].seek(0)
    args.files[0].truncate()
    args.files[1].seek(0)
    args.files[1].truncate()
                    
    l = min(len(content1),len(content2))
    for i in range(l):
        #TODO:  space non words
        if(len(content1[i].split()) > args.n or len(content2[i].split()) > args.n):
            continue
        args.files[0].write(content1[i])
        args.files[1].write(content2[i])



'''
Created on Jul 27, 2014

@author: jordan_weizmann
'''
import argparse
import re
import os

def get_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-e','--efile', type=argparse.FileType('r+'),
                       help='english file')
    parser.add_argument('-f','--ffile', type=argparse.FileType('r+'),
                       help='foreign file')
    parser.add_argument('-t','--threshold', type=int, default=60,
                       help='threshold for sentences')
    return(parser.parse_args())

if __name__ == '__main__':


    args = get_args()
    e = args.efile.readlines()
    f = args.ffile.readlines()
    t = args.threshold
    args.efile.close()
    args.ffile.close()

    et = open('etemp', 'w')
    ft = open('ftemp', 'w')

    pattern1 = r'(\S)([^\w\s])'
    pattern2 = r'([^\w\s])(\S)'
    repl = r'\g<1> \g<2>'
    l = min(len(e),len(f))
    for i in range(l):

        e[i] = re.sub(pattern1, repl, e[i])
        e[i] = re.sub(pattern2, repl, e[i])
        if(len(e[i].split()) > t or len(f[i].split()) > t):
            continue
        et.write(e[i])
        ft.write(f[i])

    et.close()
    ft.close()
    if os.path.exists(args.efile.name):
        os.remove(args.efile.name)
    if os.path.exists(args.ffile.name):
        os.remove(args.ffile.name)
    os.rename(et.name, args.efile.name)
    os.rename(ft.name, args.ffile.name)

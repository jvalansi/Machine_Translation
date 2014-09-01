'''
Created on Jul 27, 2014

@author: jordan_weizmann
'''
import argparse
import re
import os

def get_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('files', type=argparse.FileType('r+'), nargs='+', 
                       help='files (first one must be in english)')
    parser.add_argument('-t','--threshold', type=int, default=60,
                       help='threshold for sentences')
    return(parser.parse_args())

def replace(file1,file2):
    if os.path.exists(file2):
        os.remove(file2)
    os.rename(file1, file2)
    
    
if __name__ == '__main__':


    args = get_args()
    f = []
    ft = []
    for i in range(len(args.files)):
        f.append(args.files[i].readlines())
        args.files[i].close()
        ft.append(open('temp'+str(i), 'w'))

    pattern1 = r'(\S)([^\w\s])'
    pattern2 = r'([^\w\s])(\S)'
    repl = r'\g<1> \g<2>'

    l = min(map(lambda x: len(x),f))
    for i in range(l):
        f[0][i] = f[0][i].lower()
        f[0][i] = re.sub(pattern1, repl, f[0][i])
        f[0][i] = re.sub(pattern2, repl, f[0][i])
        if(any(map(lambda x: len(x[i].split()) > args.threshold, f))):
            continue
        for j in range(len(ft)):
            f[j][i] = re.sub(r'^(\d+ )?(SOS )?',r'SOS ', f[j][i])
            f[j][i] = re.sub(r'\r?\n',r' EOS\r\n', f[j][i])
            ft[j].write(f[j][i])

    for i in range(len(ft)):
        ft[i].close()
        replace(ft[i].name,args.files[i].name)


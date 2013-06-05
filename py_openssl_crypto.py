"""python frontend to open ssl en- decryption by josef@moosbauer.net
    input parameters
        inp        string to en- decrypt
        alg        algorithm to be used, defaults to des3
        passFile   salt file, 2nd line used, defaults to ~/.ssh/id_dsa
    output parameter
        on ok
            ret[0]    en- decrypted string
            ret[1]    ''
        on error
            ret[0]    ''
            ret[1]    error message
            
    and just as reminder for myself
        to use moduls from pyutils append to Pythonpath
        import sys
        sys.path.append('path to pyutils')
"""

import subprocess

err_msg = "this should not happen - arghh, "

def doEncrypt(inp, alg='des3', passFile="~/.ssh/id_dsa"):
    return _doCryptOps(inp, alg, passFile, dec=0)

def doDecrypt(inp, alg='des3', passFile="~/.ssh/id_dsa"):
    return _doCryptOps(inp, alg, passFile, dec=1)

def _doCryptOps(inp, alg, passFile, dec=0):
    if dec == 0:
        args =['openssl', 'enc', '-'+alg, '-pass', 'pass:`sed -n 2,2p '+passFile+'`', '-a']
    else:
        args =['openssl', 'enc', '-'+alg, '-pass', 'pass:`sed -n 2,2p '+passFile+'`', '-a', '-d']
    
    try:
        p1 = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ret = p1.communicate(inp)
    except:
        return ('', err_msg + sys.exc_info()[0])
    else:    
        p1.stdin.close()
        p1.stderr.close()
        p1.stdout.close()
        return ret

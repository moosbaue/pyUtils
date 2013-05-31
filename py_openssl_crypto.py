"""python frontend to open ssl en- decryption 
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
"""

import subprocess

err_msg = "this sould not happen - arghh, "

def doEncrypt(inp, alg='des3', passFile="~/.ssh/id_dsa"):
    args =['openssl', 'enc', '-'+alg, '-pass', 'pass:`sed -n 2,2p '+passFile+'`', '-a']
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

def doDecrypt(inp, alg='des3', passFile="~/.ssh/id_dsa"):
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
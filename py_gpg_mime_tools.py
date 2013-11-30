#!/usr/bin/python

# used as a base by Josef Moosbauer for py_gpg_mime tools
# With minor changes by Nathan Grigg
#
# Original Copyright 2008 Lenny Domnitser <http://domnit.org/>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

__all__ = 'clarify',
__author__ = 'Lenny Domnitser'
__version__ = '0.1'

import email

TEMPLATE = '''-----BEGIN PGP SIGNED MESSAGE-----
Hash: %(hashname)s
NotDashEscaped: You need GnuPG to verify this message

%(text)s%(sig)s'''

def strip_control_m(input):  
      
    if input:  
              
        import re  
        # ascii control characters  
        input = re.sub(r"[\x0D]", "", input)  
              
    return input  

def _do_decrypt(message, messagetext):
    '''Pipe to gpg for decryption and exit'''
    if message.get_content_type() == 'multipart/encrypted':
        if message.get_param('protocol') == 'application/pgp-encrypted':
            # normalize line endings to \n for processing
            messagetext=messagetext.replace('\r\n', '\n').replace('\r', '\n')
            import subprocess
            import string
            try:
                process = subprocess.Popen(['/usr/bin/env', 'gpg','-d','--batch'],stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = process.communicate(messagetext)
                process.wait()
            except:
                sys.exit(process.returncode)
            process.stdin.close()
            process.stdout.close()
            out=strip_control_m(out)
            
            tmpp = out.splitlines()[0]+out.splitlines()[1]
            newct = tmpp[14:-1]
            out1 = out[127:-1]
            message.replace_header('Content-Type', newct)
            message.set_boundary(message.get_boundary()[1:])
            #text = out.split('\n--"%s--\n' % message.get_boundary(), 2)
            text = out.split('\n--%s\n' % message.get_boundary())
            
            j=0
            for part in message.walk():
                if part.is_multipart():
                    j+=1
                    continue
                if j==1:
                    part.replace_header('Content-Type', 'text/plain; charset="ISO-8859-1"')
                    #part.set_charset('ISO-8859-1')
                    part.replace_header('Content-Transfer-Encoding', 'quoted-printable')
                if j==2:
                    part.replace_header('Content-Type', 'application/pgp-signature')
                    part.replace_header('Content-Description','This is a digitally signed message part')
                    part.replace_header('Content-Transfer-Encoding', '7bit')
                part.set_payload(''.join(text[j].splitlines(True)[3:]))
                j+=1
                                      
        elif message.is_multipart():
            for message in message.get_payload():
                _do_decrypt(message, messagetext)
          
    
def _clarify(message, messagetext):
    if message.get_content_type() == 'multipart/signed':
        if message.get_param('protocol') == 'application/pgp-signature':
            # normalize line endings to \n for processing
            messagetext=messagetext.replace('\r\n', '\n').replace('\r', '\n')
            hashname = message.get_param('micalg').upper()
            assert hashname.startswith('PGP-')
            hashname = hashname.replace('PGP-', '', 1)
            textmess, sigmess = message.get_payload()
            text = messagetext.split('\n--%s\n' % message.get_boundary(), 2)[1]
            sig = sigmess.get_payload()
            assert isinstance(sig, str)
            message.replace_header('Content-Type', 'application/octet')
            
            clearsign = TEMPLATE % locals()
            clearsign = clearsign.replace(
                '\r\n', '\n').replace('\r', '\n').replace('\n', '\r\n')
            message.set_payload(clearsign)
    elif message.is_multipart():
        for message in message.get_payload():
            _clarify(message, messagetext)


def clarify(messagetext):
    import string
    '''given a string containing a MIME message, returns a string
    where PGP/MIME messages are replaced with clearsigned messages.'''
    
    message = email.message_from_string(messagetext)
    if messagetext.find('-----BEGIN PGP MESSAGE-----')>0:
        _do_decrypt(message, messagetext)
        messagetext = message.as_string() 
                
    if messagetext.find('application/pgp-signature'):            
        _clarify(message, messagetext)
    
    return message.as_string()

def verify(text):
    '''Pipe to gpg for verification and exit'''
    import subprocess
    try:
        process=subprocess.Popen(['/usr/bin/env', 'gpg','-q','--verify','--batch'],stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        err, out = process.communicate(text)
    except:
        sys.exit('', process.returncode)
    process.stdin.close()
    process.stdout.close()    
    
    return out
    
def parse_args():
    try:
        import argparse
    except:
        if len(sys.argv)>1:
            sys.exit("""Error: Cannot accept argments. 

Please input a MIME message on stdin.
Example: clearsign.py < foo.txt""")
        else:
            return {'file': sys.stdin,'verify': False}

    parser=argparse.ArgumentParser(
        description='Convert a PGP/MIME signed email to a clearsigned message.  If no file is given, input is read from stdin.')
    parser.add_argument('file',metavar='file',type=argparse.FileType('r'),
        nargs="?",default=sys.stdin,help='a file containing the whole MIME email')
    parser.add_argument('-v','--verify', help="pass output to gpg to verify signature",
        action='store_true')
    parser.add_argument('-m','--mheader',help="pass mailheader along",
        action='store_true')
    return vars(parser.parse_args())
 

if __name__ == '__main__':
    import sys
    args=parse_args()
    origmail=args['file'].read()
    output = clarify(origmail)
    if args['mheader']:
        print test
    if args['verify']:
        mail = output
        #print mail
        output = (verify(output))
        output = mail+output
    sys.stdout.write(output)


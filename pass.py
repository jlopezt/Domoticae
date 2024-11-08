from hashlib import md5

import sys

args = sys.argv

pass_t=''
for pass_txt in args[1:]:
    password = md5(pass_txt.encode("utf-8")).hexdigest()
    print(pass_txt,' --> ',password)
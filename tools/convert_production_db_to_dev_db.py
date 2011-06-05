# Change DB
# Convert Production DB into Dev-purpose DB
#    - Removing Private Information and so on

# After job done,
# 1) SYSOP will remain in SYSOP
# 2) All the other users' email address will be uu[NUMBER in 6 digit]
# 3) All the users' password will be "1234" (4 letters)

# TODO: Clear private information more and more

import os
import sys

THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'gen-py'))
ARARA_PATH  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(THRIFT_PATH)
sys.path.append(ARARA_PATH)

from arara import model
from arara.util import smart_unicode

def inttostr(n):
    s = "%d" % n
    s = "0" * (6 - len(s)) + s
    return s


def main():
    model.init_database()
    s = model.Session()
    print "loading user query"
    query = s.query(model.User)

    for idx, user in enumerate(query):
        user.nickname = user.username
        user.email = smart_unicode(inttostr(user.id) + "@example.com")
        user.signature = u"x" * len(user.signature)
        user.self_introduction = u"x" * len(user.self_introduction)
        user.last_login_ip = u"127.0.0.1"
        user.set_password("1234")
        print idx, " th user done."

    print "commit begin"
    s.commit()
    s.close()
    print "commit done"

    s = model.Session()

    print "loading message query"
    query = s.query(model.Message)

    for idx, message in enumerate(query):
        message.message = u"x" * len(message.message)
        print idx, " th message done."

    print "commit begin"
    s.commit()
    print "commit done"
    print "Job Done."

if __name__ == "__main__":
    main()

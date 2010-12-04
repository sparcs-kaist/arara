# Change DB
# Convert Production DB into Dev-purpose DB
#    - Removing Private Information and so on

# After job done, SYSOP will be uu000001 and password is uu000001.

import os
import sys

THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'gen-py'))
ARARA_PATH  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(THRIFT_PATH)
sys.path.append(ARARA_PATH)

from arara import model

def inttostr(n):
    s = "%d" % n
    s = "0" * (6 - len(s)) + s
    return s


def main():
    model.init_database()
    s = model.Session()
    print "loading queries"
    query = s.query(model.User).all()
    print "loading done"

    for idx, user in enumerate(query):
        user.username = u"uu" + inttostr(user.id)
        user.nickname = u"uu" + inttostr(user.id)
        user.email = inttostr(user.id) + "@example.com"
        user.signature = u"x" * len(user.signature)
        user.self_introduction = u"x" * len(user.self_introduction)
        user.last_login_ip = u"127.0.0.1"
        user.set_password(u"uu" + inttostr(user.id))
        print idx, " th user done."

    print "loading queries"
    query = s.query(model.Message).all()
    print "loading done"
    for idx, message in enumerate(query):
        message.message = u"x" * len(message.message)
        print idx, " th message done."

    print "commit begin"
    s.commit()
    print "commit done"

    print "Job Done."

if __name__ == "__main__":
    main()

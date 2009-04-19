# -*- coding: utf-8 -*-
import MySQLdb
import sys
import md5
import time

sys.path.append('../')
sys.path.append('../gen-py/')

from arara import model
from sqlalchemy.exceptions import InvalidRequestError, IntegrityError
from sqlalchemy import *
from sqlalchemy.orm import *
from arara.model import settings

nickname = set()

LOGGING_FILENAME = 'conflicts.log'

OLDARA_DBHOST = 'mir.sparcs.org'
OLDARA_DBNAME = 'webara2g'
OLDARA_USER   = 'pipoket'
OLDARA_PASSWD = 'tnfqkrtm'

engine = create_engine(settings.DB_CONNECTION_STRING, encoding='utf-8',
                    convert_unicode=True, assert_unicode=None,
                    pool_size=50, max_overflow=100, echo=False)
Session = sessionmaker(bind=engine, autoflush=True, transactional=True)
# Check mysql first!
try:
    file = open(LOGGING_FILENAME, 'w')
    db = MySQLdb.connect(db=OLDARA_DBHOST, user=OLDARA_USER, passwd=OLDARA_PASSWD,
           host=OLDARA_DBHOST, use_unicode=True, charset='utf8')
    cursor = db.cursor()
    cursor.execute("select * from users")
    count = cursor.rowcount
    for i, row in enumerate(cursor):
        id = row[0]
        username = row[1]
        password = row[2]
        original_nickname = row[5]
        nickname = username #XXX: Apply username on nickname to prevent duplication.
        email = row[6]

        # Same e-mail address might exist(don't know why)
        # Reset the e-mail address to the example.org one.
        # User should change their e-mail and get the confirmation
        email = "%s_PLEASE_INPUT_YOUR_EMAIL@example.org" % id

        # Write original nickname to the signature
        signature = u'--\n'
        signature += u'Original Nickname: '
        signature += original_nickname
     
        print "[%d %%]Processing Username: %s, nickname: %s..." % ((i*100/count*1.0), username, nickname),
        try:
            ## Write user to the new database
            session = Session()
            new_user = model.User(username, password, nickname, email, signature, '', 'en')
            # Constructor of model receives the password and HASHES IT.
            # As the password is ALREADY HASHED, we have to put original password here
            new_user.password = password
            session.save(new_user)
            
            ## Set the activation code to the new database
            key = (username + password + nickname).encode('utf-8')
            activation_code = md5.md5(key).hexdigest()
            new_activation = model.UserActivation(new_user, activation_code)
            session.save(new_activation)

            ## If everything is fine, write them to the database
            session.commit()
            session.close()
            print "DONE."
        except IntegrityError, e:
            ## IntegrityError should never happen, but if happens, log it
            import traceback
            session.close()
            print "ALREADY ADDED! LOGGING!"
            file.write((u"***ALREADY ADDED*******User %s " % username) + traceback.format_exc())
        except Exception, e:
            import traceback
            session.close()
            print "OTHER ERROR HAPPENED! LOGGING!"
            file.write((u"+++ERROR!!++++++++++++User %s " % username) + traceback.format_exc())

except KeyboardInterrupt:
    print "\nTERMINATING!!! TERMINATING!!!"
    file.close()

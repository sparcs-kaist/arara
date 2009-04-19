# -*- coding: utf-8 -*-
# Goal: 비밀번호 설정이 날아간 사용자들을 모조리 제거한다.
import MySQLdb
import sys
import time

sys.path.append('../')
sys.path.append('../gen-py/')

from arara.settings import *

LOGGING_FILENAME = 'db.log'
QUERY_FILENAME   = 'db.query'

def main():
    file = open(LOGGING_FILENAME, 'w')
    db = MySQLdb.connect(db    =MYSQL_DBNAME,
                         user  =MYSQL_ID,
                         passwd=MYSQL_PASSWD,
                         host  =MYSQL_DBHOST,
                         use_unicode=True, charset='utf8')
    cursor = db.cursor()
    cursor.execute("select id, username, password from users")
    count = cursor.rowcount
    for i, row in enumerate(cursor):
        id = row[0]
        username = row[1]
        password = row[2]

        if len(password) < 2:
            output_string = u"%s\t%s\t%s\n" % (id, username, password)
            file.write(output_string)
            print output_string[:-1]

    db.close()
    file.close()

if __name__ == "__main__":
    main()

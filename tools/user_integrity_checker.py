# -*- coding: utf-8 -*-
# Goal: 비밀번호 설정이 날아간 사용자들을 모조리 제거한다.
import MySQLdb
import sys
import time

sys.path.append('../')
sys.path.append('../gen-py/')

from arara.settings import *

# 날리는 사용자들을 기록할 파일명
LOGGING_FILENAME = 'db.log'

def main():
    # Initialize
    file = open(LOGGING_FILENAME, 'w')
    db = MySQLdb.connect(db    =MYSQL_DBNAME,
                         user  =MYSQL_ID,
                         passwd=MYSQL_PASSWD,
                         host  =MYSQL_DBHOST,
                         use_unicode=True, charset='utf8')
    cursor = db.cursor()

    # Query
    cursor.execute("select id, username, password, nickname, last_login_time, last_logout_time from users")
    count = cursor.rowcount
    problametic_id_list = []

    for i, row in enumerate(cursor):
        id = row[0]
        username = row[1]
        password = row[2]
        nickname = row[3]

        # Extracting Problametic users
        if len(password) < 2:
            output_string = u"%s\t%s\t%s\t%s\n" % (id, username, nickname, password)
            file.write(output_string.encode('utf-8')
            problametic_id_list.append(id)

    # Eliminating them 
    for id in problametic_id_list:
        query = "delete from users where id=%s" % id
        cursor.execute(query)

    # Finalize
    db.close()
    file.close()

if __name__ == "__main__":
    main()

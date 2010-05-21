# -*- coding: utf-8 -*-
# Goal: ReadStatus 설정이 맛이 간 사용자들의 목록을 뽑아낸다.
# user_integrity_checker 를 카피한 소스여서 정리가 필요.
import MySQLdb
import sys
import time
import pickle

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
    cursor.execute("select id, user_id, read_status_data from read_status")
    count = cursor.rowcount
    problametic_id_list = []

    for i, row in enumerate(cursor):
        id = row[0]
        userid = row[1]
        read_status_data = row[2]

        output_string = repr((id, userid, read_status_data))
        file.write(output_string)
        try:
            a = pickle.loads(read_status_data)
        except Exception:
            print "EXCEPTION id: ", id, " user ", userid

    # Eliminating them 
    for id in problametic_id_list:
    #    query = "delete from users where id=%s" % id
    #    cursor.execute(query)
        pass

    # Finalize
    db.close()
    file.close()

if __name__ == "__main__":
    main()

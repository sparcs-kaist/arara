# MySQL Server Setting
MYSQL_ID = "ara"
MYSQL_PASSWD = "together"
MYSQL_DBHOST = "juk.sparcs.org"
MYSQL_DBNAME = "arara"

DB_CONNECTION_STRING = 'mysql://%s:%s@%s/%s?charset=utf8&use_unicode=1' % (MYSQL_ID, MYSQL_PASSWD, MYSQL_DBHOST, MYSQL_DBNAME)

# Mail Server Setting
WARARA_SERVER_ADDRESS = 'ara.kaist.ac.kr'
MAIL_HOST = 'localhost'
MAIL_SENDER = 'ara@ara.kaist.ac.kr'

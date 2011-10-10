#!/bin/bash

echo "Welcome, $USER! Beginning ARARA development environment setup."
echo ""

echo -n "Input your base port number: "
read base_port

echo "Choose which database you want to use: "
select database_type in mysql sqlite
do
    break
done

if [ $database_type == "mysql" ]; then
    echo -n "Input your MySQL account password: "
    read mysql_account_password
fi

echo "; User-specific supervisor configuration

[inet_http_server]          ; inet (TCP) server disabled by default
port=127.0.0.1:$base_port        ; (ip_address:port specifier, *:port for all iface)
username=admin              ; (default is no username (open server))
password=sparcs             ; (default is no password (open server))

;[program:arara_engine]
;autostart=false            ; uncomment if you don't want to use arara_engine" > etc/supervisord.conf

echo "#-*- coding: utf8 -*-

# Part 1. DB Setting
# ARAra Engine supports MySQL & SQLite.
# To use MySQL, ID / PASSWD / DB HOST / DB NAME is required.
MYSQL_ID     = \"$USER\"
MYSQL_PASSWD = \"$mysql_account_password\"
MYSQL_DBHOST = \"127.0.0.1\"
MYSQL_DBNAME = \"$USER\"
# To use SQLite, Path to the db is required.
SQLITE_PATH  = \"arara_sqlite.db\"
# Or, if you are using a DB which is supported by SQLAlchemy,
# you could use your own DB_CONNECTION_STRING.
DB_CONNECTION_STRING = \"\"
# Specify your choice between \"mysql\" / \"sqlite\" / \"other\".
ARARA_DBTYPE = \"$database_type\"

# Part 2. Backend Server Setting
ARARA_SERVER_HOST = '127.0.0.1'
ARARA_SERVER_BASE_PORT = $((base_port+2))
SESSION_EXPIRE_TIME = 3610 # seconds
ARARA_POOL_DEBUG_MODE = False
#To use POOL DEBUG MODE, turn on the flag above. (see changeset 1247)
ARARA_DEBUG_HANDLER_ON = False
#To use DEBUG Handler on, turn on the flag above.

# Part 3. Mail Server & Mail Contents Setting
# Specify Web Frontend address below.
WARARA_SERVER_ADDRESS = '143.248.234.153:$((base_port+12))'
MAIL_HOST = 'localhost'
MAIL_SENDER = 'ara@ara.kaist.ac.kr'
MAIL_CONTENT = {
        'activation': 'You have been successfully registered as the ARA member.<br />To use your account, you have to activate it.<br />Please click the link below on any web browser to activate your account.<br /><br />',
        'id_recovery': '',
}
MAIL_TITLE = {
        'activation': '[ARA] Please activate your account 아라 계정 활성화',
        'id_recovery': '[ARA] ARA Username Assistance 아라 아이디 찾기',
}

# Part 4. BOT Setting
BOT_ENABLED = True
# BOT's account name and password setting.
# Warning : Do not change BOT's password in web page.
BOT_ACCOUNT_USERNAME = u'BOT'
BOT_ACCOUNT_PASSWORD = u'i_am_ara_bot'
BOT_SERVICE_SETTING = {'weather_board_name'    : '_weather',
                       'weather_service_area'  : ('seoul', 'daejeon') }

# SYSOP Initialization Setting
SYSOP_INITIAL_USERNAME = u'SYSOP'
SYSOP_INITIAL_PASSWORD = u'SYSOP'

# LOG FILE PATH
ARARA_LOG_PATH = 'arara_server.log'
ARARA_DEBUG_LOG_PATH = 'arara_server_debug.log'

# Number of Threads to use
ARARA_NUM_THREADS = 20

# Memcache
USE_MEMCACHED = False
MEMCACHED_SERVER_LIST = [ '127.0.0.1:11211' ]
MEMCACHED_PREFIX = '$USER'

# K-Search Server Setting
KSEARCH_API_SERVER_ADDRESS = 'http://nan.sparcs.org:9000/api'
KSEARCH_API_KEY = '54ebf56de7684dba0d69bffc9702e1b4'" > etc/arara_settings.py

echo "#-*- coding: utf8 -*-
# ARARA Server Setting
ARARA_SERVER_HOST = '127.0.0.1'
ARARA_SERVER_BASE_PORT = $((base_port+2))

# Mail Server Setting
WARARA_SERVER_ADDRESS = '127.0.0.1'

# Web Server FILEDIR Setting
FILE_DIR = '/home/ara/arara/files'
FILE_MAXIMUM_SIZE = 100*1024*1024

# ARAra forecast Service Setting
USE_WEATHER_FORECAST = True
WEATHER_ICON_PATH = '/media/image/weather/'

# Indicates whether KSearch is available
KSEARCH_ENABLED = False

# Django Frontend Setting (will be imported by warara/settings.py)

# Set DEBUG to either True or False.
# DEBUG = False
DEBUG = True

ADMINS = (
        #  When you disabled DEBUG feature, you must specify your information below
        # to keep track on DEBUG information.
        # ('Your Name', 'your_email@domain.com'),
        # ('ARA SYSOP', 'ara@ara.kaist.ac.kr'),
)

# If you don't want to set SESSION_FILE_PATH using default option, uncomment below.
# SET_SESSION_FILE_PATH = False


# If you somehow want to set memcached configuration, uncomment below
# CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
# CACHE_MIDDLEWARE_SECONDS = 30  # (pipoket): Minimum caching time
" > etc/warara_settings.py

mkdir log >& /dev/null
mkdir run >& /dev/null

supervisorctl stop all >& /dev/null
supervisorctl shutdown >& /dev/null
killall -u $USER python >& /dev/null
make clean
make > /dev/null

echo ""
echo "Completed."
echo "port $base_port : Supervisor"
echo "port $((base_port+2)) : Arara backend"
echo "port $((base_port+12)) : Arara frontend"
echo ""

out=0
while [ $out -ne 1 ]
do
    echo -n "Would you run the servers now?[Y/n]: "
    read run_server
    case $run_server in
        [Yy] )
            supervisord >& /dev/null;
            python bin/warara_server.py -p $((base_port+12)) & >& /dev/null;
            echo "Connect to http://143.248.234.153:$((base_port+12))"
	    echo "You might need to manually check something else."
            out=1;
            ;;
        [Nn] )
            out=1;
            ;;
        *) 
            echo "Enter Y or n!";
            ;;
    esac
done

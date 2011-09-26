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

echo "[unix_http_server]
file=run/supervisor.sock   ; (the path to the socket file)
;chmod=0700                 ; sockef file mode (default 0700)
;chown=nobody:nogroup       ; socket file uid:gid owner
;username=user              ; (default is no username (open server))
;password=123               ; (default is no password (open server))

[inet_http_server]         ; inet (TCP) server disabled by default
port=127.0.0.1:$base_port        ; (ip_address:port specifier, *:port for all iface)
username=admin              ; (default is no username (open server))
password=tnfqkrtm               ; (default is no password (open server))

[supervisord]
logfile=log/supervisord.log ; (main log file;default \$CWD/supervisord.log)
logfile_maxbytes=50MB       ; (max main logfile bytes b4 rotation;default 50MB)
logfile_backups=10          ; (num of main logfile rotation backups;default 10)
loglevel=debug               ; (log level;default info; others: debug,warn,trace)
pidfile=run/supervisord.pid ; (supervisord pidfile;default supervisord.pid)
nodaemon=false              ; (start in foreground if true;default false)
minfds=1024                 ; (min. avail startup file descriptors;default 1024)
minprocs=200                ; (min. avail process descriptors;default 200)
;umask=022                  ; (process file creation umask;default 022)
;user=chrism                 ; (default is current user, required if root)
;identifier=supervisor       ; (supervisord identifier, default is 'supervisor')
;directory=/tmp              ; (default is not to cd during start)
;nocleanup=true              ; (don't clean up tempfiles at start;default false)
childlogdir=log            ; ('AUTO' child log dir, default \$TEMP)
;environment=KEY=value       ; (key value pairs to add to environment)
;strip_ansi=false            ; (strip ansi escape codes in logs; def. false)

; the below section must remain in the config file for RPC
; (supervisorctl/web interface) to work, additional interfaces may be
; added by defining them in separate rpcinterface: sections
[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix://run/supervisor.sock ; use a unix:// URL  for a unix socket
;serverurl=http://127.0.0.1:9001 ; use an http:// url to specify an inet socket
;username=chris              ; should be same as http_username if set
;password=123                ; should be same as http_password if set
;prompt=mysupervisor         ; cmd line prompt (default \"supervisor\")
;history_file=~/.sc_history  ; use readline history if available

; The below sample program section shows all possible program subsection values,
; create one or more 'real' program: sections to be able to control them under
; supervisor.

;[program:theprogramname]
;command=/bin/cat              ; the program (relative uses PATH, can take args)
;process_name=%(program_name)s ; process_name expr (default %(program_name)s)
;numprocs=1                    ; number of processes copies to start (def 1)
;directory=/tmp                ; directory to cwd to before exec (def no cwd)
;umask=022                     ; umask for process (default None)
;priority=999                  ; the relative start priority (default 999)
;autostart=true                ; start at supervisord start (default: true)
;autorestart=true              ; retstart at unexpected quit (default: true)
;startsecs=10                  ; number of secs prog must stay running (def. 1)
;startretries=3                ; max # of serial start failures (default 3)
;exitcodes=0,2                 ; 'expected' exit codes for process (default 0,2)
;stopsignal=QUIT               ; signal used to kill process (default TERM)
;stopwaitsecs=10               ; max num secs to wait b4 SIGKILL (default 10)
;user=chrism                   ; setuid to this UNIX account to run the program
;redirect_stderr=true          ; redirect proc stderr to stdout (default false)
;stdout_logfile=/a/path        ; stdout log path, NONE for none; default AUTO
;stdout_logfile_maxbytes=1MB   ; max # logfile bytes b4 rotation (default 50MB)
;stdout_logfile_backups=10     ; # of stdout logfile backups (default 10)
;stdout_capture_maxbytes=1MB   ; number of bytes in 'capturemode' (default 0)
;stderr_logfile=/a/path        ; stderr log path, NONE for none; default AUTO
;stderr_logfile_maxbytes=1MB   ; max # logfile bytes b4 rotation (default 50MB)
;stderr_logfile_backups=10     ; # of stderr logfile backups (default 10)
;stderr_capture_maxbytes=1MB   ; number of bytes in 'capturemode' (default 0)
;environment=A=1,B=2           ; process environment additions (def no adds)
;serverurl=AUTO                ; override serverurl computation (childutils)


[program:arara_engine]
command=./bin/thrift_arara_server.py

; The below sample eventlistener section shows all possible
; eventlistener subsection values, create one or more 'real'
; eventlistener: sections to be able to handle event notifications
; sent by supervisor.

;[eventlistener:theeventlistenername]
;command=/bin/eventlistener    ; the program (relative uses PATH, can take args)
;process_name=%(program_name)s ; process_name expr (default %(program_name)s)
;numprocs=1                    ; number of processes copies to start (def 1)
;events=EVENT                  ; event notif. types to subscribe to (req'd)
;buffer_size=10                ; event buffer queue size (default 10)
;directory=/tmp                ; directory to cwd to before exec (def no cwd)
;umask=022                     ; umask for process (default None)
;priority=-1                   ; the relative start priority (default -1)
;autostart=true                ; start at supervisord start (default: true)
;autorestart=true              ; retstart at unexpected quit (default: true)
;startsecs=10                  ; number of secs prog must stay running (def. 1)
;startretries=3                ; max # of serial start failures (default 3)
;exitcodes=0,2                 ; 'expected' exit codes for process (default 0,2)
;stopsignal=QUIT               ; signal used to kill process (default TERM)
;stopwaitsecs=10               ; max num secs to wait b4 SIGKILL (default 10)
;user=chrism                   ; setuid to this UNIX account to run the program
;redirect_stderr=true          ; redirect proc stderr to stdout (default false)
;stdout_logfile=/a/path        ; stdout log path, NONE for none; default AUTO
;stdout_logfile_maxbytes=1MB   ; max # logfile bytes b4 rotation (default 50MB)
;stdout_logfile_backups=10     ; # of stdout logfile backups (default 10)
;stderr_logfile=/a/path        ; stderr log path, NONE for none; default AUTO
;stderr_logfile_maxbytes=1MB   ; max # logfile bytes b4 rotation (default 50MB)
;stderr_logfile_backups        ; # of stderr logfile backups (default 10)
;environment=A=1,B=2           ; process environment additions
;serverurl=AUTO                ; override serverurl computation (childutils)

; The below sample group section shows all possible group values,
; create one or more 'real' group: sections to create \"heterogeneous\"
; process groups.

;[group:thegroupname]
;programs=progname1,progname2  ; each refers to 'x' in [program:x] definitions
;priority=999                  ; the relative start priority (default 999)

; The [include] section can just contain the \"files\" setting.  This
; setting can list multiple files (separated by whitespace or
; newlines).  It can also contain wildcards.  The filenames are
; interpreted as relative to this file.  Included files *cannot*
; include files themselves.

;[include]
;files = relative/directory/*.ini" > supervisord.conf

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

#!/usr/bin/python

import getopt, sys, os
from subprocess import call

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_PATH)

from etc.warara_settings import FILE_DIR, FILE_MAXIMUM_SIZE

def print_option_info(short_name, long_name, description):
    print_str = "  "+short_name[:2]+', '
    print_str += long_name[:18]
    print_str += " "*(25-len(print_str))
    i = 0
    while (i+1)*50 < len(description):
        print_str += description[i*50:(i+1)*50] + '\n' + " " * 25
        i += 1
    print_str += description[i*50:] + '\n'
    print print_str

def print_help():
    print 'Ara attachments backup script\n'
    print 'Usage: python backup_attachments.py [options]\n'
    print '\033[1mOptions:\033[0;0m'
    print_option_info('-d', '--destination=PATH', 'Specify the path to the destination. It can be a local path(e.g. /home/someuser/backup) or a remote path that can be accessed with ssh(e.g. user@some.host:/home/someuser/backup).')
    print_option_info('-h', '--help', 'Print this help page.')

try:
    opts, args = getopt.getopt(sys.argv[1:], "d:h", ["destination=", "help"])
except getopt.GetoptError, err:
    print str(err)
    sys.exit(2)

destination_path = None

for option, value in opts:
    if option in ('-h', '--help'):
        print_help()
        sys.exit(0)
    if option in ('-d', '--destination'):
        if not destination_path:
            destination_path = value
        else:
            print 'Destination path already given!'
            sys.exit(2)

if not destination_path:
    destination_path = raw_input('Please input destination path : ')

if not FILE_DIR.endswith('/'):
    FILE_DIR += '/'

call(['rsync', '-avAXzu', FILE_DIR, destination_path])

print '\nFinished backing up attachments'

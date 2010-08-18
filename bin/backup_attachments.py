#!/usr/bin/python

import getopt, sys, os
from subprocess import call

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_PATH)

from etc.warara_settings import FILE_DIR, FILE_MAXIMUM_SIZE

try:
    opts, args = getopt.getopt(sys.argv[1:], "d:", ["destination="])
except getopt.GetoptError, err:
    print str(err)
    sys.exit(2)

destination_path = None

for option, value in opts:
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

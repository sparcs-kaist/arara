# Author: Junseong Lee
# Created: 2011-07-29
# Description
#   Minimize CSS/JS codes in ARAra Engine, via YUI Compressor.
#   It requires JAVA Runtine Environment.

import getopt, sys, os, shutil
from subprocess import Popen, PIPE
YUI_VERSION = "2.4.6"
YUI_PATH = os.path.realpath(os.path.dirname(__file__))
MAKE_BACKUP = True

def usage():
    print """CSS/JS Minifier for ARAra engine

Usage:
  css_js_minifier.py [OPTIONS] [PATH]
Options:

 -n  --no-backup  Doesn't create backup files
 -h  --help       Display this page
 -v  --version    Specify YUI version (default: %s)
 -p  --path       Specify YUI path (default: %s)
""" % (YUI_VERSION, YUI_PATH)

def error(message=""):
    print "error:", message
    print
    usage()
    sys.exit(2)

def minimize(file):
    YUI = os.path.join(YUI_PATH, ("yuicompressor-%s.jar")%YUI_VERSION)
    if not os.path.isfile(YUI):
        error("Cannot find YUICompressor!")

    if file.endswith("css"):
        proc = Popen(['java', '-jar', YUI, '--type', 'css'], stdout=PIPE, stderr=PIPE, stdin=PIPE)
    elif file.endswith("js"):
        proc = Popen(['java', '-jar', YUI, '--type', 'js'], stdout=PIPE, stderr=PIPE, stdin=PIPE)
    else: return

    print file
    if MAKE_BACKUP:
        shutil.copy2(file, file + ".long")

    f = open(file, "r"); content = f.read(); f.close()
    stdout, stderr = proc.communicate(input=content)
    f = open(file, "w"); f.write(stdout); f.close()
    print str(stderr)

def traverse(path):
    if os.path.isfile(path):
        minimize(path)
    elif os.path.isdir(path):
        for subpath in os.listdir(path):
            traverse(os.path.join(path, subpath))
    else:
        error("Cannot recognize the file")

def main():
    global YUI_VERSION, YUI_PATH, MAKE_BACKUP
    try:
        opts, args = getopt.getopt(sys.argv[1:], "nhv:p:", ["no-backup", "help", "version=", "path="])
    except getopt.GetoptError, err:
        error(err)

    for o, v in opts:
        if o in ("--help", "-h"):
            usage()
            sys.exit()
        if o in ("--no-backup", "-n"):
            MAKE_BACKUP = False
        if o in ("--version", "-v"):
            YUI_VERSION = v
        if o in ("--path", "-p"):
            YUI_PATH = v

    if len(args) != 1:
        error('No file names found')

    traverse(args[0])

if __name__ == "__main__":
    main()

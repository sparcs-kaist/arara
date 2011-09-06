#!/usr/bin/python
#-*- coding: utf-8 -*-
'''
Thrift Server 에 접속하여 특정 함수를 실행한다.
해당 함수는 파라메터가 없는 함수여야 한다.
'''
import getopt
import os
import sys
import traceback

THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'gen-py'))
ARARA_PATH  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(THRIFT_PATH)
sys.path.append(ARARA_PATH)

from arara import server


def usage():
    print "  Usage: call_simple_middleware_command.py [manager_name].[command_name]"


class CommandError(Exception):
    pass


def main(argv):
    try:
        _, args = getopt.getopt(argv, "", [])
        if len(args) != 2:
            raise CommandError()
        manager, command = args[1].split(".")
    except (getopt.GetoptError, CommandError, ValueError):
        usage()
        sys.exit(2)

    try:
        getattr(server.get_server().__getattr__(manager), command)()
        print "DONE."
    except Exception:
        print traceback.format_exc()

if __name__ == "__main__":
    main(sys.argv)

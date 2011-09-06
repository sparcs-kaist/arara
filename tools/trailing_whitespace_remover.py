#!/usr/bin/python
#-*- coding: utf-8 -*-
'''
Whitespace Remover for ARAra Project
====================================

Argument 로 주어진 Python 코드 파일의 각 줄의 꼬리에 붙은 공백 문자들을 제거
주어진 파일은 UNIX 형식 (\\n 문자만으로 개행) 을 따른다고 가정
'''
import getopt
import os
import re
import stat
import sys

TRAILING_SPACE = r'[ \t\r\f\v]+\n'  # 각 줄의 꼬리에 붙은 공백 문자들을 찾는 정규식
END_OF_LINE = r'\n'  # 줄바꿈 문자


def usage():
    print 'Usage: trailing_whitespace_remover.py [FILE|PATH] ...'
    print ''
    print 'Remove trailing whitespace from given FILE.'
    print 'If a PATH is given, it will be applied to  all files under the PATH.'


def cleanup_file(filename):
    """
    주어진 파일의 각 줄 맨 마지막의 빈칸을 제거한다.

    @type  filename: str
    @param filename: 파일의 경로
    """
    with open(filename, "r") as f:
        contents = f.read()

    with open(filename, "w") as f:
        f.write(re.sub(TRAILING_SPACE, END_OF_LINE, contents))


def handle_directory(path):
    """
    주어진 디렉토리 안의 모든 파일과 하위디렉토리에 cleanup_file 을 적용한다.

    @type  path: str
    @param path: 특정 Directory 를 가리키는 경로
    """
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            if filename[-3:] == ".py":
                full_path = os.path.join(dirpath, filename)
                try:
                    cleanup_file(full_path)
                except OSError:
                    print "Error while handling:", full_path


def main(argv):
    try:
        _, args = getopt.getopt(argv, "", [])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for arg in args:
        try:
            mode = os.stat(arg).st_mode
            if stat.S_ISDIR(mode):
                handle_directory(arg)
            else:
                cleanup_file(arg)
        except OSError:
            print "Skipping unknown URI:", arg


if __name__ == "__main__":
    main(sys.argv[1:])

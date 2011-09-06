#!/bin/sh
#
# Python 소스 문제점 정적분석 도구인 pyflakes 로 다음 에러를 무시하고 검사한다.
# 
#   local variable '_' is assigned to but never used
#
# TODO: 현재 cat 으로 Error Code override 를 하고 있는데 좀더 Elegant 한 구현?

ROOT_DIR=$(dirname $0)/..

if [ $# -ne 0 ]
then
	TARGETS=$@
else
	TARGETS="$ROOT_DIR/arara $ROOT_DIR/bin/*.py $ROOT_DIR/libs $ROOT_DIR/middleware $ROOT_DIR/warara"
fi

pyflakes $TARGETS | grep -v "local variable '_' is assigned to but never used" | cat

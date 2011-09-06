#!/bin/sh
#
# Python PEP8 검사도구를 사용하여, 다음 조항들을 제외하고 코딩스타일을 검사한다.
#
#   E221 multiple spaces before operator
#   E241 multiple spaces after ','
#   E501 line too long

ROOT_DIR=$(dirname $0)/..

if [ $# -ne 0 ]
then
	TARGETS=$@
else
	TARGETS="$ROOT_DIR/arara $ROOT_DIR/bin $ROOT_DIR/libs $ROOT_DIR/middleware $ROOT_DIR/warara"
fi

pep8 -r --ignore=E221,E241,E501 --exclude=thirdparty $TARGETS

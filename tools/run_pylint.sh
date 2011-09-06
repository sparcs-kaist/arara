#!/bin/sh
#
# Python 소스 정적 분석 도구 pylint 를 써서 다음 항목들을 제외하고 검사한다.
#
#   C0103 = Invalid name
#   C0111 = Missing docstring
#   C0301 = Line too long
#   C0302 = Too many lines in module
#
#   W0142 = *args and **kwargs support
#   W0212 = Accessing protected attribute of client class
#   W0221 = Arguments number differs from overridden method
# * W0403 = Relative imports
# * W0511 = XXX (comment)
#   W0603 = Using the global statement
# * W0613 = Unused argument
#
# * R0201 = Method could be a function
#   R0902 = Too many instance attributes
#   R0903 = Too few public methods
#   R0904 = Too many public methods
#   R0912 = Too many branches
#   R0913 = Too many arguments
#   R0914 = Too many local variables
#   R0915 = Too many statements
#
# 그리고 다음 에러들을 grep 으로 일부러 무시한다.
#
#   Redefining built-in 'id'
#   Instance of 'RelationshipProperty' has no 'has' member
#   Instance of '*' has no '__table__' member
#
# 그리고 similarity check 에서 12줄 이상 유사할 때만 제안하게 한다.
#
# TODO: 에러코드를 grep 이 덮어쓰고 cat 이 덮어쓰는데, 좀더 엘레강트한 구현은?
# TODO: pylintrc 가 없을 때의 stderr 를 /dev/null 로 보내는데, 괜찮을까?

ROOT_DIR=$(dirname $0)/..

if [ $# -ne 0 ]
then
	TARGETS=$@
else
	TARGETS="$ROOT_DIR/arara $ROOT_DIR/bin $ROOT_DIR/libs $ROOT_DIR/middleware $ROOT_DIR/warara"
fi

PYTHONPATH=${PYTHONPATH}:$ROOT_DIR:$ROOT_DIR/gen-py pylint $TARGETS \
	       	--include-ids=y \
	       	--disable=C0111,C0301,W0511,C0103,W0142,W0603,W0212,W0403,R0903,R0913,R0914,R0902,W0221,R0915,R0904,R0912,C0302,R0201,W0613 \
	       	--reports=n \
	       	--min-similarity-lines=12 \
		--ignore=thirdparty 2> /dev/null \
	       	| grep -v "Redefining built-in 'id'" \
	       	| grep -v "Instance of 'RelationshipProperty' has no 'has' member" \
	       	| grep -v "has no '__table__' member" | cat

#!/usr/bin/env bash
PODIR=`dirname $0`/locale
xgettext `find . -name \*.py` -o $PODIR/ara.pot

POFILES=`find $PODIR -name \*.po`
for file in $POFILES
do
    msgmerge -U $file $PODIR/ara.pot
done

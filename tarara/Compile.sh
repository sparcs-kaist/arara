#!/usr/bin/env bash
PODIR=`dirname $0`/locale
POFILES=`find $PODIR -name \*.po`
for file in $POFILES
do
    msgfmt $file -o ${file%po}mo
done

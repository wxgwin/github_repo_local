#!/bin/sh
DIRNAME=$0
if [ "${DIRNAME:0:1}" = "/" ];then
    CURDIR=`dirname $DIRNAME`
else
    CURDIR="`pwd`"/"`dirname $DIRNAME`"
fi

CURDIR=`echo ${CURDIR} | sed 's/\/.$//g'`

if [ $# -eq 1 ];then
	echo "aaaa"
	/usr/local/bin/python2.7 ${CURDIR}/auto_sdk.py $1
else
	/usr/local/bin/python2.7 ${CURDIR}/auto_sdk.py 
fi

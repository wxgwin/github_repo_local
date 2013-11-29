#!/bin/sh

DIRNAME=$0
if [ "${DIRNAME:0:1}" = "/" ];then
    CURDIR=`dirname $DIRNAME`
else
    CURDIR="`pwd`"/"`dirname $DIRNAME`"
fi

/usr/local/bin/python2.7 ${CURDIR}/reset_folder/reset_tool.py

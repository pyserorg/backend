#!/bin/sh


BIN_DIR=`dirname $0`
. ${BIN_DIR}/common.sh
setup


flask users create -a --password Sekrit admin@example.com
flask users admin admin@example.com
flask events create `date '+%Y'`

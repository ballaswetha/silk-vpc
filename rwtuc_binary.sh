#!/bin/bash
CURRENT_HOUR=`date +%H`
TODAY_DATE=`date +"%Y/%m/%d"`
mkdir -p ${RWSENDER_INCOMING_DIRECTORY}/${TODAY_DATE}
for file in `find ${LOCAL_DIR} -type f -mmin +15 ! -name '*.log.gz'`
do
if [ "${file: -2}" != ${CURRENT_HOUR} ]
then
rwtuc ${file} --output-path=${RWSENDER_INCOMING_DIRECTORY}/${TODAY_DATE}/${file##*/} && rm  -v ${file}
fi
done

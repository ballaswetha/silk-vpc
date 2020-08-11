#!/bin/bash
CURRENT_HOUR=`date +%H`
for file in `find ${LOCAL_DIR} -type f -mmin +15 ! -name '*.log.gz'`
do
if [ "${file: -2}" != ${CURRENT_HOUR} ]
then
rwtuc ${file} --output-path=${RWSENDER_INCOMING_DIRECTORY}/${file##*/} && rm  -v ${file}
fi
done

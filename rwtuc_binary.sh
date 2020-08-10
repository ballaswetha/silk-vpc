#!/bin/bash
# This is to convert files to silk binray format
source .env
CURRENT_HOUR=`date +%H`
# Looks for files that are not updated in last 15 minutes and convert them
for file in `find ${LOCAL_DIR} -type f -mmin +15`
do
if [ "${file: -2}" != ${CURRENT_HOUR} ] #Ignore if the file exteniosn equals to current hour
then
	OUT_FILE_NAME='{}'
	echo $OUT_FILE_NAME
	if `rwtuc ${file} --output-path=${RWSENDER_INCOMING_DIRECTORY}/${file##*/}`
	then
	echo "Delete file"
	#rm  ${file} #To DO. Remove the comment and dlete file once it is processed to binary
fi
fi
done
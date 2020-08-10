#! /usr/bin/python
# -*- coding: utf-8 *-*

import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

import os
import logging
from datetime import datetime

from s3_file_download import S3FileDownload
from vpc_silk_log_insert import VPCSiLKLogMgmt

class SQSFileManagement:

    """
    Class for monitoring the SQS queue for new S3 create object events .
    Inputs:
        SQS_QUEUE_NAME: name of the SQS queue as declared in the .env file 

    Outputs:
        local_file_path: file path of the downloaded vpcflow log that needs to be parsed prior to handling by SiLK
    """

    def __init__(self, SQS_QUEUE_NAME, AWS_REGION_NAME):
        self.SQS_QUEUE_NAME = SQS_QUEUE_NAME
        self.AWS_REGION_NAME = AWS_REGION_NAME
        self.my_config = Config(
            region_name = self.AWS_REGION_NAME,
            signature_version = 'v4',
            retries = {
                'max_attempts': 10,
                'mode': 'standard'
            }
        )
        self.sqs_queue = boto3.client('sqs', config=self.my_config)
        
    def manage_s3_events(self):
        local_file_path = ""
        VPCFLOW_RAW_LOGS_DIRECTORY = os.environ.get("VPCFLOW_RAW_LOGS_DIRECTORY") # Get the directory for storing vpcSiLK logs 
        log_file_name = VPCFLOW_RAW_LOGS_DIRECTORY + str(datetime.now().strftime("%Y%m%d")) + ".log"

        try:
            response = self.sqs_queue.receive_message(QueueUrl=self.SQS_QUEUE_NAME,WaitTimeSeconds=20,MaxNumberOfMessages=1) # Retrieve one SQS message at a time 
            
            if response.get('Messages'):
                sqs_messages = response.get('Messages') 
                sqs_messages_dict = eval(sqs_messages[0]['Body'])
                sqs_receipt_handle = sqs_messages[0]['ReceiptHandle']

                for item in range(len(sqs_messages_dict['Records'])):
                    bucket_name = sqs_messages_dict['Records'][item]['s3']['bucket']['name'] 
                    file_name = str(sqs_messages_dict['Records'][item]['s3']['object']['key'])
                    
                    """ Create an S3FileDownload object and download the file to the LOCAL_DIR """
                    s3_file_handle = S3FileDownload(bucket_name, file_name)
                    local_file_path = s3_file_handle.fetch_s3_file()

                    if local_file_path:
                        response_delete = self.sqs_queue.delete_message(QueueUrl=self.SQS_QUEUE_NAME, ReceiptHandle=sqs_receipt_handle)
                        vpc_log_handle = VPCSiLKLogMgmt(log_file_name, logging.Formatter('%(asctime)s %(levelname)s %(message)s'), "SQS Message delete reponse: " + str(response_delete), logging.INFO)
                        vpc_log_handle.vpc_silk_log_insert()
        
        except Exception as e:
            vpc_log_handle = VPCSiLKLogMgmt(log_file_name, logging.Formatter('%(asctime)s %(levelname)s %(message)s'), "sqs_queue.receive_message error." + str(e), logging.ERROR)
            vpc_log_handle.vpc_silk_log_insert()

        return local_file_path
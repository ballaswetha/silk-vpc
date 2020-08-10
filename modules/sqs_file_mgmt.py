#! /usr/bin/python
# -*- coding: utf-8 *-*

import boto3
from botocore.exceptions import ClientError

from s3_file_download import S3FileDownload

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
        self.sqs_queue = boto3.client('sqs', region_name=self.AWS_REGION_NAME)
        
    def manage_s3_events(self):
        local_file_path = ""
        sqs_receipt_handle = ""
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
                        print("Delete response", response_delete)
        
        except Exception as e:
            print("sqs_queue.receive_message error.", e)

        return local_file_path, sqs_receipt_handle

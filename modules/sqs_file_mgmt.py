#! /usr/bin/python
# -*- coding: utf-8 *-*

import boto3
from botocore.exceptions import ClientError

class SQSFileManagement:

    def __init__(self, session, SQS_QUEUE_NAME):
        self.session = session 
        self.SQS_QUEUE_NAME = SQS_QUEUE_NAME
        self.sqs_queue = self.session.client('sqs')
        
    def manage_s3_events(self):
        try:
            response = self.sqs_queue.receive_message(QueueUrl=self.SQS_QUEUE_NAME,WaitTimeSeconds=20,MaxNumberOfMessages=5)
            sqs_messages = response.get('Messages') 
            print(sqs_messages)
            #print(sqs_messages[0]['Body'])
            sqs_messages_dict = eval(sqs_messages[0]['Body'])
            #print(sqs_messages_dict)
            for item in range(len(sqs_messages_dict['Records'])):
                s3_file_path = str(sqs_messages_dict['Records'][item]['s3']['bucket']['name']) + "/" + str(sqs_messages_dict['Records'][item]['s3']['object']['key'])
                print(s3_file_path)
                # TODO - download the S3 file if it exists
                # Read the file, create separate files with eni references 
                # local_file_path once the file is downloaded 
        except Exception as e:
            print("SQSClient.get_messages error, retrying.",e)

        return local_file_path 

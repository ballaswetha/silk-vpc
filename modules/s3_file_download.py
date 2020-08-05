#! /usr/bin/python
# -*- coding: utf-8 *-*

import boto3
from botocore.exceptions import ClientError
import os

from dotenv import load_dotenv

class S3FileDownload:

    """
    Class for downloading an S3 object to a local file.
    Inputs:
        session: existing session from the SQS queue management function
        bucket_name: name of the bucket where the file is located

    Outputs:
        local_file_name: A new file is created in the LOCAL_DIR preserving the path of the S3 object
    """

    def __init__(self, session, bucket_name, file_name):
        self.session = session 
        self.bucket_name = bucket_name
        self.file_name = file_name 
        self.s3_file = self.session.client('s3')
        
    def fetch_s3_file(self):
        load_dotenv()
        LOCAL_DIR = os.environ.get("LOCAL_DIR")
        try:
            if not os.path.isdir(str(LOCAL_DIR)+str(self.file_name)): # Retain structure of S3 path on the local host 
                os.makedirs(str(LOCAL_DIR)+str(self.file_name))
            response = self.s3_file.download_file(self.bucket_name, self.file_name, str(LOCAL_DIR)+str(self.file_name))
            return (str(LOCAL_DIR)+str(self.file_name)) # Return the local file path
        except Exception as e:
            print("s3_file.Bucket.download_file error.", e)
            return False # File download and write not successful, the "False" is used for error checking

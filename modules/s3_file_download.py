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
        bucket_name: name of the bucket where the file is located

    Outputs:
        local_file_name: A new file is created in the LOCAL_DIR preserving the path of the S3 object
    """

    def __init__(self, bucket_name, file_name):
        self.bucket_name = bucket_name
        self.file_name = file_name 
        self.s3_file = boto3.client('s3')
        
    def fetch_s3_file(self):
        load_dotenv()
        LOCAL_DIR = os.environ.get("LOCAL_DIR")
        try:
            s3_download_directory = LOCAL_DIR + "/".join(self.file_name.split("/")[:-1])
            if not os.path.isdir(s3_download_directory): # Retain structure of S3 path on the local host 
                os.makedirs(s3_download_directory)
            response = self.s3_file.download_file(self.bucket_name, self.file_name, LOCAL_DIR+str(self.file_name))
            return (LOCAL_DIR+str(self.file_name)) # Return the local file path
        except Exception as e:
            print("s3_file.Bucket.download_file error.", e)
            return False # File download and write not successful, the "False" is used for error checking

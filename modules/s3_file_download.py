#! /usr/bin/python
# -*- coding: utf-8 *-*

import boto3
from botocore.exceptions import ClientError
import os

from dotenv import load_dotenv

import logging
from datetime import datetime

from vpc_silk_log_insert import VPCSiLKLogMgmt

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
        VPCFLOW_RAW_LOGS_DIRECTORY = os.environ.get("VPCFLOW_RAW_LOGS_DIRECTORY") # Get the directory for storing vpcSiLK logs 
        log_file_name = VPCFLOW_RAW_LOGS_DIRECTORY + str(datetime.now().strftime("%Y%m%d")) + ".log"

        try:
            s3_download_directory = LOCAL_DIR + "/".join(self.file_name.split("/")[:-1])
            if not os.path.isdir(s3_download_directory): # Retain structure of S3 path on the local host 
                os.makedirs(s3_download_directory)
                response = self.s3_file.download_file(self.bucket_name, self.file_name, LOCAL_DIR+str(self.file_name))
                vpc_log_handle = VPCSiLKLogMgmt(log_file_name, logging.Formatter('%(asctime)s %(levelname)s %(message)s'), "VPC File download from S3.", logging.INFO)
                vpc_log_handle.vpc_silk_log_insert()
            return (LOCAL_DIR+str(self.file_name)) # Return the local file path
        except Exception as e:
            vpc_log_handle = VPCSiLKLogMgmt(log_file_name, logging.Formatter('%(asctime)s %(levelname)s %(message)s'), "s3_file.Bucket.download_file error." + str(e), logging.ERROR)
            vpc_log_handle.vpc_silk_log_insert()
            return False # File download and write not successful, the "False" is used for error checking

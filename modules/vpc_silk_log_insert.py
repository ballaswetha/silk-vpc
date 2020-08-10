#! /usr/bin/python
# -*- coding: utf-8 *-*

import boto3
from botocore.exceptions import ClientError

import logging
from datetime import datetime

class VPCSiLKLogMgmt:

    """
    Class for monitoring the SQS queue for new S3 create object events .
    Inputs:
        SQS_QUEUE_NAME: name of the SQS queue as declared in the .env file 

    Outputs:
        local_file_path: file path of the downloaded vpcflow log that needs to be parsed prior to handling by SiLK
    """

    def __init__(self, log_file_name, format, log_text, log_level):
        self.log_file_name = log_file_name
        self.format = format
        self.log_text = log_text 
        self.log_level = log_level

    def vpc_silk_log_insert(self):
        """
        Class to create log files for vpcSiLK program

        Inputs:
            log_file_name: Name of the log file - log file created for the day
            format: Format of log messages 
            log_text: Text to be added to the log file
            log_level: INFO, ERROR OR DEBUG
        """
        log_info = logging.FileHandler(self.log_file_name)
        log_info.setFormatter(self.format)
        
        log_events = logging.getLogger(self.log_file_name)
        log_events.setLevel(self.log_level)
        
        if not log_events.handlers:
            log_events.addHandler(log_info)
            if (self.log_level == logging.INFO):
                log_events.info(self.log_text)
            if (self.log_level == logging.ERROR):
                log_events.error(self.log_text)
            if (self.log_level == logging.WARNING):
                log_events.warning(self.log_text)
        
        log_info.close()
        log_events.removeHandler(log_info)
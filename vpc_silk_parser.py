#! /usr/bin/python
# -*- coding: utf-8 *-*

import subprocess
import shlex
import os
import shutil
import time
import sys

from dotenv import load_dotenv

import logging
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

from modules.parse_vpc_logs import ParseVPC
from modules.create_silk_conf import CreateSiLKConf
from modules.update_silk_conf import UpdateSiLKConf
from modules.sqs_file_mgmt import SQSFileManagement
from modules.vpc_silk_log_insert import VPCSiLKLogMgmt

parse_vpc_logs = None
create_silk_conf = None
update_silk_conf = None
sqs_file_mgmt = None
vpc_silk_log_insert = None

def get_vpcflow_file():
    """
    Function to read S3 events from the designated SQS queue, download the VPC Flow log file associated with the S3 event and then delete the event if the file is downloaded successfully
    """
    SQS_QUEUE_NAME = os.environ.get("SQS_QUEUE_NAME")
    AWS_REGION_NAME = os.environ.get("AWS_REGION_NAME")

    sqs_queue_handle = SQSFileManagement(SQS_QUEUE_NAME, AWS_REGION_NAME)
    local_file_path = sqs_queue_handle.manage_s3_events()

    return local_file_path

def parse_vpc_logs(vpc_file_name):
    acct_eni_dictionary = {}
    parse_vpc_logs = ParseVPC(vpc_file_name)
    acct_eni_dictionary = parse_vpc_logs.parse_vpc()

    return acct_eni_dictionary

def silk_conf(silk_config_file_name, acct_eni_dictionary):
    """
    Function to check whether the silk.conf file exists, in which case the file needs to be udpated in case a sensor value is not available. If the file does not exist, a new silk.conf file is created

    Inputs:
        silk_config_file_name: Name of the "silk.conf" file to be updated or created
        acct_eni_dictionary: Key, value pairs of ENI and account numbers collected from the parsed vpcflog log file.

    Outputs:
        silk_config_file_name: The "silk.conf" file will be created and populated with sensor information collected from the parsed vpcflog log file.

    """
    if os.path.isfile(silk_config_file_name):
        vpc_silk_log_insert(logging.Formatter('%(asctime)s %(levelname)s %(message)s'), "Default silk.conf file found, check whether updates are required", logging.INFO)
        update_silk_conf = UpdateSiLKConf(silk_config_file_name, acct_eni_dictionary)
        update_silk_conf.update_silk_conf()
    else:
        vpc_silk_log_insert(logging.Formatter('%(asctime)s %(levelname)s %(message)s'), "Default silk.conf file not found, attempting to create the file.", logging.INFO)
        create_silk_conf = CreateSiLKConf(silk_config_file_name, acct_eni_dictionary)
        create_silk_conf.create_silk_conf()

def vpc_silk_log_insert(format, log_text, log_level):
    VPCFLOW_RAW_LOGS_DIRECTORY = os.environ.get("VPCFLOW_RAW_LOGS_DIRECTORY") # Get the directory for storing vpcSiLK logs
    log_file_name = VPCFLOW_RAW_LOGS_DIRECTORY + str(datetime.now().strftime("%Y%m%d")) + ".log"

    vpc_log_handle = VPCSiLKLogMgmt(log_file_name, format, log_text, log_level)
    vpc_log_handle.vpc_silk_log_insert()

if __name__ == "__main__":
    response = load_dotenv()
    SILK_CONF_FILE = os.environ.get("SILK_CONF_FILE")

    while True:
        vpc_file_path = get_vpcflow_file()
        if vpc_file_path:
            acct_eni_dictionary = parse_vpc_logs(vpc_file_path)
            silk_conf(SILK_CONF_FILE, acct_eni_dictionary)
            s3_download_directory = "/".join(vpc_file_path.split("/")[:-1])
            try:
                os.remove(vpc_file_path) # Delete the processed VPC flow ascii log
                vpc_silk_log_insert(logging.Formatter('%(asctime)s %(levelname)s %(message)s'), "Processing completed. File " + str(vpc_file_path) + " deleted.", logging.INFO)
                os.rmdir(s3_download_directory) # Only deletes the directory if the folder is empty, and no other S3 log files need to processed; TODO - might have dangling folders!
            except OSError as e:
                vpc_silk_log_insert(logging.Formatter('%(asctime)s %(levelname)s %(message)s'), "Error deleting processed vpc log file from local host " + str(e), logging.ERROR)
#! /usr/bin/python
# -*- coding: utf-8 *-*

import subprocess  
import shlex
import os
import shutil
import time
import sys

from dotenv import load_dotenv

import boto3 
from botocore.exceptions import ClientError

from modules.parse_vpc_logs import ParseVPC
from modules.create_silk_conf import CreateSiLKConf
from modules.update_silk_conf import UpdateSiLKConf
from modules.sqs_file_mgmt import SQSFileManagement

session = None
parse_vpc_logs = None 
create_silk_conf = None 
update_silk_conf = None 
sqs_file_mgmt = None 

def get_vpcflow_file():
    """
    Function to read S3 events from the designated SQS queue, download the VPC Flow log file associated with the S3 event and then delete the event if the file is downloaded successfully 
    """
    SQS_QUEUE_NAME = os.environ.get("SQS_QUEUE_NAME")
    REGION_NAME = os.environ.get("REGION_NAME")
    AWS_PROFILE = os.environ.get("AWS_PROFILE")

    #TODO - how long does a session last for?
    """ Create an AWS session """
    try:
        session = boto3.Session(profile_name=AWS_PROFILE, region_name=REGION_NAME)
    except ClientError as error:
        print("AWS session creation error:", error)

    sqs_queue_handle = SQSFileManagement(session,SQS_QUEUE_NAME)
    local_file_path = sqs_queue_handle.manage_s3_events()

    return local_file_path

def parse_vpc_logs(vpc_file_name):
    acct_eni_dictionary = {}
    parse_vpc_logs = ParseVPC(vpc_file_name)
    acct_eni_dictionary = parse_vpc_logs.parse_vpc()

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
        print("updating existing silk.conf file")
        update_silk_conf = UpdateSiLKConf(silk_config_file_name, acct_eni_dictionary)
    else:
        print("creating a new silk.conf file")
        create_silk_conf = CreateSiLKConf(silk_config_file_name, acct_eni_dictionary)

def create_silk_file():
    """
    DELETE .... 
    args = shlex.split('rwtuc '+ rwtxt_file_name + ' --output-path=' + rw_file_name + ' --verbose')
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = process.communicate()[0]
    print (stdout)


    rwsender --incoming-directory=/home/ubuntu/silk_data --processing-directory=/home/ubuntu/silk_processing --error-directory=/home/ubuntu/silk_error --log-destination=/home/ubuntu/silk_logs/rwsender_logs --mode=server --identifier=vpc --server-port=127.0.0.1:5902 --client-ident=vpc --no-daemon
    cp silk_rwreceiver/vpc_1404.rwf /home/ubuntu/silk_rwreceiver/inicmp/2020/07/16/inicmp-eni-0cb2326aaa056edce_20200716.04

    rwreceiver --mode=client --log-directory=/home/ubuntu/silk_logs --server-address=vpc:127.0.0.1:5902 --identifier=vpc --destination-directory=/home/ubuntu/silk_receiver
    """

if __name__ == "__main__":
    response = load_dotenv()
    #silk_conf("/Users/swetha.balla/flow_log/silk.conf", acct_eni_dictionary)
    while True: 
        vpc_file = get_vpcflow_file()
        if vpc_file:
            parse_vpc_logs(vpc_file)
        #TODO - check if the "hourly" vpc_ascii file is created; if it is then update silk.conf and run through rwtuc 
        time.sleep(60) #Sleep for 1 minute TODO - is this required?
    
    #TODO - add a log / error message for when the loop breaks 
    #TODO - add proper logging 
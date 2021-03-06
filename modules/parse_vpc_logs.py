#! /usr/bin/python
# -*- coding: utf-8 *-*
import sys
import os
import gzip 

from dotenv import load_dotenv

import logging
from datetime import datetime

from vpc_silk_log_insert import VPCSiLKLogMgmt

class ParseVPC:

    def __init__(self, vpc_file_name):
        self.vpc_file_name = vpc_file_name
    
    def parse_vpc(self):
        """
        Function to convert a vpcflow log into a format that SiLK rwtuc can process. The mapping between the vpcflow log attributes and the text file attributes that rwtuc can process is outlined below. However, not all vpcflow log attributes map to an attribute that SiLK understands, and these have been marked as ignored. 
        version: ignored
        account-id: ignored (will be added to the silk.conf file as a description for each ENI)
        interface-id: sensor
        srcaddr: sIP
        dstaddr: dIP
        srcport: sPort
        dstport: dPort
        protocol: protocol
        packets: packets 
        bytes: bytes 
        start: sTime 
        end: eTime
        action: ignored
        log-status: ignored 

        Inputs:
            vpc_file_name: name of the vpcflow log that needs to be parsed

        Outputs: 
            acct_eni_dictionary: A dictionary of ENIs mapped to account numbers to be used for creating the silk.conf file 
            Parsed vpc_ascii files are created preserving the YYYY/MM/DD structure, so that the file can be converted to SiLK binary format
        """
        load_dotenv()
        LOCAL_DIR = os.environ.get("LOCAL_DIR")
        VPCFLOW_RAW_LOGS_DIRECTORY = os.environ.get("VPCFLOW_RAW_LOGS_DIRECTORY") # Get the directory for storing vpcSiLK logs 
        log_file_name = VPCFLOW_RAW_LOGS_DIRECTORY + str(datetime.now().strftime("%Y%m%d")) + ".log"

        """ Initialise a dictionary that will store key, value pairs of "<eni_id>":"<acct_num>" """
        acct_eni_dictionary = {}
        try: 
            """ 
            VPCFlow log file name format - AWSACCTNUM_vpcflowlogs_REGION_FLOWID_YYYYMMDDTHHMMZ_IDENTIFIER.log.gz 
            SiLK log file name format - DIR/SENSORTYPE/YYYY/MM/DD/SENSORTYPE-SENSORNAME_YYYYMMDD.HH 
            """
            
            timestamp = self.vpc_file_name.split("_")[4].split("T") # This returns YYYYMMDD in timestamp[0] and HH in timestamp[1]
            vpc_parsed_ascii_append = "_" + timestamp[0] + "." + timestamp[1][:2] # This retrieves the timestamp from the file, the ENI value needs to be prepended to 
            vpc_file_dir = LOCAL_DIR + timestamp[0][:4] + "/" + timestamp[0][4:6] + "/" + timestamp[0][6:8] + "/" # Directory structure LOCAL_DIR/YYYY/MM/DD 
            
            try: 
                with gzip.open(self.vpc_file_name, 'r') as vpc_filehandle:
                    next(vpc_filehandle) # ignore the first line of the vpcflow file which has header information
                    for event in vpc_filehandle:
                        """ Lists split in order of attributes = [version, account-id, interface-id, srcaddr, dstaddr, srcport, dstport, protocol, packets, bytes, start, end, action, log-status] and the corresponding value can be read using the index value from the list """
                        event_list = event.split(" ")
                        try: 
                            """ Convert string into a format that can be written; ignore events with "SKIPDATA" as the log-status """ 
                            if str(event_list[13].strip()) not in ("NODATA", "SKIPDATA"): # Ignore any events where there is NODATA or SKIPDATA in the VPC Flow log
                                event_line = event_list[3] + "|" + event_list[4] + "|" + event_list[5] + "|" + event_list[6] + "|" + event_list[7] + "|" + event_list[8] + "|" + event_list[9] + "|" + event_list[10] + "|" + event_list[11] + "|" + event_list[2] + "\n"
                                if event_list[2] == "interface-id":
                                    pass
                                else: 
                                    vpc_parsed_ascii_filename = vpc_file_dir + "aws-" + event_list[2] + vpc_parsed_ascii_append # Prepend the ENI name to the file with the timestamp      
                                    #vpc_parsed_ascii_filename = vpc_file_dir + "aws-" + event_list[2][4:] + vpc_parsed_ascii_append # Prepend the ENI name to the file with the timestamp and remove eni- from the name of the file
                                    
                                    if os.path.isdir(vpc_file_dir): # Check if the directory for the right time already exists 
                                        if os.path.isfile(vpc_parsed_ascii_filename): # File already exists for the hour and ENI, append to existing file
                                            rwtxt_filehandle = open(vpc_parsed_ascii_filename, "a+")
                                            rwtxt_filehandle.write(event_line) # Add the processed event 
                                            rwtxt_filehandle.close()
                                        else:
                                            rwtxt_filehandle = open(vpc_parsed_ascii_filename, "w+")
                                            rwtxt_filehandle.write("sIP|dIP|sPort|dPort|protocol|packets|bytes|sTime|eTime|sensor\n") # Add header information 
                                            rwtxt_filehandle.write(event_line) # Add the processed event 
                                            rwtxt_filehandle.close()
                                    else:
                                        try:
                                            os.makedirs(vpc_file_dir) # Create the directory, equivalent to mkdir -p 
                                            rwtxt_filehandle = open(vpc_parsed_ascii_filename, "w+") # Create the file in the directory 
                                            rwtxt_filehandle.write("sIP|dIP|sPort|dPort|protocol|packets|bytes|sTime|eTime|sensor\n") # Add header information 
                                            rwtxt_filehandle.write(event_line) # Add the processed event 
                                            rwtxt_filehandle.close()
                                        except OSError:
                                            vpc_log_handle = VPCSiLKLogMgmt(log_file_name, logging.Formatter('%(asctime)s %(levelname)s %(message)s'), "Creation of the directory failed:" + str(vpc_file_dir), logging.ERROR)
                                            vpc_log_handle.vpc_silk_log_insert()

                                acct_eni_dictionary[event_list[2]] = event_list[1]
                        except IndexError as e:
                            vpc_log_handle = VPCSiLKLogMgmt(log_file_name, logging.Formatter('%(asctime)s %(levelname)s %(message)s'), "VPC raw log file reading error." + str(e), logging.ERROR)
                            vpc_log_handle.vpc_silk_log_insert()
            except Exception as e:
                    vpc_log_handle = VPCSiLKLogMgmt(log_file_name, logging.Formatter('%(asctime)s %(levelname)s %(message)s'), "vpc raw log file - gzip file open error." + str(e), logging.ERROR)
                    vpc_log_handle.vpc_silk_log_insert()
                        
            vpc_filehandle.close()
        except IOError as e:
            vpc_log_handle = VPCSiLKLogMgmt(log_file_name, logging.Formatter('%(asctime)s %(levelname)s %(message)s'), "I/O error(" + str(e.errno) + "): " +str(e.strerror), logging.ERROR)
            vpc_log_handle.vpc_silk_log_insert()
        except: # Handle other exceptions such as attribute errors
            vpc_log_handle = VPCSiLKLogMgmt(log_file_name, logging.Formatter('%(asctime)s %(levelname)s %(message)s'), "Unexpected error:" + str(sys.exc_info()[0]), logging.ERROR)
            vpc_log_handle.vpc_silk_log_insert()

        """ Return a dictionary with key, value pairs of enis and account numbers to construct the silk.conf file """
        return acct_eni_dictionary

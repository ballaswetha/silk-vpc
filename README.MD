# Overview of SiLK installation and set-up for processing VPC Flow logs

## AWS infrastructure set-up using dockers
* Purging raw logs
* Purging ascii logs 

Limitations: 
* Only one SQS Queue can currently be processed

### SiLK configuration
The default silk.conf is created during the first run of processing vpcflow logs, by using the file `/usr/local/share/silk/twoway-silk.conf` provided as the default configuration file for SiLK. 

Some of the caveats associated with the set-up of SiLK for procesing VPC Flow logs are:
* An "aws" class type has been added to the default silk.conf and will be used for tagging all the VPC flow logs. 
* VPC Flow logs files are consolidated into hourly files per ENI, and then converted into SiLK binary files using `rwtuc`.
* The .env file where the vpcSiLK code is running needs to populated with default values for the following fields:
    * VPCFLOW_RAW_LOGS_DIRECTORY = ""
    * SILK_CONF_FILE = ""
    * RWSENDER_INCOMING_DIRECTORY = ""
    * RWSENDER_PROCESSING_DIRECTORY = ""
    * RWSENDER_ERROR_DIRECTORY = ""
    * RWSENDER_LOGS = ""
    * RWRECEIVER_LOGS = ""
    * RWRECEIVER_DESTINATION_DIRECTORY = ""
    * SQS_QUEUE_NAME = ""
    * REGION_NAME = ""
    * AWS_PROFILE = ""
    * LOCAL_DIR = "" # It is important to make sure that the directory path does not include a _ in the name

## Future enhancements
* Investigate the addition of new fields to SiLK using SiLK plugins - https://tools.netsa.cert.org/silk/silk-plugin.html

### Using a Docker Container

Build Docker Image

``` docker build -t cloudmapper . ```

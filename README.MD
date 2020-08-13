# Overview of SiLK installation and set-up for processing VPC Flow logs

## AWS infrastructure set-up using dockers
### Build Docker Image

`docker build -t silk .`

Two containers are used for downloading and processing the vpc logs:
1. Silk - Fetch VPC logs from S3 and convert them to silk format
2. Cron - Continuosly look for files and convert to silk binary format 

As both the containers are using the same files, the directories mentioned in the .env file will be mounted as a docker volume so that both the containers can read and process these files.  

Steps for creating the containers: 
- Install docker - https://docs.docker.com/engine/install/
- Install docker-compose - https://docs.docker.com/compose/install/  
- Run following command to create containers 

`docker-compose up -d`

**Note:** Make sure to supply the correct values .env 

### Limitations: 
* Only one SQS Queue can currently be processed
* The code has not been tested for a large volume of vpcflow logs; it has been tested with 4 ENIs with an average data volume of xx GB / day.

## SiLK configuration
The default silk.conf is created during the first run of processing vpcflow logs, by using the file `/usr/local/share/silk/twoway-silk.conf` provided as the default configuration file for SiLK. Please note that rwsender and rwreceiver have not been used, but have been added to the .env file for installations that use rwsender and rwreceiver. 

Some of the caveats associated with the set-up of SiLK for procesing VPC Flow logs are:
* All user provided data, including the `silk.conf` file path is under /opt 
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


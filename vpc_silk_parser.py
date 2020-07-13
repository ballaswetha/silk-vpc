import subprocess  
import shlex
import sys
import os.path 
import shutil

def parse_vpc(vpc_file_name, rwtxt_file_name, rw_file_name):
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
        rwtxt_file_name: name of the output txt file that SiLK can process 

    Outputs: 
        acct_eni_dictionary: A dictionary of ENIs mapped to account numbers to be used for creating the silk.conf file 
    """
    try: 
        rwtxt_filehandle = open(rwtxt_file_name, "w+")
        rwtxt_filehandle.write("sIP|dIP|sPort|dPort|protocol|packets|bytes|sTime|eTime|sensor\n")
    
        """ Initialise a dictionary that will store key, value pairs of "<eni_id>":"<acct_num>" """
        acct_eni_dictionary = {}

        with open(vpc_file_name, "r") as vpc_filehandle:
            next(vpc_filehandle) # ignore the first line of the vpcflow file which has header information
            for event in vpc_filehandle:
                """ Lists split in order of attributes = [version, account-id, interface-id, srcaddr, dstaddr, srcport, dstport, protocol, packets, bytes, start, end, action, log-status] and the corresponding value can be read using the index value from the list """
                event_list = event.split(" ")
                try: 
                    """ Convert string into a format that can be written; ignore events with "SKIPDATA" as the log-status """ 
                    if "SKIPDATA" not in str(event_list[13]):
                        event_line = event_list[3] + "|" + event_list[4] + "|" + event_list[5] + "|" + event_list[6] + "|" + event_list[7] + "|" + event_list[8] + "|" + event_list[9] + "|" + event_list[10] + "|" + event_list[11] + "|" + event_list[2] + "\n"
                        rwtxt_filehandle.write(event_line)
                        acct_eni_dictionary[event_list[2]] = event_list[1]
                except IndexError:
                    pass

        vpc_filehandle.close()
        rwtxt_filehandle.close()
    except IOError as e:
        print ("I/O error(", e.errno, "): ", e.strerror)
    except: # Handle other exceptions such as attribute errors
        print ("Unexpected error:", sys.exc_info()[0])

    """ Return a dictionary with key, value pairs of enis and account numbers to construct the silk.conf file """
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
        update_silk_conf(silk_config_file_name, acct_eni_dictionary)
    else:
        create_silk_conf(silk_config_file_name, acct_eni_dictionary)

def update_silk_conf(silk_config_file_name, acct_eni_dictionary):
    #TODO - Read sensor information if file exists 
    tmp_config_file_name = "./tmp.conf"
    existing_acct_eni = set()
    new_acct_eni = {} # Dicationary with all the ENIs and account numbers that are not currently in the existing silk.conf file 
    sensor_count = 0
    sensor_string = "" 
    line_number = 0 
    sensor_line_number = 0 # Line number in the file where to update the sensor information 
    sensors_line_number = 0 # Line number where all the sensors are listed 
    sensors_existing_config = "" # String that contains list of all sensors in the existing silk.conf file 

    """ Get a list of all the ENIs from the existing silk.conf file """ 
    try:
        with open(silk_config_file_name, "r") as silk_conf_filehandle: 
            for conf_line in silk_conf_filehandle:
                sensor_line = conf_line.split()
                try: 
                    if sensor_line[0] == "sensor":
                        sensor_count = sensor_line[1]
                        sensor_line_number = line_number
                        existing_acct_eni.add(sensor_line[2])
                    elif sensor_line[0] == "sensors":
                        sensors_existing_config = conf_line
                        sensors_line_number = line_number + 1 # As the list of sensors will be on the next line 
                except IndexError:
                    pass 
                line_number += 1

        for key,value in acct_eni_dictionary.items():
            if not key in existing_acct_eni: # ENI does not exist in the current silk.conf file and needs to be added 
                new_acct_eni[key] = value 
    except IOError:
        silk_conf_filehandle.close()
    finally:
        silk_conf_filehandle.close()

    """ Create a tmp.conf file with the new config, and overwrite the existing silk.conf file with contents of the tmp.conf file """ 
    #TODO - is there a better way of doing this? Also, will fail with different number of new line characters 
    tmp_line_number = 0
    sensor_count = int(sensor_count) + 1
    sensor_string = " "
    try:
        with open(silk_config_file_name, "r") as silk_conf_filehandle, open(tmp_config_file_name, "a") as tmp_conf_filehandle:
            for conf_line in silk_conf_filehandle:
 #               print("tmp:", tmp_line_number, "sensor_line", sensor_line_number)
                if tmp_line_number <= sensor_line_number: # Write all the existing lines until a new sensor needs to be inserted 
                    tmp_conf_filehandle.write(conf_line)
                    tmp_line_number += 1
                elif tmp_line_number == sensor_line_number+1:
                #    print("LEN::" , len(new_acct_eni))
                    for key,value in new_acct_eni.items():
                        tmp_conf_filehandle.write("sensor " + str(sensor_count) + " " + key + " \"" + str(sensor_count) + " " + value + "\"\n") # Insert new sensor details into the tmp conf file 
                        sensor_count = int(sensor_count) + 1
                        sensor_string = sensor_string + key + " "
                        tmp_line_number += 1
                    tmp_conf_filehandle.write(conf_line)
                    tmp_line_number += 1
                elif tmp_line_number == sensor_line_number+len(new_acct_eni)+2:
                    tmp_conf_filehandle.write(conf_line)
                    if sensor_string == " ":
                        pass
                    else:
                        sensors_new_config = sensors_existing_config.rstrip() + sensor_string + "\n"
                    #tmp_conf_filehandle.write(sensors_existing_config + sensor_string) # Update lists of sensors
                    tmp_conf_filehandle.write(sensors_new_config)
                    tmp_line_number += 1 
                elif tmp_line_number == sensor_line_number+len(new_acct_eni)+3:
                    tmp_line_number += 1 
                else:
                    tmp_conf_filehandle.write(conf_line) # Write the remainder of the file 
                    tmp_line_number += 1
    except IOError:
        tmp_conf_filehandle.close()
        silk_conf_filehandle.close()
    finally:
        tmp_conf_filehandle.close()
        silk_conf_filehandle.close()

    shutil.move(silk_config_file_name, silk_config_file_name+".bak")
    shutil.move(tmp_config_file_name, silk_config_file_name)

def create_silk_conf(silk_config_file_name, acct_eni_dictionary):
    """
    Function to create a silk.conf file by using the AWS account numbers and ENI IDs that were collected from the vpcflow log file.

    Inputs:
        silk_config_file_name: Name of the "silk.conf" file to be created
        acct_eni_dictionary: Key, value pairs of ENI and account numbers collected from the parsed vpcflog log file.

    Outputs: 
        silk_config_file_name: The "silk.conf" file will be created and populated with sensor information collected from the parsed vpcflog log file.
    """
    try:
        silk_conf_filehandle = open(silk_config_file_name, "w+")
        sensor_count = 0
        sensor_string = "" 

        """ Add default silk.conf file values """ 
        silk_conf_filehandle.write("# For a description of the syntax of this file, see silk.conf(5).\n")
        silk_conf_filehandle.write("# The syntactic format of this file\n #    version 2 supports sensor descriptions, but otherwise identical to 1\n")
        silk_conf_filehandle.write("version 2\n")
        silk_conf_filehandle.write("# NOTE: Once data has been collected for a sensor or a flowtype, the\n # sensor or flowtype should never be removed or renumbered.  SiLK Flow\n # files store the sensor ID and flowtype ID as integers; removing or\n # renumbering a sensor or flowtype breaks this mapping.\n")
        
        """ Adding sensor information to the silk.conf file """ 
        for key, value in acct_eni_dictionary.items():
            try:
                silk_conf_filehandle.write("sensor " + str(sensor_count) + " " + key + " \"" + str(sensor_count) + " " + value + "\"\n")
            except Exception as e:
                print("Couldn't write to the silk.conf file", e)

            sensor_string = sensor_string + key + " "
            sensor_count +=1 
        
        silk_conf_filehandle.write("\nclass all\n sensors ")
        silk_conf_filehandle.write(sensor_string + "\n")
        silk_conf_filehandle.write("end class\n\n")

        """ Default values """ 
        silk_conf_filehandle.write("# Be sure you understand the workings of the packing system before \n # editing the class and type definitions below.  In particular, if you \n # change or add-to the following, the C code in silk.c \n # will need to change as well.\n")
        silk_conf_filehandle.write("class all \n   type  0 in      in \n    type  1 out     out \n    type  2 inweb   iw \n    type  3 outweb  ow \n    type  4 innull  innull \n    type  5 outnull outnull \n    type  6 int2int int2int \n    type  7 ext2ext ext2ext \n    type  8 inicmp  inicmp \n    type  9 outicmp outicmp \n    type 10 other   other \n    default-types in inweb inicmp \nend class \ndefault-class all \n")
        silk_conf_filehandle.write("# The layout of the tree below SILK_DATA_ROOTDIR. \n # Use the default, which assumes a single class. \n # path-format \"%T/%Y/%/%d\/%x\" \n \n # The plug-in to load to get the packing logic to use in rwflowpack. \n # The --packing-logic switch to rwflowpack will override this value. \n # If SiLK was configured with hard-coded packing logic, this value is \n # ignored. \n")
        silk_conf_filehandle.write("packing-logic \"silk.so\"\n")
    except IOError:
        silk_conf_filehandle.close()
    finally:
        silk_conf_filehandle.close()

def create_silk_file():
    args = shlex.split('rwtuc '+ rwtxt_file_name + ' --output-path=' + rw_file_name + ' --verbose')
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = process.communicate()[0]
    print (stdout)

if __name__ == "__main__":
    #TODO parse hourly and create rw files - directory structure needs to change 
    acct_eni_dictionary = parse_vpc("/Users/swetha.balla/flow_log/sample.txt", "/Users/swetha.balla/flow_log/rwtxt_sample.log", "/Users/swetha.balla/flow_log/vpc_output_sample.rw")
    silk_conf("/Users/swetha.balla/flow_log/silk.conf", acct_eni_dictionary)
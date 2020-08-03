#! /usr/bin/python
# -*- coding: utf-8 *-*

import sys

class CreateSiLKConf:
    def __init__(self, silk_config_file_name, acct_eni_dictionary):
        self.silk_config_file_name = silk_config_file_name
        self.acct_eni_dictionary = acct_eni_dictionary
        
    def create_silk_conf(self):
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
            silk_conf_filehandle.write("packing-logic \"packlogic-twoway.so\"\n")
        except IOError:
            silk_conf_filehandle.close()
        finally:
            silk_conf_filehandle.close()

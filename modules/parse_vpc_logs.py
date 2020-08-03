# -*- coding: utf-8 *-*
import sys

class ParseVPC:

    def __init__(self, vpc_file_name, rwtxt_file_name, rw_file_name):
        self.vpc_file_name = vpc_file_name
        self.rwtxt_file_name = rwtxt_file_name
        self.rw_file_name = rw_file_name
    
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
            rwtxt_file_name: name of the output txt file that SiLK can process 

        Outputs: 
            acct_eni_dictionary: A dictionary of ENIs mapped to account numbers to be used for creating the silk.conf file 
        """
        try: 
            rwtxt_filehandle = open(self.rwtxt_file_name, "w+")
            rwtxt_filehandle.write("sIP|dIP|sPort|dPort|protocol|packets|bytes|sTime|eTime|sensor\n")
        
            """ Initialise a dictionary that will store key, value pairs of "<eni_id>":"<acct_num>" """
            acct_eni_dictionary = {}

            with open(self.vpc_file_name, "r") as vpc_filehandle:
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
                    except IndexError as e:
                        print("VPC raw log file reading error", e)
                        pass

            vpc_filehandle.close()
            rwtxt_filehandle.close()
        except IOError as e:
            print ("I/O error(", e.errno, "): ", e.strerror)
        except: # Handle other exceptions such as attribute errors
            print ("Unexpected error:", sys.exc_info()[0])

        """ Return a dictionary with key, value pairs of enis and account numbers to construct the silk.conf file """
        return acct_eni_dictionary
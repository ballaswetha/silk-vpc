# -*- coding: utf-8 *-*
import shutil, sys

class UpdateSiLKConf:

    def __init__(self, silk_config_file_name, acct_eni_dictionary):
        self.silk_config_file_name = silk_config_file_name
        self.acct_eni_dictionary = acct_eni_dictionary
    
    def update_silk_conf(self):
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
            with open(self.silk_config_file_name, "r") as silk_conf_filehandle: 
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

            for key,value in self.acct_eni_dictionary.items():
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
        if not new_acct_eni: # Only update the file if there are new ENIs to be added to the conf file, otherwise do nothing! 
            try:
                with open(self.silk_config_file_name, "r") as silk_conf_filehandle, open(tmp_config_file_name, "a") as tmp_conf_filehandle:
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
                                sensors_new_config = sensors_existing_config
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
                shutil.move(self.silk_config_file_name, self.silk_config_file_name+".bak")
                shutil.move(tmp_config_file_name, self.silk_config_file_name)
                tmp_conf_filehandle.close()
                silk_conf_filehandle.close()
        else:
            silk_conf_filehandle.close()

#----------Imports-------------------
import os
import json
import phreeqpy.iphreeqc.phreeqc_dll as phreeqc_module
from os import walk

#-----------Setttings-----------------#
phreeq_database = ""
input_file_folder = ""
output_file_folder = ""
output_file_extension = ""

#-----------Constants-----------------


#-----------Variables-----------------
input_file_names = []
generated_output_files = []

#-----------File Methods-------------------------------
def load_config():
    global phreeq_database
    global input_file_folder
    global output_file_folder
    global output_file_extension

    config_file = open(os.path.dirname(__file__) + "/PhreeqpyBatchRun_config.json", "r")
    summary_config = config_file.read()
    summary_config = json.loads(summary_config)

    phreeq_database = summary_config["phreeq_database"]
    input_file_folder  = summary_config["input_file_folder"]
    output_file_folder = summary_config["output_file_folder"]
    output_file_extension = summary_config["output_file_extension"]

def write_line(open_file, text):
    open_file.write(text)
    open_file.write("\n")

def create_new_file(file_name):
    file = open(file_name,"x")
    return file   

def load_input_file_names():
    global input_file_names

    input_file_names = []
    for (dirpath, dirnames, filenames) in walk(input_file_folder):
        input_file_names.extend(filenames)
        break
    print(input_file_names)

def output_file_name(input_file_name, output_file_extension):
    new_file_name = ""
    file_name_parts = input_file_name.split(r".")
    file_name_parts.pop(len(file_name_parts) - 1)
    new_file_name = ".".join(file_name_parts)
    new_file_name = new_file_name + "." + output_file_extension

    return new_file_name

#-----------Phreeq Methods-------------------------------
def execute_input_file(input_file_name, output_file_name):
    global phreeq_database
    success = False

    phreeqc = phreeqc_module.IPhreeqc()
    phreeqc.create_iphreeqc()
    phreeqc.load_database(phreeq_database)
    input_file = open(input_file_name,"r")
    input_string =input_file.read()
    input_file.close()
    try:
        phreeqc.run_string(input_string)
        success = True
    except:
        print ( r"phreeqc failed to run the input file '" + input_file_name + "'." )

    if success == True:                 
        output = phreeqc.get_selected_output_array()
        output_file = open(output_file_name, "x")
        for line in range(len(output)):
            for column in range(len(output[line])):
                output_value = output[line][column]
                try: 
                    output_file.write("%.5E"%output_value)
                except:
                    output_file.write(output_value)
                output_file.write("\t")
            output_file.write("\n")
        output_file.close()

#---------------MAIN-------------------
def main():
    load_config()
    load_input_file_names()
    for input_file_name in input_file_names:
        execute_input_file(input_file_folder + input_file_name, output_file_folder + output_file_name(input_file_name, output_file_extension))

if __name__ == '__main__':
    main()
#----------Imports-------------------

import phreeqpy.iphreeqc.phreeqc_dll as phreeqc_module
from os import walk

#-----------Setttings-----------------#
#------- Edit as needed --------------#
phreeq_database = r"C:\\Temp\\PhreeqpyMonteCarlo\\phreeqc.dat"
input_file_folder = r"C:\\Temp\\PhreeqpyMonteCarlo\\input\\"

output_file_folder = r"C:\\Temp\\PhreeqpyMonteCarlo\\output\\"
output_file_extension = r"txt"


#-----------Constants-----------------


#-----------Variables-----------------
input_file_names = []
generated_output_files = []

#-----------File Methods-------------------------------
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

#-----------Phreeq Methods-------------------------------
def execute_input_file(input_file_name, output_file_name):
    global phreeq_database

    phreeqc = phreeqc_module.IPhreeqc()
    phreeqc.create_iphreeqc()
    phreeqc.load_database(phreeq_database)
    input_file = open(input_file_name,"r")
    input_string =input_file.read()
    input_file.close()
    phreeqc.run_string(input_string)
                            
    output = phreeqc.get_selected_output_array()
    output_file = open(output_file_name, "x")
    for line in range(len(output)):
        for column in range(len(output[line])):
            output_value = output[line][column]
            try: 
                output_file.write("%.3f"%output_value)
            except:
                output_file.write(output_value)
            output_file.write("\t")
        output_file.write("\n")
    output_file.close()

#---------------MAIN-------------------
 
load_input_file_names()
for input_file_name in input_file_names:
    execute_input_file(input_file_folder + input_file_name, output_file_folder + input_file_name)
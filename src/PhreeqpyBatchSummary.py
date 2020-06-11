#----------Imports-------------------
import os
import json

#-----------Setttings-----------------#
#------- Edit as needed --------------#
result_file_directory = r"C:\\Personal\\Development\\PhreeqpyMonteCarlo\\example\\output\\"
summary_file_directory = r"C:\\Personal\\Development\\PhreeqpyMonteCarlo\\example\\summary\\"
summary_config_file_name = r"C:\\Personal\\Development\\PhreeqpyMonteCarlo\\example\\summary_config.json"
summary_file_extension = "txt"

#-----------Variables-----------------
result_file_names = []
summary_config = {}

#-----------File Methods-------------------------------
def load_result_file_names():
    global result_file_names

    result_file_names = []
    for (dirpath, dirnames, filenames) in os.walk(result_file_directory):
        result_file_names.extend(filenames)
        break

def load_summmary_config():
    global summary_config

    config_file = open(summary_config_file_name, "r")
    summary_config = config_file.read()
    summary_config = json.loads(summary_config)
    #summary_files = summary_config["summaryFiles"]
    #for summary_file in summary_files:
    #    row_filters = summary_file["rowFilters"]
    #    for row_filter in row_filters:
    #        print(row_filter["column"])
    #        print(row_filter["value"])
    #        print(row_filter["match"])
    #params = summary_config["parameters"]
    #for param in params:
    #
    # 
    #     print(param)

def open_result_file(file_name):
    try:
        full_file_name = result_file_directory + file_name
        file = open(full_file_name, "r")
    except:
        raise Exception(r"unable to open file: " + full_file_name)

    return file  

def create_summary_file(summary_file_name):
    global summary_file_directory
    global summary_file_extension

    try:
        file_name = summary_file_directory + summary_file_name + r"." + summary_file_extension
        summary_file = open(file_name, "w") #'w' will open the existing file & overwrite if it already exists, otherwise create new file
        summary_file.write("File")
        for parameter in summary_config["parameters"]:
            summary_file.write("\t" + parameter)
    except:
        raise Exception(r"unable to create summary_file: " + file_name)

    return summary_file

def open_summary_file(summary_file_name):
    global summary_file_directory
    global summary_file_extension

    try:
        file_name = summary_file_directory + summary_file_name + r"." + summary_file_extension
        summary_file = open(file_name, "a") #'a' will open the existing file & append if it already exists, otherwise create new file
        summary_file.write("File")
    except:
        raise Exception(r"unable to create summary_file: " + file_name)

    return summary_file

def summarise_result_file(result_file, summary_file, row_filters):
    global summary_config

    parameter_indices = []
    interpolation_index = -1

    low_value = -999999999
    high_value = 999999999
    match_values = []
    match_low_values = []
    match_high_values = []

    result_file.seek(0)
    content = result_file.read()
    rows = content.split("\n")

    #if the last line of the file is not a data row, remove it
    if len(rows[len(rows)-1].split("\t")) == 1:
        rows.pop(len(rows)-1)

    #read the headings, and remove the header row
    header_row = rows[0]
    headings = header_row.split("\t")
    rows.pop(0)

    #find the indices for the relevant columns
    #parameters to summarize, as well as row filters
    for parameter in summary_config["parameters"]:  
        found = False
        for heading_index in range(len(headings)):
            if parameter == headings[heading_index]:
                parameter_indices.append(heading_index)
                found = True
                break
        if found == False:
            raise Exception("Parameter '" + parameter + "' not found in file '" + result_file.name + "'.")
    
    #loop through row filters to find a match
    for rowFilter in row_filters:
        found = False
        filter_parameter = rowFilter["column"]
        print('row filter: %s = %s' % (filter_parameter, rowFilter["value"]))
        for heading_index in range(len(headings)):
            if filter_parameter == headings[heading_index]:
                rowFilter["index"] = heading_index
                found = True
                break
        if found == False:
            raise Exception("Row Filter Column '" + filter_parameter + "' not found in file '" + result_file.name + "'.")


    for row in rows:
        values = row.split("\t")
        match = "untested"
        match_low = "untested"
        match_high = "untested"
        for row_filter in row_filters:
            target_value = float(row_filter["value"])
            value = float(values[row_filter["index"]])
            if row_filter["match"] == "exact":
                if value == target_value:
                    match = "true"
                else:
                    match = "false"
            if row_filter["match"] == "interpolate":
                interpolation_index = row_filter["index"]
                interpolation_value = float(row_filter["value"])
                if value == target_value:
                    match_low = "true"
                    low_value = value
                    match_high = "true"
                    high_value = value
                if value < target_value:
                    match_high = "false"
                    if value < low_value:
                        match_low = "false"
                    else:
                        match_low = "true"
                        low_value = value
                if value > target_value:
                    match_low = "false"
                    if value > high_value:
                        match_high = "false"
                    else:
                        match_high = "true"
                        high_value = value
        if match != "false":
            if match_low == "true":
                match_low_values = values
            if match_high == "true":
                match_high_values = values
            if match == "true" and match_low == "untested" and match_high == "untested":
                match_values = values

    summary_file.write("\n")
    summary_file.write(os.path.basename(result_file.name))

    for parameter_index in parameter_indices:
        if interpolation_index == -1:
            final_value = float(match_values[parameter_index])
        else:
            final_value = calculate_final_value(match_values, match_low_values, match_high_values, parameter_index, interpolation_index, interpolation_value)

        summary_file.write("\t%.3f" % final_value)

        
def calculate_final_value(match_values, low_values, high_values, parameter_index, interpolation_index, interpolation_target_value):
    if len(match_values) > 0:
        final_value = float(match_values[parameter_index])
        print("exact")
    else:
        if len(low_values) == 0:
            raise Exception("No 'low' values provided for interpolation")
        if  len(high_values) == 0:
            raise Exception("No 'high' values provided for interpolation")
        low_value = float(low_values[parameter_index])
        low_interpolation_value = float(low_values[interpolation_index])
        high_value = float(high_values[parameter_index])
        high_interpolation_value = float(high_values[interpolation_index])

        print("low value: %.3f" % low_value)
        print("high value: %.3f" % high_value)
        print("low interpolation value: %.3f" % low_interpolation_value)
        print("high interpolation value: %.3f" % high_interpolation_value)

        if low_interpolation_value == high_interpolation_value:
            final_value = high_value
        else:
            step_percent = (interpolation_target_value - low_interpolation_value) / (high_interpolation_value - low_interpolation_value)
            step_value = (high_value - low_value) * step_percent
            final_value = low_value + step_value

            print("step percent: %.3f" % step_percent)
            print("step value: %3f" % step_value)

    return final_value

def summarise_results():
    global result_file_names

    load_summmary_config()
    load_result_file_names()
    
    first_loop = True
    for result_file_name in result_file_names:
        print("summarising '%s'" % result_file_name)
        result_file = open_result_file(result_file_name)
        summary_files_config = summary_config["summaryFiles"]
        for summary_file_config in summary_files_config:
            if first_loop == True:
                summary_file = create_summary_file(summary_file_config["name"])
            else:
                summary_file = open_summary_file(summary_file_config["name"])
            print("updating summary file '%s'" % summary_file.name)
            row_filters = summary_file_config["rowFilters"]
            summarise_result_file(result_file, summary_file, row_filters)
        summary_file.close()
        first_loop = False
    result_file.close()

#---------------MAIN-------------------
def main():
    summarise_results()

if __name__ == '__main__':
    main()
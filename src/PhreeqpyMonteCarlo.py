#----------Imports-------------------
import os
import json
from random import seed
from random import random
import numpy
from numpy.random import default_rng
import re
import phreeqpy.iphreeqc.phreeqc_dll as phreeqc_module


#-----------Setttings-----------------#
template_file_name =""
generated_file_folder = ""
generated_file_name = ""
generated_file_extension = ""
iterations = 0

#-----------Constants-----------------
NULL = -9999


#-----------Variables-----------------
tags = []
template_content = ""
generated_input_files = []
generated_output_files = []

#-----------File Methods-------------------------------
def load_config():
    global template_file_name
    global generated_file_folder
    global generated_file_name
    global generated_file_extension
    global iterations

    config_file = open(os.path.dirname(__file__) + "/PhreeqpyMonteCarlo_config.json", "r")
    summary_config = config_file.read()
    summary_config = json.loads(summary_config)

    template_file_name = summary_config["template_file_name"]
    generated_file_folder  = summary_config["generated_file_folder"]
    generated_file_name = summary_config["generated_file_name"]
    generated_file_extension = summary_config["generated_file_extension"]
    iterations = summary_config["iterations"]

#-----------Class Tag-----------------
class Tag:
    name = r""
    text = r""
    parts = []
    replacement_text = r""
    value = NULL
    
    def set_string(self, string):
        self.text = string
        temporary_text = string.split(r"<<")[1].split(r">>")[0]
        self.parts = temporary_text.split(r"|")
        self.name = self.parts.pop(0)
        
#------------Number Methods------------------------
def between(number, minimum, maximum):
    if minimum != NULL:
        if number < minimum:
            return False
    if maximum != NULL:
        if number > maximum:
            return False

    return True
        
#------------Stats Methods------------------------
def Random_Triangular_Value(Left, Mode, Right):
    Random_Triangular_Variable = numpy.random.default_rng().triangular(Left,Mode,Right,1)
    return Random_Triangular_Variable

#-----------String Methods-------------------------------
def format_number(number, decimals):
    if decimals != NULL:
        format_string = r"%." + str(decimals) +r"f"
    else:
        format_string = r"%f"
    formatted_number = format_string % number
    
    return(formatted_number)

#-----------File Methods-------------------------------
def write_line(open_file, text):
    open_file.write(text)
    open_file.write("\n")

def create_new_file(file_name):
    file = open(file_name,"x")
    return file   


#------------Template & Tag Methods------------------------
def monte_carlo(template_text):
    global tags
    
    tags = []
    load_tags(template_text)
    generate_tags_replacement_text()
    result = replace_tags_by_text(template_text)

    return(result)

def load_template():
    global template_file_name
    global template_content
    
    try:
        template_file = open(template_file_name)
    except:
        raise Exception("failed to open template file '%s'" % template_file_name)
    template_content = template_file.read()
    template_file.close()

def load_tags(text):
    global tags

    matches = re.split(r"<<", text)
    matches.pop(0) #remove any text prior to the first tag
    for match in matches:
        tag_string = match.split(r">>")[0]
        tag = Tag()
        tag.set_string(r"<<" + tag_string + r">>")
        if find_tag_by_name(tag.name) != None:
            raise Exception(r"multiple tags with name '" + tag.name + "' were found. All tag names must be unique.")
        else:
            tags.append(tag)
        
def find_tag_by_name(name):
    global tags
    
    for tag in tags:
        if tag.name == name:
            return(tag)

def replace_tags_by_text(text):
    global tags
    
    new_text = text
    for tag in tags:
        new_text = new_text.replace(tag.text, tag.replacement_text)

    return(new_text)

def replace_tags_by_name(text):
    global tags
    
    new_text = text
    for tag in tags:
        new_text = new_text.replace(tag.name, tag.replacement_text)

    return(new_text)

#-----------Tag Processing methods-----------------
def generate_tags_replacement_text():
    global tags

    for tag in tags:
        if tag.parts[0] == r"number":
            generate_tag_replacement_number(tag)
        elif tag.parts[0] == r"calculation":
            generate_tag_replacement_calculation(tag)

def generate_tag_replacement_number(tag):
    if tag.parts[1] == r"normal":
        generate_tag_replacement_number_normal(tag)
        return(tag)
    elif tag.parts[1] == r"lognormal":
        generate_tag_replacement_number_lognormal(tag)
        return(tag)
    elif tag.parts[1] == r"uniform":
        generate_tag_replacement_number_uniform(tag)
        return(tag)
    elif tag.parts[1] == r"triangle":
        generate_tag_replacement_number_triangle(tag)
        return(tag)

def generate_tag_replacement_calculation(tag):
    
    decimals = NULL

    for part in tag.parts:
        sections = part.split(r":")
        if sections[0] == r"decimals":
            decimals = int(sections[1])
        elif sections[0] == r"calculation":
            pass
        else:
            expression = part

    expression = replace_tags_by_name(expression)
    try:
        calculated_number = eval(expression)
    except:
        raise Exception(r"Failed to evaluate the calculation tag '" + tag.name + "'; Expression: '" + expression + "'; Please check syntax and variable names.")

    tag.replacement_text = format_number(calculated_number, decimals)
    
    return(tag)

def generate_tag_replacement_number_normal(tag):
    mean = NULL
    standard_deviation = NULL
    minimum = NULL
    maximum = NULL
    decimals = NULL
    generated_number = NULL
    in_range = False
    
    for part in tag.parts:
        sections = part.split(r":")
        if sections[0] == r"mean":
            mean = float(sections[1])
        if sections[0] == r"stddev":
            standard_deviation = float(sections[1])
        if sections[0] == r"min":
            minimum = float(sections[1])
        if sections[0] == r"max":
            maximum = float(sections[1])
        if sections[0] == r"decimals":
            decimals = int(sections[1])

    count = 0
    while in_range == False:
        generated_number = numpy.random.default_rng().normal(mean,standard_deviation,1)[0]
        if between(generated_number, minimum, maximum):
            in_range = True
        if count == 1000:
            print ( r"failed to generate random number within minimum & maximum range after %d tries." % count )
            
    tag.value = generated_number
    tag.replacement_text = format_number(generated_number, decimals)
    
    return(tag)

def generate_tag_replacement_number_lognormal(tag):
    mean = NULL
    sigma = NULL
    minimum = NULL
    maximum = NULL
    decimals = NULL
    generated_number = NULL
    in_range = False
    
    for part in tag.parts:
        sections = part.split(r":")
        if sections[0] == r"mean":
            mean = float(sections[1])
        if sections[0] == r"sigma":
            sigma = float(sections[1])
        if sections[0] == r"min":
            minimum = float(sections[1])
        if sections[0] == r"max":
            maximum = float(sections[1])
        if sections[0] == r"decimals":
            decimals = int(sections[1])

    count = 0
    while in_range == False:
        generated_number = numpy.random.default_rng().lognormal(mean,sigma,1)[0]
        if between(generated_number, minimum, maximum):
            in_range = True
        if count == 1000:
            print ( r"failed to generate random number within minimum & maximum range after %d tries." % count )
            
    tag.value = generated_number
    tag.replacement_text = format_number(generated_number, decimals)
    
    return(tag)

def generate_tag_replacement_number_uniform(tag):
    minimum = NULL
    maximum = NULL
    decimals = NULL
    generated_number = NULL
    
    for part in tag.parts:
        sections = part.split(r":")
        if sections[0] == r"min":
            minimum = float(sections[1])
        if sections[0] == r"max":
            maximum = float(sections[1])
        if sections[0] == r"decimals":
            decimals = int(sections[1])

    generated_number = numpy.random.default_rng().uniform(minimum,maximum,1)[0]

    tag.value = generated_number
    tag.replacement_text = format_number(generated_number, decimals)
    
    return(tag)

def generate_tag_replacement_number_triangle(tag):
    left = NULL
    right = NULL
    decimals = NULL
    generated_number = NULL
    
    for part in tag.parts:
        sections = part.split(r":")
        if sections[0] == r"left":
            left = float(sections[1])
        if sections[0] == r"mode":
            mode = float(sections[1])
        if sections[0] == r"right":
            right = float(sections[1])
        if sections[0] == r"decimals":
            decimals = int(sections[1])

    generated_number = numpy.random.default_rng().triangular(left,mode,right,1)[0]

    tag.value = generated_number
    tag.replacement_text = format_number(generated_number, decimals)
    
    return(tag)

def generate_files():
    load_config()
    load_template()
    for count in range(iterations):
        new_file_content = monte_carlo(template_content)
        new_file = create_new_file(generated_file_folder + generated_file_name + "%d" % count + "." + generated_file_extension)
        new_file.write(new_file_content)
        new_file.close()

#---------------MAIN-------------------
def main():
    generate_files()

if __name__ == '__main__':
    main()
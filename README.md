# PhreeqpyMonteCarlo
Python package to run a Monte Carlo analysis using PhreeqC

This package of python scripts works in 3 distinct steps:
* Use a template to generate multiple PhreeqC input files, with random numbers assigned to appropriate variables.
* Run each of the PhreeqC input files, generating an output file
* Summarise the outputs, by copying the equivalent data from each output file into a single summary file, for easy comparison and analysis purposes.

Each step has its own configuration (in a json file), and the details are described below:
---
# 1. Generating input files from a template
## Config file
The config file for this package is named *'PhreeqpyMonteCarlo_config.json'*. The json file must be placed in the same folder as the python script file, and contain the following settings:
- **template_file_name** : the full path to the template file
- **generated_file_folder** : the full path to the folder in which to write the generated Phreeq input files
- **generated_file_name** : the name to use for the generated files. Each generated file's name will be suffixed with a number
- **generated_file_extension** : the file extension to use for the generated input files (typically *'pqi'*)
- **iterations** : the number of files to be generated

## Template file
The template template is a standard PhreeqC input file (a text file with a '.pqi' extension) except that it uses tags to indicate where random numbers should be inserted, as well as the parameters for the random number generator.

Each tag starts with *'<<'* and ends with *'>>'*
For example:
  *<<sulphur|number|normal|mean:23.56|stddev:2.56>>*
 
 Every tag consists of several parts, each separated with "|"
 The first part is always a name (e.g. *"sulphur"*)
 The second part is always the data type, which is one of *'number'*, and *'calculation'*.
 
 The remaining parts depend on the type as follows:
 ## number
 *'number'* is for random numbers. The next part of the tag is a choice alogorithm which is one of *'normal'*, *'lognormal'*, *'uniform'*, and *'triangle'*.
 Each algorithm has a set of available parameters, which are provided in the subsequent parts of the tag.

  ### number | normal
 *'normal'* is a random number from a normal distribution. The remaining parts of the tag provide the following parameters:
 - *'mean'* - the mean of the distribution
 - *'stddev'* - the standard deviation of the distribution
 - *'min'* - minimum value [optional] (e.g. where values must be positive, set min to zero)
 - *'max'* - maximum values [optional] (e.g where values are a percentage, set max to 100)
 - *'decimals'* - the number of decimal places to include [optional]
 
 *example: <<pH|number|normal|mean:7.052|stddev:1.303|min:0|max:14|decimals:3>>*
 
  ### number | lognormal
 *'lognormal'* is a random number from a log normal distribution. The remaining parts of the tag provide the following parameters:
 - *'mean'* - the mean of the distribution
 - *'sigma'* - the sigma value of the distribution
 - *'min'* - minimum value [optional]  (e.g. where values must be positive, set min to zero)
 - *'max'* - maximum values [optional]  (e.g where values are a percentage, set max to 100)
 - *'decimals'* - the number of decimal places to include [optional] 
  
  *example: <<pH|number|lognormal|mean:32.056|sigma:9.241|min:0|max:14|decimals:3>>*
  
 ### number | uniform
 *'uniform'* is a random number from a uniform distribution. The remaining parts of the tag provide the following parameters:
 - *'min'* - minimum value of the range of allowable numbers
 - *'max'* - maximum value of the range of allowable numbers
 - *'decimals'* - the number of decimal places to include [optional] 
 
 *example: <<porosity|number|uniform|min:0.5|max:0.8|decimals:2>>*
 
 ### number | triangle
 *'triangle'* is a random number from a triangular distribution. The remaining parts of the tag provide the following parameters:
 - *'left'* - minimum value of the distribution
 - *'right'* - maximum value of the distribution
 - *'mode'* - the peak value of the distribution
 - *'decimals'* - the number of decimal places to include [optional] 
 
 *example: <<sulphur|number|triangle|left:12.3|right:23.8|mode:21.5>>*
 
 ## calculation
 *'calculation'* is for a numeric calculation. The remaining parts of the tag contain the expression. The expression is a standard python expression, using standard mathematical functions. You can use numbers, as well as the values from other tags. The remaining parts of the tag provide the following parameters:
 - *'decimals'* - the number of decimal places to include [optional] 
 
 *example: <<rate_per_minute|number|normal|mean:120.225|stddev:18.26|decimals:3>>
 <<rate_per_day|calculation|rate_per_minute * 60 * 24|decimals:3>>*
 
**Note:** tags are processed in the order in which they occur in the template. If a calculation uses the value from another tag, that tag must exist earlier in the template. If you need a random number for a parameter in your calculation, but don't require it for the Phreeq model, place it inside a comment. The tag will still be evaluated, but Phreeq will then ignore it.

---
# 2. Executing a batch of PhreeqC input files
This module will find all files in the designated folder, and attempt to run them in PhreeqC. The results will be written as individual output files in a specified folder. The output files will all have the same names as their corresponding input files, although they can have a different file extension.
## config file
The config file for this package is named 'PhreeqpyBatchRun_config.json. The json file must be placed in the same folder as the python script file, and contain the following settings:
- **phreeq_database** : the full path to the PhreeqC database file
- **input_file_folder** : the full path to the folder containing the input files (note there must be no other files in the folder)
- **output_file_folder** : the full path to the folder in which to write the output files
- **output_file_extension** : the file extension to use for the created output files

---
# 3. Summarising the output files
This module will read the contents of the multiple generated output files, create multiple summary files. Each summary file contains the rows from the output files that meet certain criteria. For example the output values for a specified cell at a specified time.
## config file
The config file for this package is named 'PhreeqpyBatchRun_config.json. The json file must be placed in the same folder as the python script file, and contain the following settings:
- **result_file_directory** : the full path to the folder containing the result files generated by PhreeqC that need to be summarised (note there must be no other files in the folder)
- **summary_file_directory** : the full path to the folder in which to write the summary files
- **summary_file_extension** : the file extension to use for the created summary files
- **summary_files** : an array of summary file requirements (one per file to be generated). Each item in the array must contain the following settings:
    - **name** : the name of the summary file to be generated
    - **rowFilters** : an array of filters used to identify the correct row in each result file to be written to the summary file. Each item in the array must contain the following settings:
        - **column** : the name of the column from the result file to compare
        - **value** : the value to test for in the specified column
        - **match** : either *'exact'* to find only the row that exactly matches the value, or *'interpolate'* to find the two closest rows, and interpolate between them. Note that 'exact' uses a text match, and not a numeric match so '7.000' does not match '7'. Note that only one filter for a summary file can use 'interpolate'.
- **parameters** : an array of parameters to be included in the summary files. These are strings that match the headings in the result files. If all rowFilters used 'exact' matches, the exact value from the row will be written to the summary file. If any of the rowFilters used 'interpolate', the value will be calculated using a linear interpolation between the two closest rows.

# PhreeqpyMonteCarlo
Python package to run a Monte Carlo analysis using PhreeqC

This package of python scripts work with a template PhreeqC file, and will generate multiple PhreeqC input files, assigning random numbers to appropriate variables.
It will then execute each of the input files in turn, writing an output file for each.

# Template file
The template template is a text file that uses tags to indicate where random numbers should be inserted, as well as the parameters for the random number generator.

Each tag starts with "<<" and ends with ">>"
For example:
  <<sulphur|number|normal|mean:23.56|stddev:2.56>>
 
 Every tag consists of several parts, each separated with "|"
 The first part is always a name (e.g. "sulphur")
 The second part is always the data type, which is one of 'number', and 'calculation'.
 
 The remaining parts depend on the type as follows:
 ## number
 'number' is for random numbers. The next part of the tag is a choice alogorithm which is one of 'normal', 'uniform', and 'triangle".
 Each algorithm has a set of available parameters, which are provided in the subsequent parts of the tag.
 ### number | normal
 'normal' is a random number from a normal distribution. The remaining parts of the tag provide the following parameters:
 - 'mean' - the mean of the distribution
 - 'stddev' - the standard deviation of the distribution
 - 'min' - minimum value (e.g. where values must be positive, set min to zero)
 - 'max' - maximum values (e.g where values are a percentage, set max to 100)
 - 'decimals' - the number of decimal places to include
 
 *example: <<pH|number|normal|mean:7.052|stddev:1.303|min:0|max:14|decimals:3>>*
 
 ### number | uniform
 'uniform' is a random number from a uniform distribution. The remaining parts of the tag provide the following parameters:
 - 'min' - minimum value of the range of allowable numbers
 - 'max' - maximum value of the range of allowable numbers
 - 'decimals' - the number of decimal places to include
 
 *example: <<porosity|number|uniform|min:0.5|max:0.8|decimals:2>>*
 
 ### number | triangle
 'triangle' is a random number from a triangular distribution. The remaining parts of the tag provide the following parameters:
 - 'left' - minimum value of the distribution
 - 'right' - maximum value of the distribution
 - 'mode' - the peak value of the distribution
 - 'decimals' - the number of decimal places to include
 
 *example: <<sulphur|number|triangle|left:12.3|right:23.8|mode:21.5>>*
 
 ## calculation
 'calculation' is for a numeric calculation. The remaining parts of the tag contain the expression. The expression is a standard python expression, using standard mathematical functions. You can use numbers, as well as the values from other tags. The remaining parts of the tag provide the following parameters:
 - 'decimals' - the number of decimal places to include
 
 *example: <<rate_per_minute|number|normal|mean:120.225|stddev:18.26|decimals:3>>
 <<rate_per_day|calculation|rate_per_minute * 60 * 24|decimals:3>>*
 
**Note:** tags are processed in the order in which they occur in the template. If a calculation uses the value from another tag, that tag must exist earlier in the template. If you need a random number for a parameter in your calculation, but don't require it for the Phreeq model, place it inside a comment. The tag will still be evaluated, but Phreeq will then ignore it.

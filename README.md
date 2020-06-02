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
 The second part is always the data type (e.g. "number")
 The remaining parts depend on the type as follows:
 ## number
 'number' is followed by an alogorithm which is one of 'normal', 'uniform', and 'triangle
 each algorithm has a set of available parameters, which are provided in the subsequent parts of the tag.
 ### normal
 'normal' is a random number from a normal distribution. The remaining parts of the tag provied the following parameters:
 * 'mean' - the mean of the distribution
 * 'stddev' - the standard deviation of the distribution
 * 'min' - minimum value (e.g. where values must be positive, set min to zero)
 * 'max' - maximum values (e.g where values are a percentage, set max to 100)
 ### uniform
 'uniform' is a random number from a uniform distribution
  

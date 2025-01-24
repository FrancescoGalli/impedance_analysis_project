# Impedance Analysis Library
This repository is for an impedance analysis library written entirely in
python. Before delving into the code aspect, just some words about the physics
behind the project.\
In electrochemical spectrospy, the analysis of the impedance sweeping
the frequency allows to understand the physical/chemical processes of the
trasmission of electrical signals.\
The main object is the analysis of impedance vs frequency data. It is
dedicated to systems that can be schematized using only three types of passive
elements: resistors, capacitors and constant phase elements.

Given in input an equivalent circuit of passive elements, an impedance
function of the frequency (that depends on each value of the elements) is
created. This library finds the optimized values of the aforementioned
passive elements that best-fit the impedance function. These values are a
consequence of the dominant charge transport process happening in a certain
range of frequencies, and are crucial to explain and characterize the whole
physical system.


## Core features
The impedance analysis is simply a fitting process of the impedance function
over the impedance data, and it consists in the minimization of the error
function:
$$Error = \sum_{i}\frac{|Impedance_{i,\ data} - Impedance_{i,\ function}|}
    {|Impedance_{i,\ data}|}$$
where the $Impedance_{i,\ function}$ is an impedance value given by the
impedance function that describes the equivalent circuit, with the current
value of the elements values (the parameters). The sum is over every $i$
point (one for each frequency).\
The minimization is done using the `minimize` function from `scipy.optimize`,
where the numerical method `Nelder-Mead` has proven to be the best one among
the options. A maximum iterations of 1000 has been set, but with circuits
composed of less than six elements (as usually is), this number is rarely hit.

## Installation and usage
To install the application clone the repository with
```
git clone https://github.com/FrancescoGalli/impedance_analysis_project.git
```

To use the library, either to generate or to analyze the data, the user has
to modify the appropriate module to set the input information (in
`Generate_data.py` or in `Impedance_analysis.py`, respectively). This regards
the setting functions (placed at the top of the file) of the circuit string,
the parameters, and the data file name for both files, while the range and
number of points of the frequency only for the generation, and the constat
elements conditions for the analysis.\
Then the user has to run the modified file.

## Requirements
The library is entirely written and tested using `python 3.9.12`, but should
work with any older version of `python 3`. The running code relies on the
following standard libraries:
- `csv`
- `sys`
- `os.path`

And on the following scientific libraries:
- `numpy`
- `scipy.optimize`
- `matplotlib.pyplot`

All the code, except for the plotting and saving functions are tested using
`inspect`, `pytest` and `hypothesis` libraries.

## Structure
The library is divided in 5 modules:

[Generate_data.py](https://github.com/FrancescoGalli/impedance_analysis_project/blob/main/generate_data.py) creates fictitious impedance data with a small simulated random noise
($\sim 1%$). To do so, the number and values of the frequency points, the
circuit diagram and the physical description of its elements (i.e. the
parameters) must be set by the user through a configuration file. With these
two specifications the impedance function is created, and, according to the
frequency points, the impedance complex data are calculated. After the
generation, a random noise on both real and imaginary parts is added to the
generated data, using `numpy.random.rand` and a seed specified in the
configuration file. The module then prints the impedance module and phase vs
frequency of the results, and saves the graphs in a `.pdf` file and the points
in a `.txt` file.

[Impedance_analysis.py](https://github.com/FrancescoGalli/impedance_analysis_project/blob/main/impedance_analysis.py) is dedicated to the analysis (fitting) of the
impedance data. It reads a .txt file containing the impedance vs frequency
points. The accepted formats are either frequency, impedance module and phase,
or frequency and complex impedance. Similarly to the generation module, a
circuit diagram and the physical description of its elements (i.e. the fitting
parameters) must be set by the user. In addition each element can be set as
constant, i.e. its parameter will still contribute to the circuit impedance,
but will NOT be considered during the fitting process as a minimizing
parameter. The reason behind this is that it happens that, with data in a
certain range of frequecy, some elements are less relevant than others for the
impedance trend.\
Based on these three settings, (again, written in a configuration file) an
impedance function will be created, and the fit function will try to minimize
the error function mentioned before, varying the value of the non-constant
parameters.\
After the fitting process is complete, the results are printed in the command
line and both data and fit curves of the impedance modulus and phase graphs 
are plotted and saved as `.pdf`.

[generate_impedance.py](https://github.com/FrancescoGalli/impedance_analysis_project/blob/main/generate_impedance.py) is the core module that generates an impedance function
starting from the circuit diagram and the element parameters (taking into
account if any parameter is set constant).

[plot_and_save.py](https://github.com/FrancescoGalli/impedance_analysis_project/blob/main/plot_and_save.py) contains the functions to extract the impedance modulus
and the phase of the complex impedances and to plot the data or the data
with the fit and the results.

[test_impedance_analysis.py](https://github.com/FrancescoGalli/impedance_analysis_project/blob/main/test_impedance.py) contains all the tests.

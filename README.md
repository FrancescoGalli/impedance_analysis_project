# Impedance Analysis Library
This repository is for an impedance analysis library written entirely in
python. Before delving into the code aspects, just some words about the
physics behind the project.\
In electrochemical spectroscopy, the analysis of the impedance frequency
sweeping allows to understand the physical/chemical processes of the
trasmission of electrical signals.\
Thus, the main object is the analysis of impedance vs frequency data. It is
dedicated to systems that can be schematized using only three types of passive
elements: resistors, capacitors and constant phase elements.

Given in input an equivalent circuit of passive elements, an impedance
function of the frequency and is parametrized by each value of the elements is
created. This library finds the optimized values of the aforementioned
passive elements that best-fit the impedance function. These values are a
consequence of the dominant charge transport process happening in a certain
range of frequencies, and are crucial to explain and characterize the whole
physical system.


## Core features
The impedance analysis is simply a fitting process of the impedance function
over the impedance data, and it consists of the minimization of this chosen
error function:
$$Error = \sum_{i}\frac{|Impedance_{i,\ data} - Impedance_{i,\ function}|}
    {|Impedance_{i,\ data}|}$$
where the $Impedance_{i,\ function}$ is the impedance value given by the
impedance function that describes the equivalent circuit, with the given
elements values (the parameters). The sum is over every $i$ point (one for
each frequency).\
The minimization is done using the `minimize` function from `scipy.optimize`,
where the numerical method `Nelder-Mead` has proven to be the best one among
the options. A maximum iterations of 1000 has been set, but with circuits
composed of less than six elements (as usually it is), this number is rarely
hit.

## Installation and Requirements
To install the application clone the repository with
```
git clone https://github.com/FrancescoGalli/impedance_analysis_project.git
```

The library is entirely written and tested using `python 3.9.12`, but should
work with any older version of `python 3`. The running code relies on the
following standard libraries:
- `configparser`
- `argparse`
- `csv`
- `sys`
- `os.path`
- `pathlib`

and on the following scientific libraries:
- `numpy`
- `scipy.optimize`
- `matplotlib.pyplot`

All the code, except for the plotting and saving functions, are tested using
`pytest`, `inspect` and `hypothesis` libraries.


## Usage
To use the library, either to generate or to analyze the data, the user can
set all the input information (which are specified throughout `Tutorial_0`)
in a configuration file, i.e. a file with the `.ini` extention.
This regards the circuit diagram, the parameters, and the data file name for
both files, while the range and number of points of the frequency and the
seed for the random noise only for the generation, while the constant
conditions for the analysis.\
To run the desired file with the chosen configuration file, the user can use
the command
```
python3 <module_name>.py --config=<configuration_file_name>
```
where `<module_name>` is either the generation module `generate_data` or
`impedance_analysis`, while `<confi_file_name>` is the name, without the
`.ini` extention, of the configuration file. This is done in order to keep
track of the input settings given to the program. This command is optional,
and the default value is `config_generation` for the generation module and
`config_analysis` for the analysis module.

## Structure
The library is divided in 5 modules:

[Generate_data.py](https://github.com/FrancescoGalli/impedance_analysis_project/blob/main/generate_data.py) creates fictitious impedance data with a small simulated random noise of an amplitude of ($\sim 1%$) of the ideal signal.
To do so, the number and values of the frequency points, the circuit diagram
and the physical description of its elements (i.e. the parameters) must be
set by the user through the configuration file. With the last two
specifications the impedance function is created, and, according to the
frequency points, the impedance complex data are calculated. After the
generation, the random noise on both real and imaginary parts is added to the
generated data, using `numpy.random.rand` and a seed specified in the same
configuration file. The module then prints the impedance amplitude and
phase vs frequency of the results, and saves the graphs in a `.pdf` file and
the points in a `.txt` file.

[Impedance_analysis.py](https://github.com/FrancescoGalli/impedance_analysis_project/blob/main/impedance_analysis.py) is dedicated to
the analysis (fitting) of the impedance data. It reads a .txt file containing
the impedance vs frequency points. The accepted formats are either frequency, impedance amplitude and phase, or frequency and complex impedance.
Similarly to the generation module, a circuit diagram and the physical
description of its elements (i.e. the fitting parameters) must be set by the
user in a configuration file. In addition, each element can be set as
constant, i.e. its parameter will still contribute to the circuit impedance
function, but will NOT be considered during the fitting process as a
minimizing parameter. The reason behind this is that it happens that, with
data in a certain range of frequecy, some elements are less relevant than
others for the impedance trend, or they could be already known from another
analysis.\
Based on these three settings, an impedance function will be created, and the
fit function will try to minimize the error function mentioned before,
varying the value of the non-constant parameters.\
After the fitting process is complete, the results are printed in the command
line and both data and fit curves of the impedance amplitude and phase graphs 
are plotted and saved as `.pdf`.

[generate_impedance.py](https://github.com/FrancescoGalli/impedance_analysis_project/blob/main/generate_impedance.py) is the core module that first generates an instance of the `Circuit` class from the input
information. Then analyzed this circuit and create an impedance function and
a list of non-constant parameters (taking into account if any parameter is set constant).

[plot_and_save.py](https://github.com/FrancescoGalli/impedance_analysis_project/blob/main/plot_and_save.py) contains the functions to extract the impedance amplitude and the phase of the complex impedances and to plot the data or the
data with the fit and the results.

[read.py](https://github.com/FrancescoGalli/impedance_analysis_project/blob/main/read.py) contains all the functions to read the input information.

Then, there are two folders:\
`Tutorials` containes three Jupiter (`.ipynb`) files that
should work as a guide through the specifics of the input information, the
generation module and the analysis module, respectively.\
`tests` instead is the collection of tests of the project.

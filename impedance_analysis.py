"""This module takes impedance vs frequency data from a .txt file, either in
complex impedance form of modulus and phase form, and plots the modulus and
phase of the data.
Then starting from a circuit string, the initial parameters of the components
of each element, set by the user, a fit is performed. Is is possible to not
take into account in the fit any initial parameter through the element
constant conditions.
The fit is done minimizing a certain error function using the Nelder-Mead
algorithm, and then the fit results are written both in the command line and
in the final plot of the fit, containing the modulus and phase of both data
and fit.
"""

import os.path
import sys
from csv import reader

import numpy as np

def generate_circuit_fit():
    """Return the circuit string for the fit."""
    circuit_string_fit = '(R1C2[R3Q4])'
    return circuit_string_fit

def generate_circuit_parameters():
    """Return the initial parameters for the fit in standard units."""
    parameter_1 = 7000
    parameter_2 = 8e-6
    parameter_3 = 10000
    parameter_4 = ([0.07e-6, 0.7])
    circuit_parameters = ([parameter_1, parameter_2, parameter_3,
                           parameter_4])
    return circuit_parameters

def generate_constant_elements_array_fit():
    """Return the constant elements condition for the fit."""
    constant_elements_fit = ([0, 0, 1, 0])
    return constant_elements_fit

def get_file_name():
    """Sets the data file name from which the data are read."""
    file_name = 'data_impedance'
    file_name += '.txt'
    return file_name

##############################################################################

def get_number_of_columns(file_name):
    """Return the number of columns inside the data file, ignoring the
    comment lines.

    Parameters
    ----------
    file_name : string
        Name of the file where the data are saved

    Returns
    -------
    number_of_columns : int
        Number of data array (columns) inside the data file
    """
    number_of_columns = 0
    comment_character = '%'
    with open(file_name) as file:
        for row in reader(file, delimiter=';', skipinitialspace=True):
            if row[0][0]!=comment_character:
                number_of_columns = len(row)
    return number_of_columns

def read_data(file_name):
    """Return the (real) frequency vector and the complex impedance vector.
    The impedance data can be a single complex column or two real
    columns: modulus first and phase (in deg) second. Based on the number of
    columns in the data file, one of the two structure will be assumed.

    Parameters
    ----------
    file_name : string
        Name of the file where the data are saved

    Returns
    -------
    frequency_vector : array
        Data frequencies array from the data file
    impedance_data_vector : array
        Complex array either directly imported from the data file, or
        constructed combining the modulus and the phase from the data file,
        depending on the data file format
    """
    try:
        if not os.path.exists(file_name):
            raise FileNotFoundError('no file \'' + str(file_name)
                                    + '\' found in this directory')
        if not os.path.isfile(file_name):
            raise FileNotFoundError(str(file_name) + 'is not a file')
    except FileNotFoundError as error:
        print('FatalError: ' + repr(error))
        sys.exit(0)
    number_of_columns = get_number_of_columns(file_name)
    frequency_vector = []
    impedance_data_vector = []
    if number_of_columns==2:
        frequency_complex_vector, impedance_data_vector = np.loadtxt(
            file_name, dtype=np.complex128, comments='%', delimiter=';',
            unpack=True)
        frequency_vector = np.real(frequency_complex_vector)
    if number_of_columns==3:
        frequency_vector, modulus_data_vector, phase_data_vector = np.loadtxt(
            file_name, comments='%', delimiter=';', unpack=True)
        impedance_data_vector = modulus_data_vector * np.e**(
            1j * phase_data_vector * np.pi/180)
    return frequency_vector, impedance_data_vector

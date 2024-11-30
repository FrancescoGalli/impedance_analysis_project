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

def list_string_elements(circuit_string):
    """Return the list of input elements (type 'C', 'Q' or 'R' ) of a circuit
    string.

    Parameters
    ----------
    circuit_string : string
        String representing the disposition of elements of a circuit

    Returns
    -------
    string_elements : string
        String listing the elements in order of apparition in a circuit string
    """
    string_elements = []
    for i, char in enumerate(circuit_string):
        if char in {'C', 'Q', 'R'}:
            string_elements.append(circuit_string[i:i+2])
    #string_elements = (['R1', 'C2', 'Q4'])
    return string_elements

def error_function(parameters, impedance_data_vector, impedance_function,
                   frequency):
    """Error function to be minimized to perform the fit. The first argument
    must be the parameters to be optimized

    Parameters
    ----------
    parameters : list
        List of current parameters value
    impedance_data_vector : array
        Complex array containing the impedance data from the data file
    impedance_function : function
        Impedance function of the circuit, depending on the frequencies and on
        the parameters
    frequency_vector : array
        Data frequencies array from the data file

    Returns
    -------
    error : float
        Value of the error function, to be minimized for the fitting process

    """
    impedance_calaculated = impedance_function(parameters, frequency)
    error = np.sum(np.abs(impedance_data_vector-impedance_calaculated)/np.abs(
        impedance_data_vector))
    #print('parameters = ' + str(parameters) + ' error = ' + str(error))
    return error

def get_initial_parameters_string_vector(circuit_string_fit,
                                         circuit_parameters,
                                         constant_elements_fit,
                                         initial_error):
    """Return a string vector in which each element is the circuit element
    name followed by its parameter value. Then the error estimated with the
    initial values of the parameters is added as last element.
    Used to print the parameters value and error.

    Parameters
    ----------
    circuit_string_fit : string
        String representing the disposition of elements of the fitting circuit
    circuit_parameters : list
        List of parameters for the circuit given by input
    constant_elements_fit : list
        List of constant element conditions for the fit given by input
    initial_error : float
        Output given by the error function used in the fit with the initial
        parameters

    Returns
    -------
    parameters_string_vector : list
        List of strings containing the name and inital value of the
        parameters. If the parameters is set constant, a '(constant)' follows
        the parameter value. Then the error estimated with the initial values
        of the parameters is added as last element.
    """
    string_elements = list_string_elements(circuit_string_fit)
    parameters_string_vector = [' ' for _ in string_elements]
    for i, parameter in enumerate(circuit_parameters):
        if string_elements[i][0]=='Q':
            parameters_string_vector[i] = ('  ' + string_elements[i] + ': '
            + str(parameter[0]) + ', ' + str(parameter[1]))
        else:
            parameters_string_vector[i] = ('  ' + string_elements[i] + ': '
            + str(parameter))
        if constant_elements_fit[i]:
            parameters_string_vector[i] += ' (constant)'
    parameters_string_vector.append('Error: ' + f'{initial_error:.4f}')
    return parameters_string_vector

def get_string(string_vector):
    """From a string vector creates a single string, concatenating each
    element.
    """
    string_ = ''
    new_line = '\n'
    string_ = new_line.join(string_vector)
    return string_
    
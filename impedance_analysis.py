"""This module takes impedance vs frequency data from a .txt file, either in
complex impedance form of modulus and phase form, and plots the modulus and
phase of the data.
Then, starting from a circuit string and the initial parameters of the
components of each element set by the user, a Circuit object is created.
Using the impedance function stored inside this object, a fit of the data
can be done. The parameters of the fit are the ones inside the Circuit object
(i.e. the ones defined by the user in this module). It is possible to not
take into account in the fit any initial parameter through the element
constant conditions, also defined by the user.
The fit is done minimizing a certain error function using the Nelder-Mead
algorithm, and then the fit results are written both in the command line and
in the final plot of the fit, containing the modulus and phase of both data
and fit.
"""

import os.path
import sys
import configparser
from csv import reader

import numpy as np
from scipy.optimize import minimize

from generate_impedance import generate_circuit, get_string
from plot_and_save import plot_data, plot_fit


#######################
#Input functions

def read_input_circuit_diagram_fit(config):
    """Read the circuit diagram specified in the configuration file for the
    fit.

    Parameters
    ----------
    config : configparser.ConfigParser
        Parser object with the information inside the configuration file

    Returns
    -------
    circuit_diagram_fit : str
        Circuit diagram given in the configuration file
    """
    circuit_diagram_fit = config.get('Circuit','diagram')
    return circuit_diagram_fit

def read_input_parameters_fit(config):
    """Read the parameters specified in the configuration file for the
    fit.

    Parameters
    ----------
    config : configparser.ConfigParser
        Parser object with the information inside the configuration file

    Returns
    -------
    parameters_fit : dict
        Parameters given in the configuration file
    """
    parameters_fit = {}
    for parameter_name in config['Parameters']:
        string_parameter_name = (str(parameter_name)).upper()
        if string_parameter_name.startswith('Q'):
            string_list = config.get('Parameters',
                                     string_parameter_name).split()
            parameters_fit[string_parameter_name] = [float(i) for i in
                                                        string_list]
        else:
            parameters_fit[string_parameter_name] = config.getfloat(
                'Parameters', string_parameter_name)
    return parameters_fit

def read_input_constant_parameter_configurations_fit(config):
    """Read the constant conditions specified in the configuration file for
    the fit.

    Parameters
    ----------
    config : configparser.ConfigParser
        Parser object with the information inside the configuration file

    Returns
    -------
    constant_elements_fit : dict
        Constant conditions for the fit given in the configuration file
    """
    constant_elements_fit = {}
    for parameter_name in config['Constant_parameter_conditions']:
        string_parameter_name = (str(parameter_name)).upper()
        constant_elements_fit[string_parameter_name] = config.getint(
            'Constant_parameter_conditions', string_parameter_name)
    return constant_elements_fit

def read_input_file_name(config):
    """Read the file name, from where the data will be read, specified in the
    configuration file for the fit.

    Parameters
    ----------
    config : configparser.ConfigParser
        Parser object with the information inside the configuration file

    Returns
    -------
    file_name : str
        Name of the input file
    """
    file_name = config.get('File', 'file_name')
    file_name += '.txt'
    return file_name



############################
#Read functions

def get_number_of_columns(file_name):
    """Return the number of columns inside the data file, ignoring the
    comment lines.

    Parameters
    ----------
    file_name : str
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
    file_name : str
        Name of the file where the data are saved

    Returns
    -------
    frequency_array : array
        Data frequencies array from the data file
    impedance_data_array : array
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
    if number_of_columns==2:
        frequency_complex_array, impedance_data_array = np.loadtxt(
            file_name, dtype=np.complex128, comments='%', delimiter=';',
            unpack=True)
        frequency_array = np.real(frequency_complex_array)
    if number_of_columns==3:
        frequency_array, modulus_data_vector, phase_data_vector = np.loadtxt(
            file_name, comments='%', delimiter=';', unpack=True)
        impedance_data_array = modulus_data_vector * np.e**(
            1j * phase_data_vector * np.pi/180)
    return frequency_array, impedance_data_array

###############################
#Fit functions

def error_function(parameters, impedance_data_vector, impedance_function,
                   frequency_vector):
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
    impedance_calaculated = impedance_function(parameters, frequency_vector)
    error = np.sum(np.abs(impedance_data_vector-impedance_calaculated)/np.abs(
        impedance_data_vector))
    #print('parameters = ' + str(parameters) + ' error = ' + str(error))
    return error

def bounds_definitions(elements):
    """Return the parameters bounds for the fit algorithm, based on the type
    of elements.

    Parameters
    ----------
    elements : list
        List of elements (strings) that compose the circuit and that will
        figure in the fit, in order of analysis

    Returns
    -------
    bounds_list : list
        List of tuples (a pair of numbers/None) to make sure the optimized
        parameters will not have unreasonable values
    """
    bounds_list = []
    r_bound = (10, None)
    c_bound = (1e-9, None)
    q_bound = (1e-9, None)
    n_bound = (0, 1)
    for element in elements:
        if element.startswith('R'):
            bounds_list.append(r_bound)
        elif element.startswith('C'):
            bounds_list.append(c_bound)
        elif element.startswith('Q'):
            bounds_list.append(q_bound)
            bounds_list.append(n_bound)
        else:
            raise Exception('FatalError: Invalid initial parameter name for '
                            + 'the fit bounds')
    return bounds_list

def fit(frequency_array, impedance_data_vector, analyzed_circuit):
    """Perform the fit minimizing a specified error function, with certain
    bonds. The method used is the Nelder-Mead, with a maximum iteration of
    1000.

    Parameters
    ----------
    frequency_array : array
        Data frequencies array from the data file
    impedance_data_vector : array
        Complex array containing the impedance data from the data file
    analyzed_circuit : AnalyzedCircuit
        Instance of the class AnalyzedCircuit, containing the analysis of
        the circuit

    Returns
    -------
    optimized_parameters : list
        List of optimized parameter values, i.e. the parameters value that
        minimized the error function
    succes flag : str
        String containing the convergence outcome of the algorithm
    """
    bounds_list = bounds_definitions(analyzed_circuit.list_elements())
    result = minimize(error_function, analyzed_circuit.list_parameters(),
        args=(impedance_data_vector, analyzed_circuit.impedance,
              frequency_array),
        method='Nelder-Mead', options= {'maxiter': 1000, 'disp': False},
        bounds=bounds_list)
    optimized_parameters = result.x
    i_q = 0
    for element in analyzed_circuit.parameters_map.keys():
        index = list(analyzed_circuit.parameters_map.keys()).index(element)
        if element.startswith('Q'):
            analyzed_circuit.parameters_map[element] = ([optimized_parameters[
                index], optimized_parameters[index+1+i_q]])
            i_q += 1
        else:
            analyzed_circuit.parameters_map[element] = optimized_parameters[
                index+i_q]
    success_flag = str(result.success)
    return optimized_parameters, success_flag


def get_constant_parameter_info(element, parameter):
    """Return a string containing the element string and its parameter,
    rounded to have a reasonable amount of significative digits, followed by
    a '(constant)'

    Parameters
    ----------
    element : str
        Element string
    parameter
        Parameter of the element (constant)

    Returns
    -------
    element_info : str
        String containing the aforementioned information
    """
    if element.startswith('Q'):
        element_info = (element + ': ' + str(parameter[0][0]) + ', '
                        + str(parameter[0][1]))
    else:
        element_info = element + ': ' + str(parameter[0])
    element_info += ' (constant)'
    return element_info

def get_optimized_parameters_info(element, optimized_parameter):
    """Return a string containing the element string and its (optimized)
    parameter, rounded to have a reasonable amount of significative digits.

    Parameters
    ----------
    element : str
        Element string
    optimized_parameter
        Parameter of the element

    Returns
    -------
    element_info : str
        String containing the aforementioned information
    """
    low_precision = 3
    high_precision = 11
    if element.startswith('R'):
        element_info = (element + ': ' + str(round(optimized_parameter,
                                                   low_precision)))
    elif element.startswith('C'):
        element_info = (element + ': ' + str(round(optimized_parameter,
                                                   high_precision)))
    elif element.startswith('Q'):
        element_info = (
            element + ': ' + str(round(optimized_parameter[0], high_precision))
            + ', ' + str(round(optimized_parameter[1], low_precision)))
    else:
        raise Exception('FatalError: Invalid optmized parameter name to '
                        + 'exctract info')
    return element_info

def get_results_info(analyzed_circuit_fit, final_error, initial_circuit_fit):
    """Return a string containing all the circuit elements name followed
    by their own optimized parameter value. Then the final error estimated
    with these values is added at the last line.
    Used to print the optimized parameters value and the relative error.

    Parameters
    ----------
    analyzed_circuit_fit : AnalysisCircuit
        Instance of the class AnalysisCircuit, created from the analysis of
        the input circuit with the optimized parameters given by the fit
    final_error : int or float
        Final error of the optimized parameters
    initial_circuit_fit : Circuit
        Initial circuit, object of the analysis and fit

    Returns
    -------
    result_string : str
        Strings containing the name and optimized value of all the
        non-constant parameters. If the parameters is set constant, a
        '(constant)' follows the parameter value. Then the error estimated
        with the optimized and constant values of the parameters is added as
        last element.
    """
    parameters_string_vector = []
    for element, parameter in initial_circuit_fit.parameters_map.items():
        constant_considtion = parameter[1]
        if constant_considtion:
            element_info = get_constant_parameter_info(element, parameter)
        else:
            optimized_parameter = analyzed_circuit_fit.parameters_map[element]
            element_info = get_optimized_parameters_info(
                element, optimized_parameter)
        parameters_string_vector.append(element_info)
    parameters_string_vector.append('Error: ' + f'{final_error:.4f}')
    result_string = get_string(parameters_string_vector)
    return result_string



if __name__=="__main__":
    config = configparser.ConfigParser()
    config.read('config_analysis.ini')

    FILE_NAME = read_input_file_name(config)
    print('\nReading data . . . ')
    frequency, impedance_data = read_data(FILE_NAME)
    plot_data(frequency, impedance_data)

    CIRCUIT_DIAGRAM_FIT = read_input_circuit_diagram_fit(config)
    parameters_fit = read_input_parameters_fit(config)
    constant_elements_fit = read_input_constant_parameter_configurations_fit(
        config)

    initial_circuit_fit = generate_circuit(
        CIRCUIT_DIAGRAM_FIT, parameters_fit, constant_elements_fit)
    analyzed_circuit_fit = initial_circuit_fit.generate_analyzed_circuit()
    impedance_function = analyzed_circuit_fit.impedance
    initials_parameters = analyzed_circuit_fit.list_parameters()
    initial_circuit_fit.error = error_function(
        initials_parameters, impedance_data, impedance_function, frequency)

    INITIAL_PARAMETERS = initial_circuit_fit.get_parameters_info()
    print('\nInitial fit parameters:\n' + INITIAL_PARAMETERS)

    print('\nFitting . . . ')
    optimized_parameters, success_flag = fit(frequency, impedance_data,
                                             analyzed_circuit_fit)
    print('Success flag: ' + success_flag)
    final_error = error_function(optimized_parameters, impedance_data,
                                 impedance_function, frequency)

    RESULT_STRING = get_results_info(analyzed_circuit_fit, final_error,
                                      initial_circuit_fit)
    print('\nOptimized fit parameters:\n' + RESULT_STRING)

    print('\nPlotting results . . . ')
    final_impedance_calculated = impedance_function(optimized_parameters,
                                                    frequency)
    plot_fit(frequency, impedance_data, final_impedance_calculated,
             RESULT_STRING)
    print('Done.\n')

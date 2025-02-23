"""This module takes impedance vs frequency data from a .txt file, either in
complex impedance form of amplitude and phase form, and plots the amplitude
and phase of the data.
Then, starting from a circuit diagram and the initial parameters of the
components of each element set by the user in the configuration file, a
Circuit object is created.
Using the impedance function stored inside this object, a fit of the data
can be done. The parameters of the fit are the ones inside the Circuit object.
It is possible to not take into account in the fit any initial parameter
through the element constant conditions, also defined in the configuration
file.
The fit is done minimizing a certain error function using the Nelder-Mead
algorithm, and then the fit results are written both in the command line and
in the final plot of the fit, containing the amplitude and phase of both data
and fit.
"""


import numpy as np
np.seterr(all='raise')
from scipy.optimize import minimize
import sys

from read import read_configuration
from read import read_input_circuit_diagram, read_input_parameters
from read import read_input_constant_parameter_configurations_fit
from read import read_input_file_name, read_data
from generate_impedance import generate_circuit, get_string
from plot_and_save import plot_data, plot_fit



def error_function(parameters, impedance_data, impedance_function,
                   frequency):
    """Error function to be minimized to perform the fit. The first argument
    must be the parameters to be optimized. Raise a FloatingPointError if
    there is a zero division in the calculation of the impedance.

    Parameters
    ----------
    parameters : list
        List of current parameters value
    impedance_data : array
        Complex array containing the impedance data from the data file
    impedance_function : function
        Impedance function of the circuit, depending on the parameters and on
        the frequencies
    frequency : array
        Frequencies from the data file

    Returns
    -------
    error : float
        Value of the error function given the input values, to be minimized
        for the fitting process

    """
    try:
        impedance_calculated = impedance_function(parameters, frequency)
    except FloatingPointError as error:
        sys.exit('FatalError: ' + repr(error))
    error = np.sum(np.abs(impedance_data-impedance_calculated)/np.abs(
        impedance_data))
    #print('parameters = ' + str(parameters) + ' error = ' + str(error))
    return error


def bounds_definitions(elements):
    """Return the parameters bounds for the fit algorithm, based on the
    element types. Raise an Exception if any of the element names is invalid.

    Parameters
    ----------
    elements : list
        List of element names (strings) that compose the circuit and that will
        figure in the fit, in order of analysis

    Returns
    -------
    bounds_list : list
        List of tuples (a pair of numbers/None) to make sure the optimized
        parameters will not have unreasonable values
    """
    bounds_list = []
    resistance_bound = (10, None)
    capacitance_bound = (1e-9, None)
    n_bound = (0, 1)
    for element in elements:
        if element.startswith('R'):
            bounds_list.append(resistance_bound)
        elif element.startswith('C'):
            bounds_list.append(capacitance_bound)
        elif element.startswith('Q'):
            bounds_list.append(capacitance_bound)
            bounds_list.append(n_bound)
        else:
            raise Exception('FatalError: Invalid initial parameter name for '
                            + 'the fit bounds')
    return bounds_list

def fit(frequency, impedance_data, analyzed_circuit):
    """Perform the fit minimizing a specified error function, with certain
    parameters bounds. The method used for the minimization is the
    Nelder-Mead, with a maximum iteration of 1000.

    Parameters
    ----------
    frequency : array
        Frequencies from the data file
    impedance_data : array
        Complex array containing the impedance data from the data file
    analyzed_circuit : AnalyzedCircuit
        Instance of the class AnalyzedCircuit, containing the analysis of
        the circuit

    Returns
    -------
    optimized_parameters : list
        List of optimized parameter values, i.e. the parameters values that
        minimize the error function
    succes flag : str
        String containing the convergence outcome of the algorithm
    """
    element_list = list(analyzed_circuit.parameters_map.keys())
    bounds_list = bounds_definitions(element_list)
    result = minimize(error_function, analyzed_circuit.list_parameters(),
        args=(impedance_data, analyzed_circuit.impedance, frequency),
        method='Nelder-Mead', options= {'maxiter': 1000, 'disp': False},
        bounds=bounds_list)
    optimized_parameters = result.x
    success_flag = str(result.success)

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

    return optimized_parameters, success_flag


def get_constant_parameter_info(element, parameter):
    """Return a string containing the constant element name and its (initial)
    parameter followed by a '(constant)'.

    Parameters
    ----------
    element : str
        Element name
    parameter : float or list
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

def get_optimized_parameter_info(element, optimized_parameter):
    """Return a string containing the element name and its (optimized)
    parameter, rounded to a reasonable amount of significative digits. Raise
    an Exception if the element name is not valid.

    Parameters
    ----------
    element : str
        Element name
    optimized_parameter : float or list
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

def get_results_info(analyzed_circuit, final_error, initial_circuit):
    """Return a string containing all the circuit element names followed
    by their own optimized parameter value if non-constant or initial
    prameter value if constant. Then the final error estimated
    with these values is added at the last line.

    Parameters
    ----------
    analyzed_circuit : AnalysisCircuit
        Instance of the class AnalysisCircuit, created from the analysis of
        the input circuit with the optimized parameters given by the fit
    final_error : float
        Final error of the optimized parameters
    initial_circuit : Circuit
        Initial circuit, target of the analysis and fit

    Returns
    -------
    result_string : str
        Strings containing the names and optimized values of all the
        non-constant parameters. If the parameters is set constant, a
        '(constant)' follows the parameter value. Then the error estimated
        with the optimized and constant values of the parameters is added at
        the end of the string.
    """
    parameters_string_vector = []
    for element, parameter in initial_circuit.parameters_map.items():
        constant_considtion = parameter[1]
        if constant_considtion:
            element_info = get_constant_parameter_info(element, parameter)
        else:
            optimized_parameter = analyzed_circuit.parameters_map[element]
            element_info = get_optimized_parameter_info(element,
                                                        optimized_parameter)
        parameters_string_vector.append(element_info)
    parameters_string_vector.append('Error: ' + f'{final_error:.4f}')
    result_string = get_string(parameters_string_vector)
    return result_string



if __name__=="__main__":

    DEFAULT_NAME = 'config_analysis'
    config = read_configuration(DEFAULT_NAME)

    FILE_NAME = read_input_file_name(config)
    print('\nReading data . . . ')
    frequency, impedance_data = read_data(FILE_NAME)
    plot_data(frequency, impedance_data)

    CIRCUIT_DIAGRAM = read_input_circuit_diagram(config)
    input_parameters = read_input_parameters(config)
    constant_conditions = read_input_constant_parameter_configurations_fit(
        config)
    initial_circuit = generate_circuit(CIRCUIT_DIAGRAM, input_parameters,
                                       constant_conditions)

    print('\nAnalyzing circuit . . . ')
    analyzed_circuit = initial_circuit.generate_analyzed_circuit()
    impedance_function = analyzed_circuit.impedance
    initial_parameters = analyzed_circuit.list_parameters()
    initial_circuit.error = error_function(initial_parameters, impedance_data,
                                           impedance_function, frequency)
    INITIAL_PARAMETERS = initial_circuit.get_parameters_info()
    print('\nInitial fit parameters:\n' + INITIAL_PARAMETERS)

    print('\nFitting . . . ')
    optimized_parameters, success_flag = fit(frequency, impedance_data,
                                             analyzed_circuit)
    print('Success flag: ' + success_flag)
    final_error = error_function(optimized_parameters, impedance_data,
                                 impedance_function, frequency)
    RESULT_STRING = get_results_info(analyzed_circuit, final_error,
                                      initial_circuit)
    print('\nOptimized fit parameters:\n' + RESULT_STRING)

    print('\nPlotting results . . . ')
    final_impedance_calculated = impedance_function(optimized_parameters,
                                                    frequency)
    plot_fit(frequency, impedance_data, final_impedance_calculated,
             RESULT_STRING)
    print('Done.\n')

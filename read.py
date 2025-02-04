"""This module contains all the function to read the input information given
by the user. They are needed for the data generation module and fit module.
All the input information are set with configuration files, and with a parser
these function read them. The functions to read .txt data file are present as
well
"""

import numpy as np
import os.path
import sys
from csv import reader


def read_input_circuit_diagram(config):
    """Read the circuit diagram specified in the configuration file for the
    generation.

    Parameters
    ----------
    config : configparser.ConfigParser
        Parser object with the information inside the configuration file

    Returns
    -------
    circuit_diagram : str
        Circuit diagram given in the configuration file
    """
    circuit_diagram = config.get('Circuit','diagram')
    return circuit_diagram

def read_input_parameters(config):
    """Read the parameters specified in the configuration file for the
    generation.

    Parameters
    ----------
    config : configparser.ConfigParser
        Parser object with the information inside the configuration file

    Returns
    -------
    parameters : dict
        Parameters given in the configuration file
    """
    parameters = {}
    for parameter_name in config['Parameters']:
        string_parameter_name = (str(parameter_name)).upper()
        if string_parameter_name.startswith('Q'):
            string_list = config.get('Parameters',
                                     string_parameter_name).split()
            parameters[string_parameter_name] = [float(i) for i in
                                                        string_list]
        else:
            parameters[string_parameter_name] = config.getfloat(
                'Parameters', string_parameter_name)
    return parameters

def read_input_frequencies(config):
    """Read the frequencies specifications in the configuration file for the
    generation.

    Parameters
    ----------
    config : configparser.ConfigParser
        Parser object with the information inside the configuration file

    Returns
    -------
    frequency : array
        Array of frequencies
    """
    lower_limit_oom = config.getfloat('Frequencies',
                                      'lower_order_of_magnitude')
    upper_limit_oom = config.getfloat('Frequencies',
                                      'upper_order_of_magnitude')
    number_of_points = config.getint('Frequencies', 'number_of_points')
    log_frequency = np.linspace(lower_limit_oom, upper_limit_oom,
                                number_of_points)
    frequency = 10.**log_frequency
    return frequency

def read_input_seed(config):
    """Read the seed for the pseudo-rsndom noise generation name, specified in
    the configuration file for the generation.

    Parameters
    ----------
    config : configparser.ConfigParser
        Parser object with the information inside the configuration file

    Returns
    -------
    seed_number : int
        Seed for the psudo-random noise generation
    """
    seed_number = config.getint('Noise', 'seed')
    return seed_number

def read_output_file_name(config):
    """Read the file name, where the data will be written, specified in the
    configuration file for the generation.

    Parameters
    ----------
    config : configparser.ConfigParser
        Parser object with the information inside the configuration file

    Returns
    -------
    file_name : str
        Name of the output file
    """
    file_name = config.get('File', 'file_name')
    file_name += '.txt'
    return file_name

def read_output_file_format(config):
    """Read the file format, where the data will be written, specified in the
    configuration file for the generation.

    Parameters
    ----------
    config : configparser.ConfigParser
        Parser object with the information inside the configuration file

    Returns
    -------
    number_of_columns : int
        Format of the saved data, that can be only 3 columnns or 2 columns
    """
    number_of_columns = config.getint('File', 'format')
    return number_of_columns



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
    columns: amplitude first and phase (in deg) second. Based on the number of
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
        constructed combining the amplitude and the phase from the data file,
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
        frequency_array, amplitude_data_vector, phase_data_vector = np.loadtxt(
            file_name, comments='%', delimiter=';', unpack=True)
        impedance_data_array = amplitude_data_vector * np.e**(
            1j * phase_data_vector * np.pi/180)
    return frequency_array, impedance_data_array

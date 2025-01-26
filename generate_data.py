"""This module simulates impedance data starting from the circuit string, the
initial parameters of each element and the element constant conditions.
These three pieces of information are stored inside of an Circuit class object
named initial_circuit. The circuit string containes the elements type and
their disposition, while their values in the parameters list. The element
constant conditions are all set to 1, since they are not relevant to the
generation of the data.
Starting from this signal, a small randomized noise is added to it.
The final data are plotted and saved .pdf. The data are also saved in a .txt
file, with the complex impedance format.
"""

import numpy as np
import configparser

from generate_impedance import generate_circuit
from plot_and_save import plot_data, save_data


#######################
#Input functions

def read_input_circuit_diagram_data(config):
    """Read the circuit diagram specified in the configuration file for the
    generation.

    Parameters
    ----------
    config : configparser.ConfigParser
        Parser object with the information inside the configuration file

    Returns
    -------
    circuit_diagram_data : str
        Circuit diagram given in the configuration file
    """
    circuit_diagram_data = config.get('Circuit','diagram')
    return circuit_diagram_data

def read_input_parameters_data(config):
    """Read the parameters specified in the configuration file for the
    generation.

    Parameters
    ----------
    config : configparser.ConfigParser
        Parser object with the information inside the configuration file

    Returns
    -------
    parameters_data : dict
        Parameters given in the configuration file
    """
    parameters_data = {}
    for parameter_name in config['Parameters']:
        string_parameter_name = (str(parameter_name)).upper()
        if string_parameter_name.startswith('Q'):
            string_list = config.get('Parameters',
                                     string_parameter_name).split()
            parameters_data[string_parameter_name] = [float(i) for i in
                                                        string_list]
        else:
            parameters_data[string_parameter_name] = config.getfloat(
                'Parameters', string_parameter_name)
    return parameters_data

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

############################
#Input data manipulation

def generate_constant_elements_data(parameters_data):
    """Generate an array for constant elements conditions for the data
    generation.

    Parameters
    ----------
    parameters_data : dict
        Dictionary of the parameters of the circuit's elements given by input

    Returns
    -------
    constant_elements_data : dict
        Dictionary of constant elements conditions, all set to 1
    """
    elements = list(parameters_data.keys())
    constant_elements_data = dict.fromkeys(elements, 1)
    return constant_elements_data

############################
#Noise simulation

def generate_random_error_component(seed_number, signal_length):
    """Generate a random array of numbers between 0 and 1 of length
    signal_length.

    Parameters
    ----------
    seed_number : int
        Seed for the psudo-random noise generation
    signal_length : int
        Length of the generated signal

    Returns
    -------
    random_error_component : array
        Array for constant elements conditions, with the same length of the
        parameters list. During the data generation both 0 and 1 have the same
        effect, thus this array is set to contain only 1 (faster process).
    """
    np.random.seed(seed_number)
    random_error_component = np.random.uniform(-0.5, 0.5, signal_length)
    return random_error_component

def simulate_noise(seed_number, impedance_signal):
    """For each of the real and imaginary part of the signal, add a uniform
    probability distribution noise between 0 and 1%/np.sqrt(2) of the
    impedance to the signal.

    Parameters
    ----------
    seed_number : int
        Seed for the psudo-random noise generation
    impedance_signal : array
        Impedances given by the generated impedance function of the circuit

    Returns
    -------
    impedance_data : array
        Simulation of impedances with a random error component
    """
    signal_length = len(impedance_signal)
    noise_factor = 0.01/np.sqrt(2)
    real_part_error = generate_random_error_component(seed_number,
                                                      signal_length)
    imaginary_part_error = generate_random_error_component(seed_number+1,
                                                           signal_length)
    noise = noise_factor*impedance_signal * (real_part_error
                                          + 1j*imaginary_part_error)
    impedance_data = impedance_signal + noise
    return impedance_data



if __name__=="__main__":
    config = configparser.ConfigParser()
    config.read('config_generation.ini')

    CIRCUIT_DIAGRAM_DATA = read_input_circuit_diagram_data(config)
    parameters_data = read_input_parameters_data(config)
    constant_elements_data = generate_constant_elements_data(parameters_data)
    initial_circuit_data = generate_circuit(CIRCUIT_DIAGRAM_DATA,
                                            parameters_data,
                                            constant_elements_data)
    analyzed_circuit_data = initial_circuit_data.generate_analyzed_circuit()
    impedance_function = analyzed_circuit_data.impedance

    frequency = read_input_frequencies(config)
    final_parameters = analyzed_circuit_data.list_parameters()
    impedance_signal = impedance_function(final_parameters, frequency)
    seed_number = read_input_seed(config)
    impedance_data = simulate_noise(seed_number, impedance_signal)

    plot_data(frequency, impedance_data)
    FILE_NAME = read_output_file_name(config)
    NUMBER_OF_COLUMNS = read_output_file_format(config)
    save_data(FILE_NAME, NUMBER_OF_COLUMNS, frequency, impedance_data)

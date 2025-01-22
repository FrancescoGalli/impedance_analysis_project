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

from generate_impedance import Circuit, list_elements_circuit
from plot_and_save import plot_data, save_data


#####################################
#Input functions, free to edit

def generate_circuit_diagram_data():
    """Generate a circuit diagram for the data generation."""
    circuit_diagram_data = '(R1C2[R3Q4])'
    return circuit_diagram_data


def generate_parameters_data():
    """Generate a list of parameters for the data generation in standard
    units.
    """
    parameter_1 = 3000
    parameter_2 = 2e-6
    parameter_3 = 10000
    parameter_4 = ([0.2e-6, 0.82])
    parameters_data = ([parameter_1, parameter_2, parameter_3, parameter_4])
    return parameters_data


def set_frequencies():
    """Set the range and number of frequencies for the data generation."""
    lower_limit_oom = -1
    upper_limit_oom = 6
    number_of_points = 100
    log_frequency = np.linspace(lower_limit_oom, upper_limit_oom,
                                 number_of_points)
    frequency = 10.**log_frequency
    return frequency


def set_file_name():
    """Set the .txt data file name where the data will be saved."""
    file_name = 'data_impedance'
    file_name += '.txt'
    return file_name

#No modifications below this line
##############################################################################

###############################
#Setting-up functions

def generate_constant_elements_data(parameters_data):
    """Generate an array for constant elements conditions for the data
    generation.

    Parameters
    ----------
    parameters_data : list
        List of the parameters of the circuit's elemetns given by input

    Returns
    -------
    constant_elements_data : list
        List of constant elements conditions, all set to 1
    """
    parameters_data_length = len(parameters_data)
    constant_elements_data = [1] * parameters_data_length
    return constant_elements_data

def generate_circuit_data(circuit_diagram_data, parameters_data):
    """Build the Circuit instance based on the circuit diagram and parameters
    input data.

    Parameters
    ----------
    circuit_diagram_data : str
        Circuit diagram given by input
    parameters_data : list
        List of the parameters of the circuit's elements given by input

    Returns
    -------
    initial_circuit_data : Circuit
        Circuit object for the input data
    """
    constant_elements_data = generate_constant_elements_data(
        parameters_data)
    parameters = {}
    elements = list_elements_circuit(circuit_diagram_data)
    for i, element in enumerate(elements):
        parameters[element] = (parameters_data[i], constant_elements_data[i])
    initial_circuit_data = Circuit(circuit_diagram_data, parameters)
    return initial_circuit_data

############################
#Noise simulation

def generate_random_error_component(signal_length):
    """Generate a random array of numbers between 0 and 1 of length
    signal_length.

    Parameters
    ----------
    signal_length : int
        Length of the generated signal

    Returns
    -------
    random_error_component : array
        Array for constant elements conditions, with the same length of the
        parameters list. During the data generation both 0 and 1 have the same
        effect, thus this array is set to contain only 1 (faster process).
    """
    random_error_component = np.random.uniform(-0.5, 0.5, signal_length)
    return random_error_component

def simulate_noise(impedance_signal):
    """For each of the real and imaginary part of the signal, add a uniform
    probability distribution noise between 0 and 1%/np.sqrt(2) of the
    impedance to the signal.

    Parameters
    ----------
    impedance_signal : array
        Impedances given by the generated impedance function of the circuit

    Returns
    -------
    impedance_data : array
        Simulation of impedances with a random error component
    """
    signal_length = len(impedance_signal)
    noise_factor = 0.01/np.sqrt(2)
    real_part_error = generate_random_error_component(signal_length)
    imaginary_part_error = generate_random_error_component(signal_length)
    noise = noise_factor*impedance_signal * (real_part_error
                                          + 1j*imaginary_part_error)
    impedance_data = impedance_signal + noise
    return impedance_data



if __name__=="__main__":
    CIRCUIT_DIAGRAM_DATA = generate_circuit_diagram_data()
    parameters_data = generate_parameters_data()
    initial_circuit_data = generate_circuit_data(CIRCUIT_DIAGRAM_DATA,
                                                 parameters_data)
    analyzed_circuit_data = initial_circuit_data.generate_analyzed_circuit()
    impedance_function = analyzed_circuit_data.impedance

    frequency = set_frequencies()
    final_parameters = analyzed_circuit_data.list_parameters()
    impedance_signal = impedance_function(final_parameters, frequency)
    impedance_data = simulate_noise(impedance_signal)

    plot_data(frequency, impedance_data)
    FILE_NAME = set_file_name()
    NUMBER_OF_COLUMNS = 2
    save_data(FILE_NAME, NUMBER_OF_COLUMNS, frequency, impedance_data)

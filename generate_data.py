"""This module simulates impedance data starting from the circuit diagram, the
initial parameters of each element and the element constant conditions.
These three pieces of information are stored inside of an Circuit class object
named initial_circuit. The circuit diagram containes the elements type and
their disposition, while their values in the parameters list. The element
constant conditions are all set to 1, since they are not relevant to the
generation of the data.
Starting from this signal, a small randomized noise is added to it.
The final data are plotted and saved .pdf. The data are also saved in a .txt
file, with the complex impedance format.
"""

import numpy as np
import sys

from read import read_configuration
from read import read_input_circuit_diagram, read_input_parameters
from read import read_input_frequencies, read_input_seed
from read import read_output_file_name, read_output_file_format
from generate_impedance import generate_circuit
from plot_and_save import plot_data, save_data


############################
#Input data manipulation

def generate_constant_conditions_data(parameters_data):
    """Generate an array for constant elements conditions for the data
    generation.

    Parameters
    ----------
    parameters_data : dict
        Dictionary of the parameters of the circuit's elements given by input

    Returns
    -------
    constant_conditions_data : dict
        Dictionary of constant elements conditions, all set to 1
    """
    elements = list(parameters_data.keys())
    constant_conditions_data = dict.fromkeys(elements, 1)
    return constant_conditions_data

############################
#Singla generation

def calculate_impedance(impedance_function, frequency):
    """Claculate the impedance data based on the final impedance function and
    on the input frequency points.

    Parameters
    ----------
    impedance_function : func
        Final function of the circuit.
    frequency : list
        List of input frequency of which the impedance data are generate on.

    Returns
    -------
    impedance_signal : array
        Ideal impedance signal of the analyzed circuit.
    """
    try:
        impedance_signal = impedance_function([], frequency)
    except ZeroDivisionError as error:
        print('FatalError: ' + repr(error))
        sys.exit(0) 
    return impedance_signal

def generate_random_error_component(seed_number, signal_length):
    """Generate a random array of numbers between -1 and 1 of length
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
        Array for simulated noise, of the same length of the signal input.
        Its numbers ranges from -1 to 1, through a uniform distribution.
    """
    np.random.seed(seed_number)
    random_error_component = np.random.uniform(-1, 1, signal_length)
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
    default_name = 'config_generation'
    config = read_configuration(default_name)

    CIRCUIT_DIAGRAM_DATA = read_input_circuit_diagram(config)
    parameters_data = read_input_parameters(config)
    constant_conditions_data = generate_constant_conditions_data(
        parameters_data)
    initial_circuit_data = generate_circuit(CIRCUIT_DIAGRAM_DATA,
                                            parameters_data,
                                            constant_conditions_data)
    analyzed_circuit_data = initial_circuit_data.generate_analyzed_circuit()
    impedance_function = analyzed_circuit_data.impedance

    frequency = read_input_frequencies(config)
    impedance_signal = calculate_impedance(impedance_function, frequency)
    seed_number = read_input_seed(config)
    impedance_data = simulate_noise(seed_number, impedance_signal)

    plot_data(frequency, impedance_data)
    FILE_NAME = read_output_file_name(config)
    NUMBER_OF_COLUMNS = read_output_file_format(config)
    save_data(FILE_NAME, NUMBER_OF_COLUMNS, frequency, impedance_data)

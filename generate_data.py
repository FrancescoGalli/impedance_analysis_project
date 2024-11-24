"""This module simulates impedance data starting from the circuit string, the
initial parameters of each element and the element constant conditions. It
plots them and saves the plot and the data as .pdf and .txt respectively.
"""

import numpy as np
import matplotlib.pyplot as plt

from generate_impedance import generate_impedance_function

OHM_CHARACTER_UNICODE = u'\u03A9'

def generate_circuit_data():
    """Generate a circuit string for the data generation."""
    circuit_string_data = '(R1C2[R3Q4])'
    return circuit_string_data

def generate_parameters_data():
    """Generate a list of parameters for the data generation."""
    parameter_1 = 3000
    parameter_2 = 2e-6
    parameter_3 = 10000
    parameter_4 = ([0.2e-6, 0.82])
    parameters_data = ([parameter_1, parameter_2, parameter_3, parameter_4])
    return parameters_data

def generate_constant_elements_array_data():
    """Generate an array for constant elements conditions for the data
    generation."""
    constant_elements_data = ([0, 0, 1, 0])
    return constant_elements_data

def set_frequencies():
    """Set the range and number of frequencies for the data generation."""
    lower_limit_oom = -1
    upper_limit_oom = 6
    number_of_points = 100
    log_frequency_vector = np.linspace(lower_limit_oom, upper_limit_oom,
                                       number_of_points)
    frequency_vector = 10.**log_frequency_vector
    return frequency_vector

def set_file_name():
    """Set the data file name where the data will be saved."""
    file_name = 'data_impedance.txt'
    return file_name

##############################################################################


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
        Array of random numbers to simulate random noise
    """
    random_error_component = np.random.rand(signal_length)
    return random_error_component

def simulate_noise(signal_vector):
    """For each of the real and imaginary part of the signal, add a uniform
    probability distribution noise between 0 and 1%/np.sqrt(2) of the
    impedance to the signal.

    Parameters
    ----------
    signal_vector : array
        Impedances given by the generated impedance function of the circuit

    Returns
    -------
    impedance_vector : array
        Simulation of impedances with a random error
    """
    signal_length = len(signal_vector)
    noise_factor = 0.01/np.sqrt(2)
    real_part_error = generate_random_error_component(signal_length)
    imaginary_part_error = generate_random_error_component(signal_length)
    noise = noise_factor*signal_vector * (real_part_error
                                          + 1j*imaginary_part_error)
    impedance_vector = signal_vector + noise
    return impedance_vector

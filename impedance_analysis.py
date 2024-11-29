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

"""This module containes all the test functions (and the tested help functions
for the tests) for the generate_data.py module.
"""

import numpy as np
from hypothesis import given, settings
import hypothesis.strategies as st

import sys
from pathlib import Path
sys.path.append(str(Path.cwd().parent))

from generate_data import generate_random_error_component, simulate_noise


def wrong_numbers_generate_random_error_value(random_error_component):
    """Find the numbers in the random_error_component that are not within
    -1 and 1. Used for testing.

    Parameters
    ----------
    random_error_component : array
        Array of numbers within -1 and 1

    Returns
    -------
    wrong_numbers : list
        List that contains all the wrong numbers
    wrong_number_index : list
        List of indexes of the wrong numbers in the array
    """
    wrong_numbers = ''
    wrong_number_index = []
    for i, number in enumerate(random_error_component):
        if abs(number)>1.:
            wrong_numbers += str(number) + ' '
            wrong_number_index.append(i)
    return wrong_numbers, wrong_number_index

def test_wrong_numbers_generate_random_error_empty_list():
    """Check that the function to detect numbers with a modulus bigger than 1
    works for an empty list.
    If no invalid number is detected, the returned string and list given
    by the function under test are empty.

    GIVEN: an empty list
    WHEN: I check if there are invalid numbers (modulus bigger than 1) inside
    the list
    THEN: no invalid number is detected
    """
    empty_list = []
    (wrong_number,
     wrong_number_index) = wrong_numbers_generate_random_error_value(
         empty_list)

    assert not wrong_number, (
        'ValueError for the number(s) ' + str(wrong_number) + 'in position(s) '
        + str(wrong_number_index) + '. Cannot find invalid numbers because '
        + 'there are no numbers')

def test_wrong_numbers_generate_random_error_value_single_number():
    """Check that the function to detect numbers with a modulus bigger than 1
    works for a list with a single number.
    If no invalid number is detected, the returned string and list given
    by the function under test are empty.

    GIVEN: a list with a single number which modulus is smaller that 1
    WHEN: I check if there are invalid numbers inside the list
    THEN: no invalid number is detected
    """
    single_number = [0.34]
    (wrong_number,
     wrong_number_index) = wrong_numbers_generate_random_error_value(
         single_number)

    assert not wrong_number, (
        'ValueError for the number(s) ' + str(wrong_number) + 'in position(s) '
        + str(wrong_number_index) + '. The modulus must be smaller than 1')

def test_wrong_numbers_generate_random_error_value_many_numbers():
    """Check that the function to detect numbers with a modulus bigger than
    1 works for a list with three numbers.
    If no invalid number is detected, the returned string and list given
    by the function under test are empty.

    GIVEN: a list with three numbers which modulus are smaller that 1
    WHEN: I check if there are invalid numbers inside the list
    THEN: no invalid number is detected
    """
    three_numbers = [0., -0.234, 0.9]
    (wrong_number,
     wrong_number_index) = wrong_numbers_generate_random_error_value(
         three_numbers)

    assert not wrong_number, (
        'ValueError for the number(s) ' + str(wrong_number) + 'in position(s) '
        + str(wrong_number_index) + '. The modulus must be smaller than 1')

def test_wrong_numbers_generate_random_error_value_invalid_numbers():
    """Check that the function to detect numbers with a modulus bigger than
    1 works for a list with three numbers, which the first and the last one
    are invalid.
    If invalid numbers are detected, the returned string contains the invalid
    numbers, while the returned list contains their index in the list.

    GIVEN: a list with three numbers: only the second one has a modulus
    smaller that 1
    WHEN: I check if there are invalid numbers inside the list
    THEN: all and only the invalid numbers are detected as such
    """
    invalid_numbers = [-22.0 , -0.34, 1.01]
    expected_result = '-22.0 1.01 '
    (wrong_number,
     wrong_number_index) = wrong_numbers_generate_random_error_value(
        invalid_numbers)

    assert wrong_number==expected_result, (
        'ValueError for the number(s) ' + str(wrong_number) + 'in position(s) '
        + str(wrong_number_index) + '. The modulus must be smaller than 1')


@given(signal_length=st.integers(min_value=1, max_value=100),
       seed=st.integers(min_value=0, max_value=1000000))
@settings(max_examples=10)
def test_generate_random_error_component_array(seed, signal_length):
    """Check that the output of generate_random_error_component() is an array
    with pseudo-random numbers, all within -1 and 1.

    GIVEN: a valid seed and length of the generated signal
    WHEN: the function to generate random numbers to simulate noise is called
    THEN: the random noise is an array of all numbers within -1 and 1
    """
    random_error_component = generate_random_error_component(seed,
                                                             signal_length)

    assert isinstance(random_error_component, np.ndarray), (
        'TypeError in generate_random_error_component(): the output must be '
        + 'a numpy.ndarray')
    assert random_error_component.size>0, (
        'StructuralError in generate_random_error_component(): the output'
        + 'cannot be empty')
    (wrong_number,
     wrong_number_index) = wrong_numbers_generate_random_error_value(
         random_error_component)
    assert not wrong_number, (
        'ValueError in output of generate_random_error_component(): number(s) '
        + str(wrong_number) + ' in position(s) ' + str(wrong_number_index)
        + ' are not within -1 and 1')


def test_simulate_noise_single_element_resistor():
    """Check that the output of simulate_noise() is a valid impedance array,
    with similar values of the input (but with added psudo-random noise) in
    the case of a single value signal from a resistor circuit and a valid
    seed.

    GIVEN: a single value signal (resistor-like) and a valid seed (for
    reproducibility)
    WHEN: I call the function to generate random numbers (noise) and add them
    to the signal
    THEN: the output is  avalid complex 1D array. The noise amplitude (the
    difference between the output and the input signal), is smaller than 1%
    of the input signal.
    """
    seed = 0
    input_signal = np.array([complex(100,0)])
    simulated_signal = simulate_noise(seed, input_signal)

    assert isinstance(simulated_signal, np.ndarray), (
        'TypeError in simulate_noise(): the output must be a numpy.ndarray')
    assert simulated_signal.size>0, ('TypeError in simulate_noise(): the '
                                     + 'output cannot be an empty array')
    assert simulated_signal.ndim==1, (
        'TypeError in simulate_noise(): the output must be a one-dimention '
        + 'array, while it is ' + str(simulated_signal.ndim))
    assert simulated_signal.dtype==complex, (
        'TypeError in simulate_noise(): the output must be a float array, '
        + 'while it is ' + str(simulated_signal.dtype))

    noise = simulated_signal - input_signal
    assert (np.all((abs(noise/input_signal))<=0.01)), (
        'ValueError in simulate_noise(): the amplitude of the noise is '
        + 'bigger than 1% the input signal')

def test_simulate_noise_many_elements_capacitor():
    """Check that the output of simulate_noise() is a valid impedance array,
    with similar values of the input (but with added psudo-random noise) in
    the case of a five-value signal from a capacitor circuit and a valid seed.

    GIVEN: a four values signal (capacitor-like) and a valid seed (for
    reproducibility)
    WHEN: I call the function to generate random numbers (noise) and add them
    to the signal
    THEN: the output is  avalid complex 1D array. The noise amplitude (the
    difference between the output and the input signal), is smaller than 1%
    of the input signal for all the points.
    """
    seed = 12
    input_signal = np.array([complex(0,-1000), complex(0,-100),
                             complex(0,-10), complex(0,-1)])
    simulated_signal = simulate_noise(seed, input_signal)

    assert isinstance(simulated_signal, np.ndarray), (
        'TypeError in simulate_noise(): the output must be a numpy.ndarray')
    assert simulated_signal.size>0, ('TypeError in simulate_noise(): the '
                                     + 'output cannot be an empty array')
    assert simulated_signal.ndim==1, (
        'TypeError in simulate_noise(): the output must be a one-dimention '
        + 'array, while it is ' + str(simulated_signal.ndim))
    assert simulated_signal.dtype==complex, (
        'TypeError in simulate_noise(): the output must be a float array, '
        + 'while it is ' + str(simulated_signal.dtype))

    noise = simulated_signal - input_signal
    assert (np.all((abs(noise/input_signal))<=0.01)), (
        'ValueError in simulate_noise(): for at least one point, the '
        + 'amplitude of the noise is bigger than 1% the input signal')

def test_simulate_noise_many_elements_rc():
    """Check that the output of simulate_noise() is a valid impedance array,
    with similar values of the input (but with added psudo-random noise) in
    the case of a five-value signal from an rc circuit and a valid seed.

    GIVEN: a four values signal (rc-like) and a valid seed
    WHEN: I call the function to generate random numbers (noise) and add them
    to the signal
    THEN: the output is a valid complex 1D array. The noise amplitude (the
    difference between the output and the input signal), is smaller than 1%
    the input signal for all the points.
    """
    seed = 145
    input_signal = np.array([complex(100, 1000), complex(100, 100),
                             complex(100,10), complex(100,1)])
    simulated_signal = simulate_noise(seed, input_signal)

    assert isinstance(simulated_signal, np.ndarray), (
        'TypeError in simulate_noise(): the output must be a numpy.ndarray')
    assert simulated_signal.size>0, ('TypeError in simulate_noise(): the '
                                     + 'output cannot be an empty array')
    assert simulated_signal.ndim==1, (
        'TypeError in simulate_noise(): the output must be a one-dimention '
        + 'array, while it is ' + str(simulated_signal.ndim))
    assert simulated_signal.dtype==complex, (
        'TypeError in simulate_noise(): the output must be a float array, '
        + 'while it is ' + str(simulated_signal.dtype))

    noise = simulated_signal - input_signal
    assert (np.all((abs(noise/input_signal))<=0.01)), (
        'ValueError in simulate_noise(): for at least one point, the '
        + 'amplitude of the noise is bigger than 1% the input signal')

def test_simulate_noise_no_elements():
    """Check that the output of simulate_noise() is a an empty array in the
    case of an empty array as input.

    GIVEN: an invalid empty array as input and a valid seed (for
    reproducibility)
    WHEN: I call the function to generate random numbers (noise) and add them
    to the signal
    THEN: the output is an invalid empty array
    """
    seed = 15
    input_signal = np.array([])
    simulated_signal = simulate_noise(seed, input_signal)

    assert isinstance(simulated_signal, np.ndarray), (
        'TypeError in simulate_noise(): the output must be a numpy.ndarray')
    assert simulated_signal.size==0, ('TypeError in simulate_noise(): the '
                                      + 'output is not empty as expected')

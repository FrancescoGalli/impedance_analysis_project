"""This module containes all the test functions (and the tested help functions
for the tests) for all the functions inside the generate_impedance.py module,
apart from the AnalysisCircuit class and the generate circuit functions
"""


import inspect
import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis.extra import numpy as enp
import hypothesis.strategies as st

import sys
from pathlib import Path
sys.path.append(str(Path.cwd().parent))

from generate_impedance import Circuit, AnalisysCircuit
from generate_impedance import (
    impedance_resistor, impedance_capacitor, impedance_cpe, add, serial_comb,
    reciprocal, parallel_comb, get_position_opening_bracket, get_string,
    list_elements_circuit)


################################
#Test impedance definitions

@given(frequency=enp.arrays(dtype=float, shape=10, elements=st.floats(1, 1e4),
                            unique=True),
       resistance=st.floats(min_value=10, max_value=1e5))
@settings(max_examples=10)
def test_impedance_resistor_type(resistance, frequency):
    """Check that the definition of the impedance of resistors returns a
    valid type of impedance array.

    GIVEN: the value of resistance and frequencies are valid
    WHEN: I call the definition of resistive impedance
    THEN: the impedance is an array of complex impedances of the same size of
    the fequency array.
    """
    impedance = impedance_resistor(resistance, frequency)

    assert isinstance(impedance, np.ndarray), (
        'TypeError for resistive impedance. It must be a numpy array')
    assert np.iscomplexobj(impedance), (
        'TypeError for resistive impedance. It must be a complex numpy array')
    assert impedance.size>0, ('StructuralError for resistive impedance. It'
                              + 'cannot be empty')


def test_impedance_resistor_value_single_zero():
    """Check that the definition of the impedance of resistors returns a
    proper impedance value in the case of zero resistance and a single
    frequency point.
    For a resistor, the impedance amplitude is the the absolute value of the
    resistance, while the phase is always zero.

    GIVEN: a valid (zero) resistance and a valid frequency list with just one
    value
    WHEN: I call the definition of resistive impedance
    THEN: the amplitude and phase of the impedence are the ones expected
    (valid ones)
    """
    resistance = 0.
    frequency = [10.]
    impedance = impedance_resistor(resistance, frequency)
    expected_amplitude = [0.]
    expected_phase = [0.]

    assert abs(impedance)==expected_amplitude, (
        'ValueError from the definition of impedance of the ' + str(resistance)
        + ' resistor: the impedance amplitude is incorrect')
    assert np.angle(impedance, deg=True)==expected_phase, (
        'ValueError from the definition of impedance of the ' + str(resistance)
        + ' resistor: the impedance phase is incorrect')

def test_impedance_resistor_value_many_zeros():
    """Check that the definition of the impedance of resistors returns a
    proper impedance value in the case of zero resistance and five
    frequency points.
    For a resistor, the impedance amplitude is the the absolute value of the
    resistance, while the phase is always zero.

    GIVEN: a valid (zero) resistance and a valid frequency list with five
    values
    WHEN: I call the definition of resistive impedance
    THEN: the amplitude and phase of the impedence are the ones expected
    (valid ones)
    """
    resistance = 0.
    frequency = [1., 10., 100, 1000., 10000.]
    impedance = impedance_resistor(resistance, frequency)
    expected_amplitude = [0., 0., 0., 0., 0.]
    expected_phase = [0., 0., 0., 0., 0.]

    assert np.all(abs(impedance)==expected_amplitude), (
        'ValueError from the definition of impedance of the ' + str(resistance)
        + ' resistor: the impedance amplitude is incorrect')
    assert np.all(np.angle(impedance, deg=True)==expected_phase), (
        'ValueError from the definition of impedance of the ' + str(resistance)
        + ' resistor: the impedance phase is incorrect')

def test_impedance_resistor_value_positive_value():
    """Check that the definition of the impedance of resistors returns a
    proper impedance value in the case of a positive value of resistance and
    five frequency points.
    For a resistor, the impedance amplitude is the the absolute value of the
    resistance, while the phase is always zero.

    GIVEN: a valid resistance and a valid frequency list with five values
    WHEN: I call the definition of resistive impedance
    THEN: the amplitude and phase of the impedence are the ones expected
    (valid ones)
    """
    resistance = 101.2
    frequency = [1., 10., 100, 1000., 10000.]
    impedance = impedance_resistor(resistance, frequency)
    expected_amplitude = [101.2, 101.2, 101.2, 101.2, 101.2]
    expected_phase = [0., 0., 0., 0., 0.]

    assert np.all(abs(impedance)==expected_amplitude), (
        'ValueError from the definition of impedance of the ' + str(resistance)
        + ' resistor: the impedance amplitude is incorrect')
    assert np.all(np.angle(impedance, deg=True)==expected_phase), (
        'ValueError from the definition of impedance of the ' + str(resistance)
        + ' resistor: the impedance phase is incorrect')

def test_impedance_resistor_value_invalid_negative_value():
    """Check that the definition of the impedance of resistors returns an
    invalid impedance value in the case of a negative (thus invalid) value of
    resistance and three frequency points.
    For a resistor, the impedance amplitude is the the absolute value of the
    resistance, while the phase is always zero.

    GIVEN: an invalid resistance and a valid frequency list with three values
    WHEN: I call the definition of resistive impedance
    THEN: the amplitude and phase of the impedance are the expected invalid
    ones, up to a certain high precision
    """
    resistance = -2. #Invalid resistance, cannot be negative
    frequency = [1., 10., 100]
    impedance = impedance_resistor(resistance, frequency)
    expected_amplitude = [2., 2., 2.]
    expected_phase = np.ones(3)*180. #Invalid phase: it is 180 instead of 0

    assert np.all(abs(impedance)==expected_amplitude), (
        'ValueError from the definition of impedance of the ' + str(resistance)
        + ' resistor: the impedance amplitude is different from the expeted '
        + 'one')
    assert np.all(np.angle(impedance, deg=True)==expected_phase), (
        'ValueError from the definition of impedance of the ' + str(resistance)
        + ' resistor: the impedance phase is different from the expeted one')


@given(frequency=enp.arrays(dtype=float, shape=10, elements=st.floats(1, 1e4),
                            unique=True),
       capacitance=st.floats(min_value=1e-9, max_value=1e-5))
@settings(max_examples=10)
def test_impedance_capacitor_type(capacitance, frequency):
    """Check that the definition of the impedance of capacitors returns a
    valid type of impedance array.

    GIVEN: the value of capacitance and frequencies are valid
    WHEN: I call the definition of capacitative impedance
    THEN: the impedance is an array of complex impedances of the same size of
    the fequency array.
    """
    impedance = impedance_capacitor(capacitance, frequency)
    assert isinstance(impedance, np.ndarray), (
        'TypeError for capacitative impedance. It must be a numpy array')
    assert np.iscomplexobj(impedance), (
        'TypeError for capacitative impedance. It must be a complex numpy '
        + 'array')
    assert impedance.size>0, ('StructuralError for capacitative impedance.'
                              + 'It cannot be empty')

def test_impedance_capacitor_value_single_value():
    """Check that the definition of the impedance of capacitors returns a
    proper impedance value in the case of a valid positive capacitance and a
    single frequency point.
    For a capacitor, the amplitude is the absolute value of one over the
    product of the value of the capacitance and the fequencies, and then
    divided by 2pi. The phase is always -90 deg (or -pi/2 in rad).

    GIVEN: a valid capacitance and a valid frequency list with just one
    value
    WHEN: I call the definition of capacitative impedance
    THEN: the amplitude and phase of the impedance are the ones expected
    (valid ones)
    """
    capacitance = 1e-3
    frequency = np.array([1000.])
    impedance = impedance_capacitor(capacitance, frequency)
    expected_amplitude = np.array([1.])/(2*np.pi)
    expected_phase = np.array([-90.])

    assert np.all(abs(impedance)==expected_amplitude), (
        'ValueError from the definition of impedance of the '+ str(capacitance)
        + ' capacitor: the impedance amplitude is incorrect')
    assert np.all(np.angle(impedance, deg=True)==expected_phase), (
        'ValueError from the definition of impedance of the ' + str(capacitance)
        + ' capacitor: the impedance phase is incorrect')

def test_impedance_capacitor_value_many_values():
    """Check that the definition of the impedance of capacitors returns a
    proper impedance value in the case of a valid positive capacitance and
    five frequency points.
    For a capacitor, the amplitude is the absolute value of one over the
    product of the value of the capacitance and the fequencies, and then
    divided by 2*pi. The phase is always -90 deg (or -pi/2 in rad).

    GIVEN: a valid capacitance and a valid frequency list with five values
    WHEN: I call the definition of capacitative impedance
    THEN: the amplitude and phase of the impedance are the ones expected
    (valid ones), up to a certain high precision
    """
    capacitance = 1e-4
    frequency = np.array([0.1, 1., 10., 100., 1000.])
    impedance = impedance_capacitor(capacitance, frequency)
    rounded_amplitude = np.ndarray.round(np.array(abs(impedance)), 5)
    expected_amplitude =  np.array([1e5, 1e4, 1e3, 1e2, 1e1])/(2*np.pi)
    rounded_expected_amplitude = np.ndarray.round(expected_amplitude, 5)
    expected_phase = np.ones(5)*[-90.]

    assert np.all(rounded_amplitude==rounded_expected_amplitude), (
        'ValueError from the definition of impedance of the '+ str(capacitance)
        + ' capacitor: the impedance amplitude is incorrect')
    assert np.all(np.angle(impedance, deg=True)==expected_phase), (
        'ValueError from the definition of impedance of the ' + str(capacitance)
        + ' capacitor: the impedance phase is incorrect')

def test_impedance_capacitor_negative_value():
    """Check that the definition of the impedance of capacitors returns an
    invalid impedance value in the case of a negative (thus invalid) value of
    capacitance and three frequency points.
    For a capacitor, the amplitude is the absolute value of one over the
    product of the value of the capacitance and the fequencies, and then
    divided by 2*pi. The phase is always -90 deg (or -pi/2 in rad).

    GIVEN: an invalid negative capacitance and a valid frequency list with
    three values
    WHEN: I call the definition of capacitative impedance
    THEN: the amplitude and phase of the impedance are the expected invalid
    ones, up to a certain high precision
    """
    capacitance = -1e-5 #Negative, thus invalid
    frequency = np.array([0.1, 1., 10., 100., 1000.])
    impedance = impedance_capacitor(capacitance, frequency)
    rounded_amplitude = np.ndarray.round(np.array(abs(impedance)), 5)
    expected_amplitude =  np.array([1e6, 1e5, 1e4, 1e3, 1e2])/(2*np.pi)
    rounded_expected_amplitude = np.ndarray.round(expected_amplitude, 5)
    expected_phase = np.ones(5)*[90.] #A phase of +90 instead of -90 for a
                                          #capacitor is invalid

    assert np.all(rounded_amplitude==rounded_expected_amplitude), (
        'ValueError from the definition of impedance of the ' + str(capacitance)
        + ' capacitor: the impedance amplitude is different from the expeted '
        + 'one')
    assert np.all(np.angle(impedance, deg=True)==expected_phase), (
        'ValueError from the definition of impedance of the ' + str(capacitance)
        + ' capacitor: the impedance phase is different from the expeted one')

def test_impedance_capacitor_zero_capacitance():
    """Check that the definition of the impedance of capacitors raises an
    Exception with a certain message when the value of the capacitance is zero.
    Since the impedance goes as 1/capacitance, that would lead to a division
    by 0.

    GIVEN: an invalid zero capacitance and a valid frequency list with one
    value
    WHEN: I call the definition of capacitative impedance
    THEN: the impedance definition function raises an Exception with a message
    that states the division by 0
    """
    capacitance = 0 #Zero, invalid
    frequency = np.array([1.])

    with pytest.raises(Exception) as excinfo:
        _ = impedance_capacitor(capacitance, frequency)
    message = excinfo.value.args[0]
    assert message==('Zero Division in capacitance impedance definition')

def test_impedance_capacitor_zero_frequency():
    """Check that the definition of the impedance of capacitors raises an
    Exception with a certain message when the value of the capacitance is
    finite but one of the frequencies is zero.
    Since the impedance goes as 1/frequency, that would lead to a division
    by 0.

    GIVEN: a valid capacitance but an invalid zero frequency in a list with
    three values
    WHEN: I call the definition of capacitative impedance
    THEN: the impedance definition function raises an Exception with a message
    that states the division by 0
    """
    capacitance = 1e-4
    frequency = np.array([1, 0.1, 0]) #There is a zero, invalid

    with pytest.raises(Exception) as excinfo:
        _ = impedance_capacitor(capacitance, frequency)
    message = excinfo.value.args[0]
    assert message==('Zero Division in capacitance impedance definition')


@given(frequency=enp.arrays(dtype=float, shape=10, elements=st.floats(1, 1e4),
                            unique=True),
       q_parameter=st.floats(min_value=1e-9, max_value=1e-5),
       ideality_factor=st.floats(min_value=0., max_value=1.))
@settings(max_examples=10)
def test_impedance_cpe_type(q_parameter, ideality_factor, frequency):
    """Check that the definition of the impedance of cpes returns a
    valid type of impedance array.

    GIVEN: the value of Q,  ideality_factor and frequencies are valid
    WHEN: I call the definition of cpe impedance
    THEN: the impedance is an array of complex impedances of the same size of
    the fequency array.
    """
    impedance = impedance_cpe(q_parameter, ideality_factor, frequency)

    assert isinstance(impedance, np.ndarray), (
        'TypeError for CPE impedance. It must be a numpy array')
    assert np.iscomplexobj(impedance), (
        'TypeError for CPE impedance. It must be a complex numpy array')
    assert impedance.size>0, ('StructuralError for CPE impedance. It cannot '
                              + 'be empty')

def test_impedance_cpe_value_resistor_like():
    """Check that the definition of the impedance of cpe returns a
    proper impedance value in the case of a valid positive Q, an iedality
    factor of 0 and a single frequency point. If ideality_factor is zero, the
    impedance behaviour is similar to a resistor one, with 1/q_factor as
    "resistance".
    For a cpe, the amplitude is inversely proportional to Q and frequency
    to the power of ideality_factor, while the phase ranges from -90 to 0,
    depending on the value of ideality_factor (that ranges between 0 and 1).

    GIVEN: a valid Q, a valid (zero) ideality factor n and a valid frequency
    list with just one value
    WHEN: I call the definition of cpe impedance
    THEN: the amplitude and phase of the impedance are the ones expected
    (valid ones)
    """
    q_factor = 1e-4
    ideality_factor = 0
    frequency = np.array([1000.])
    impedance = impedance_cpe(q_factor, ideality_factor, frequency)
    expected_amplitude = [10000.]
    expected_phase = [0.]

    assert np.all(abs(impedance)==expected_amplitude), (
        'ValueError from the definition of impedance of the '+ str(q_factor)
        + ' cpe: the impedance amplitude is incorrect')
    assert np.all(np.angle(impedance, deg=True)==expected_phase), (
        'ValueError from the definition of impedance of the ' + str(q_factor)
        + ' cpe: the impedance phase is incorrect')

def test_impedance_cpe_value_capacitor_like():
    """Check that the definition of the impedance of cpe returns a
    proper impedance value in the case of a valid positive Q, an iedality
    factor of 1 and a five frequency points. If ideality_factor is 1, the
    impedance behaviour is similar to a capacitor one, with q_factor as
    "capacitance".
    For a cpe, the amplitude is inversely proportional to Q and frequency
    to the power of ideality_factor, while the phase ranges from -90 to 0,
    depending on the value of ideality_factor (that ranges between 0 and 1).

    GIVEN: a valid Q, a valid (one) ideality factor and a valid frequency list
    with just one value
    WHEN: I call the definition of cpe impedance
    THEN: the amplitude and phase of the impedance are the ones expected
    (valid ones)
    """
    q_factor = 1e-3
    ideality_factor = 1
    frequency = np.array([0.1, 1., 10., 100., 1000.])
    impedance = impedance_cpe(q_factor, ideality_factor, frequency)
    rounded_amplitude = np.ndarray.round(np.array(abs(impedance)), 5)
    expected_amplitude = np.array([1e4, 1e3, 1e2, 1e1, 1.])/(2*np.pi)
    rounded_expected_amplitude = np.ndarray.round(expected_amplitude, 5)
    expected_phase = np.ones(5)*[-90.]

    assert np.all(rounded_amplitude==rounded_expected_amplitude), (
        'ValueError from the definition of impedance of the '+ str(q_factor)
        + ' cpe: the impedance amplitude is incorrect')
    assert np.all(np.angle(impedance, deg=True)==expected_phase), (
        'ValueError from the definition of impedance of the ' + str(q_factor)
        + ' cpe: the impedance phase is incorrect')

def test_impedance_cpe_value_half_way():
    """Check that the definition of the impedance of cpe returns a
    proper impedance value in the case of a valid positive Q, an iedality
    factor of 0.5 and a a frequency point. If ideality_factor is 0.5, the
    impedance behaviour has not an easy interpretation, but we could say that,
    it is half-way beteween a resistor and a capacitor.
    For a cpe, the amplitude is inversely proportional to Q and frequency
    to the power of ideality_factor, while the phase ranges from -90 to 0,
    depending on the value of ideality_factor (that ranges between 0 and 1).

    GIVEN: a valid Q, a valid (0.5) ideality factor and a valid frequency list
    with just one value
    WHEN: I call the definition of cpe impedance
    THEN: the amplitude and phase of the impedance are the ones expected
    (valid ones)
    """
    q_factor = 1e-5
    ideality_factor = 0.5
    frequency = np.array([1.])
    impedance = impedance_cpe(q_factor, ideality_factor, frequency)
    rounded_amplitude = np.ndarray.round(np.array(abs(impedance)), 5)
    expected_amplitude =  np.array([1e5])/(2*np.pi)**0.5
    rounded_expected_amplitude = np.ndarray.round(expected_amplitude, 5)
    expected_phase = np.ones(5)*[-45.] #-45 because it is halfway between -90
                                       # and 0

    assert np.all(rounded_amplitude==rounded_expected_amplitude), (
        'ValueError from the definition of impedance of the '+ str(q_factor)
        + ' cpe: the impedance amplitude is incorrect')
    assert np.all(np.angle(impedance, deg=True)==expected_phase), (
        'ValueError from the definition of impedance of the ' + str(q_factor)
        + ' cpe: the impedance phase is incorrect')

def test_impedance_cpe_zero_q():
    """Check that the definition of the impedance of cpe raises an
    Exception with a certain message when the value of q_factor is zero.
    Since the impedance goes as 1/q_factor, that would lead to a division by
    0.

    GIVEN: an invalid (zero) Q, a valid (one) ideality_factor and a valid
    frequency list with one value
    WHEN: I call the definition of capacitative impedance
    THEN: the impedance definition function raises an Exception with a message
    that states the division by 0
    """
    q_factor = 0 #Zero, invalid
    ideality_factor = 0.2
    frequency = np.array([1.])

    with pytest.raises(Exception) as excinfo:
        _ = impedance_cpe(q_factor, ideality_factor, frequency)
    message = excinfo.value.args[0]
    assert message==('Zero Division in cpe impedance definition')

def test_impedance_cpe_zero_frequency():
    """Check that the definition of the impedance of cpe raises an
    Exception with a certain message when the value of q_factor is finite but
    one of the frequencies is zero.
    Since the impedance goes as 1/frequency, that would lead to a division
    by 0.

    GIVEN: a valid q_factor and ideality_factor, but an invalid zero frequency
    in a list with three values
    WHEN: I call the definition of capacitative impedance
    THEN: the impedance definition function raises an Exception with a message
    that states the division by 0
    """
    q_factor = 1e-4
    ideality_factor = 0.8
    frequency = np.array([1, 0.1, 0]) #There is a zero, invalid

    with pytest.raises(Exception) as excinfo:
        _ = impedance_cpe(q_factor, ideality_factor, frequency)
    message = excinfo.value.args[0]
    assert message==('Zero Division in cpe impedance definition')


def test_add_double_zero():
    """Check that the add function returns a valid sum function in the case of
    two functions that are always zero.

    GIVEN: two functions that are always zero (zero functions).
    WHEN: the add function is called
    THEN: the result of the add function is a proper sum function that is
    always zero
    """
    first_zero_function = lambda x, y: 0
    second_zero_function = lambda x, y: 0
    sum_function = add(first_zero_function, second_zero_function)
    x_inputs = [0, 1, 2, 4]
    y_inputs = [0, 1, 5, 10]
    expected_result = 0

    assert inspect.isfunction(sum_function), (
        'TypeError for the output function of the add() test. It must be a '
        + 'function')
    assert sum_function(x_inputs, y_inputs)==expected_result, (
        'ValueError for the output function of the add() test. The output is '
        + 'incorrect')

def test_add_one_zero():
    """Check that the add function returns a valid sum function in the case of
    a function that returns just the first input and a zero function.

    GIVEN: a function that is just the first input and a zero function
    WHEN: the add function is called
    THEN: the result of the add function is a proper sum function
    """
    first_function = lambda x, y: x
    zero_function = lambda x, y: 0
    sum_function = add(first_function, zero_function)
    x_inputs = np.array([0, 1, 2, 4])
    y_inputs = np.array([0, 1, 5, 10])
    expected_result = [0, 1, 2, 4]

    assert inspect.isfunction(sum_function), (
        'TypeError for the output function of the add() test. It must be a '
        + 'function')
    assert np.all(sum_function(x_inputs, y_inputs)==expected_result), (
        'ValueError for the output function of the add() test. The output is '
        + 'incorrect')

def test_add_directly_proportional():
    """Check that the add function returns a valid sum function in the case of
    a function that returns the first input and a secod one that returns the
    second input.

    GIVEN: a function that returns just the first input and a secod one that
    returns the second input
    WHEN: the add function is called
    THEN: the result of the add function is a proper sum function
    """
    first_function = lambda x, y: x
    second_function = lambda x, y: y
    sum_function = add(first_function, second_function)
    x_inputs = np.array([0, 1, 2, 4])
    y_inputs = np.array([0, 1, 5, 10])
    expected_result = [0, 2, 7, 14]

    assert inspect.isfunction(sum_function), (
        'TypeError for the output function of the add() test. It must be a '
        + 'function')
    assert np.all(sum_function(x_inputs, y_inputs)==expected_result), (
        'ValueError for the output function of the add() test. The output is '
        + 'incorrect')


def test_serial_comb_single_function():
    """Check that the serial comb function returns a valid sum function in the
    case of a single function (i.e. returns the input function).

    GIVEN: a list of functions with just one function
    WHEN: the function to perform the serial comb is called
    THEN: the result of the serial comb function is a proper sum function, in
    this case the input function
    """
    singe_function = lambda x, y: x + y
    serial_comb_function = serial_comb([singe_function])
    x_inputs = np.array([0, 1, 2, 4])
    y_inputs = np.array([0, 1, 5, 10])
    expected_result = [0, 2, 7, 14]

    assert inspect.isfunction(serial_comb_function), (
        'TypeError for the output of function of serial_comb() test. It must '
        + 'be a function')
    assert np.all(serial_comb_function(x_inputs, y_inputs)==expected_result), (
        'ValueError for the output of function of function of the '
        + 'serial_comb() test. The output is incorrect')

def test_serial_comb_two_functions():
    """Check that the serial comb function returns a valid sum function in the
    case of two functions.

    GIVEN: a list of functions with two functions
    WHEN: the function to perform the serial comb is called
    THEN: the result of the serial comb function is a proper sum function.
    """
    first_function = lambda x, y: 2*x +1
    second_function = lambda x, y: y/5
    serial_comb_function = serial_comb([first_function, second_function])
    x_inputs = np.array([0, 1, 2, 4])
    y_inputs = np.array([0, 1, 5, 10])
    expected_result = [1, 3.2, 6, 11]

    assert inspect.isfunction(serial_comb_function), (
        'TypeError for the output of function of serial_comb() test. It must '
        + 'be a function')
    assert np.all(serial_comb_function(x_inputs, y_inputs)==expected_result), (
        'ValueError for the output of function of function of the '
        + 'serial_comb() test. The output is incorrect')

def test_serial_comb_three_functions():
    """Check that the serial comb function returns a valid sum function in the
    case of three functions.

    GIVEN: a list of functions with three functions
    WHEN: the function to perform the serial comb is called
    THEN: the result of the serial comb function is a proper sum function
    """
    first_function = lambda x, y: (x + y)/2
    second_function = lambda x, y: y**2/4
    third_function = lambda x, y: np.sqrt(x**2+y**2)
    serial_comb_function = serial_comb([first_function, second_function,
                                        third_function])
    x_inputs = np.array([0, 3, 6, 9])
    y_inputs = np.array([0, 4, 8, 12])
    expected_result = [0., 12.5, 33., 61.5]

    assert inspect.isfunction(serial_comb_function), (
        'TypeError for the output of function of serial_comb() test. It must '
        + 'be a function')
    assert np.all(serial_comb_function(x_inputs, y_inputs)==expected_result), (
        'ValueError for the output of function of function of the '
        + 'serial_comb() test. The output is incorrect')

def test_serial_comb_no_functions():
    """Check that the serial comb function returns a valid sum function in the
    case of no functions.

    GIVEN: an empty list of functions (invalid input)
    WHEN: the function to perform the serial comb is called
    THEN: the result of the serial comb function is the zero function, instead
    of a possible None type
    """
    serial_comb_function = serial_comb([])
    x_inputs = np.array([0, 2, 6, 9])
    y_inputs = np.array([0, 3, 8, 12])
    expected_result = 0

    assert inspect.isfunction(serial_comb_function), (
        'TypeError for the output of function of serial_comb() test. It must '
        + 'be a function')
    assert np.all(serial_comb_function(x_inputs, y_inputs)==expected_result), (
        'ValueError for the output of function of function of the '
        + 'serial_comb() test. The output is different than the one expected')


def test_reciprocal_constant():
    """Check that the reciprocal function returns a valid reciprocal
    function in the case of a constant function.

    GIVEN: a valid constant of function
    WHEN: the functions to get the reciprocal of a function is called
    THEN: the output function is the reciprocal function of the input one
    """
    input_function = lambda x, y: 3
    reciprocal_function = reciprocal(input_function)
    x_inputs = [0, 1, 2, 4]
    y_inputs = [0, 1, 5, 10]
    expected_result = 1/3

    assert inspect.isfunction(reciprocal_function), (
        'TypeError for the output function of reciprocal() test. It must be a '
        'function')
    assert reciprocal_function(x_inputs, y_inputs)==expected_result, (
        'ValueError for the output function of the reciprocal() test. The '
        + 'output is incorrect')
    second_reciprocal = reciprocal(reciprocal_function)
    assert second_reciprocal(x_inputs, y_inputs)==(
        input_function(x_inputs, y_inputs)), (
        'ValueError for the output function of the reciprocal() test. The '
        + 'reciprocal of the reciprocal must be the initial function')

def test_reciprocal_x():
    """Check that the serial comb function returns a valid reciprocal
    function in the case of an proportional law function.

    GIVEN: a valid x function
    WHEN: the functions to get the reciprocal of a function is called
    THEN: the output function is the reciprocal function of the input one
    """
    input_function = lambda x, y: x
    reciprocal_function = reciprocal(input_function)
    x_inputs = np.array([0.5, 1, 2, 4 ])
    y_inputs = np.array([1, 5, 6, 10])
    expected_result = [2., 1., 0.5, 0.25]

    assert inspect.isfunction(reciprocal_function), (
        'TypeError for the output function of reciprocal() test. It must be a '
        'function')
    assert np.all(reciprocal_function(x_inputs, y_inputs)==expected_result), (
        'ValueError for the output function of the reciprocal() test. The '
        + 'output is incorrect')
    second_reciprocal = reciprocal(reciprocal_function)
    assert np.all(second_reciprocal(x_inputs, y_inputs)==(
        input_function(x_inputs, y_inputs))), (
        'ValueError for the output function of the reciprocal() test. The '
        + 'reciprocal of the reciprocal must be the initial function')

def test_reciprocal_one_over_x():
    """Check that the serial comb function returns a valid reciprocal
    function in the case of an inverse law function.

    GIVEN: a valid 1/x function
    WHEN: the functions to get the reciprocal of a function is called
    THEN: the output function is the reciprocal function of the input one
    """
    input_function = lambda x, y: 1/x
    reciprocal_function = reciprocal(input_function)
    x_inputs = np.array([0.5, 1, 2, 4 ])
    y_inputs = np.array([1, 5, 6, 10])
    expected_result = np.copy(x_inputs)

    assert inspect.isfunction(reciprocal_function), (
        'TypeError for the output function of reciprocal() test. It must be a '
        'function')
    assert np.all(reciprocal_function(x_inputs, y_inputs)==expected_result), (
        'ValueError for the output function of the reciprocal() test. The '
        + 'output is incorrect')
    second_reciprocal = reciprocal(reciprocal_function)
    assert np.all(second_reciprocal(x_inputs, y_inputs)==(
        input_function(x_inputs, y_inputs))), (
        'ValueError for the output function of the reciprocal() test. The '
        + 'reciprocal of the reciprocal must be the initial function')


def test_parallel_comb_single_function():
    """Check that the parallel comb function returns a valid function in the
    case of a single function (i.e. returns the input function).

    GIVEN: a list of functions with just one function
    WHEN: the function to perform the parallel comb is called
    THEN: the result of the parallel comb function is the proper function, in
    this case the input function.
    """
    singe_function = lambda x, y: x + y
    parallel_comb_function = parallel_comb([singe_function])
    x_inputs = np.array([1, 2, 4, 5])
    y_inputs = np.array([1, 5, 10, 15])
    expected_result = [2, 7, 14, 20] #Also output of the input function

    assert inspect.isfunction(parallel_comb_function), (
        'TypeError for the output of function of parallel_comb() test. It must '
        + 'be a function')
    assert np.all(parallel_comb_function(x_inputs, y_inputs)==expected_result), (
        'ValueError for the output of function of function of the '
        + 'parallel_comb() test. The output is incorrect')

def test_parallel_comb_two_functions():
    """Check that the parallel comb function returns a valid sum function in
    the case of two functions.

    GIVEN: a list of functions with two functions
    WHEN: the function to perform the parallel comb is called
    THEN: the result of the parallel comb function is a proper sum function.
    """
    first_function = lambda x, y: 1/x
    second_function = lambda x, y: 1/y
    parallel_comb_function = parallel_comb([first_function, second_function])
    x_inputs = np.array([1, 2, 4, 1])
    y_inputs = np.array([1, 3, 16, 9])
    expected_result = [0.5, 0.2, 0.05, 0.1]

    assert inspect.isfunction(parallel_comb_function), (
        'TypeError for the output of function of parallel_comb() test. It must '
        + 'be a function')
    assert np.all(parallel_comb_function(x_inputs, y_inputs)==expected_result), (
        'ValueError for the output of function of function of the '
        + 'parallel_comb() test. The output is incorrect')

def test_parallel_comb_three_functions():
    """Check that the parallel comb function returns a valid sum function in
    the case of three functions.

    GIVEN: a list of functions with three functions
    WHEN: the function to perform the parallel comb is called
    THEN: the result of the parallel comb function is a proper sum function.
    """
    first_function = lambda x, y: 5
    second_function = lambda x, y: 1/x
    third_function = lambda x, y: 1/y
    parallel_comb_function = parallel_comb([first_function, second_function,
                                        third_function])
    x_inputs = np.array([0.1, 0.8, 11.3])
    y_inputs = np.array([0.2, 1, 13.5])
    expected_result = [2., 0.5, 0.04]

    assert inspect.isfunction(parallel_comb_function), (
        'TypeError for the output of function of parallel_comb() test. It must '
        + 'be a function')
    assert np.all(parallel_comb_function(x_inputs, y_inputs)==expected_result), (
        'ValueError for the output of function of function of the '
        + 'parallel_comb() test. The output is incorrect')


################################
#Test mischellanous functions

def test_get_position_opening_bracket_single_cell():
    """Check that the function to find the position of the corresponding
    opening bracket, given the position of the closing bracket, in a string
    works properly in the case of just one cell.

    GIVEN: valid circuit diagram with just one cell and valid close bracket
    index
    WHEN: I call the function to divide the circuit diagram in cells
    THEN: the index found is the expected valid index of the correct opening
    bracket
    """
    diagram = '(R1)'
    i_end = 3
    position_bracket = get_position_opening_bracket(diagram, i_end)
    expected_result = 0

    assert isinstance(position_bracket, int), (
        'TypeError in output of get_position_opening_bracket(). Last '
        + 'opening bracket position must be an integer')
    assert position_bracket>=0, ('ValueError in output of '
        + 'get_position_opening_bracket(). Last opening bracket position '
        + 'must be non-negative')
    assert position_bracket==expected_result, (
        'ValueError for the output of the get_position_opening_bracket() '
        + 'test. It does not match the correct position')

def test_get_position_opening_bracket_nested_cells():
    """Check that the function to find the position of the corresponding
    opening bracket, given the position of the closing bracket, in a string
    works properly in the case of two nested cells.

    GIVEN: valid circuit diagram with two nested cells and valid close bracket
    index for the most nested one (the one that in the code would be the first
    one to be found)
    WHEN: I call the function to divide the circuit diagram in cells
    THEN: the index found is the expected valid index of the correct opening
    bracket
    """
    diagram = '(C1R2[R3])'
    i_end = 8
    position_bracket = get_position_opening_bracket(diagram, i_end)
    expected_result = 5

    assert isinstance(position_bracket, int), (
        'TypeError in output of get_position_opening_bracket(). Last '
        + 'opening bracket position must be an integer')
    assert position_bracket>=0, ('ValueError in output of '
        + 'get_position_opening_bracket(). Last opening bracket position '
        + 'must be non-negative')
    assert position_bracket==expected_result, (
        'ValueError for the output of the get_position_opening_bracket() '
        + 'test. It does not match the correct position')

def test_get_position_opening_bracket_complex():
    """Check that the function to find the position of the corresponding
    opening bracket, given the position of the closing bracket, in a string
    works properly in the case of multiple cells.

    GIVEN: valid circuit diagram with many cells and valid close bracket
    index for the first most nested one (the one that in the code would be
    the first one to be found)
    WHEN: I call the function to divide the circuit diagram in cells
    THEN: the index found is the expected valid index of the correct opening
    bracket
    """
    diagram = '(C1R2[R3Q4][R5C6])'
    i_end = 10
    position_bracket = get_position_opening_bracket(diagram, i_end)
    expected_result = 5

    assert isinstance(position_bracket, int), (
        'TypeError in output of get_position_opening_bracket(). Last '
        + 'opening bracket position must be an integer')
    assert position_bracket>=0, ('ValueError in output of '
        + 'get_position_opening_bracket(). Last opening bracket position '
        + 'must be non-negative')
    assert position_bracket==expected_result, (
        'ValueError for the output of the get_position_opening_bracket() '
        + 'test. It does not match the correct position')

def test_get_position_opening_bracket_inconsistency():
    """Check that the function to find the position of the corresponding
    opening bracket, given the position of the closing bracket, in a string
    raises an Exception with a certain message if the desired type of opening
    brackets cannot be found, due to the invalidity of the diagram.

    GIVEN: invalid circuit diagram with a missing bracket (thus inconsistent),
    and a valid
    WHEN: I call the function to divide the circuit diagram in cells
    THEN: the function raises an Exception with a message that states the
    impossibility to find the desired opening bracket
    """
    invalid_diagram = '(C1R2R3Q4][R5C6])' #Missing [ after the (, invalid
    i_end = 9
    with pytest.raises(Exception) as excinfo:
        _ = get_position_opening_bracket(invalid_diagram, i_end)
    message = excinfo.value.args[0]
    assert message==('StructuralError: Impossible to find the opening '
                     + 'bracket. Possible brackets inconsistency')


def test_get_string_empty():
    """Check that the output of get_string() is a valid joined string in the
    case of an empty list (i.e. the string will be empty).

    GIVEN: an empty list
    WHEN: I call the function to concatenate strings from a list of strings
    THEN: the output of get_string() is an empty string, as expected
    """
    empty_list = []
    joined_string = get_string(empty_list)
    expected_result = ''

    assert isinstance(joined_string, str), (
        'TypeError for output of get_string(): the output must be a string, '
        + 'not a ' + str(type(joined_string)))
    assert (joined_string==expected_result), (
        'ValueError for the output of get_string(): the output does not '
        + 'match the correct string')

def test_get_string_single_element():
    """Check that the output of get_string() is a valid joined string in the
    case of a list with just one string element.

    GIVEN: a list with just one string element
    WHEN: I call the function to concatenate strings from a list of strings
    THEN: the output of get_string() is the expected joined string, as
    expected
    """
    single_element_list = ['1']
    joined_string = get_string(single_element_list)
    expected_result = '1'

    assert isinstance(joined_string, str), (
        'TypeError for output of get_string(): the output must be a '
        + 'string, not a ' + str(type(joined_string)))
    assert (joined_string==expected_result), (
        'ValueError for the output of get_string(): the output does not '
        + 'match the correct string')

def test_get_string_many_element():
    """Check that the output of get_string() is a valid joined string in the
    case of a list with three string elements.

    GIVEN: a list with three one string elements
    WHEN: I call the function to concatenate strings from a list of strings
    THEN: the output of get_string() is the expected joined string, as
    expected
    """
    many_element_list = ['1', 'and', '2']
    joined_string = get_string(many_element_list)
    expected_result = '1\nand\n2'

    assert isinstance(joined_string, str), (
        'TypeError for output of get_string(): the output must be a '
        + 'string, not a ' + str(type(joined_string)))
    assert (joined_string==expected_result), (
        'ValueError for the output of get_string(): the output does not '
        + 'match the correct string')


##########################
#Test Circuit Class

def wrong_match_element_initial_circuit_final_parameters(initial_parameters,
                                                         final_parameters):
    """Find any incongruence between the elements of initial_parameters and
    final_parameters: all the non-constant elements of the initial circuit
    must be present in the final parameters_map with the same element name a
    key. No constant element of the initial circuit must be present in the
    final parameters_map and no element that is not present in the initial
    parameters must be present in the final parameters map. Used for testing.

    Parameters
    ----------
    initial_parameters : dict
        Input parameters map
    final_parameters : dict
        Final parameters map

    Returns
    -------
    wrong_elements : str
        String that contains any anomality about elements, separated by a
        whitespace
    """
    wrong_elements = ''
    final_elements = final_parameters.keys()
    if not set(final_elements).issubset(initial_parameters.keys()):
        wrong_elements += 'Extra element in the final parameters '
    else:
        for element, parameter in initial_parameters.items():
            if not parameter[1]:
                if not element in final_elements:
                    wrong_elements += element + ' '
            else:
                if element in final_elements:
                    wrong_elements += element + ' '
    return wrong_elements

def test_wrong_match_element_initial_final_parameters_no_element():
    """Check that the help function that finds the element mismatch between
    input parameters dictionaries and final parameters dictionaries works in
    the case of two empty dictionaries.
    All and only the initial parameters elements that are not constant must be
    in the final parameters elements.
    If no invalid match is detected, the returned string given by the function
    under test is empty.

    GIVEN: two empty dictionaries
    WHEN: I check if the final parameters elements are correctly set from the
    initial parameters elements
    THEN: no invalid final parameters elements detected
    """
    input_parameters_map = {}
    final_parameters_map = {}
    wrong_elements = wrong_match_element_initial_circuit_final_parameters(
        input_parameters_map, final_parameters_map)

    assert not wrong_elements, (
        'Bad match between non constant elements of the initial circuit and '
        + 'the final analysis parameter. ' + wrong_elements + 'not found. '
        + 'Cannot find any bad match because the dictionaries are both empty')

def test_wrong_match_element_initial_final_parameters_single_element():
    """Check that the help function that finds the element mismatch between
    input parameters dictionaries and final parameters dictionaries works in
    the case of a non constant element in the initial dictionary and the same
    element in the final dictonary.
    All and only the initial parameters elements that are not constant must be
    in the final parameters elements.
    If no invalid match is detected, the returned string given by the function
    under test is empty.

    GIVEN: a non constant element in the initial dictionary and the same
    element in the final dictonary
    WHEN: I check if the final parameters elements are correctly set from the
    initial parameters elements
    THEN: no invalid final parameters elements detected
    """
    input_parameters_map = {'R1': (1000., 0)}
    final_parameters_map = {'R1': 1000.}
    wrong_elements = wrong_match_element_initial_circuit_final_parameters(
        input_parameters_map, final_parameters_map)

    assert not wrong_elements, (
        'Bad match between non constant elements of the initial circuit and '
        + 'the final analysis parameter. ' + wrong_elements + 'not found. ')

def test_wrong_match_element_initial_final_parameters_two_elements():
    """Check that the help function that finds the element mismatch between
    input parameters dictionaries and final parameters dictionaries works in
    the case of both a non constant element a constant element in the initial
    dictionary and only the non constant element in the final dictonary.
    All and only the initial parameters elements that are not constant must be
    If no invalid match is detected, the returned string given by the function
    under test is empty.

    GIVEN: a non constant element  and a constant element in the initial
    dictionary and only the non constant element in the final dictonary
    WHEN: I check if the final parameters elements are correctly set from the
    initial parameters elements
    THEN: no invalid final parameters elements detected
    """
    input_parameters_map = {'C1': (1e-6, 0), 'Q2': ([1e-5, 0.76], 1)}
    final_parameters_map = {'C1': 1e-6}
    wrong_elements = wrong_match_element_initial_circuit_final_parameters(
        input_parameters_map, final_parameters_map)

    assert not wrong_elements, (
        'Bad match between non constant elements of the initial circuit and '
        + 'the final analysis parameter. ' + wrong_elements + 'not found. ')

def test_wrong_match_element_initial_final_parameters_missing_element():
    """Check that the help function that finds the element mismatch between
    input parameters dictionaries and final parameters dictionaries works in
    the case of two non constant elements in the initial dictionary and only
    one of them in the final dictonary.
    All and only the initial parameters elements that are not constant must be
    in the final parameters elements.
    If invalid matches (by element) are detected, the returned string given
    by the function under test contains the elements of the bad matches.

    GIVEN: a non constant element and a constant element in the initial
    dictionary and only one of them in the final dictonary
    WHEN: I check if the final parameters elements are correctly set from the
    initial parameters elements
    THEN: the missing element in the final parameters elements is detected
    """
    input_parameters_map = {'R1': (300., 0), 'R2': (100., 0)}
    final_parameters_map = {'R1': 200.}
    wrong_elements = wrong_match_element_initial_circuit_final_parameters(
        input_parameters_map, final_parameters_map)
    expected_result = 'R2 '

    assert wrong_elements==expected_result, (
        'Bad match between non constant elements of the initial circuit '
        + 'and the final analysis parameter. ' + wrong_elements + 'not '
        + 'found. Different invalid elements than the one expeted: '
        + expected_result)

def test_wrong_match_element_initial_final_parameters_extra_element():
    """Check that the help function that finds the element mismatch between
    input parameters dictionaries and final parameters dictionaries works in
    the case of one non constant elements and a constant one in the initial
    dictionary, while the final dictonary has the same non-constant element
    but also an entirely new element.
    All and only the initial parameters elements that are not constant must be
    in the final parameters elements.
    If invalid matches (by element) are detected, the returned string given
    by the function under test contains the elements of the bad matches.

    GIVEN: one non constant element and a constant one in the initial
    dictionary, while the final dictonary has the same non-constant element
    but also and an entirely new element
    WHEN: I check if the final parameters elements are correctly set from the
    initial parameters elements
    THEN: the extra element in the final parameters elements is detected as
    invalid
    """
    input_parameters_map = {'R1': (300., 0), 'R2': (100., 0)}
    final_parameters_map = {'R1': 300., 'C2': 100.}
    wrong_elements = wrong_match_element_initial_circuit_final_parameters(
        input_parameters_map, final_parameters_map)
    expected_result = 'Extra element in the final parameters '

    assert wrong_elements==expected_result, (
        'Bad match between non constant elements of the initial circuit '
        + 'and the final analysis parameter. ' + wrong_elements + 'not '
        + 'found. Different invalid elements than the one expeted: '
        + expected_result)

def test_wrong_match_element_initial_final_parameters_bad_match():
    """Check that the help function that finds the element mismatch between
    input parameters dictionaries and final parameters dictionaries works in
    the case of one non constant elements and a constant one in the initial
    dictionary, while the final dictonary has the same non-constant element
    but also an entirely new element.
    All and only the initial parameters elements that are not constant must be
    in the final parameters elements.
    If invalid matches (by element) are detected, the returned string given
    by the function under test contains the elements of the bad matches.

    GIVEN: one non constant element and a constant one in the initial
    dictionary, while the final dictonary has the the same elements (though
    only the non constant one should be there)
    WHEN: I check if the final parameters elements are correctly set from the
    initial parameters elements
    THEN: the constant element in the final parameters element is detected as
    invalid
    """
    input_parameters_map = {'R1': (300., 1), 'R2': (100., 0)}
    final_parameters_map = {'R1': 300., 'R2': 100.}
    wrong_elements = wrong_match_element_initial_circuit_final_parameters(
        input_parameters_map, final_parameters_map)
    expected_result = 'R1 '

    assert wrong_elements==expected_result, (
        'Bad match between non constant elements of the initial circuit '
        + 'and the final analysis parameter. ' + wrong_elements + 'not '
        + 'found. Different invalid elements than the one expeted: '
        + expected_result)


def wrong_match_parameter_initial_circuit_final_parameters(initial_parameters,
                                                           final_parameters):
    """Find any incongruence between the parameters of initial_parameters and
    final_parameters: all the non-constant parameter of the initial circuit
    must be present in the final parameters_map with the same element name a
    key. No constant parameter of the initial circuit must be present in the
    final parameters_map and no parameter that is not present in the initial
    parameter must be present in the final parameters map. Used for testing.

    Parameters
    ----------
    initial_parameters : dict
        Input parameters map
    final_parameters : dict
        Final parameters map

    Returns
    -------
    wrong_parameters : str
        String that contains any anomality about parameters, separated by a
        whitespace
    """
    wrong_parameters = ''
    #'set' does not accept nested lists, (Q's parameter case), so a convertion
    # to tuple is needed
    intitial_parameters_values = [
        tuple(parameter[0]) if isinstance(parameter[0], list) else parameter[0]
        for parameter in initial_parameters.values()]
    final_parameters_values = [
        tuple(parameter) if isinstance(parameter, list) else parameter
        for parameter in final_parameters.values()]

    if not set(final_parameters_values).issubset(intitial_parameters_values):
        wrong_parameters += 'Extra parameter in the final parameters '
    else:
        for element, parameter in initial_parameters.items():
            if not parameter[1]:
                if parameter[0] not in list(final_parameters.values()):
                    wrong_parameters += element + ' '
                elif parameter[0]!=final_parameters[element]:
                    wrong_parameters += element + ' '
            else:
                if parameter[0] in final_parameters.values():
                    wrong_parameters += element + ' '
    return wrong_parameters

def test_wrong_match_parameter_initial_final_parameters_no_element():
    """Check that the help function that finds the parameter mismatch between
    input parameters dictionaries and final parameters dictionaries works in
    the case of two empty dictionaries.
    All and only the initial parameters that are not constant must be in the
    final parameters.
    If no invalid match is detected, the returned string given by the function
    under test is empty.

    GIVEN: two empty dictionaries
    WHEN: I check if the final parameters are correctly set from the initial
    parameters parameters
    THEN: no invalid final parameters detected
    """
    input_parameters_map = {}
    final_parameters_map = {}
    wrong_parameter = wrong_match_parameter_initial_circuit_final_parameters(
        input_parameters_map, final_parameters_map)

    assert not wrong_parameter, (
        'Bad match between non constant parameters of the initial circuit '
        + 'and the final analysis parameter. ' + wrong_parameter + 'not '
        + 'found. Cannot find any bad match because the dictionaries are both '
        + 'empty')

def test_wrong_match_parameter_initial_final_parameters_single_element():
    """Check that the help function that finds the parameter mismatch between
    input parameters dictionaries and final parameters dictionaries works in
    the case of a non constant parameter in the initial dictionary and the
    same parameter in the final dictonary.
    All and only the initial parameters that are not constant must be
    in the final parameters.
    If no invalid match is detected, the returned string given by the function
    under test is empty.

    GIVEN: a non constant parameter in the initial dictionary and the same
    parameter (with the same element name) in the final dictonary
    WHEN: I check if the final parameters are correctly set from the
    initial parameters
    THEN: no invalid final parameters detected
    """
    input_parameters_map = {'R1': (1000., 0)}
    final_parameters_map = {'R1': 1000.}
    wrong_parameter= wrong_match_parameter_initial_circuit_final_parameters(
        input_parameters_map, final_parameters_map)

    assert not wrong_parameter, (
        'Bad match between non constant parameters of the initial circuit '
        + 'and the final analysis parameter. ' + wrong_parameter + 'not '
        + 'found. ')

def test_wrong_match_parameter_initial_final_parameters_two_elements():
    """Check that the help function that finds the parameter mismatch between
    input parameters dictionaries and final parameters dictionaries works in
    the case of both a non constant parameter a constant parameter in the
    initial dictionary and only the non constant parameter in the final
    dictonary.
    All and only the initial parameters that are not constant must be
    in the final parameters.
    If no invalid match is detected, the returned string given by the function
    under test is empty.

    GIVEN: a non constant parameter and a constant parameter in the initial
    dictionary and only the non constant parameter in the final dictonary
    (with the same element names)
    WHEN: I check if the final parameters are correctly set from the
    initial parameters
    THEN: no invalid final parameters detected
    """
    input_parameters_map = {'C1': (1e-6, 0), 'Q2': ([1e-5, 0.76], 1)}
    final_parameters_map = {'C1': 1e-6}
    wrong_parameter = wrong_match_parameter_initial_circuit_final_parameters(
        input_parameters_map, final_parameters_map)

    assert not wrong_parameter, (
        'Bad match between non constant parameters of the initial circuit '
        + 'and the final analysis parameter. ' + wrong_parameter + 'not '
        + 'found. ')

def test_wrong_match_parameter_initial_final_parameters_missing_parameter():
    """Check that the help function that finds the parameter mismatch between
    input parameters dictionaries and final parameters dictionaries works in
    the case of two non constant parameters in the initial dictionary and only
    one of them in the final dictonary.
    All and only the initial parameters that are not constant must be
    in the final parameters.
    If invalid matches (by parameter) are detected, the returned string given
    by the function under test contains the correspondant elements of the bad
    matches.

    GIVEN: a non constant parameter and a constant parameter in the initial
    dictionary and only one of them in the final dictonary (with the same
    element name)
    WHEN: I check if the final parameters are correctly set from the
    initial parameters
    THEN: the missing parameter in the final parameters is detected
    """
    input_parameters_map = {'R1': (300., 0), 'R2': (100., 0)}
    final_parameters_map = {'R1': 300.}
    wrong_parameters = wrong_match_parameter_initial_circuit_final_parameters(
        input_parameters_map, final_parameters_map)
    expected_result = 'R2 '

    assert wrong_parameters==expected_result, (
        'Bad match between non constant parameters of the initial circuit '
        + 'and the final analysis parameter. ' + wrong_parameters + 'not '
        + 'found. Different invalid parameters than the one expeted: '
        + expected_result)

def test_wrong_match_parameter_initial_final_parameters_extra_parameter():
    """Check that the help function that finds the parameter mismatch between
    input parameters dictionaries and final parameters dictionaries works in
    the case of one non constant parameters and a constant one in the initial
    dictionary, while the final dictonary has the same non-constant parameter
    but also an entirely new parameter (with the same element of the constant
    element).
    All and only the initial parameters that are not constant must be
    in the final parameters.
    If invalid matches (by parameter) are detected, the returned string given
    by the function under test contains the correspondant elements of the bad
    matches.

    GIVEN: one non constant parameter and a constant one in the initial
    dictionary, while the final dictonary has the same non-constant parameter
    (with the same element name) but also and an entirely new parameter (with
    the same element of the constant element)
    WHEN: I check if the final parameters are correctly set from the
    initial parameters
    THEN: the extra parameter in the final parameters is detected as
    invalid
    """
    input_parameters_map = {'R1': (300., 0), 'R2': (100., 1)}
    final_parameters_map = {'R1': 300., 'R2': 200.}
    wrong_parameters = wrong_match_parameter_initial_circuit_final_parameters(
        input_parameters_map, final_parameters_map)
    expected_result = 'Extra parameter in the final parameters '

    assert wrong_parameters==expected_result, (
        'Bad match between non constant parameters of the initial circuit '
        + 'and the final analysis parameter. ' + wrong_parameters + 'not '
        + 'found. Different invalid parameters than the one expeted: '
        + expected_result)

def test_wrong_match_parameter_initial_final_parameters_bad_match():
    """Check that the help function that finds the parameter mismatch between
    input parameters dictionaries and final parameters dictionaries works in
    the case of one non constant parameter and a constant one in the initial
    dictionary, while the final dictonary has the same non-constant parameter
    but also an entirely new parameter.
    All and only the initial parameters that are not constant must be
    in the final parameters.
    If invalid matches (by parameter) are detected, the returned string given
    by the function under test contains the correspondant elements of the bad
    matches.

    GIVEN: one non constant parameter and a constant one in the initial
    dictionary, while the final dictonary has the the same parameters (though
    only the non constant one should be there)
    WHEN: I check if the final parameters are correctly set from the
    initial parameters
    THEN: the constant parameter in the final parameters is detected as
    invalid
    """
    input_parameters_map = {'R1': (300., 1), 'R2': (100., 0)}
    final_parameters_map = {'R1': 300., 'R2': 100.}
    wrong_parameters = wrong_match_parameter_initial_circuit_final_parameters(
        input_parameters_map, final_parameters_map)
    expected_result = 'R1 '

    assert wrong_parameters==expected_result, (
        'Bad match between non constant parameters of the initial circuit '
        + 'and the final analysis parameters. ' + wrong_parameters + 'not '
        + 'found. Different invalid parameters than the one expeted: '
        + expected_result)

def test_wrong_match_parameter_initial_final_parameters_duplicates():
    """Check that the help function that finds the parameter mismatch between
    input parameters dictionaries and final parameters dictionaries works in
    the case of two non constant parameters in the initial dictionary and two
    parameters in the final dictonary, but even tough the elements are correct,
    the parameters in the final parameters are both the valid parameter of
    the first initial parameters, thus leaving the second parameters (that
    should be in the final parameters too since it is not constant) behind.
    All and only the initial parameters that are not constant must be
    in the final parameters.
    If invalid matches (by parameter) are detected, the returned string given
    by the function under test contains the correspondant elements of the bad
    matches.

    GIVEN: two non constant parameters in the initial dictionary and two
    parameters in the final dictonary, but even tough the elements are correct,
    the parameters in the final parameters are both the valid parameter of
    the first initial parameters
    WHEN: I check if the final parameters are correctly set from the
    initial parameters
    THEN: the second parameter in the final parameters is detected as invalid
    """
    input_parameters_map = {'C1': (1e-6, 0), 'C2': (2e-6, 0)}
    final_parameters_map = {'C1': 1e-6, 'C2': 1e-6}
    wrong_parameter = wrong_match_parameter_initial_circuit_final_parameters(
        input_parameters_map, final_parameters_map)
    expected_result = 'C2 '

    assert wrong_parameter==expected_result, (
        'Bad match between non constant parameters of the initial circuit '
        + 'and the final analysis parameter. ' + wrong_parameter + 'not '
        + 'found. Different invalid parameters than the one expeted: '
        + expected_result)


def generate_valid_circuit_resistor():
    """Generate an AnalysisCircuit object of a circuit with one valid non
    constant resistor element.
    """
    diagram = '(R1)'
    parameter_map = {'R1': (1000., 0)}
    resistor_circuit = Circuit(diagram, parameter_map)
    return resistor_circuit

@pytest.fixture
def valid_circuit_resistor():
    """Fixture for the single resistor Circuit."""
    return generate_valid_circuit_resistor()

def test_generate_analyzed_circuit_circuit_resistor(valid_circuit_resistor):
    """Check that the generate_analyzed_circuit() method return a valid
    AnalysisCircuit instance in the case of a single resistor circuit.

    GIVEN: a valid initial circuit of a single resistor.
    WHEN: the function to generate the AnalisysCircuit object to analyze the
    circuit is called
    THEN: the output is a valid AnalysisCircuit instance.
    """
    analyzed_circuit = valid_circuit_resistor.generate_analyzed_circuit()

    caller = 'generate_analyzed_circuit()'
    assert isinstance(analyzed_circuit, AnalisysCircuit), (
        'TyperError for output of ' + caller + ' method. It must be an '
        + 'instance of the \'AnalisysCircuit\' class')

    diagram_analyzed_circuit = analyzed_circuit.circuit_diagram
    assert isinstance(diagram_analyzed_circuit, str), (
        'TypeError for the circuit diagram of the output of ' + caller
        + ' It must be a string')
    assert inspect.isfunction(analyzed_circuit.impedance), (
        'TypeError for the final impedance of the output of ' + caller
        + '. It must be a function')

    parameters_map = analyzed_circuit.parameters_map
    assert isinstance(parameters_map, dict), (
        'TypeError for the parameters map of the output of ' + caller
        + '. It must be a dictionary')
    initial_parameters_map = valid_circuit_resistor.parameters_map
    wrong_elements = wrong_match_element_initial_circuit_final_parameters(
        initial_parameters_map, parameters_map)
    assert not wrong_elements, (
        'Bad match between non constant elements of the initial circuit and '
        + 'the final analysis parameter. ' + wrong_elements + 'not found')
    wrong_parameters = wrong_match_parameter_initial_circuit_final_parameters(
        initial_parameters_map, parameters_map)
    assert not wrong_parameters, (
        'Bad match between parameters of the initial circuit and the final '
        + 'analysis parameter. Parameter of element ' + wrong_elements
        + 'not found')

def generate_valid_circuit_rc():
    """Generate an AnalysisCircuit object of a circuit with one valid constant
    resistor element and a valid non-constant capacitor element.
    """
    diagram = '(R1C2)'
    parameter_map = {'R1': (100., 1), 'C2': (1e-6, 0)}
    rc_circuit = Circuit(diagram, parameter_map)
    return rc_circuit

@pytest.fixture
def valid_circuit_rc():
    """Fixture for the RC Circuit."""
    return generate_valid_circuit_rc()

def test_generate_analyzed_circuit_circuit_rc(valid_circuit_rc):
    """Check that the generate_analyzed_circuit() method return a valid
    AnalysisCircuit instance in the case of a RC circuit.

    GIVEN: a valid initial circuit of a constant resistor and a non-constant
    capacitor in series.
    WHEN: the function to generate the AnalisysCircuit object to analyze the
    circuit is called
    THEN: the output is a valid AnalysisCircuit instance.
    """
    analyzed_circuit = valid_circuit_rc.generate_analyzed_circuit()

    caller = 'generate_analyzed_circuit()'
    assert isinstance(analyzed_circuit, AnalisysCircuit), (
        'TyperError for output of ' + caller + ' method. It must be an '
        + 'instance of the \'AnalisysCircuit\' class')

    diagram_analyzed_circuit = analyzed_circuit.circuit_diagram
    assert isinstance(diagram_analyzed_circuit, str), (
        'TypeError for the circuit diagram of the output of ' + caller
        + ' It must be a string')
    assert inspect.isfunction(analyzed_circuit.impedance), (
        'TypeError for the final impedance of the output of ' + caller
        + '. It must be a function')

    parameters_map = analyzed_circuit.parameters_map
    assert isinstance(parameters_map, dict), (
        'TypeError for the parameters map of the output of ' + caller
        + '. It must be a dictionary')
    initial_parameters_map = valid_circuit_rc.parameters_map
    wrong_elements = wrong_match_element_initial_circuit_final_parameters(
        initial_parameters_map, parameters_map)
    assert not wrong_elements, (
        'Bad match between non constant elements of the initial circuit and '
        + 'the final analysis parameter. ' + wrong_elements + 'not found')
    wrong_parameters = wrong_match_parameter_initial_circuit_final_parameters(
        initial_parameters_map, parameters_map)
    assert not wrong_parameters, (
        'Bad match between parameters of the initial circuit and the final '
        + 'analysis parameter. Parameter of element ' + wrong_elements
        + 'not found')

def generate_valid_circuit_complex():
    """Generate an AnalysisCircuit object of a circuit with many valid
    constant and non-constant elements.
    """
    diagram = '(R1C2[R3Q4])'
    parameter_map = {'R1': (100., 0), 'C2': (1e-6, 0), 'R3': (10000., 1),
                     'Q4': ([1e-5, 0.86], 0)}
    complex_circuit = Circuit(diagram, parameter_map)
    return complex_circuit

@pytest.fixture
def valid_circuit_complex():
    """Fixture for the many elements Circuit."""
    return generate_valid_circuit_complex()

def test_generate_analyzed_circuit_circuit_complex(valid_circuit_complex):
    """Check that the generate_analyzed_circuit() method return a valid
    AnalysisCircuit instance in the case of a circuit with many valid
    elements.

    GIVEN: a valid initial circuit of many valid constant and non-constant
    elements
    WHEN: the function to generate the AnalisysCircuit object to analyze the
    circuit is called
    THEN: the output is a valid AnalysisCircuit instance.
    """
    analyzed_circuit = valid_circuit_complex.generate_analyzed_circuit()

    caller = 'generate_analyzed_circuit()'
    assert isinstance(analyzed_circuit, AnalisysCircuit), (
        'TyperError for output of ' + caller + ' method. It must be an '
        + 'instance of the \'AnalisysCircuit\' class')

    diagram_analyzed_circuit = analyzed_circuit.circuit_diagram
    assert isinstance(diagram_analyzed_circuit, str), (
        'TypeError for the circuit diagram of the output of ' + caller
        + ' It must be a string')
    assert inspect.isfunction(analyzed_circuit.impedance), (
        'TypeError for the final impedance of the output of ' + caller
        + '. It must be a function')

    parameters_map = analyzed_circuit.parameters_map
    assert isinstance(parameters_map, dict), (
        'TypeError for the parameters map of the output of ' + caller
        + '. It must be a dictionary')
    initial_parameters_map = valid_circuit_complex.parameters_map
    wrong_elements = wrong_match_element_initial_circuit_final_parameters(
        initial_parameters_map, parameters_map)
    assert not wrong_elements, (
        'Bad match between non constant elements of the initial circuit and '
        + 'the final analysis parameter. ' + wrong_elements + 'not found')
    wrong_parameters = wrong_match_parameter_initial_circuit_final_parameters(
        initial_parameters_map, parameters_map)
    assert not wrong_parameters, (
        'Bad match between parameters of the initial circuit and the final '
        + 'analysis parameter. Parameter of element ' + wrong_elements
        + 'not found')

def test_generate_analyzed_circuit_circuit_extra_parameter():
    """Check that the generate_analyzed_circuit() method return an invalid
    AnalysisCircuit instance in the case of a circuit with an extra parameter
    in the initial parameters dictionary.

    GIVEN: an valid initial circuit with an extra non-constant parameter in
    the initial parameters dictionary
    WHEN: the function to generate the AnalisysCircuit object to analyze the
    circuit is called
    THEN: the output is an AnalysisCircuit that is missing the extra
    parameter.
    """
    diagram = '(R1)'
    bad_match_parameter_map = {'R1': (100., 1), 'C2': (1e-6, 0)} #Extra C2
    bad_match_circuit = Circuit(diagram, bad_match_parameter_map)
    analyzed_circuit = bad_match_circuit.generate_analyzed_circuit()
    expected_result = 'C2 '

    caller = 'generate_analyzed_circuit()'
    assert isinstance(analyzed_circuit, AnalisysCircuit), (
        'TyperError for output of ' + caller + ' method. It must be an '
        + 'instance of the \'AnalisysCircuit\' class')

    diagram_analyzed_circuit = analyzed_circuit.circuit_diagram
    assert isinstance(diagram_analyzed_circuit, str), (
        'TypeError for the circuit diagram of the output of ' + caller
        + ' It must be a string')
    assert inspect.isfunction(analyzed_circuit.impedance), (
        'TypeError for the final impedance of the output of ' + caller
        + '. It must be a function')

    parameters_map = analyzed_circuit.parameters_map
    assert isinstance(parameters_map, dict), (
        'TypeError for the parameters map of the output of ' + caller
        + '. It must be a dictionary')
    initial_parameters_map = bad_match_circuit.parameters_map
    wrong_elements = wrong_match_element_initial_circuit_final_parameters(
        initial_parameters_map, parameters_map)
    assert wrong_elements==expected_result, (
        'Bad match between non constant elements of the initial circuit and '
        + 'the final analysis parameter. ' + wrong_elements + 'not found. '
        + 'Invalid elements fpund differs from the expected ones: '
        + expected_result)
    wrong_parameters = wrong_match_parameter_initial_circuit_final_parameters(
        initial_parameters_map, parameters_map)
    assert wrong_parameters==expected_result, (
        'Bad match between parameters of the initial circuit and the final '
        + 'analysis parameter. Parameter of element ' + wrong_elements
        + 'not found. Invalid elements fpund differs from the expected ones: '
        + expected_result)

def test_generate_analyzed_circuit_no_closing_bracket():
    """Check that the generate_analyzed_circuit() method raises an Exception
    with a certain message in the case of a circuit with a diagram with no
    closing brackets.

    GIVEN: an invalid initial circuit with a diagram with no closing brackets
    (invalid diagram)
    WHEN: the function to generate the AnalisysCircuit object to analyze the
    circuit is called
    THEN: the function raises an Exception with a message that states the
    invalidity of the diagram
    """
    invalid_diagram = '(R1' #No closing bracket, invalid
    parameter_map = {'R1': (300., 0)}
    invalid_circuit = Circuit(invalid_diagram, parameter_map)

    with pytest.raises(Exception) as excinfo:
        _ = invalid_circuit.generate_analyzed_circuit()
    message = excinfo.value.args[0]
    assert message==('InputError: impossible to find any closing bracket in '
                     + 'the diagram')

def test_generate_analyzed_circuit_inconsistent_opening_brackets():
    """Check that the generate_analyzed_circuit() method raises an Exception
    with a certain message in the case of a circuit with a diagram with at
    least an inconsistent pair of brackets.

    GIVEN: an invalid initial circuit with a diagram with an inconsistent
    pair of brackets (invalid diagram)
    WHEN: the function to generate the AnalisysCircuit object to analyze the
    circuit is called
    THEN: the function raises an Exception with a message that states the
    invalidity of the diagram
    """
    invalid_diagram = '(R1C2])' #Inconsistent brackets, invalid
    parameter_map = {'R1': (300., 0), 'C2': (1e-6, 1)}
    invalid_circuit = Circuit(invalid_diagram, parameter_map)

    with pytest.raises(Exception) as excinfo:
        _ = invalid_circuit.generate_analyzed_circuit()
    message = excinfo.value.args[0]
    assert message==('StructuralError: Impossible to find the opening '
                     + 'bracket. Possible brackets inconsistency')


def test_get_parameters_info_circuit_resistor():
    """Check that the output of get_parameters_info() is the desired string
    in the case of a circuit with just one non-constant resistor.

    GIVEN: a valid inital circuit (initial error included) with just one
    resistor.
    WHEN: I call the function to get all the initial parameters information
    THEN: the output is string containing all the desired information
    """
    resistor_circuit = generate_valid_circuit_resistor()
    resistor_circuit.error = 225.8
    parameters_info = resistor_circuit.get_parameters_info()
    expected_result = 'R1: 1000.0\nError: 225.8000'

    assert isinstance(parameters_info, str), (
        'TypeError for output of get_parameters_info(): the output '
        + 'must be a string, not a ' + str(type(parameters_info)))
    assert parameters_info==expected_result, (
        'ValueError for output of get_parameters_info(): the output '
        + 'is incorrect')

def test_get_parameters_info_circuit_rc():
    """Check that the output of get_parameters_info() is the desired string
    in the case of a circuit with one constant resistor and a non-constant
    capacitor.

    GIVEN: a valid inital circuit (initial error included) with one constant
    resistor and a non-constant capacitor.
    WHEN: I call the function to get all the initial parameters information
    THEN: the output is string containing all the desired information
    """
    rc_circuit = generate_valid_circuit_rc()
    rc_circuit.error = 1247.3
    parameters_info = rc_circuit.get_parameters_info()
    expected_result = 'R1: 100.0 (constant)\nC2: 1e-06\nError: 1247.3000'

    assert isinstance(parameters_info, str), (
        'TypeError for output of get_parameters_info(): the output '
        + 'must be a string, not a ' + str(type(parameters_info)))
    assert parameters_info==expected_result, (
        'ValueError for output of get_parameters_info(): the output '
        + 'is incorrect')

def test_get_parameters_info_circuit_complex():
    """Check that the output of get_parameters_info() is the desired string
    in the case of a circuit with many constant non-constant elements.

    GIVEN: a valid inital circuit (initial error included) with many constant
    non-constant elements.
    WHEN: I call the function to get all the initial parameters information
    THEN: the output is string containing all the desired information
    """
    complex_circuit = generate_valid_circuit_complex()
    complex_circuit.error = 337.45
    parameters_info = complex_circuit.get_parameters_info()
    expected_result = ('R1: 100.0\nC2: 1e-06\nR3: 10000.0 (constant)\n'
                      + 'Q4: 1e-05, 0.86\nError: 337.4500')

    assert isinstance(parameters_info, str), (
        'TypeError for output of get_parameters_info(): the output '
        + 'must be a string, not a ' + str(type(parameters_info)))
    assert parameters_info==expected_result, (
        'ValueError for output of get_parameters_info(): the output '
        + 'is incorrect')


def invalid_elements_type(element_list):
    """Given the elements in the circuit, return any object that is not a
    2-length string. Used for testing.

    Parameters
    ----------
    elements_circuit : list
        List of the elements in the circuit

    Returns
    -------
    wrong_type : str
        String that contains all the invalid elements, separated by a
        whitespace
    wrong_type_index : list
        List of indexes of the invalid invalid elements in the list
    """
    wrong_types = ''
    wrong_types_index = []
    for i, element in enumerate(element_list):
        if not isinstance(element, str):
            wrong_types+= str(element) + ' '
            wrong_types_index.append(i)
        elif len(element)!=2:
            wrong_types += str(element) + ' '
            wrong_types_index.append(i)
    return wrong_types, wrong_types_index

def test_invalid_elements_type_no_element():
    """Check that the help function to find the elements with the wrong type
    works on an empty list.
    If no invalid element is detected, the returned string given by the
    function under test is empty.

    GIVEN: an empty list
    WHEN: I check if there are invalid elements inside the list
    THEN: no invalid element is found
    """
    no_element = []
    wrong_types, wrong_types_index = invalid_elements_type(no_element)

    assert not wrong_types, (
        'TypeError for element(s) number ' + str(wrong_types_index) + ' '
        + wrong_types + ' in the empty list from invalid_elements_type().'
        + 'Elements can only be strings')

def test_invalid_elements_type_two_elements():
    """Check that the help function to find the elements with the wrong type
    works on a list of strings.
    If no invalid element is detected, the returned string given by the
    function under test is empty.

    GIVEN: a list of two strings, with right type and length
    WHEN: I check if there are invalid elements inside the list
    THEN: no invalid element type is found
    """
    two_elements = ['C1', 'CC']
    wrong_types, wrong_types_index = invalid_elements_type(two_elements)

    assert not wrong_types, (
        'TypeError for element(s) number ' + str(wrong_types_index) + ' '
        + wrong_types + ' in ' + str(two_elements)
        + ' from invalid_elements_type(). Elements can only be strings')

def test_invalid_elements_type_three_elements():
    """Check that the help function to find the elements with the wrong type
    works on a list of strings, with an element that is not a circuit element.
    If no invalid element is detected, the returned string given by the
    function under test is empty.

    GIVEN: a list of three strings, with right type and length
    WHEN: I check if there are invalid elements inside the list
    THEN: no invalid element type is found
    """
    three_elements = ['Q1', 'C2', '&w']
    wrong_types, wrong_types_index = invalid_elements_type(three_elements)

    assert not wrong_types, (
        'TypeError for element(s) number ' + str(wrong_types_index) + ' '
        + wrong_types + ' in ' + str(three_elements)
        + ' from invalid_elements_type(). Elements can only be strings')

def test_invalid_elements_type_wrong_element():
    """Check that the help function to find the elements with the wrong type
    works on a list of strings, with the first three elements that have a
    wrong type or length (two of them are not a string, and the third one is
    only 1 char long).
    If invalid elements are detected, the returned string given by the
    function under test contains the correspondant elements of the bad
    matches.

    GIVEN: a list of four objects, with only the last one that has a right
    type and length
    WHEN: I check if there are invalid elements inside the list
    THEN: the first three elements are detected as invalid
    """
    three_elements = [1.2, ['C2'], 'R', 'R4']
    expected_result = '1.2 [\'C2\'] R '
    wrong_types, wrong_types_index = invalid_elements_type(three_elements)

    assert wrong_types==expected_result, (
        'TypeError for element(s) number ' + str(wrong_types_index) + ' '
        + wrong_types + ' in ' + str(three_elements)
        + ' from invalid_elements_type(). The wrong element types are '
        + 'different from the expected: ' + str(expected_result))


def invalid_elements_character(elements_circuit):
    """Given an element list, return any character that as a fist character
    invalid, i.e. any outside R, C, Q, or as a second character invalid, i.e.
    not numerical. Used for testing.

    Parameters
    ----------
    elements_circuit : list
        List of the elements in the circuit that will figure in the fit

    Returns
    -------
    wrong_char : str
        String that contains all the invalid elements, separated by a
        whitespace
    wrong_char_index : list
        List of indexes of the invalid invalid elements in the list
    """
    wrong_char = ''
    wrong_char_index = []
    for i, element in enumerate(elements_circuit):
        if (element[0] not in {'R', 'C', 'Q'} or not element[1].isnumeric()):
            wrong_char += str(element) + ' '
            wrong_char_index.append(i)
        else:
            for j, other_element in enumerate(elements_circuit[i+1:]):
                if element[1]==other_element[1]:
                    wrong_char += ('(\'' + str(element) + '\', \''
                                   + str(other_element) + '\')')
                    wrong_char_index.append((i, j+i+1))
    return wrong_char, wrong_char_index

def test_invalid_elements_characters_no_element():
    """Check that the help function to find the elements with the wrong letter
    or number works on an empty list.
    If no invalid character is detected, the returned string and list given
    by the function under test are empty.

    GIVEN: an empty list
    WHEN: I check if there are invalid characters inside the element of the
    list
    THEN: no invalid element is found
    """
    no_element = []
    wrong_char, wrong_char_index = invalid_elements_character(no_element)

    assert not wrong_char, (
        'StructuralError for element(s) number '
        + str(wrong_char_index) + ' ' + wrong_char + ' in '
        + 'the empty list in invalid_elements_char_letter(). All '
        + 'elements must begin with a letter among \'C\', \'R\' ' + 'and '
        + '\'Q\' and must end with a natural number and each element '
        + 'number must be uinque')

def test_invalid_elements_characters_one_element():
    """Check that the help function to find the elements with the wrong letter
    or number works on a list with one valid element.
    If no invalid character is detected, the returned string and list given
    by the function under test are empty.

    GIVEN: an list of an string of length 2 that is a valid elements
    WHEN: I check if there are invalid characters inside the element of the
    list
    THEN: no invalid element is found
    """
    one_element = ['R1']
    wrong_char, wrong_char_index = invalid_elements_character(one_element)

    assert not wrong_char, (
        'StructuralError for element(s) number '
        + str(wrong_char_index) + ' ' + wrong_char + ' in ' + str(one_element)
        + 'in invalid_elements_char_letter(). All elements must begin with'
        + 'a letter among \'C\', \'R\' and \'Q\' and must end with a natural'
        + 'number and each element number must be uinque')

def test_invalid_elements_characters_three_elements():
    """Check that the help function to find the elements with the wrong letter
    or number works on a list with three valid elements.
    If no invalid character is detected, the returned string and list given
    by the function under test are empty.

    GIVEN: an list of three strings of length 2 with only valid elements
    WHEN: I check if there are invalid characters inside the element of the
    list
    THEN: no invalid element is found
    """
    three_elements = ['Q1', 'C2', 'R3']
    wrong_char, wrong_char_index = invalid_elements_character(three_elements)

    assert not wrong_char, (
        'StructuralError for element(s) number '
        + str(wrong_char_index) + ' ' + wrong_char + ' in ' + str(three_elements)
        + 'in invalid_elements_char_letter(). All elements must begin with'
        + 'a letter among \'C\', \'R\' and \'Q\' and must end with a natural'
        + 'number and each element number must be uinque')

def test_invalid_elements_type_invalid_characters():
    """Check that the help function to find the elements with the wrong letter
    or number works on a list with three elements, of which only the first one
    is valid.
    If invalid characters are detected, the returned string contains the
    invalid characters, while the returned list contains their index in the
    string.

    GIVEN: an list of three strings of length 2 with only valid element, the
    first one
    WHEN: I check if there are invalid characters inside the element of the
    list
    THEN: only the last two elements are detected as invalid
    """
    three_elements = ['R1', '1C', 'r3']
    expected_result = '1C r3 '
    wrong_char, wrong_char_index = invalid_elements_character(three_elements)

    assert wrong_char==expected_result, (
        'StructuralError for element(s) number ' + str(wrong_char_index) + ' '
        + wrong_char + ' in ' + str(three_elements)
        + 'in invalid_elements_char_letter(). The elements with wrong'
        + 'characters are different from the expected: '
        + str(expected_result))

def remove_elements(elements_list, diagram):
    """Given an element list of a circuit diagram and the diagram itself,
    removes th elements from the diagram. Used for testing.

    Parameters
    ----------
    elements_list : list
        List of the elements in the circuit
    diagram: str
        Diagram of a circuit

    Returns
    -------
    diagram : str
        Diagram filtered from the element in the list
    """
    for element in elements_list:
        diagram = diagram.replace(element, '')
    return diagram


def test_remove_elements_empty_diagram():
    """Check that the help function to remove the elements from a diagram
    works on an empty diagram.

    GIVEN: the circuit diagram is an empty one and the element list is valid
    (is empty)
    WHEN: I remove all the valid elements reported in a list
    THEN: the diagrams contains only brackets, invalid charaters or undetected
    elements
    """
    empty_diagram = ''
    elements_list = []
    replaced_diagram = remove_elements(elements_list, empty_diagram)

    assert set(replaced_diagram).issubset({'(', ')', '[', ']'}), (
        'StructuralError for the output of '
        + 'remove_elements(). Cannot find extra characters because they are'
        + 'both empty')

def test_remove_elements_one_element():
    """Check that the help function to remove the elements from a diagram
    works on a single element diagram.

    GIVEN: the circuit diagram is valid, with a single element and the
    element list is valid
    WHEN: I remove all the valid elements reported in a list
    THEN: the diagrams contains only brackets
    """
    diagram = '(R1)'
    elements_list = ['R1']

    replaced_diagram = remove_elements(elements_list, diagram)
    assert set(replaced_diagram).issubset({'(', ')', '[', ']'}), (
        'StructuralError for the output of remove_elements(). Extra '
        + 'characters found, bad removal')

def test_remove_elements_many_elements():
    """Check that the help function to remove the elements from a diagram
    works on a many element diagram.

    GIVEN: the circuit diagram is valid, with many elements and the
    element list is valid
    WHEN: I remove all the valid elements reported in a list
    THEN: the diagrams contains only brackets
    """
    diagram = '(R1C2[Q3R4])'
    elements_list = ['R1', 'C2', 'Q3', 'R4']
    replaced_diagram = remove_elements(elements_list, diagram)

    assert set(replaced_diagram).issubset({'(', ')', '[', ']'}), (
        'StructuralError for the output of remove_elements(). Extra '
        + 'characters found, bad removal')

def test_remove_elements_wrong_list():
    """Check that the help function fails to remove all the elements from
    a diagram on a two elements diagram if the element list is invalid.

    GIVEN: the circuit diagram is valid, with a two elements but the
    element list is invalid
    WHEN: I remove all the valid elements reported in a list
    THEN: the diagrams contains some undetected elements other than only
    brackets
    """
    diagram = '(R1C2)'
    wrong_elements_list = ['R1'] #One element is missing
    replaced_diagram = remove_elements(wrong_elements_list, diagram)
    expected_result = '(C2)'

    assert replaced_diagram==expected_result, (
        'StructuralError for the output of remove_elements(). Extra '
        + 'characters found, bad removal')

def test_remove_elements_invalid_diagram():
    """Check that the help function fails to remove all the elements from
    a diagram if the diagram contains invalid elements.

    GIVEN: the circuit diagram is invalid
    WHEN: I remove all the valid elements reported in a list
    THEN: the diagrams contains some undetected elements other than only
    brackets
    """
    invalid_diagram = '(R1C2S3)' #One invalid element: it starts with S
    elements_list = ['R1', 'C2']
    replaced_diagram = remove_elements(elements_list, invalid_diagram)
    expected_result = '(S3)'

    assert replaced_diagram==expected_result, (
        'StructuralError for the output of remove_elements(). Invalid '
        + 'element not found in the final diagram, bad removal')


def test_list_elements_circuit_empty_string():
    """Check if the function that list the elements inside a diagram works on
    an empty diagram.

    GIVEN: the circuit diagram is an empty one
    WHEN: I call the function to list the elements of a diagram
    THEN: the listed elements are the expected ones (here none)
    """
    empty_diagram = ''
    elements_list = list_elements_circuit(empty_diagram)
    expected_listing = []

    caller = 'list_elements_circuit()'
    assert isinstance(elements_list, list), (
        'TypeError for output in ' + caller + '. It must be a list')
    wrong_types, wrong_types_index = invalid_elements_type(elements_list)
    assert not wrong_types, (
        'TypeError for element(s) number ' + str(wrong_types_index) + ' '
        + wrong_types + ' in ' + str(elements_list) + ' in ' + caller
        + '. Elements (here dictionary keys) can only be strings of length 2')
    (wrong_char_letter,
        wrong_char_letter_index) = invalid_elements_character(elements_list)
    assert not wrong_char_letter, (
        'StructuralError for element(s) number ' + str(wrong_char_letter_index)
        + ' ' + wrong_char_letter + ' in ' + str(elements_list) + ' in '
        + caller + '. All elements must begin with a letter among \'C\', '
        + '\'R\' and \'Q\', and end with a natural number and each element '
        + 'number must be unique')

    replaced_diagram = remove_elements(elements_list, empty_diagram)
    assert set(replaced_diagram).issubset({'(', ')', '[', ']'}), (
        'StructuralError for the output of remove_elements(). Some elements '
        + 'are not in the elements list')

    assert elements_list==expected_listing, (
        'StructuralError for the output of list_elements_circuit().It is not '
        + 'the correct listing of elements')

def test_list_elements_circuit_single_element():
    """Check if the function that list the elements inside a diagram works on
    a single element diagram.

    GIVEN: the circuit diagram has only a valid element
    WHEN: I call the function to list the elements of a diagram
    THEN: the listed elements are the expected one
    """
    empty_diagram = '(R1)'
    elements_list = list_elements_circuit(empty_diagram)
    expected_listing = ['R1']

    caller = 'list_elements_circuit()'
    assert isinstance(elements_list, list), (
        'TypeError for output in ' + caller + '. It must be a list')
    wrong_types, wrong_types_index = invalid_elements_type(elements_list)
    assert not wrong_types, (
        'TypeError for element(s) number ' + str(wrong_types_index) + ' '
        + wrong_types + ' in ' + str(elements_list) + ' in ' + caller
        + '. Elements (here dictionary keys) can only be strings of length 2')
    (wrong_char_letter,
        wrong_char_letter_index) = invalid_elements_character(elements_list)
    assert not wrong_char_letter, (
        'StructuralError for element(s) number ' + str(wrong_char_letter_index)
        + ' ' + wrong_char_letter + ' in ' + str(elements_list) + ' in '
        + caller + '. All elements must begin with a letter among \'C\', '
        + '\'R\' and \'Q\', and end with a natural number and each element '
        + 'number must be unique')

    replaced_diagram = remove_elements(elements_list, empty_diagram)
    assert set(replaced_diagram).issubset({'(', ')', '[', ']'}), (
        'StructuralError for the output of remove_elements(). Some elements '
        + 'are not in the elements list')

    assert elements_list==expected_listing, (
        'StructuralError for the output of list_elements_circuit().It is not '
        + 'the correct listing of elements')

def test_list_elements_circuit_many_elements():
    """Check if the function that list the elements inside a diagram works on
    a many elements diagram.

    GIVEN: the circuit diagram has many valid elements and brackets
    WHEN: I call the function to list the elements of a diagram
    THEN: the listed elements are the expected one
    """
    empty_diagram = '(R1C2[R3Q4][C5R6])'
    elements_list = list_elements_circuit(empty_diagram)
    expected_listing = ['R1', 'C2', 'R3', 'Q4', 'C5', 'R6']

    caller = 'list_elements_circuit()'
    assert isinstance(elements_list, list), (
        'TypeError for output in ' + caller + '. It must be a list')
    wrong_types, wrong_types_index = invalid_elements_type(elements_list)
    assert not wrong_types, (
        'TypeError for element(s) number ' + str(wrong_types_index) + ' '
        + wrong_types + ' in ' + str(elements_list) + ' in ' + caller
        + '. Elements (here dictionary keys) can only be strings of length 2')
    (wrong_char_letter,
        wrong_char_letter_index) = invalid_elements_character(elements_list)
    assert not wrong_char_letter, (
        'StructuralError for element(s) number ' + str(wrong_char_letter_index)
        + ' ' + wrong_char_letter + ' in ' + str(elements_list) + ' in '
        + caller + '. All elements must begin with a letter among \'C\', '
        + '\'R\' and \'Q\', and end with a natural number and each element '
        + 'number must be unique')

    replaced_diagram = remove_elements(elements_list, empty_diagram)
    assert set(replaced_diagram).issubset({'(', ')', '[', ']'}), (
        'StructuralError for the output of remove_elements(). Some elements '
        + 'are not in the elements list')

    assert elements_list==expected_listing, (
        'StructuralError for the output of list_elements_circuit().It is not '
        + 'the correct listing of elements')

def test_list_elements_circuit_invalid_elements():
    """Check if the list elements function works on an invalid diagram.

    GIVEN: the circuit diagram has a valid element but two invalid ones
    WHEN: I call the function to list the elements of a diagram
    THEN: the listed elements are only the valid ones
    """
    empty_diagram = '(S1C2G3)' #Invalid letters
    elements_list = list_elements_circuit(empty_diagram)
    expected_listing = ['C2']

    caller = 'list_elements_circuit()'
    assert isinstance(elements_list, list), (
        'TypeError for output in ' + caller + '. It must be a list')
    wrong_types, wrong_types_index = invalid_elements_type(elements_list)
    assert not wrong_types, (
        'TypeError for element(s) number ' + str(wrong_types_index) + ' '
        + wrong_types + ' in ' + str(elements_list) + ' in ' + caller
        + '. Elements (here dictionary keys) can only be strings of '
        + 'length 2')
    (wrong_char_letter,
        wrong_char_letter_index) = invalid_elements_character(elements_list)
    assert not wrong_char_letter, (
        'StructuralError for element(s) number ' + str(wrong_char_letter_index)
        + ' ' + wrong_char_letter + ' in ' + str(elements_list) + ' in '
        + caller + '. All elements must begin with a letter among \'C\', '
        + '\'R\' and \'Q\', and end with a natural number and each element '
        + 'number must be unique')

    replaced_diagram = remove_elements(elements_list, empty_diagram)
    assert not set(replaced_diagram).issubset({'(', ')', '[', ']'}), (
        'StructuralError for the output of remove_elements(). The extra  '
        + 'characters are not found after removing the detected elements')

    assert elements_list==expected_listing, (
        'StructuralError for the output of list_elements_circuit().It is not '
        + 'the correct listing of elements')

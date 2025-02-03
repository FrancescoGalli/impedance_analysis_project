"""This module containes all the test functions (and the function needed for
the tests) for all the functions inside the generate_impedance.py module,
apart from the AnalysisCircuit class and the generate circuit functions
It assesses, for example, that both input data and the output of all the
functions in the class are valid.
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

from generate_impedance import AnalisysCircuit
from generate_impedance import (
    generate_circuit, impedance_resistor, impedance_capacitor, impedance_cpe,
    add, serial_comb, reciprocal, parallel_comb, get_position_opening_bracket,
    get_string, list_elements_circuit)

################################
#Test mischellanous functions

@given(frequency=enp.arrays(dtype=float, shape=10, elements=st.floats(1, 1e4),
                            unique=True),
       resistance=st.floats(min_value=10, max_value=1e5))
@settings(max_examples=10)
def test_impedance_resistor_type(resistance, frequency):
    """Check that the definition of the impedance of resistors returns a
    valid impedance vector.

    GIVEN: the value of resistance and frequencies are valid
    WHEN: every time the impedance of a resistor is needed
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

def generate_example_resistor_impedance_formula():
    """Generate values of impedance of a resistor from the function for the
    test of the impedance definition of a resisitor. Only the last one is
    incorrect.
    """
    resistances = [100., 1000., 1234., 2j]
    frequencies = [[1.], [10.], [1000.], [10000.]]
    resistor_impedances = []
    for i, r in enumerate(resistances):
        impedance_value = impedance_resistor(r, frequencies[i])
        resistor_impedances.append(impedance_value)
    return resistor_impedances

@pytest.fixture
def example_resistor_impedance_formula():
    return generate_example_resistor_impedance_formula()

def generate_example_resistor_impedance():
    """Returns values of impedance of a resistor for the test of the impedance
    definition of a resisitor.
    """
    resistor_impedances = [100., 1000., 1234., 100.]
    return resistor_impedances

@pytest.fixture
def example_resistor_impedance():
    return generate_example_resistor_impedance()

def test_impedance_resistor_value(example_resistor_impedance_formula,
                                  example_resistor_impedance):
    """Check that the definition of the impedance of resistors returns proper
    impedance values

    GIVEN: the value of resistance and frequencies are valid
    WHEN: every time the impedance of a resistor is needed
    THEN: the impedance values are correct
    """
    for i, impedance in enumerate(example_resistor_impedance_formula):
        assert round(np.real(impedance[0]), 5)==example_resistor_impedance[i], (
            'ValueError from the definition of impedance of the ' + str(i+1)
            + 'th resistor: the impedance is incorrect')
        assert round(np.imag(impedance[0]), 5)==0., (
            'ValueError from the definition of impedance of the ' + str(i+1)
            + 'th resistor: the impedance is incorrect')


@given(frequency=enp.arrays(dtype=float, shape=10, elements=st.floats(1, 1e4),
                            unique=True),
       capacitance=st.floats(min_value=1e-9, max_value=1e-5))
@settings(max_examples=10)
def test_impedance_capacitor_type(capacitance, frequency):
    """Check that the definition of the impedance of capacitors returns a
    valid impedance vector.

    GIVEN: the value of capacitance and frequencies are valid
    WHEN: every time the impedance of a capacitor is needed
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


def generate_example_capacitor_impedance_formula():
    """Generate values of impedance of a capacitor from the function, for the
    test of the impedance definition of a capacitor.  Only the last one is
    incorrect.
    """
    capacitances = [1e-6, 1.2e-7, 2e-6, -0.0002j]
    frequencies = [1., 10., 1000., 10000.]
    capacitor_impedances = []
    for i, c in enumerate(capacitances):
        impedance_value = impedance_capacitor(c, frequencies[i])
        capacitor_impedances.append(impedance_value)
    return capacitor_impedances

@pytest.fixture
def example_capacitor_impedance_formula():
    return generate_example_capacitor_impedance_formula()

def generate_example_capacitor_impedance():
    """Returns values of impedance of a capacitor, for the test of the
    impedance definition of a capacitor.
    """
    capacitor_impedances = [159154.94309, 132629.11924, 79.57747, 0.07958]
    return capacitor_impedances

@pytest.fixture
def example_capacitor_impedance():
    return generate_example_capacitor_impedance()

def test_impedance_capacitor_value(example_capacitor_impedance_formula,
                                   example_capacitor_impedance):
    """Check that the definition of the impedance of capacitors returns proper
    impedance values

    GIVEN: the value of resistance and frequencies are valid
    WHEN: every time the impedance of a resistor is needed
    THEN: the impedance values are correct
    """
    for i, impedance in enumerate(example_capacitor_impedance_formula):
        assert abs(impedance)>0, (
            'ValueError from the definition of impedance of the ' + str(i+1)
            + 'th capacitor: the impedance must be positive')
        assert round(abs(impedance), 5)==example_capacitor_impedance[i], (
            'ValueError from the definition of impedance of the ' + str(i+1)
            + 'th capacitor: the impedance is incorrect')
        angle_capacitor = round(-np.pi/2, 5)
        assert round(np.angle(impedance), 5)==angle_capacitor, (
            'ValueError from the definition of impedance of the ' + str(i+1)
            + 'th capacitor: the impedance is incorrect')


@given(frequency=enp.arrays(dtype=float, shape=10, elements=st.floats(1, 1e4),
                            unique=True),
       q_parameter=st.floats(min_value=1e-9, max_value=1e-5),
       ideality_factor=st.floats(min_value=0., max_value=1.))
@settings(max_examples=10)
def test_impedance_cpe_type(q_parameter, ideality_factor, frequency):
    """Check that the definition of the impedance of capacitors returns a
    valid impedance vector.

    GIVEN: the value of Q, idealuty factor and frequencies are valid
    WHEN: every time the impedance of a capacitor is needed
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

def generate_example_cpe_impedance_formula():
    """Generate values of impedance of a cpe from the function, for the test
    of the impedance definition of a cpe. Only the last one is incorrect.
    """
    qs = [1e-6, 1.2e-7, 2e-6, 3e-6]
    ns = [0.1, 0.4, 0.89, 1.5]
    frequencies = [1., 10., 1000., 10000.]
    cpe_impedances = []
    for i, q in enumerate(qs):
        impedance_value = impedance_cpe(q, ns[i], frequencies[i])
        cpe_impedances.append(impedance_value)
    return cpe_impedances

@pytest.fixture
def example_cpe_impedance_formula():
    return generate_example_cpe_impedance_formula()

def generate_example_cpe_impedance():
    """Returns values of impedance of a cpe, for the test of the impedance
    definition of a cpe.
    """
    cpe_impedances = [832112.43702, 1590548.09782, 208.25236, 5.30516]
    return cpe_impedances

@pytest.fixture
def example_cpe_impedance():
    return generate_example_cpe_impedance()

def generate_example_cpe_impedance_angle():
    """Returns values of impedance angle of a cpe, for the test of the
    impedance definition of a cpe.
    """
    cpe_impedance_angles = [-0.15708, -0.62832, -1.39801, -1.57080]
    return cpe_impedance_angles

@pytest.fixture
def example_cpe_impedance_angle():
    return generate_example_cpe_impedance_angle()

def test_impedance_cpe_value(example_cpe_impedance_formula,
                             example_cpe_impedance,
                             example_cpe_impedance_angle):
    """Check that the definition of the impedance of cpes returns proper
    impedance values

    GIVEN: the value of resistance and frequencies are valid
    WHEN: every time the impedance of a resistor is needed
    THEN: the impedance values are correct
    """
    for i, impedance in enumerate(example_cpe_impedance_formula):
        assert abs(impedance)>0, (
            'ValueError from the definition of impedance of the ' + str(i+1)
            + 'th cpe: the impedance must be positive')
        assert round(abs(impedance), 5)==example_cpe_impedance[i], (
            'ValueError from the definition of impedance of the ' + str(i+1)
            + 'th cpe: the impedance is incorrect')
        assert round(np.angle(impedance), 5)==example_cpe_impedance_angle[i], (
            'ValueError from the definition of impedance of the ' + str(i+1)
            + 'th cpe: the impedance is incorrect')


def generate_examples_sum_functions():
    """Generate examples of sum of functions, for the test of the add
    function. Only the last one is incorrect.
    """
    first_function_1 = lambda x, y: x + y
    second_function_1 = lambda x, y: x*y
    sum_function_1 = add(first_function_1, second_function_1)
    first_function_2 = lambda x, y: x
    second_function_2 = lambda x, y: y
    sum_function_2 = add(first_function_2, second_function_2)
    first_function_3 = lambda x, y: (x + y)/2
    second_function_3 = lambda x, y: 1/x
    sum_function_3 = add(first_function_3, second_function_3)
    first_function_4 = lambda x, y: 2*x
    second_function_4 = lambda x, y: 1/y
    sum_function_4 = add(first_function_4, second_function_4)
    examples_sum_functions = [sum_function_1, sum_function_2, sum_function_3,
                              sum_function_4]
    return examples_sum_functions

@pytest.fixture
def examples_sum_functions():
    return generate_examples_sum_functions()

def generate_examples_function_inputs():
    """Generate examples of inputs for the functions. Only the last one is
    incorrect.
    """
    inputs = [(1, 2), (3.2, 4), (2, 5) , (0, 1)]
    return inputs

@pytest.fixture
def examples_function_inputs():
    return generate_examples_function_inputs()

def generate_examples_sum_function_outputs():
    """Generate examples of outputs for the result of the add function."""
    outputs = [5, 7.2, 4, 3]
    return outputs

@pytest.fixture
def examples_sum_function_outputs():
    return generate_examples_sum_function_outputs()

def test_add(examples_sum_functions, examples_function_inputs,
             examples_sum_function_outputs):
    """Check that the add function returns a valid sum function.

    GIVEN: the two adding functions are functions.
    WHEN: an addition of functions is performed
    THEN: the result of the add function is a proper sum function.
    """
    for i, function_ in enumerate(examples_sum_functions):
        assert inspect.isfunction(function_), (
            'TypeError for the ' + str(i+1) + 'th function of the add() test. '
            + 'It must be a function')
        inputs = examples_function_inputs[i]
        assert function_(inputs[0], inputs[1])==(
            examples_sum_function_outputs[i]), (
                'ValueError for the ' + str(i+1) + 'th function of the add() '
                + 'test. The output is incorrect')


def generate_examples_s_comb_functions():
    """Generate examples of serial comb of functions, fot he serial comb
    function test. Only the last one is incorrect.
    """
    first_function_1 = lambda x, y: x + y
    s_comb_function_1 = serial_comb([first_function_1])
    first_function_2 = lambda x, y: x
    second_function_2 = lambda x, y: y
    s_comb_function_2 = serial_comb([first_function_2, second_function_2])
    first_function_3 = lambda x, y: (x + y)/2
    second_function_3 = lambda x, y: 1/x
    third_function_3 = lambda x, y: 2*x
    s_comb_function_3 = serial_comb([first_function_3, second_function_3,
                                  third_function_3])
    first_function_4 = lambda x, y: 2*y
    s_comb_function_4 = serial_comb([])
    examples_s_comb_functions = [s_comb_function_1, s_comb_function_2,
                              s_comb_function_3, s_comb_function_4]
    return examples_s_comb_functions

@pytest.fixture
def examples_s_comb_functions():
    return generate_examples_s_comb_functions()

def generate_examples_function_s_comb_outputs():
    """Generate examples of outputs for the result of the functions. Only the
    last one is incorrect.
    """
    outputs = [3, 7.2, 8, 1]
    return outputs

@pytest.fixture
def examples_function_s_comb_outputs():
    return generate_examples_function_s_comb_outputs()


def test_serial_comb(examples_s_comb_functions, examples_function_inputs,
                     examples_function_s_comb_outputs):
    """Check that the serial comb function returns a valid function.

    GIVEN: a list of functions
    WHEN: a serial comb of functions is performed
    THEN: the equivalent function is a function.
    """
    for i, function_ in enumerate(examples_s_comb_functions):
        assert inspect.isfunction(function_), (
            'TypeError for the ' + str(i+1) + 'th function of serial_comb() '
            + 'test. It must be a function')
        inputs = examples_function_inputs[i]
        assert function_(inputs[0], inputs[1])==(
            examples_function_s_comb_outputs[i]), (
                'ValueError for the ' + str(i+1) + 'th function of the add() '
                + 'test. The output is incorrect')


def generate_examples_initial_reciprocal_functions():
    """Generate examples of reciprocal functions."""
    function_1 = lambda x, y: x
    function_2 = lambda x, y: x/y
    function_3 = lambda x, y: 1/x
    function_4 = lambda x, y: 2*y
    examples_initial_functions = [function_1, function_2, function_3,
                                  function_4]
    return examples_initial_functions

@pytest.fixture
def examples_initial_reciprocal_functions():
    return generate_examples_initial_reciprocal_functions()

def generate_examples_reciprocal_functions():
    """Generate examples of reciprocal functions, for the reciprocal function
    test.
    """
    examples_reciprocal_functions = []
    examples_initial_functions = generate_examples_initial_reciprocal_functions()
    for function_ in examples_initial_functions:
        examples_reciprocal_functions.append(reciprocal(function_))
    return examples_reciprocal_functions

@pytest.fixture
def examples_reciprocal_functions():
    return generate_examples_reciprocal_functions()

def generate_examples_function_reciprocal_outputs():
    """Generate examples of outputs for the result of the reciprocal
    function.
    """
    outputs = [1, 1.25, 2, 1]
    return outputs

@pytest.fixture
def examples_function_reciprocal_outputs():
    return generate_examples_function_reciprocal_outputs()


def test_reciprocal(examples_reciprocal_functions, examples_function_inputs,
                    examples_function_reciprocal_outputs,
                    examples_initial_reciprocal_functions):
    """Check that the serial comb function returns a valid function.

    GIVEN: a list of functions
    WHEN: a serial comb of functions is performed
    THEN: the equivalent function is a function.
    """
    for i, function_ in enumerate(examples_reciprocal_functions):
        assert inspect.isfunction(function_), (
            'TypeError for the ' + str(i+1) + 'th function of reciprocal() '
            + 'test. It must be a function')
        inputs = examples_function_inputs[i]
        assert function_(inputs[0], inputs[1])==(
            examples_function_reciprocal_outputs[i]), (
                'ValueError for the ' + str(i+1) + 'th function of the '
                + 'reciprocal() test. The output is incorrect')
        assert function_(inputs[0], inputs[1])==(
            examples_function_reciprocal_outputs[i]), (
                'ValueError for the ' + str(i+1) + 'th function of the '
                + 'reciprocal() test. The output is incorrect')
        initial_function = examples_initial_reciprocal_functions[i]
        second_reciprocal = reciprocal(function_)
        assert second_reciprocal(inputs[0], inputs[1])==(
            initial_function(inputs[0], inputs[1])), (
                'ValueError for the ' + str(i+1) + 'th function of the '
                + 'reciprocal() test. The reciprocal of the reciprocal must'
                + 'be the initial function')


def generate_examples_p_comb_functions():
    """Generate examples of parallel comb of functions, for the parallel comb
    function test. Only the last one is incorrect.
    """
    first_function_1 = lambda x, y: x + y
    p_comb_function_1 = parallel_comb([first_function_1])
    first_function_2 = lambda x, y: x + 0.8
    second_function_2 = lambda x, y: y
    p_comb_function_2 = parallel_comb([first_function_2, second_function_2])
    first_function_3 = lambda x, y: (x + y)/7
    second_function_3 = lambda x, y: 1/x
    third_function_3 = lambda x, y: y
    p_comb_function_3 = parallel_comb([first_function_3, second_function_3,
                                       third_function_3])
    first_function_4 = lambda x, y: 2*y
    p_comb_function_4 = parallel_comb([third_function_3])
    examples_p_comb_functions = [p_comb_function_1, p_comb_function_2,
                                 p_comb_function_3, p_comb_function_4]
    return examples_p_comb_functions

@pytest.fixture
def examples_p_comb_functions():
    return generate_examples_p_comb_functions()

def generate_examples_function_p_comb_outputs():
    """Generate examples of outputs of the parallel comb function."""
    outputs = [3, 2, 0.3125, 0.5]
    return outputs

@pytest.fixture
def examples_function_p_comb_outputs():
    return generate_examples_function_p_comb_outputs()

def test_parallel_comb(examples_p_comb_functions, examples_function_inputs,
                       examples_function_p_comb_outputs):
    """Check that the parallel comb function returns a valid function.

    GIVEN: a list of functions
    WHEN: a parallel comb of functions is performed
    THEN: the equivalent function is a function.
    """
    for i, function_ in enumerate(examples_p_comb_functions):
        assert inspect.isfunction(function_), (
            'TypeError for the ' + str(i+1) + 'th function of parallel_comb() '
            + 'test. It must be a function')
        inputs = examples_function_inputs[i]
        assert function_(inputs[0], inputs[1])==(
            examples_function_p_comb_outputs[i]), (
                'ValueError for the ' + str(i+1) + 'th function of the add() '
                + 'test. The output is incorrect')


def generate_examples_position_opening_bracket():
    """Return examples of last opening bracket in a circuit diagram, for the
    test_get_position_opening_bracket test.
    """
    diagrams = ['(R1)', '(C1R2[R3])', '(C1R2[R3Q4][R5C6])']
    i_ends = [3, 8, 10]
    examples_position = []
    for i, diagram in enumerate(diagrams):
        position_barckets = get_position_opening_bracket(diagram, i_ends[i])
        examples_position.append(position_barckets)
    return examples_position

@pytest.fixture
def examples_position_opening_bracket():
    return generate_examples_position_opening_bracket()

def generate_examples_position_opening_bracket_result():
    """Return the correct last opening bracket in a circuit diagram, for the
    test_get_position_opening_bracket test.
    """
    examples_position_results = [0, 5, 5]
    return examples_position_results

@pytest.fixture
def examples_position_opening_bracket_result():
    return generate_examples_position_opening_bracket_result()

def test_get_position_opening_bracket(
        examples_position_opening_bracket,
        examples_position_opening_bracket_result):
    """Check that the function to find the position of the last opening
    brackets works properly.

    GIVEN: a valid circuit diagram and position of the closing bracket
    WHEN: the function to divide the circuit diagram in cell i called
    THEN: the index of the start of the cell is the position of the opening
    bracket
    """
    for i, position in enumerate(examples_position_opening_bracket):
        assert isinstance(position, int), (
            'TypeError in output of get_position_opening_bracket(). Last '
            + 'opening bracket position must be an integer')
        assert position>=0, ('ValueError in output of '
            + 'get_position_opening_bracket(). Last opening bracket position '
            + 'must be non-negative')
        assert position==examples_position_opening_bracket_result[i], (
            'ValueError for the ' + str(i+1) +'th example of '
            'the get_position_opening_bracket() test. It does not match the '
            + 'correct position')


def generate_examples_joined_string():
    """Generate examples of joined string from string vectors, for the
    gets_string test."""
    examples_list_string = [['1'], ['1', ' and 2'],
                            ['first', ' and', ' third']]
    examples_joined_strings = []
    for example in examples_list_string:
        examples_joined_strings.append(get_string(example))
    return examples_joined_strings

@pytest.fixture
def examples_joined_string():
    return generate_examples_joined_string()

def generate_examples_string():
    """Generate examples of already joined strings, for the gets_string
    test.
    """
    examples_string = ['1', '1\n and 2', 'first\n and\n third']
    return examples_string

@pytest.fixture
def examples_string():
    return generate_examples_string()

def test_get_string(examples_joined_string, examples_string):
    """Check that the output of get_string() is a valid joined string.

    GIVEN: a list of strings
    WHEN: the function to concatenate a list of strings is called
    THEN: the output of get_string() is a valid string
    """
    for i, string_ in enumerate(examples_joined_string):
        assert isinstance(string_, str), (
            'TypeError for output of get_string(): the output must be a '
            + 'string, not a ' + str(type(string_)))
        assert (string_.startswith(examples_string[i])
                and string_.endswith(examples_string[i])), (
                    'ValueError for the ' + str(i+1) + 'th example of '
                    + 'get_string(): the output does not match the correct '
                    + 'string')

##########################
#Test Circuit Class

def wrong_match_element_initial_circuit_final_parameters(final_parameters_map,
                                                         initial_parameters):
    """Find any non-constant element in the initial circuit that is missing
    in the final parameters_map.

    Parameters
    ----------
    final_parameters_map : dict
        Final parameters map
    initial_parameters : dict
        Input parameters map

    Returns
    -------
    wrong_elements : str
        String that contains all the absent elements, separated by a comma and
        a whitespace
    """
    wrong_elements = ''
    for element, parameter in initial_parameters.items():
        if not parameter[1]:
            if not element in final_parameters_map.keys():
                wrong_elements += '\'' + element + '\', '
    return wrong_elements

def generate_examples_final_parameters_map_wrong_match():
    """Generate examples of final parameters, for the wrong match test.
    Only the last one is incorrect.
    """
    example_final_parameters_map_wrong_match = [
        {'R1': 1000.}, {'C1': 1e-6}, {'C1': 1e-6, 'R2': 100.},
        {'R1': 200.}]
    return example_final_parameters_map_wrong_match

@pytest.fixture
def example_final_parameters_map_wrong_match():
    return generate_examples_final_parameters_map_wrong_match()

def generate_examples_input_parameters_wrong_match_element():
    """Generate examples of input parameters, for the wrong match test.
    Only the last one is incorrect.
    """
    example_input_parameters_map_wrong_match = [
        {'R1': (1000., 0)}, {'C1': (1e-6, 0), 'Q2': ([1e-5, 0.76], 1)},
        {'C1': (1e-6, 0), 'R2': (100., 0)},
        {'R1': (300., 0), 'R2': (100., 0)}]
    return example_input_parameters_map_wrong_match

@pytest.fixture
def example_input_parameters_map_wrong_match_element():
    return generate_examples_input_parameters_wrong_match_element()

def test_wrong_match_element_initial_circuit_final_parameters(
        example_final_parameters_map_wrong_match,
        example_input_parameters_map_wrong_match_element):
    """Check that the help function that finds the element mismatch between
    input parameters dictionaries and final parameters dictionaries works

    GIVEN: a valid analyzed circuit.
    WHEN: the results of the analysis are set into the analysis circuit object
    THEN: the final parameters are valid.
    """
    for i, final_parameters_map in enumerate(
        example_final_parameters_map_wrong_match):
        wrong_elements = wrong_match_element_initial_circuit_final_parameters(
            final_parameters_map,
            example_input_parameters_map_wrong_match_element[i])
        assert not wrong_elements, (
            'Bad match between non constant elements of the initial circuit '
            + 'and the final analysis parameter. ' + wrong_elements + 'not '
            + 'found')


def wrong_match_parameter_initial_circuit_final_parameters(
        final_parameters_map, initial_parameters):
    """Find any non-constant parameter in the initial circuit that is missing
    in the final parameters_map.

    Parameters
    ----------
    final_parameters_map : dict
        Final parameters map
    initial_parameters : dict
        Input parameters map

    Returns
    -------
    wrong_elements : str
        String that contains all the absent parameters, separated by a comma
        and a whitespace
    """
    wrong_parameters = ''
    for element, parameter in initial_parameters.items():
        if not parameter[1]:
            if final_parameters_map[element]!=initial_parameters[element][0]:
                wrong_parameters += '\'' + element + '\', '
    return wrong_parameters

def generate_examples_input_parameters_wrong_match_value():
    """Generate examples of input parameters, for the wrong value test.
    Only the last one is incorrect.
    """
    example_input_parameters_map_wrong_match = [
        {'R1': (1000., 0)}, {'C1': (1e-6, 0), 'Q2': ([1e-5, 0.76], 1)},
        {'C1': (1e-6, 0), 'R2': (100., 0)}, {'R1': (300., 0)}]
    return example_input_parameters_map_wrong_match

@pytest.fixture
def example_input_parameters_map_wrong_match_value():
    return generate_examples_input_parameters_wrong_match_value()

def test_wrong_match_parameter_initial_circuit_final_parameters(
        example_final_parameters_map_wrong_match,
        example_input_parameters_map_wrong_match_value):
    """Check that the help function that finds the element mismatch between
    input parameters dictionaries and final parameters dictionaries works

    GIVEN: a valid analyzed circuit.
    WHEN: the results of the analysis are set into the analysis circuit object
    THEN: the final parameters are valid.
    """
    for i, final_parameters_map in enumerate(
        example_final_parameters_map_wrong_match):
        wrong_parameters = wrong_match_parameter_initial_circuit_final_parameters(
            final_parameters_map,
            example_input_parameters_map_wrong_match_value[i])
        assert not wrong_parameters, (
            'Bad match between parameters of the initial circuit and the '
            + 'final analysis parameter. Parameter of element '
            + wrong_parameters + 'not found')


def wrong_match_constant_element(final_parameters_map, initial_parameters_map):
    """Find any constant element in the initial circuit that is also present
    in the final parameters_map of the analyzed circuit (as it should not be).

    Parameters
    ----------
    initial_parameters_map : dict
        Dictionary of the elements in the inital circuit
    final_parameters_map : dict
        Dictionary containing all the non-constant elements

    Returns
    -------
    wrong_const_elements : str
        String that contains all the constant elements, separated by a comma
        and a whitespace
    """
    wrong_const_elements = ''
    for element, parameter in initial_parameters_map.items():
        if parameter[1]:
            if element in final_parameters_map.keys():
                wrong_const_elements += '\'' + element + '\', '
    return wrong_const_elements

def generate_examples_input_parameters_wrong_match_constant():
    """Generate examples of input parameters, for the wrong match constant
    test. Only the last one is incorrect.
    """
    example_input_parameters_map_wrong_match = [
        {'R1': (1000., 0)}, {'C1': (1e-6, 0), 'Q2': ([1e-5, 0.76], 1)},
        {'C1': (1e-6, 0), 'R2': (100., 0)}, {'R1': (300., 1)}]
    return example_input_parameters_map_wrong_match

@pytest.fixture
def examples_input_parameters_wrong_match_constant():
    return generate_examples_input_parameters_wrong_match_constant()

def test_wrong_match_constant_element(
        example_final_parameters_map_wrong_match,
        examples_input_parameters_wrong_match_constant):
    """Check that the help function that finds the constant element of the
    initial circuit that are also present in the final circuit works.

    GIVEN: a valid analyzed circuit.
    WHEN: the results of the analysis are set into the analysis circuit object
    THEN: the final parameters are valid.
    """
    for i, final_parameters_map in enumerate(
        example_final_parameters_map_wrong_match):
        wrong_const_elements = wrong_match_constant_element(
            final_parameters_map,
            examples_input_parameters_wrong_match_constant[i])
        assert not wrong_const_elements, (
            'Bad match between elements of the initial circuit and the final '
            + 'analysis elements. Element ' + wrong_const_elements
            + 'is constant but is found in the fitting elements')


def wrong_non_existent_element(final_parameters_map, initial_parameters_map):
    """Find any non-constant element in the initial circuit that is not present
    in the final parameters_map of the analyzed circuit.

    Parameters
    ----------
    initial_parameters_map : dict
        Dictionary of the elements in the inital circuit
    final_parameters_map : dict
        Dictionary containing all the non-constant elements

    Returns
    -------
    wrong_non_e_elements : str
        String that contains all the absent elements, separated by a comma
        and a whitespace
    """
    wrong_non_e_elements = ''
    for element in final_parameters_map.keys():
        if element not in initial_parameters_map.keys():
            wrong_non_e_elements += '\'' + element + '\', '
    return wrong_non_e_elements

def generate_examples_input_parameters_non_existent():
    """Generate examples of input parameters, for the non existent element
    test. Only the last one is incorrect.
    """
    example_input_parameters_map_wrong_match = [
        {'R1': (1000., 0)}, {'C1': (1e-6, 0), 'Q2': ([1e-5, 0.76], 1)},
        {'C1': (1e-6, 0), 'R2': (100., 0)}, {'C1': (1e-6, 1)}]
    return example_input_parameters_map_wrong_match

@pytest.fixture
def examples_input_parameters_non_existent():
    return generate_examples_input_parameters_non_existent()

def test_wrong_non_existent_element(example_final_parameters_map_wrong_match,
                                    examples_input_parameters_non_existent):
    """Check that the help function that finds the constant element of the
    initial circuit that are also present in the final circuit works.

    GIVEN: a valid analyzed circuit.
    WHEN: the results of the analysis are set into the analysis circuit object
    THEN: the final parameters are valid.
    """
    for i, final_parameters_map in enumerate(
        example_final_parameters_map_wrong_match):
        wrong_non_e_elements = wrong_non_existent_element(
            final_parameters_map, examples_input_parameters_non_existent[i])
        assert not wrong_non_e_elements, (
            'Bad match between elements of the initial circuit and the final '
            + 'analysis elements. Element ' + wrong_non_e_elements
            + 'is non-existent in the initial elements')


def generate_examples_initial_circuit():
    """Generate examples of initial circuits, for the
    generate_analyzed_circuit test.
    """
    circuit_diagram_1 = '(R1)'
    parameters_1 = {'R1': 100.}
    c_c_1 = {'R1': 0}
    circuit_1 = generate_circuit(circuit_diagram_1, parameters_1, c_c_1)

    circuit_diagram_2 = '(R1C2)'
    parameters_2 = {'R1': 100., 'C2': 1e-6}
    c_c_2 = {'R1': 0, 'C2': 0}
    circuit_2 = generate_circuit(circuit_diagram_2, parameters_2, c_c_2)

    circuit_diagram_3 = '(R1C2[R3Q4])'
    parameters_3 = {'R1': 100., 'C2': 1e-6, 'R3': 10000., 'Q4': [1e-5, 0.86]}
    c_c_3 = {'R1': 0, 'C2': 0, 'R3': 1, 'Q4': 0}
    circuit_3 = generate_circuit(circuit_diagram_3, parameters_3, c_c_3)

    examples_initial_circuits = [circuit_1, circuit_2, circuit_3]
    return examples_initial_circuits

@pytest.fixture
def examples_initial_circuit():
    return generate_examples_initial_circuit()

def generate_examples_full_analyzed_circuit():
    """Generate examples of analyzed circuit, for the
    generate_analyzed_circuit test."""
    initial_circuits = generate_examples_initial_circuit()
    examples_analyzed_circuit = []
    for circuit_ in initial_circuits:
        analyzed_circuit = circuit_.generate_analyzed_circuit()
        examples_analyzed_circuit.append(analyzed_circuit)
    return examples_analyzed_circuit

@pytest.fixture
def examples_full_analyzed_circuit():
    return generate_examples_full_analyzed_circuit()

def test_generate_analyzed_circuit(examples_full_analyzed_circuit,
                                   examples_initial_circuit):
    """Check that the generate_analyzed_circuit() method return a
    valid AnalysisCircuit instance.

    GIVEN: a initial circuit.
    WHEN: the analysis of a circuit is required
    THEN: the output is a valid AnalysisCircuit instance.
    """
    caller = 'generate_analyzed_circuit()'
    for i, analyzed_circuit in enumerate(examples_full_analyzed_circuit):
        assert isinstance(analyzed_circuit, AnalisysCircuit), (
            'TyperError for output of ' + caller + ' method. It must be an '
            + 'instance of the \'AnalisysCircuit\' class')

        diagram_analyzed_circuit = analyzed_circuit.circuit_diagram
        assert isinstance(diagram_analyzed_circuit, str), (
            'TypeError for the circuit string of the output of ' + caller
            + ' It must be a string')
        assert inspect.isfunction(analyzed_circuit.impedance), (
            'TypeError for the final impedance of the output of ' + caller
            + '. It must be a function')

        parameters_map = analyzed_circuit.parameters_map
        assert isinstance(parameters_map, dict), (
            'TypeError for the parameters map of the output of ' + caller
            + '. It must be a dictionary')
        initial_circuit = examples_initial_circuit[i]
        initial_parameters_map = initial_circuit.parameters_map
        wrong_elements = wrong_match_element_initial_circuit_final_parameters(
            parameters_map, initial_parameters_map)
        assert not wrong_elements, (
            'Bad match between non constant elements of the initial circuit '
            + 'and the final analysis parameter. ' + wrong_elements + 'not '
            + 'found')
        wrong_parameters = wrong_match_parameter_initial_circuit_final_parameters(
            parameters_map, initial_parameters_map)
        assert not wrong_parameters, (
            'Bad match between parameters of the initial circuit and the '
            + 'final analysis parameter. Parameter of element '
            + wrong_elements + 'not found')
        wrong_const_elements = wrong_match_constant_element(
            parameters_map, initial_parameters_map)
        assert not wrong_const_elements, (
            'Bad match between elements of the initial circuit and the final '
            + 'analysis elements. Element ' + wrong_const_elements
            + 'is constant but is found in the fitting elements')
        wrong_non_e_elements = wrong_non_existent_element(
            parameters_map, initial_parameters_map)
        assert not wrong_non_e_elements, (
            'Bad match between elements of the initial circuit and the final '
            + 'analysis elements. Element ' + wrong_non_e_elements
            + 'is non-existent in the initial elements')


def generate_examples_parameters_string():
    """Generate an example of initial parameters string, for the
    get_parameters_info test."""
    examples_initial_circuit = generate_examples_initial_circuit()
    example_parameter_string = []
    for example in examples_initial_circuit:
        example.error = 225.8
        parameters_string = example.get_parameters_info()
        example_parameter_string.append(parameters_string)
    return example_parameter_string

@pytest.fixture
def examples_parameters_string():
    return generate_examples_parameters_string()

def test_get_parameters_info(examples_parameters_string):
    """Check that the output of get_parameters_info() is a valid string.

    GIVEN: a valid inital circuit.
    WHEN: the initial parametrs string is created.
    THEN: the output is a string.
    """
    for string_ in examples_parameters_string:
        assert isinstance(string_, str), (
            'TypeError for output of get_initial_parameters(): the output '
            + 'must be a string, not a ' + str(type(string_)))


def invalid_elements_type(element_list):
    """Given the elements in the circuit, return any object that is not a
    string. Used for testing.

    Parameters
    ----------
    elements_circuit : list
        List of the elements in the circuit

    Returns
    -------
    wrong_type : str
        String that contains all the invalid elements, separated by a comma
        and a whitespace
    wrong_type_index : list
        List of indexes of the invalid invalid elements in the list
    """
    wrong_types = ''
    wrong_types_index = []
    for i, element in enumerate(element_list):
        if not isinstance(element, str):
            wrong_types+= '\'' + str(element) + '\', '
            wrong_types_index.append(i)
    return wrong_types, wrong_types_index

def generate_example_elements_type():
    """Generate examples for the invalid element test. Only the last one is
    incorrect.
    """
    example_elements_type = ([['C1'], ['C1', '&'], ['Q1', 'C2', 'R'],
                              [1.2, ['C2'], 'R3']])
    return example_elements_type

@pytest.fixture
def example_elements_type():
    return generate_example_elements_type()

def test_invalid_elements_type(example_elements_type):
    """Check that the help function to find the elements with the wrong type
    works.

    GIVEN: the elements are in a form of a list
    WHEN: the elements validity is tested
    THEN: the elements list contains only valid types
    """
    for elements in example_elements_type:
        wrong_types, wrong_types_index = invalid_elements_type(elements)
        assert not wrong_types, (
            'TypeError for element(s) number ' + str(wrong_types_index) + ' '
            + wrong_types + ' in ' + str(elements) + ' in '
            + 'invalid_elements_type(). Elements can only be strings')


def invalid_elements_length(element_list):
    """Given the elements in the circuit that will figure in the fit, return
    any element with a length different than 2, thus invalid. Used for
    testing.

    Parameters
    ----------
    elements_circuit : list
        List of the elements in the circuit that will figure in the fit

    Returns
    -------
    wrong_length : str
        String that contains all the invalid elements, separated by a comma
        and a whitespace
    wrong_length_index : list
        List of indexes of the invalid invalid elements in the list
    """
    wrong_length = ''
    wrong_length_index = []
    for i, element in enumerate(element_list):
        if len(element)!=2:
            wrong_length += '\'' + str(element) + '\', '
            wrong_length_index.append(i)
    return wrong_length, wrong_length_index

def generate_example_elements_length():
    """Generate examples for the invalid element length test. Only the last
    one is incorrect.
    """
    example_elements_length = ([['C1'], ['Cy', 'CC'], ['Q1', 'C2', 'R3'],
                                ['C', 'C12', 'R3']])
    return example_elements_length

@pytest.fixture
def example_elements_length():
    return generate_example_elements_length()

def test_invalid_elements_length(example_elements_length):
    """Check that the help function to find the elements with the wrong length
    works.

    GIVEN: the elements are in a form of a list of strings
    WHEN: the elements validity is tested
    THEN: the elements list contains only strings with length 2
    """
    for elements in example_elements_length:
        wrong_length, wrong_length_index = invalid_elements_length(elements)
        assert not wrong_length, (
            'LengthError for element(s) number ' + str(wrong_length_index)
            + ' ' + wrong_length + ' in ' + str(elements) + ' in '
            + 'invalid_elements_type(). Elements must all be of length 2')


def invalid_elements_char_letter(elements_circuit):
    """Given the elements in the circuit that will figure in the fit, return
    any character that as a fist character invalid, i.e. any out of R, C, Q.
    Used for testing.

    Parameters
    ----------
    elements_circuit : list
        List of the elements in the circuit that will figure in the fit

    Returns
    -------
    wrong_char : str
        String that contains all the invalid elements, separated by a comma
        and a whitespace
    wrong_char_index : list
        List of indexes of the invalid invalid elements in the list
    """
    wrong_char = ''
    wrong_char_index = []
    for i, element in enumerate(elements_circuit):
        if element[0] not in {'R', 'C', 'Q'}:
            wrong_char += '\'' + str(element) + '\', '
            wrong_char_index.append(i)
    return wrong_char, wrong_char_index

def generate_example_elements_char_letter():
    """Generate examples for the invalid element letter test. Only the last
    one is incorrect.
    """
    example_elements_char_letter = ([['R1'], ['Cy', 'CC'], ['Q1', 'C2', 'R3'],
                                     ['1C', 'C2']])
    return example_elements_char_letter

@pytest.fixture
def example_elements_char_letter():
    return generate_example_elements_char_letter()

def test_invalid_elements_char_letter(example_elements_char_letter):
    """Check that the help function to find the elements with the wrong letter
    (first character) works.

    GIVEN: the elements are in a form of a list of strings
    WHEN: the elements validity is tested
    THEN: the elements list contains only elements with the valid letters as
    first character
    """
    #Only the last example is incorrect
    for elements in example_elements_char_letter:
        (wrong_char_letter,
         wrong_char_letter_index) = invalid_elements_char_letter(elements)
        assert not wrong_char_letter, (
            'StructuralError for element(s) number '
            + str(wrong_char_letter_index) + ' ' + wrong_char_letter + ' in '
            + str(elements) + ' in invalid_elements_char_letter(). All '
            + 'elements must begin with a letter among \'C\', \'R\' ' + 'and '
            +  '\'Q\'')


def invalid_elements_char_number(elements_circuit):
    """Given the elements in the circuit that will figure in the fit, return
    any character that as a second character invalid, i.e. not numerical.
    Used for testing.

    Parameters
    ----------
    elements_circuit : list
        List of the elements in the circuit that will figure in the fit

    Returns
    -------
    wrong_char : str
        String that contains all the invalid elements, separated by a comma
        and a whitespace
    wrong_char_index : list
        List of indexes of the invalid invalid elements in the list
    """
    wrong_char = ''
    wrong_char_index = []
    for i, element in enumerate(elements_circuit):
        if not element[1].isnumeric():
            wrong_char += '\'' + str(element) + '\', '
            wrong_char_index.append(i)
        else:
            for j, other_element in enumerate(elements_circuit[i+1:]):
                if element[1]==other_element[1]:
                    wrong_char += ('(\'' + str(element) + '\', \''
                                   + str(other_element) + '\')')
                    wrong_char_index.append((i, j+i+1))
    return wrong_char, wrong_char_index

def generate_example_elements_char_number():
    """Generate examples for the invalid element number test. Only the last
    one is incorrect.
    """
    example_elements_char_number = ([['R1'], ['y1', '22'], ['Q1', 'C2', 'R3'],
                                     ['1C', 'C2', 'R2', 'R4']])
    return example_elements_char_number

@pytest.fixture
def example_elements_char_number():
    return generate_example_elements_char_number()

def test_invalid_elements_char_number(example_elements_char_number):
    """Check that the help function to find the elements with the wrong number
    (second character) works.

    GIVEN: the elements are in a form of a list of strings
    WHEN: the elements validity is tested
    THEN: the elements list contains only elements with the a valid number as
    as second character
    """
    #Only the last example is incorrect
    for elements in example_elements_char_number:
        (wrong_char_number,
            wrong_char_number_index) = invalid_elements_char_number(elements)
        assert not wrong_char_number, (
            'StructuralError for element(s) number '
            + str(wrong_char_number_index) + ' ' + wrong_char_number + ' in '
            + str(elements) + ' in invalid_elements_char_number(). All '
            + 'elements must end with a natural number and each element '
            + 'number must be unique')

def remove_elements(elements_list, diagram):
    """Given an element list of a circuit diagram and the diagram itself,
    removes th elements from the diagram.

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

def generate_example_elements_list_result():
    """Generate examples for the remove element test. Only the last
    one is incorrect.
    """
    element_list = [['R1'], ['C1', 'R2'], ['R3', 'Q4', 'R1', 'C2'], ['R1']]
    return element_list

@pytest.fixture
def example_elements_list_result():
    return generate_example_elements_list_result()

def generate_example_diagrams_elements_list():
    """Generate examples of removed diagrams for the remove element test."""
    example_diagrams_elements_list = ['(R1)', '(C1R2)', '(R1C2[R3Q4]',
                                      '[R1C2]']
    return example_diagrams_elements_list

@pytest.fixture
def example_diagrams_elements_list():
    return generate_example_diagrams_elements_list()

def test_remove_elements(example_elements_list_result,
                         example_diagrams_elements_list):
    """Check that the help function to remove the elementsfrom a diagram
    works.

    GIVEN: the element list and the diagrams are valid 
    WHEN: the element listing validity is tested
    THEN: the elements list contains all the elements
    """
    for i, elements_list in enumerate(example_elements_list_result):
        replaced_diagram = remove_elements(elements_list,
                                           example_diagrams_elements_list[i])
        assert set(replaced_diagram).issubset({'(', ')', '[', ']'}), (
            'StructuralError for the ' + str(i+1) + 'th example of '
            + 'remove_elements(). Some elements are not in the elements list')


def generate_example_elements_list():
    """Generate examples of element list for the list_elements test."""
    example_diagrams = generate_example_diagrams_elements_list()
    examples_element_list = []
    for diagram in example_diagrams:
        element_list = list_elements_circuit(diagram)
        examples_element_list.append(element_list)
    return examples_element_list

@pytest.fixture
def example_elements_list():
    return generate_example_elements_list()

def test_list_elements(example_elements_list, example_diagrams_elements_list):
    """Check if the list elements function works properly.

    GIVEN: the circuit diagram is valid
    WHEN: there is the necessity to list the elements of a diagram
    THEN: the list elements function works properly
    """
    caller = 'generate_circuit()'
    for i, elements_list in enumerate(example_elements_list):
        assert isinstance(elements_list, list), (
            'TypeError for output in ' + caller + '. It must be a list')
        wrong_types, wrong_types_index = invalid_elements_type(elements_list)
        assert not wrong_types, (
            'TypeError for element(s) number ' + str(wrong_types_index) + ' '
            + wrong_types + ' in ' + str(elements_list) + ' in ' + caller
            + '. Elements (here dictionary keys) can only be strings')
        wrong_length, wrong_length_index = invalid_elements_length(
            elements_list)
        assert not wrong_length, (
            'LengthError for element(s) number ' + str(wrong_length_index)
            + ' ' + wrong_length + ' in ' + str(elements_list) + ' in '
            + caller + '. Elements must all be of length 2')
        (wrong_char_letter,
            wrong_char_letter_index) = invalid_elements_char_letter(
                elements_list)
        assert not wrong_char_letter, (
            'StructuralError for element(s) number '
            + str(wrong_char_letter_index) + ' ' + wrong_char_letter + ' in '
            + str(elements_list) + ' in ' + caller + '. All elements must '
            + 'begin with a letter among \'C\', \'R\' ' + 'and \'Q\'')
        (wrong_char_number,
            wrong_char_number_index) = invalid_elements_char_number(
                elements_list)
        assert not wrong_char_number, (
            'StructuralError for element(s) number '
            + str(wrong_char_number_index) + ' ' + wrong_char_number + ' in '
            + str(elements_list) + ' in ' + caller + '. All elements must '
            + 'end with a natural number and each element number must be '
            + 'unique')
        
        replaced_diagram = remove_elements(elements_list,
                                           example_diagrams_elements_list[i])
        assert set(replaced_diagram).issubset({'(', ')', '[', ']'}), (
            'StructuralError for the ' + str(i+1) + 'th example of '
            + 'remove_elements(). Some elements are not in the elements list')

"""This module containes all the test functions (and the function needed for
the tests) for the generate_impedance.py module.
It assesses, for example, that both input data and the output of all the
fucntions in the module are valid.
"""


import inspect
import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis.extra import numpy as enp
import hypothesis.strategies as st

from generate_data import generate_circuit_data
from generate_data import generate_parameters_data
from generate_data import generate_constant_elements_array_data
from generate_data import set_frequencies
from generate_data import set_file_name
from generate_data import generate_random_error_component
from generate_data import simulate_noise
from generate_impedance import impedance_resistor
from generate_impedance import impedance_capacitor
from generate_impedance import impedance_cpe
from generate_impedance import get_impedance_const_input_element
from generate_impedance import get_impedance_input_element
from generate_impedance import get_impedance_function_element
from generate_impedance import add
from generate_impedance import serial_comb
from generate_impedance import reciprocal
from generate_impedance import parallel_comb
from generate_impedance import get_position_opening_bracket
from generate_impedance import generate_cell_impedance
from generate_impedance import update_string
from generate_impedance import generate_impedance_function
from plot_and_save import get_modulus
from plot_and_save import get_phase
from impedance_analysis import generate_circuit_fit
from impedance_analysis import generate_circuit_parameters
from impedance_analysis import generate_constant_elements_array_fit
from impedance_analysis import get_file_name
from impedance_analysis import get_number_of_columns
from impedance_analysis import read_data


##############################################################################
#String tests of generate_circuit_data() in generate_data.py

@pytest.fixture
def circuit_string():
    return generate_circuit_data()

@pytest.fixture
def caller():
    return 'generate_circuit_data()'

def test_is_string(circuit_string, caller):
    """Check that the circuit string is a string."""
    assert isinstance(circuit_string, str), (
        'type error for circuit scheme in ' + caller
        + '. It must be a string')

def test_empty_string(circuit_string, caller):
    """Check that the string is not empty."""
    assert circuit_string, 'empty string in ' + caller

def test_input_string_open_brakets(circuit_string, caller):
    """Check that there is an open round or square bracket as second character
    in the string.
    """
    assert (circuit_string.startswith('(')
            or circuit_string.startswith('[')), (
                'no initial open bracket detected in ' + caller)

def test_input_string_close_brakets(circuit_string, caller):
    """Check that there is a close round or square bracket as last character
    in the string.
    """
    assert (circuit_string.endswith(')')
            or circuit_string.endswith(']')), (
        'no final close bracket detected')

def same_number_of_brackets(circuit_string):
    """Given a circuit string, return if the count of open brackets is the
    same of close brackets. Used for testing.

    Parameters
    ----------
    circuit_string : string
        String of the circuit given by input

    Returns
    -------
    equality_count : bool
        Boolean of the equality count condition
    """
    equality_count = (
        circuit_string.count('(')==circuit_string.count(')')
        and circuit_string.count('[')==circuit_string.count(']'))
    return equality_count

def test_string_different_number_brackets(circuit_string, caller):
    """Check that there is an equal number of close and open bracket, for
    both square and round types.
    """
    assert same_number_of_brackets(circuit_string), (
        'inconsistent number of open and close brackets in \''
        + circuit_string + '\' in ' + caller)

def test_string_consistency_brackets(circuit_string, caller):
    """Check that there is a consistency among the brackets.

    GIVEN: circuit_string is a string with an equal number of open and
    close brackets of the same type (round or square)
    """
    position_of_brackets = [i for i, _ in enumerate(circuit_string)
                            if (circuit_string.startswith(')', i)
                                or circuit_string.startswith(']', i))]
    cut_parameter = 0
    for _ in position_of_brackets:
        for i, char_i in enumerate(circuit_string):
            if char_i in (')', ']'):
                if char_i==')': bracket, wrong_bracket = '(', '['
                if char_i==']': bracket, wrong_bracket = '[', '('
                found = False
                analyzed_string = circuit_string[:i]
                for j, _ in enumerate(analyzed_string):
                    bracket_index = len(analyzed_string) - 1 - j
                    if (circuit_string[bracket_index]==bracket
                        and not found):
                        found = True
                        index_wrong_bracket = circuit_string[
                            bracket_index+1:i].find(wrong_bracket)
                        assert index_wrong_bracket==-1, (
                            'inconsistent \'' + wrong_bracket + '\' at '
                            + str(index_wrong_bracket + bracket_index
                            + 1 + cut_parameter) + ': '
                            + circuit_string + ' in ' + caller)
                        circuit_string = (
                            circuit_string[:bracket_index]
                            + circuit_string[bracket_index+1:i]
                            + circuit_string[i+1:])
                        cut_parameter += 2
                        break
                if found:
                    break

def elements(circuit_string):
    """Return the list of elements ('C', 'Q' or 'R' ) of a string. Used for
    testing.

    Parameters
    ----------
    circuit_string : string
        String of the circuit given by input

    Returns
    -------
    elements_types : list
        List of single characters representing the type of elements in the
        same order as they are written
    """
    elements_types = []
    for char in circuit_string:
        if char in {'C', 'Q', 'R'}:
            elements_types.append(char)
    return elements_types

def test_no_element(circuit_string, caller):
    """Check if the circuit string contains at least an element type ('C',
    'Q' or 'R').
    """
    elements_types = elements(circuit_string)
    assert elements_types, (
        'Structural error: no element found in ' + circuit_string + ' from '
        + caller + '. An element begins with one of the three letter C, Q or '
        + 'R')

def find_invalid_characters(circuit_string):
    """Given a circuit string, return any invalid character, i.e. different
    than '(', ')', '[', ']', 'C', 'Q', 'R' or natural numbers. Used for
    testing.

    Parameters
    ----------
    circuit_string : string
        String of the circuit given by input

    Returns
    -------
    wrong_characters : string
        String that contains all the invald characters, sebarated by a comma
        and a space
    wrong_characters_index : list
        List of indexes of the invalid characters in the string
    """
    wrong_characters = ''
    wrong_characters_index = []
    for i, char in enumerate(circuit_string):
        if (char not in {'(', ')', '[', ']', 'C', 'Q', 'R'}
            and not char.isnumeric()):
            wrong_characters += '\'' + char + '\', '
            wrong_characters_index.append(i)
    return wrong_characters, wrong_characters_index

def test_input_string_characters(circuit_string, caller):
    """Check that a string containes only valid characters:
    '(', ')', '[', ']', 'C', 'Q', 'R' and natural numbers.
    """
    wrong_characters, wrong_characters_index = find_invalid_characters(
        circuit_string)
    assert not wrong_characters, (
        'Invalid character(s) ' + wrong_characters + ' at '
        + str(wrong_characters_index) + ' in ' + circuit_string + 'from '
        + caller + '. Only round and square brackets, C, Q, R and natural '
        + 'numbers are allowed')

def find_inconsistent_elements(circuit_string):
    """Given a circuit string, return any inconsistent element character: each
    element is composed by a capital letter among {'C', 'Q', 'R'} followed
    by a natural number. Used for testing.

    Parameters
    ----------
    circuit_string : string
        String of the circuit given by input

    Returns
    -------
    wrong_elements : string
        String that contains all the inconsistent elements, sebarated by a
        comma and a space
    wrong_element_index : list
        List of indexes of the inconsistent elements in the string
    """
    wrong_elements = ''
    wrong_element_index = []
    for i, char in enumerate(circuit_string):
        if (char in {'C', 'Q', 'R'} and circuit_string[-1]!=char):
            if not circuit_string[i+1].isnumeric():
                wrong_elements += ('\'' + char
                                   + str(circuit_string[i+1])
                                   + '\', ')
                wrong_element_index.append(i)
        elif (char.isnumeric() and circuit_string[0]!=char):
            if not (circuit_string[i-1] in {'C', 'Q', 'R'}):
                wrong_elements += ('\'' + str(circuit_string[i-1])
                                   + char + '\', ')
                wrong_element_index.append(i-1)
    return wrong_elements, wrong_element_index

def test_input_string_element_consistency(circuit_string, caller):
    """Check the element consistency of a string.

    GIVEN: a valid string
    """
    wrong_elements, wrong_element_index = find_inconsistent_elements(
        circuit_string)
    assert not wrong_elements, (
        'element inconsistency for '+ wrong_elements + ' at '
        + str(wrong_element_index) + ': ' + circuit_string + '. An '
        + 'element is composed by a valid letter followed by a natural '
        + 'number in ' + caller)

def find_inconsistent_numbers(circuit_string):
    """Given a circuit string, return any inconsistent element number: each
    element has a number that is the same of its order of writing in the
    string. Used for testing.

    Parameters
    ----------
    circuit_string : string
        String of the circuit given by input

    Returns
    -------
    wrong_numbers : string
        String that contains all the inconsistent element number, sebarated by
        a comma and a space
    wrong_numbers_index : list
        List of indexes of the inconsistent element number in the string
    """
    wrong_numbers = ''
    wrong_numbers_index = []
    numeric_char_counter = 0
    for i, char in enumerate(circuit_string):
        if char.isnumeric():
            numeric_char_counter += 1
            if numeric_char_counter!=int(char):
                wrong_numbers += ('\'' + str(circuit_string[i-1:i+1])
                                  + '\', ')
                wrong_numbers_index.append(i)
    return wrong_numbers, wrong_numbers_index

def test_input_string_number_sequency(circuit_string, caller):
    """Check that there is a correspondency between the element number and the
    order of appearance of its element.
    """
    wrong_numbers, wrong_numbers_index = find_inconsistent_numbers(
        circuit_string)
    assert not wrong_numbers, (
        'wrong number for element(s) '+ wrong_numbers + 'at '
        + str(wrong_numbers_index) + ' in ' + circuit_string + 'from '
        + caller + '. Element numbers must increase of 1 unit per time')

##############################################################################
#Parameters tests of generate_parameters_list() in generate_data.py

@pytest.fixture
def parameters_list():
    return generate_parameters_data()

def test_parameters_is_list(parameters_list, caller):
    """Check that the parameters are a list."""
    assert isinstance(parameters_list, list), (
        'type error for parameters in ' + caller + ' . It must be a list')

def find_invalid_parameters_type(parameters_list):
    """Given a parameters list, return any wrong type parameter: each
    parameter can be an integer, a float or a list. Used for testing.

    Parameters
    ----------
    parameters_list : list
        List of the parameters given by input

    Returns
    -------
    wrong_type : string
        String that contains all the invalid parameters, sebarated by a comma
        and a space
    wrong_type_index : list
        List of indexes of the invalid parameters in the list
    """
    wrong_type = ''
    wrong_type_index = []
    for i, parameter in enumerate(parameters_list):
        if (not isinstance(parameter, float)
            and not isinstance(parameter, int)
            and not isinstance(parameter, list)):
            wrong_type += '\'' + str(parameter) + '\', '
            wrong_type_index.append(i)
    return wrong_type, wrong_type_index

def test_parameters_type(parameters_list, caller):
    """Check that the only valid types as parameters are float, integer
    and lists.

    GIVEN: a list (parameters_list)
    """
    wrong_type, wrong_type_index = find_invalid_parameters_type(
        parameters_list)
    assert not wrong_type, (
        'type error for parameter(s) number ' + str(wrong_type_index)
        + ' ' + wrong_type + 'in ' + str(parameters_list) + ' in '
        + caller + '. Parameters can only be floats, integers or lists')

def find_invalid_parameters_value(parameters_list):
    """Given a parameters list, return any integer of float parameter that has
    a non-positive value, thus invalid. Used for testing.

    Parameters
    ----------
    parameters_list : list
        List of the parameters given by input

    Returns
    -------
    wrong_value : string
        String that contains all the invalid parameters, sebarated by a comma
        and a space
    wrong_value_index : list
        List of indexes of the invalid parameters in the list
    """
    wrong_value = ''
    wrong_value_index = []
    for i, parameter in enumerate(parameters_list):
        if isinstance(parameter, (float, int)):
            if parameter<=0:
                wrong_value += '\'' + str(parameter) + '\', '
                wrong_value_index.append(i)
    return wrong_value, wrong_value_index

def test_parameters_values(parameters_list, caller):
    """Check that parameters that are not a list are positive.

    GIVEN: parameters_list is a float, an integer or a list
    """
    wrong_value, wrong_value_index = find_invalid_parameters_value(
        parameters_list)
    assert not wrong_value, (
        'value error for parameter(s) number ' + str(wrong_value_index) + ' '
        + wrong_value + ' in ' + str(parameters_list) + ' in ' + caller
        + '. Float parameters must be positive')

def find_invalid_parameters_list(parameters_list):
    """Given a parameters list, return any parameter that is a list with a
    length different from 2, thus invalid. Used for testing.

    Parameters
    ----------
    parameters_list : list
        List of the parameters given by input

    Returns
    -------
    wrong_parameters : string
        String that contains all the invalid parameters, sebarated by a comma
        and a space
    wrong_parameters_index : list
        List of indexes of the invalid parameters in the list
    """
    wrong_parameters = ''
    wrong_parameters_index = []
    for i, parameter in enumerate(parameters_list):
        if isinstance(parameter, list):
            if len(parameter)!=2:
                wrong_parameters_index.append(i)
                wrong_parameters+= '\''+str(parameter)+'\', '
    return wrong_parameters, wrong_parameters_index

def test_parameters_list_two_elements(parameters_list, caller):
    """Check that the list parameters contain exactly 2 parameters.

    GIVEN: parameters_list is a float or integer
    """
    wrong_parameters, wrong_parameters_index = find_invalid_parameters_list(
        parameters_list)
    assert not wrong_parameters, (
        'type error for parameter(s) number ' + str(wrong_parameters_index)
        + ': \'' + wrong_parameters + '\' in ' + str(parameters_list)
        + ' in ' + caller + '. Lists parameters must contain exactly 2 '
        + 'parameters')

def find_invalid_parameters_list_type(parameters_list):
    """Given a parameters list, return any parameter that is a list and does
    not contains floats or integers, thus is invalid. Used for testing.

    Parameters
    ----------
    parameters_list : list
        List of the parameters given by input

    Returns
    -------
    wrong_type : string
        String that contains all the invalid parameters, sebarated by a comma
        and a space
    wrong_type_index : list
        List of indexes of the invalid parameters in the list
    """
    wrong_types = ''
    wrong_types_index = []
    for i, parameter in enumerate(parameters_list):
        if isinstance(parameter, list):
            for _, sub_prameter in enumerate(parameter):
                if (not isinstance(sub_prameter, float)
                    and not isinstance(sub_prameter, int)):
                    wrong_types += '\'' + str(sub_prameter) + '\', '
                    wrong_types_index.append(i)
    return wrong_types, wrong_types_index

def test_parameters_list_type(parameters_list, caller):
    """Check that parameters contains only floats or integers.

    GIVEN: parameters_list is a list of length 2.
    """
    wrong_types, wrong_types_index = find_invalid_parameters_list_type(
        parameters_list)
    assert not wrong_types, (
        'type error for parameter(s) '+ wrong_types  +' in parameter(s) '
        + 'number ' + str(wrong_types_index) + ' contained in: \'' + '\' in '
        + str(parameters_list) + ' in ' + caller + '. Lists parameters '
        + 'must only contain floats or integers')

def find_invalid_parameters_list_value(parameters_list):
    """Given a parameters list, return any parameter that is a list of length
    2 of floats or integers with invalid values: the second must be positive,
    the second must be within 0 and 1. Used for testing.

    Parameters
    ----------
    parameters_list : list
        List of the parameters given by input

    Returns
    -------
    wrong_value : string
        String that contains all the invalid parameters, sebarated by a comma
        and a space
    wrong_value_index : list
        List of indexes of the invalid parameters in the list
    """
    wrong_value = ''
    wrong_value_index = ''
    for i, parameter in enumerate(parameters_list):
        if isinstance(parameter, list):
            if parameter[0]<=0:
                wrong_value += '\'' + str(parameter[0]) + '\', '
                wrong_value_index += 'second of [' + str(i) + ']'
            if (parameter[1]<0 or parameter[1]>1):
                wrong_value += '\'' + str(parameter[1]) + '\', '
                wrong_value_index += 'second of [' + str(i) + ']'
    return wrong_value, wrong_value_index

def test_parameters_list_value(parameters_list, caller):
    """Check that the two object contained in the list parameters meet the
    value requirements: the second one is positive, the second one is between
    0 and 1.

    GIVEN: parameters is a list of float or integer of length 2.
    """
    wrong_value, wrong_value_index = find_invalid_parameters_list_value(
        parameters_list)
    assert not wrong_value, (
        'value error for parameter(s) '+ wrong_value + wrong_value_index
        + ' parameter(s) ' + ' contained in: \'' + str(parameters_list)
        + ' in ' + caller  + '. Lists parameters must contain as second '
        + 'parameter a positive float and as second parameter a float '
        + 'between 0 and 1')

def number_of_elements_is_equal_to_number_of_parameters(
        circuit_string, parameters_list):
    """Given the string circuit and its parameters list, return wheter the
    length of the parameters list and the number of elements in the string is
    the same. Used for testing

    Parameters
    ----------
    circuit_string : string
        String of the circuit given by input
    parameters_list : list
        List of the parameters given by input

    Returns
    -------
    length_equality : bool
        Boolean of the equality length condition
    """
    elements_types = elements(circuit_string)
    length_equality = len(elements_types)==len(parameters_list)
    return length_equality

def test_parameters_length(circuit_string, parameters_list, caller):
    """Check that the list of elements and the list of parameters
    have the same size.
    """
    length_equality = number_of_elements_is_equal_to_number_of_parameters(
        circuit_string, parameters_list)
    assert length_equality, (
        'element count and parameters list size must be the same in ' + caller
        + '. Element count: ' + str(len(length_equality))
        + ', parameters size: ' + str(len(parameters_list)))

def elements_parameters_match(circuit_string, parameters_list):
    """Given the string circuit and its parameters list, return any element
    and parameter that do not match in type: R and C have a float
    or integer type, while Q has a list. Used for testing.

    Parameters
    ----------
    circuit_string : string
        String of the circuit given by input
    parameters_list : list
        List of the parameters given by input

    Returns
    -------
    wrong_match : string
        String that contains all the invalid elements and parameters,
        sebarated by a comma and a space
    wrong_match_index : list
        List of indexes of the invalid elements in the string
    """
    elements_types = elements(circuit_string)
    wrong_match = ''
    wrong_match_index = []
    for i, elements_type in enumerate(elements_types):
        if elements_type in {'C', 'R'}:
            if (not isinstance(parameters_list[i], float)
                and not isinstance(parameters_list[i], int)):
                wrong_match += ('\'[' + str(elements_type) + ','
                                + str(parameters_list[i]) + ']\', ')
                wrong_match_index.append(i)
        else:
            if not isinstance(parameters_list[i], list):
                wrong_match += ('\'[' + str(elements_type) + ','
                                + str(parameters_list[i]) + ']\', ')
                wrong_match_index.append(i)
    return wrong_match, wrong_match_index, elements_types

def test_parameters_match(circuit_string, parameters_list, caller):
    """Check that there is a consistent correspondance between the elements
    and the parameters: C and R must have a float as parameter, Q a list.
    """
    wrong_match, wrong_match_index, elements_type = elements_parameters_match(
        circuit_string, parameters_list)
    assert not wrong_match, (
        'bad match for '+ wrong_match + ' in ' + str(wrong_match_index)
        + ': elements \'' + str(elements_type) + ' with parameters '
        + str(parameters_list) + 'from ' + caller + '. \'R\' and \'C\' ' 
        + 'elements must have a float as parameter, \'Q\' must have a list')

##############################################################################
#Constant vector tests

def return_constant_elements_array_data():
    parameters_list = generate_parameters_data()
    constant_elements_array_data = generate_constant_elements_array_data(
        parameters_list)
    return constant_elements_array_data

@pytest.fixture
def constant_elements_list():
    return return_constant_elements_array_data()

def test_constant_type(constant_elements_list, caller):
    """Check that the constant arrey is a list."""
    assert isinstance(constant_elements_list, list), (
        'type error for circuit scheme in ' + caller + '. It must be a list')

def find_invalid_constant_type(constant_elements_list):
    """Given a constant elements condition list, return any wrong type
    constant elements condition: they can only be integers. Used for testing.

    Parameters
    ----------
    constant_elements_list : list
        List of the constant elements condition given by input

    Returns
    -------
    wrong_type : string
        String that contains all the invalid constant elements conditions,
        sebarated by a comma and a space
    wrong_type_index : list
        List of indexes of the invalid invalid constant elements conditions in
        the list
    """
    wrong_types = ''
    wrong_types_index = []
    for i, constant_element in enumerate(constant_elements_list):
        if not isinstance(constant_element, int):
            wrong_types+= '\'' + str(constant_element) + '\', '
            wrong_types_index.append(i)
    return wrong_types, wrong_types_index

def test_constant_list_type(constant_elements_list, caller):
    """Check that the constant elements in constant_elements are integers.

    GIVEN: constant_elements_list is an array
    """
    wrong_types, wrong_types_index = find_invalid_constant_type(
        constant_elements_list)
    assert not wrong_types, (
        'type error for constant element(s) ' + str(wrong_types) + ' number '
        + str(wrong_types_index) + ' in ' + str(constant_elements_list)
        + 'from ' + caller + '. Constant element must be an integer')

def find_invalid_constant_value(constant_elements_list):
    """Given a constant_elements list, return any wrong type constant elements
    condition: each on can only be either 0 or 1. Used for testing.

    Parameters
    ----------
    constant_elements_list : list
        List of the constant elements condition given by input

    Returns
    -------
    wrong_value : string
        String that contains all the invalid constant elements conditions,
        sebarated by a comma and a space
    wrong_value_index : list
        List of indexes of the invalid invalid constant elements conditions in
        the list
    """
    wrong_value = ''
    wrong_value_index = []
    for i, constant_element in enumerate(constant_elements_list):
        if constant_element<0 or constant_element>1:
            wrong_value+= '\'' + str(constant_element) + '\', '
            wrong_value_index.append(i)
    return wrong_value, wrong_value_index

def test_constant_list_value(constant_elements_list, caller):
    """Check that the constant elements in constant_elements_list are non
    negative.

    GIVEN: constant_elements_list an array
    """
    wrong_value, wrong_value_index = find_invalid_constant_value(
        constant_elements_list)
    assert not wrong_value, (
        'value error for constant element(s) '+ wrong_value + 'at '
        + str(wrong_value_index) + 'in \'' + str(constant_elements_list)
        + '\' from ' + caller + '. Constant array must contain only 0 or 1')

def number_of_parameters_is_equal_to_number_of_const_elements(
        parameters_list, constant_elements_list):
    """Given the parameters of a circuit and they constant conditions, return
    wheter the length of the parameters list and the constant conditions list
    is the same. Used for testing

    Parameters
    ----------
    parameters_list : list
        List of the parameters given by input
    constant_elements_list : list
        List of the constant elements condition given by input

    Returns
    -------
    length_equality : bool
        Boolean of the equality length condition
    """
    length_equality = len(parameters_list)==len(constant_elements_list)
    return length_equality

def test_constant_length(parameters_list, constant_elements_list, caller):
    """Check that the list of elements and the list of parameters have
    the same size.
    """
    length_equality = number_of_parameters_is_equal_to_number_of_const_elements(
        parameters_list, constant_elements_list)
    assert length_equality, (
        'Error from ' + caller + ': parameters and constant array list size'
        + 'must be the same. Parameters size: ' + str(len(parameters_list))
        + ', constant array size: ' + str(len(constant_elements_list)))

##############################################################################
#generate_impedance.py test

@given(impedance=enp.arrays(dtype=float, shape=10, elements=st.floats(1, 1e4),
                            unique=True),
       resistance=st.floats(min_value=10, max_value=1e5))
@settings(max_examples = 10)
def test_impedance_resistor_array(resistance, impedance):
    """Check that the definition of the impedance of resistors returns an
    array.
    """
    impedance = impedance_resistor(resistance, impedance)
    assert isinstance(impedance, np.ndarray), (
        'type error for resistive impedance. It must be a numpy array')

@given(impedance=enp.arrays(dtype=float, shape=10, elements=st.floats(1, 1e4),
                            unique=True),
       resistance=st.floats(min_value=10, max_value=1e5))
@settings(max_examples = 10)
def test_impedance_resistor_complex_array(resistance, impedance):
    """Check that the definition of the impedance of resistors returns a
    complex object.
    """
    impedance = impedance_resistor(resistance, impedance)
    assert np.iscomplexobj(impedance), (
        'type error for resistive impedance. It must be a complex '
        + 'numpy array')

@given(impedance=enp.arrays(dtype=float, shape=10, elements=st.floats(1, 1e4),
                            unique=True),
       resistance=st.floats(min_value=10, max_value=1e5))
@settings(max_examples = 10)
def test_impedance_resistor_empty(resistance, impedance):
    """Check that the definition of the impedance of resistors returns an
    array that is not empty.
    """
    impedance = impedance_resistor(resistance, impedance)
    assert impedance.size>0, ('structural error for resistive impedance. It'
                              + 'cannot be empty')

@given(impedance=enp.arrays(dtype=float, shape=10, elements=st.floats(1, 1e4),
                            unique=True),
       capacitance=st.floats(min_value=1e-9, max_value=1e-5))
@settings(max_examples = 10)
def test_impedance_capacitor_array(capacitance, impedance):
    """Check that the definition of the impedance of capacitors returns an
    array.
    """
    impedance = impedance_capacitor(capacitance, impedance)
    assert isinstance(impedance, np.ndarray), (
        'type error for capacitative impedance. It must be a numpy array')

@given(impedance=enp.arrays(dtype=float, shape=10, elements=st.floats(1, 1e4),
                            unique=True),
       capacitance=st.floats(min_value=1e-9, max_value=1e-5))
@settings(max_examples = 10)
def test_impedance_capacitor_complex_array(capacitance, impedance):
    """Check that the definition of the impedance of capacitors returns a
    complex object.
    """
    impedance = impedance_capacitor(capacitance, impedance)
    assert np.iscomplexobj(impedance), (
        'type error for capacitative impedance. It must be a complex numpy '
        + 'array')

@given(impedance=enp.arrays(dtype=float, shape=10, elements=st.floats(1, 1e4),
                            unique=True),
       capacitance=st.floats(min_value=1e-9, max_value=1e-5))
@settings(max_examples = 10)
def test_impedance_capacitor_empty(capacitance, impedance):
    """Check that the definition of the impedance of capacitors returns an
    array that is not empty.
    """
    impedance = impedance_capacitor(capacitance, impedance)
    assert impedance.size>0, ('structural error for capacitative impedance.'
                              + 'It cannot be empty')

@given(impedance=enp.arrays(dtype=float, shape=10, elements=st.floats(1, 1e4),
                            unique=True),
       q_parameter=st.floats(min_value=1e-9, max_value=1e-5),
       ideality_factor=st.floats(min_value=0., max_value=1.))
@settings(max_examples = 10)
def test_impedance_cpe_array(q_parameter, ideality_factor, impedance):
    """Check that the definition of the impedance of CPE returns an array."""
    impedance = impedance_cpe(q_parameter, ideality_factor, impedance)
    assert isinstance(impedance, np.ndarray), (
        'type error for CPE impedance. It must be a numpy array')

@given(impedance=enp.arrays(dtype=float, shape=10, elements=st.floats(1, 1e4),
                            unique=True),
       q_parameter=st.floats(min_value=1e-9, max_value=1e-5),
       ideality_factor=st.floats(min_value=0., max_value=1.))
@settings(max_examples = 10)
def test_impedance_cpe_complex_array(q_parameter, ideality_factor, impedance):
    """Check that the definition of the impedance of CPE returns a complex
    object.
    """
    impedance = impedance_cpe(q_parameter, ideality_factor, impedance)
    assert np.iscomplexobj(impedance), (
        'type error for CPE impedance. It must be a complex numpy array')

@given(impedance=enp.arrays(dtype=float, shape=10, elements=st.floats(1, 1e4),
                            unique=True),
       q_parameter=st.floats(min_value=1e-9, max_value=1e-5),
       ideality_factor=st.floats(min_value=0., max_value=1.))
@settings(max_examples = 10)
def test_impedance_cpe_empty(q_parameter, ideality_factor, impedance):
    """Check that the definition of the impedance of CPE returns a
    array that is not empty.
    """
    impedance = impedance_cpe(q_parameter, ideality_factor, impedance)
    assert impedance.size>0, ('structural error for CPE impedance.'
                              + 'It cannot be empty')

def generate_element_types():
    """Generate the three possible element types."""
    element_types = (['R', 'C', 'Q'])
    return element_types

@pytest.fixture
def element_types():
    return generate_element_types()

def generate_parameters_types_input():
    """Generate three possible element parameters."""
    element_parameters_const = ([10, 3e-6, [2e-6, 0.5]])
    return element_parameters_const

@pytest.fixture
def parameters_type_input():
    return generate_parameters_types_input()

def find_wrong_impedance_get_impedance_const_input(element_types,
                                                   parameters_type_input):
    """Given the element types that get_impedance_const_input takes in input,
    find for which element the retuned impedance function is not a function.
    Used for testing

    Parameters
    ----------
    element_types : list
        List of the element types given by input
    element_parameters_type : list
        List of the parameters given by input

    Returns
    -------
    wrong_elements : string
        String that contains all the wrong elements, sebarated by a comma and
        a space
    wrong_element_index : list
        List of indexes of the wrong elements in the string
    """
    wrong_element = ''
    wrong_element_index = []
    for i, element_type in enumerate(element_types):
        const_parameter = parameters_type_input[i]
        impedance_element = get_impedance_const_input_element(element_type,
                                                        const_parameter)
        if not inspect.isfunction(impedance_element):
            wrong_element+= '\'' + str(element_type) + '\', '
            wrong_element_index.append(i)
    return wrong_element, wrong_element_index

def test_get_impedance_const_input_element(element_types,
                                           parameters_type_input):
    """Check that get_impedance_const_input_element_type function returns a
    function.

    GIVEN: element_type is a valid element type (R, C or Q) and a valid
    parameter.
    WHEN: I am calculating the correspondant impedance function while keeping
    the parameter(s) of this element constant.
    THEN: the impedance funtion is a function
    """
    (wrong_element,
     wrong_element_index) = find_wrong_impedance_get_impedance_const_input(
         element_types, parameters_type_input)
    assert not wrong_element, (
        'type error in output of get_impedance_const_input_element_type() '
        + 'for element type(s) number ' + str(wrong_element_index)
        + ' \'' + wrong_element + '\' in ' + str(element_types)
        + '. Impedance function for an element must return a function')

def generate_analyzed_parameters():
    """Generate a possible list of already analyzed parameters list."""
    analyzed_parameters = ([100])
    return analyzed_parameters

@pytest.fixture
def analyzed_parameters():
    return generate_analyzed_parameters()

def find_wrong_impedance_get_impedance_input(element_types,
                                             analyzed_parameters,
                                             parameters_type_input):
    """Given the element types that get_impedance_const_input takes in input,
    find for which element the retuned impedance function is not a function.
    Used for testing

    Parameters
    ----------
    element_types : list
        List of the element types given by input
    analyzed_parameters : list
        List of parameters of elements previously analyzed, that will figure
        in the fit
    parameters_type_input : list
        List of the parameters given by input

    Returns
    -------
    wrong_elements : string
        String that contains all the wrong elements, sebarated by a comma and
        a space
    wrong_element_index : list
        List of indexes of the wrong elements in the string
"""
    wrong_element = ''
    wrong_element_index = []
    for i, element_type in enumerate(element_types):
        impedance_element, _ = get_impedance_input_element(
            element_type, analyzed_parameters, parameters_type_input[i])
        if not inspect.isfunction(impedance_element):
            wrong_element+= '\'' + str(element_type) + '\', '
            wrong_element_index.append(i)
    return wrong_element, wrong_element_index

def test_get_impedance_input_element_function(element_types,
                                              analyzed_parameters,
                                              parameters_type_input):
    """Check that get_impedance_input_element function returns a function as
    second argument.

    GIVEN: element_type as a valid element type (R, C or Q), a valid parameter
    and a valid parameter list.
    WHEN: I am calculating the correspondant impedance function.
    THEN: the impedance funtion is a function.
    """
    (wrong_element,
     wrong_element_index) = find_wrong_impedance_get_impedance_input(
         element_types, analyzed_parameters, parameters_type_input)
    assert not wrong_element, (
        'type error in output of get_impedance_input_element() '
        + 'for element type(s) number ' + str(wrong_element_index)
        + ' \'' + wrong_element + '\' in ' + str(element_types)
        + '. Impedance function for an element must return as second argument '
        + 'a function')

def test_get_impedance_input_element_parameters(element_types,
                                                analyzed_parameters,
                                                parameters_type_input):
    """ Check that the second argument of get_impedance_input_element function
    is a valid list of parameters.

    GIVEN: a valid element type (R, C or Q), a valid description of the
    circuit and valid parameters of the analysed circuit so far.
    WHEN: I am calculating the correspondant impedance function.
    THEN: the parameters for the current element funtion are valid.
    """
    caller = 'get_impedance_input_element()'
    for i, element_type in enumerate(element_types):
        _, parameters_test = get_impedance_input_element(
            element_type, analyzed_parameters, parameters_type_input[i])
        test_parameters_is_list(parameters_test, caller)
        test_parameters_type(parameters_test, caller)
        test_parameters_list_two_elements(parameters_test, caller)
        test_parameters_list_type(parameters_test, caller)
        test_parameters_values(parameters_test, caller)
        test_parameters_list_value(parameters_test, caller)

def generate_element_strings():
    """Generate the three possible element types. Used for testing."""
    elements_string_type = (['R2', 'C2', 'Q2', 'Z2'])
    return elements_string_type

@pytest.fixture
def elements_string_type():
    return generate_element_strings()

def generate_impedance_circuit():
    """Generate the impedance function of a circuit of just a 100 Ohm
    resistor, to simulate a portion of the circuit already analyzed. Used for
    testing.
    """
    element_type = 'R'
    list_parameters = []
    element_parameter = 100
    impedance_circuit = []
    impedance_element, _ = get_impedance_input_element(element_type,
                                                     list_parameters,
                                                     element_parameter)
    impedance_circuit.append(impedance_element)
    impedance_circuit.append(impedance_element)
    return impedance_circuit

@pytest.fixture
def impedance_circuit():
    return generate_impedance_circuit()

def generate_possible_parameters():
    """Generate a list of possible parameters (one ofor each type)."""
    possible_parameters = ([10, 2e-6, [1e-6, 0.5], 100])
    return possible_parameters

@pytest.fixture
def possible_parameters():
    return generate_possible_parameters()

def generate_analyzed_elements():
    """Generate a possible list of already analyzed elements list."""
    analyzed_elements = (['R1'])
    return analyzed_elements

@pytest.fixture
def analyzed_elements():
    return generate_analyzed_elements()

def generate_constant_elements_two_parameters():
    """Generate the three possible element types."""
    constant_elements_two_parameters = ([0, 0])
    return constant_elements_two_parameters

@pytest.fixture
def constant_elements_two_parameters():
    return generate_constant_elements_two_parameters()

def find_wrong_impedance_get_impedance_function_element(
        elements_string_type, impedance_circuit, possible_parameters,
        analyzed_parameters, analyzed_elements,
        constant_elements_two_parameters):
    """Given the input for get_impedance_function_element(), find for which
    element the retuned impedance function is not a function. Used for
    testing.
    """
    wrong_element = ''
    wrong_element_index = []
    nominal_parameters = ([100, 0])
    for i, element_string in enumerate(elements_string_type):
        nominal_parameters[1] = possible_parameters[i]
        elements_circuit = analyzed_elements.copy()
        impedance_element, *_ = get_impedance_function_element(
            element_string, impedance_circuit, nominal_parameters,
            analyzed_parameters, elements_circuit,
            constant_elements_two_parameters)
        if not inspect.isfunction(impedance_element):
            wrong_element+= '\'' + str(element_string) + '\', '
            wrong_element_index.append(i)
    return wrong_element, wrong_element_index

def test_get_impedance_function_element_function(
        elements_string_type, impedance_circuit, possible_parameters,
        analyzed_parameters, analyzed_elements,
        constant_elements_two_parameters):
    """Check that get_impedance_function_element function returns a function
    as second argument.

    GIVEN: a valid element type (R, C, Q or Z followed by a number), a valid
    description of the circuit and valid parameters of the analysed circuit so
    far.
    WHEN: I am calculating the correspondant impedance function.
    THEN: the impedance funtion is a function.
    """
    (wrong_element,
     wrong_element_index) = find_wrong_impedance_get_impedance_function_element(
        elements_string_type, impedance_circuit, possible_parameters,
        analyzed_parameters, analyzed_elements,
        constant_elements_two_parameters)
    assert not wrong_element, (
        'type error in output of get_impedance_function() '
        + 'for element type(s) number ' + str(wrong_element_index)
        + ' \'' + wrong_element + '\' in ' + str(elements_string_type)
        + '. Impedance function for an element must return as second argument '
        + 'a function')

def test_get_impedance_function_element_parameters(
        elements_string_type, impedance_circuit, possible_parameters,
        analyzed_parameters, analyzed_elements,
        constant_elements_two_parameters):
    """Check that the second argument of get_impedance_function_element
    function is a valid list of parameters.

    GIVEN: a valid element type (R, C or Q), a valid description of the
    circuit and valid parameters of the analysed circuit so far.
    WHEN: I am calculating the correspondant impedance function.
    THEN: the list of parameters for the current funtion are valid.
    """
    caller = 'get_impedance_function_element()'
    nominal_parameters = ([100, 0])
    for i, element_string in enumerate(elements_string_type):
        nominal_parameters[1] = possible_parameters[i]
        elements_circuit = analyzed_elements.copy()
        _, parameters_test, _ = get_impedance_function_element(
            element_string, impedance_circuit, nominal_parameters,
            analyzed_parameters, elements_circuit,
            constant_elements_two_parameters)
        test_parameters_is_list(parameters_test, caller)
        test_parameters_type(parameters_test, caller)
        test_parameters_list_two_elements(parameters_test, caller)
        test_parameters_list_type(parameters_test, caller)
        test_parameters_values(parameters_test, caller)
        test_parameters_list_value(parameters_test, caller)

def elements_is_list(elements_circuit, caller):
    """Check that the elements_circuit is a list."""
    assert isinstance(elements_circuit, list), (
        'type error for elements in ' + caller + ' . It must be a list')

def find_invalid_elements_type(elements_circuit):
    """Given the elements in the circuit that will figure in the fit, return
    any character that is not a string. Used for testing.

    Parameters
    ----------
    elements_circuit : list
        List of the elements in the circuit that will figure in the fit

    Returns
    -------
    wrong_type : string
        String that contains all the invalid elements, separated by a comma
        and a space
    wrong_type_index : list
        List of indexes of the invalid invalid elements in the list
    """
    wrong_types = ''
    wrong_types_index = []
    for i, element in enumerate(elements_circuit):
        if not isinstance(element, str):
            wrong_types+= '\'' + str(element) + '\', '
            wrong_types_index.append(i)
    return wrong_types, wrong_types_index

def elements_type(elements_circuit, caller):
    """Check that the list elements_circuit is a string list.

    GIVEN: elements_circuit is a list.
    """
    wrong_types, wrong_types_index = find_invalid_elements_type(
        elements_circuit)
    assert not wrong_types, (
        'type error for element(s) number ' + str(wrong_types_index) + ' '
        + wrong_types + ' in ' + str(elements_circuit) + ' in ' + caller
        + '. Elements can only be strings')

def find_invalid_elements_length(elements_circuit):
    """Given the elements in the circuit that will figure in the fit, return
    any element with a length different than 2, thus invalid. Used for
    testing.

    Parameters
    ----------
    elements_circuit : list
        List of the elements in the circuit that will figure in the fit

    Returns
    -------
    wrong_length : string
        String that contains all the invalid elements, separated by a comma
        and a space
    wrong_length_index : list
        List of indexes of the invalid invalid elements in the list
    """
    wrong_length = ''
    wrong_length_index = []
    for i, element in enumerate(elements_circuit):
        if len(element)!=2:
            wrong_length += '\'' + str(element) + '\', '
            wrong_length_index.append(i)
    return wrong_length, wrong_length_index

def elements_string_length(elements_circuit, caller):
    """Check that each string in elements_circuit has a length of 2.

    GIVEN: elements_circuit is a list of strings.
    """
    wrong_length, wrong_length_index = find_invalid_elements_length(
        elements_circuit)
    assert not wrong_length, (
        'length error for element(s) number ' + str(wrong_length_index)
        + ' ' + wrong_length + ' in ' + str(elements_circuit) + ' in '
        + caller + '. Elements must all be of length 2')


def find_invalid_elements_char_letter(elements_circuit):
    """Given the elements in the circuit that will figure in the fit, return
    any character that as a fist character invalid, i.e. any out of R, C, Q.
    Used for testing.

    Parameters
    ----------
    elements_circuit : list
        List of the elements in the circuit that will figure in the fit

    Returns
    -------
    wrong_char : string
        String that contains all the invalid elements, separated by a comma
        and a space
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


def elements_letter(elements_circuit, caller):
    """Check that each string in elements_circuit has a valid second character:
    either R, C or Q.

    GIVEN: elements_circuit is a list of strings of length 2.
    """
    wrong_char, wrong_char_index = find_invalid_elements_char_letter(
        elements_circuit)
    assert not wrong_char, (
        'structural error for element(s) number ' + str(wrong_char_index)
        + ' ' + wrong_char + ' in ' + str(elements_circuit) + ' in '
        + caller + '. All elements must begin with a letter among \'C\', '
        + '\'R\' and \'Q\'')

def find_invalid_elements_char_number(elements_circuit):
    """Given the elements in the circuit that will figure in the fit, return
    any character that as a second character invalid, i.e. not numerical.
    Used for testing.

    Parameters
    ----------
    elements_circuit : list
        List of the elements in the circuit that will figure in the fit

    Returns
    -------
    wrong_char : string
        String that contains all the invalid elements, separated by a comma
        and a space
    wrong_char_index : list
        List of indexes of the invalid invalid elements in the list
    """
    wrong_char = ''
    wrong_char_index = []
    for i, element in enumerate(elements_circuit):
        if not element[1].isnumeric():
            wrong_char += '\'' + str(element) + '\', '
            wrong_char_index.append(i)
    return wrong_char, wrong_char_index

def elements_number(elements_circuit, caller):
    """Check that each string in elements_circuit has a valid second character
    (a number).

    GIVEN: elements_circuit is a list of strings of length 2.
    """
    wrong_char, wrong_char_index = find_invalid_elements_char_number(
        elements_circuit)
    assert not wrong_char, (
        'structural error for element(s) number ' + str(wrong_char_index)
        + ' ' + wrong_char + ' in ' + str(elements_circuit) + ' in ' + caller
        + '. All elements must end with a natural number')

def find_elements_duplicate(elements_circuit):
    """Given the elements in the circuit that will figure in the fit, return
    any element that has the same number of a previous one. Used for testing.

    Parameters
    ----------
    elements_circuit : list
        List of the elements in the circuit that will figure in the fit

    Returns
    -------
    wrong_char : string
        String that contains all the duplictaes elements, separated by a comma
        and a space
    wrong_char_index : list
        List of indexes of the invalid duplictaes elements in the list
    """
    wrong_char = ''
    wrong_char_index = []
    for i, element in enumerate(elements_circuit):
        if element[1].isnumeric():
            for j, other_element in enumerate(elements_circuit[i+1:]):
                if element[1]==other_element[1]:
                    wrong_char += '\'' + str(element[1]) + '\', '
                    wrong_char_index.append((i, j+i+1))
    return wrong_char, wrong_char_index

def elements_number_duplicates(elements_circuit, caller):
    """Check that in elements_circuit there is no duplicate in number.

    GIVEN: elements_circuit is a list of strings of length 2, with as second
    character a number.
    """
    wrong_char, wrong_char_index = find_elements_duplicate(elements_circuit)
    assert not wrong_char, (
        'structural error for element(s). Found duplicate of number '
        + wrong_char + ' in positions ' + str(wrong_char_index) + ' in '
        + str(elements_circuit) + ' in ' + caller + '. Each element number '
        + 'must be unique')

def test_get_impedance_function_element_elements(
        elements_string_type, impedance_circuit, possible_parameters,
        analyzed_parameters, analyzed_elements,
        constant_elements_two_parameters):
    """Check that get_impedance_function_element() returns a valid elements
    array.

    GIVEN: a valid element type (R, C or Q), a valid description of the
    circuit and valid parameters of the analysed circuit so far.
    WHEN: I am calculating the correspondant impedance function.
    THEN: the list of elements for the current funtion are valid.
    """
    caller = 'get_impedance_function_element()'
    nominal_parameters = ([100, 0])
    for i, element_string in enumerate(elements_string_type):
        nominal_parameters[1] = possible_parameters[i]
        elements_circuit = analyzed_elements.copy()
        *_, elements_circuit = get_impedance_function_element(
            element_string, impedance_circuit, nominal_parameters,
            analyzed_parameters, elements_circuit,
            constant_elements_two_parameters)
        elements_is_list(elements_circuit, caller)
        elements_type(elements_circuit, caller)
        elements_string_length(elements_circuit, caller)
        elements_letter(elements_circuit, caller)
        elements_number(elements_circuit, caller)
        elements_number_duplicates(elements_circuit, caller)

def generate_first_function():
    """Generate a function."""
    first_function = lambda x, y: x + y
    return first_function

@pytest.fixture
def first_function():
    return generate_first_function()

def generate_second_fucntion():
    """Generate a function."""
    second_function = lambda x, y: x*y
    return second_function

@pytest.fixture
def second_function():
    return generate_second_fucntion()

def test_add(first_function, second_function):
    """Check that the add function returns a function.

    GIVEN: first_function, second_function are functions.
    WHEN: I want the sum function of them.
    THEN: the sum function is a function.
    """
    assert inspect.isfunction(add(first_function, second_function)),(
        'type error in output of add(). It must be a function')

def generate_function_list():
    """Generate a list of function."""
    first_function = lambda x, y: x + y
    second_function = lambda x, y: x*y
    function_list = ([first_function, second_function])
    return function_list

@pytest.fixture
def function_list():
    return generate_function_list()

def test_serial_comb(function_list):
    """Check that the serial_comb function returns a function.

    GIVEN: function_list is a list of fucntions.
    WHEN: I want the equivalent function of a serial comb of them.
    THEN: the equivalent function is a function.
    """
    assert inspect.isfunction(serial_comb(function_list)), (
        'type error in output of serial_comb(). It must be a function')

def generate_function():
    """Generate a function."""
    function_ = lambda x, y: x*y
    return function_

@pytest.fixture
def function_():
    return generate_function()

def test_reciprocal(function_):
    """Check that the add function returns a function.

    GIVEN: function_ is a funtion.
    WHEN: I want the inverse function of function_.
    THEN: the inverse function is a function.
    """
    assert inspect.isfunction(reciprocal(function_)),(
        'type error in output of reciprical(). It must be a function')

def test_parallel_comb(function_list):
    """Check that the serial_comb function returns a function.

    GIVEN: function_list is a list of fucntions.
    WHEN: I want the equivalent function of a parallel comb of them.
    THEN: the equivalent function is a function.
    """
    assert inspect.isfunction(parallel_comb(function_list)), (
        'type error in output of parallelComb(). It must be a function')

def generate_circuit():
    """Generate a test circuit string."""
    circuit_string = '(R1C2[R3Q4])'
    return circuit_string

@pytest.fixture
def valid_circuit_string():
    return generate_circuit()

def generate_i_end():
    """Generate a position for a close bracket."""
    i_end = 10
    return i_end

@pytest.fixture
def i_end():
    return generate_i_end()

def test_get_position_opening_bracket_type(valid_circuit_string, i_end):
    """Check that get_position_opening_bracket() returns an integer.

    GIVEN: a valid string, i_end is the position of a closed bracket.
    """
    last_opening_bracket_position = get_position_opening_bracket(
        valid_circuit_string, i_end)
    assert isinstance(last_opening_bracket_position, int), (
        'type error in output of get_position_opening_bracket(). Last '
        + 'opening bracket position must be an integer')

def test_get_position_opening_bracket_value(valid_circuit_string, i_end):
    """Check that get_position_opening_bracket() returns a non-negative
    number.

    GIVEN: a valid string, i_end is the position of a closed bracket and
    last_opening_bracket_position is an integer.
    """
    last_opening_bracket_position = get_position_opening_bracket(
        valid_circuit_string, i_end)
    assert last_opening_bracket_position>=0, ('value error in output of '
        + 'get_position_opening_bracket(). Last opening bracket position '
        + 'must be non-negative')

def generate_i_start():
    """Generate a position for a closing bracket."""
    i_end = generate_i_end()
    circuit_string = generate_circuit()
    i_start = get_position_opening_bracket(
        circuit_string, i_end)
    return i_start

@pytest.fixture
def i_start():
    return generate_i_start()

def generate_initial_parameters():
    """Generate a list of parameters."""
    parameter_1 = 7000
    parameter_2 = 8e-6
    parameter_3 = 10000
    parameter_4 = ([0.07e-6, 0.7])
    initial_parameters = ([parameter_1, parameter_2, parameter_3,
                           parameter_4])
    return initial_parameters

@pytest.fixture
def valid_parameters():
    return generate_initial_parameters()

def generate_constant_elements_array():
    """Generate an array for constant elements."""
    constant_array = ([0, 0, 1, 0])
    return constant_array

@pytest.fixture
def valid_constant_elements():
    return generate_constant_elements_array()

def test_generate_cell_impedance_function_list(
        valid_circuit_string, i_start, i_end, impedance_circuit,
        valid_parameters, analyzed_parameters,
        analyzed_elements, valid_constant_elements):
    """Check that get_impedance_function_element function returns a list
    as second argument.

    GIVEN: a proper description of the circuit
    """
    impedance_cell, *_ = generate_cell_impedance(
        valid_circuit_string, i_start, i_end, impedance_circuit,
        valid_parameters, analyzed_parameters,
        analyzed_elements, valid_constant_elements)
    assert isinstance(impedance_cell, list), (
        'type error in output of generate_cell_impedance(). Its second '
        + 'argument must be a list')

def find_wrong_generate_cell_impedance_element(
        valid_circuit_string, i_start, i_end, impedance_circuit,
        valid_parameters, analyzed_parameters,
        analyzed_elements, valid_constant_elements):
    """Given the input for generate_cell_impedance(), find for which
    element the retuned impedance function is not a function. Used for
    testing.
    """
    wrong_type_index = []
    impedance_cell, *_ = generate_cell_impedance(
        valid_circuit_string, i_start, i_end, impedance_circuit,
        valid_parameters, analyzed_parameters,
        analyzed_elements, valid_constant_elements)
    for i, function in enumerate(impedance_cell):
        if not inspect.isfunction(function):
            wrong_type_index.append(i)
    return wrong_type_index

def test_generate_cell_impedance_function_type(
        valid_circuit_string, i_start, i_end, impedance_circuit,
        valid_parameters, analyzed_parameters,
        analyzed_elements, valid_constant_elements):
    """Check that generate_cell_impedance_function() returns a list of
    functions.

    GIVEN: generate_cell_impedance() returns a list as second argument
    """
    wrong_type_index = find_wrong_generate_cell_impedance_element(
        valid_circuit_string, i_start, i_end, impedance_circuit,
        valid_parameters, analyzed_parameters,
        analyzed_elements, valid_constant_elements)
    assert not wrong_type_index, (
        'type error for function(s) number ' + str(wrong_type_index) + ' '
        + ' in ' + str(analyzed_elements) + ', in output of '
        + 'generate_cell_impedance(). Its second argument must be a list of '
        + 'functions')

def test_generate_cell_impedance_parameters(
        valid_circuit_string, i_start, i_end, impedance_circuit,
        valid_parameters, analyzed_parameters,
        analyzed_elements, valid_constant_elements):
    """Check that the second argument of generate_cell_impedance function is
    a valid list of parameters.

    GIVEN: a valid circuit string, a valid description of the
    circuit and valid parameters of the analysed circuit so far.
    WHEN: I am calculating the correspondant impedance function of a cell.
    THEN: the list of parameters for the current funtion are valid.
    """
    _, parameters_test, _ = generate_cell_impedance(
        valid_circuit_string, i_start, i_end, impedance_circuit,
        valid_parameters, analyzed_parameters,
        analyzed_elements, valid_constant_elements)
    caller = 'generate_cell_impedance()'
    test_parameters_is_list(parameters_test, caller)
    test_parameters_type(parameters_test, caller)
    test_parameters_list_two_elements(parameters_test, caller)
    test_parameters_list_type(parameters_test, caller)
    test_parameters_values(parameters_test, caller)
    test_parameters_list_value(parameters_test, caller)

def test_generate_cell_impedance_elements(
        valid_circuit_string, i_start, i_end, impedance_circuit,
        valid_parameters, analyzed_parameters,
        analyzed_elements, valid_constant_elements):
    """Check that generate_cell_impedance() returns a valid elements
    array.

    GIVEN: a valid circuit string, a valid description of the
    circuit and valid parameters of the analysed circuit so far.
    WHEN: I am calculating the correspondant impedance function of a cell.
    THEN: the list of elements for the current funtion are valid.
    """
    *_, elements_circuit = generate_cell_impedance(
        valid_circuit_string, i_start, i_end, impedance_circuit,
        valid_parameters, analyzed_parameters,
        analyzed_elements, valid_constant_elements)
    caller = 'generate_cell_impedance()'
    elements_is_list(elements_circuit, caller)
    elements_type(elements_circuit, caller)
    elements_string_length(elements_circuit, caller)
    elements_letter(elements_circuit, caller)
    elements_number(elements_circuit, caller)
    elements_number_duplicates(elements_circuit, caller)

def generate_last_impedance_element():
    """Return the number of cycles of analysis, i.e. the index of the previous
    impedance analyzed. In this case is 1 to simulate only one ciìycle of
    analysis.
    """
    last_impedance_element = 1
    return last_impedance_element

@pytest.fixture
def last_impedance_element():
    return generate_last_impedance_element()

def test_update_string_valid_string(valid_circuit_string, i_start, i_end,
                                    last_impedance_element):
    """Check that update_string returns a valid string.


    GIVEN: a valid circuit string, a valid position of the start and end of
    the string substitution.
    WHEN: I am substituting the old string with the updated string, acording
    to the analysis done so far.
    THEN: the updated string is valid, excpet for the characters and the
    element consistency.
    """
    updated_circuit_string = update_string(valid_circuit_string, i_start,
                                           i_end, last_impedance_element)
    caller = 'update_string()'
    test_is_string(updated_circuit_string, caller)
    test_empty_string(updated_circuit_string, caller)
    test_string_different_number_brackets(updated_circuit_string, caller)
    test_string_consistency_brackets(updated_circuit_string, caller)

def find_invalid_characters_updated_string(valid_circuit_string, i_start,
                                           i_end, last_impedance_element):
    """Given a valid circuit string, a valid position of the start and end of
    the string substitution, find the invalid characters in the updated
    string. The obly valid characters are (, ), [, ], Z, R, C, Q and numbers.
    Used for testing.

    Parameters
    ----------
    valid_circuit_string : string
        String of the circuit of the last cell analysis
    i_start : int
        Index of the beginning of the analyzed cell
    i_end : int
        Index of the end of the analyzed cell
    last_impedance_element : int
        Integer that represent the number of analysis cycles made so far

    Returns
    -------
    wrong_characters : string
        String that contains all the invald characters, sebarated by a comma
        and a space
    wrong_characters_index : list
        List of indexes of the invalid characters in the string
    updated_circuit_string : string
        Updated string
    """
    updated_circuit_string = update_string(valid_circuit_string, i_start,
                                           i_end, last_impedance_element)
    wrong_characters = ''
    wrong_characters_index = []
    for i, char in enumerate(updated_circuit_string):
        if (char not in {'(', ')', '[', ']', 'Z', 'C', 'Q', 'R'}
                and not char.isnumeric()):
            wrong_characters += '\'' + char + '\', '
            wrong_characters_index.append(i)
    return wrong_characters, wrong_characters_index, updated_circuit_string

def test_update_string_characters(valid_circuit_string, i_start, i_end,
                                  last_impedance_element):
    """Check that a string containes only valid characters:
    '(', ')', '[', ']', 'Z', 'C', 'Q', 'R' and natural numbers.

    GIVEN: a valid circuit string, a valid position of the start and end of
    the string substitution.
    WHEN: I am substituting the old string with the updated string, acording
    to the analysis done so far.
    THEN: the updated string has valid characters.
    """
    (wrong_characters, wrong_characters_index,
     updated_circuit_string) = find_invalid_characters_updated_string(
         valid_circuit_string, i_start, i_end, last_impedance_element)
    assert not wrong_characters, (
        'Invalid character(s) ' + wrong_characters + ' at '
        + str(wrong_characters_index) + ' in ' + updated_circuit_string
        + ' in update_string(). Only round and square brackets, C, Q, R '
        + 'and natural numbers are valid characters')

def find_inconsistent_elements_updated_string(valid_circuit_string, i_start,
                                              i_end, last_impedance_element):
    """Given a valid circuit string, a valid position of the start and end of
    the string substitution, find the inconsistent element in the updated
    string. Each element has a number that is the same of its order of writing
    in the string. Used for testing.

    Parameters
    ----------
    valid_circuit_string : string
        String of the circuit of the last cell analysis
    i_start : int
        Index of the beginning of the analyzed cell
    i_end : int
        Index of the end of the analyzed cell
    last_impedance_element : int
        Integer that represent the number of analysis cycles made so far

    Returns
    -------
    wrong_elements : string
        String that contains all the inconsistent elements, sebarated by a
        comma and a space
    wrong_element_index : list
        List of indexes of the inconsistent elements in the updated string
    updated_circuit_string : string
        Updated string
    """
    updated_circuit_string = update_string(valid_circuit_string, i_start,
                                           i_end, last_impedance_element)
    wrong_elements=''
    wrong_element_index=[]
    for i, char in enumerate(updated_circuit_string):
        if (char in {'Z', 'C', 'Q', 'R'}
            and updated_circuit_string[-1]!=char):
            if not updated_circuit_string[i+1].isnumeric():
                wrong_elements += ('\'' + char
                                   + str(updated_circuit_string[i+1])
                                   + '\', ')
                wrong_element_index.append(i)
        elif (char.isnumeric() and updated_circuit_string[0]!=char):
            if not (updated_circuit_string[i-1] in {'Z','C', 'Q', 'R'}):
                wrong_elements += ('\'' + str(updated_circuit_string[i-1])
                                   + char + '\', ')
                wrong_element_index.append(i-1)
    return wrong_elements, wrong_element_index, updated_circuit_string

def test_update_string_element_consistency(valid_circuit_string, i_start,
                                           i_end, last_impedance_element):
    """Check the element consistency of a string that containes only valid
    characters: each element is composed by a capital letter among
    {'C', 'Q', 'R'} followed by a natural number.

    GIVEN: a valid circuit string, a valid position of the start and end of
    the string substitution.
    WHEN: I am substituting the old string with the updated string, acording
    to the analysis done so far.
    THEN: the updated string has element consistency.
    """
    (wrong_elements, wrong_element_index,
     updated_circuit_string) = find_inconsistent_elements_updated_string(
         valid_circuit_string, i_start, i_end, last_impedance_element)
    assert not wrong_elements, (
        'element inconsistency for '+ wrong_elements + ' at '
        + str(wrong_element_index) + ' in updated string: '
        + updated_circuit_string + '. An element is composed by a '
        + 'valid letter followed by a natural number')

def test_generate_impedance_function(valid_circuit_string, valid_parameters,
                                     valid_constant_elements):
    """Check that generate_impedance_function returns a function as second
    argument.

    GIVEN: the description of the initial circuit is valid.
    WHEN: I am taking the initial description of the circuit to have a proper
    impedance function to describe it.
    THEN: the second argument returned is a fucntion.
    """
    impedance, *_ = generate_impedance_function(valid_circuit_string,
                                                valid_parameters,
                                                valid_constant_elements)
    assert inspect.isfunction(impedance), (
        'type error in output of generate_impedance_function(). Impedance '
        + 'function must return as second argument a function')

def test_generate_impedance_parameters(valid_circuit_string,
                                       valid_parameters,
                                       valid_constant_elements):
    """Check that generate_impedance_function returns a valid list of
    parameters as second argument.

    GIVEN: the description of the initial circuit is valid.
    WHEN: I am taking the initial description of the circuit to have a proper
    impedance function to describe it.
    THEN: the second argument returned is a list of valid parameters.
    """
    _, parameters, _ = generate_impedance_function(valid_circuit_string,
                                                   valid_parameters,
                                                   valid_constant_elements)
    caller = 'generate_impedance_function()'
    test_parameters_is_list(parameters, caller)
    test_parameters_type(parameters, caller)
    test_parameters_list_two_elements(parameters, caller)
    test_parameters_list_type(parameters, caller)
    test_parameters_values(parameters, caller)
    test_parameters_list_value(parameters, caller)

def test_generate_impedance_elements(valid_circuit_string, valid_parameters,
                                     valid_constant_elements):
    """Check that generate_impedance_function returns a valid list of
    elements as third argument.

    GIVEN: the description of the initial circuit is valid.
    WHEN: I am taking the initial description of the circuit to have a proper
    impedance function to describe it.
    THEN: the third argument returned is a list of valid elements.
    """
    *_, elements_circuit = generate_impedance_function(
        valid_circuit_string, valid_parameters, valid_constant_elements)
    caller = 'generate_impedance()'
    elements_is_list(elements_circuit, caller)
    elements_type(elements_circuit, caller)
    elements_string_length(elements_circuit, caller)
    elements_letter(elements_circuit, caller)
    elements_number(elements_circuit, caller)
    elements_number_duplicates(elements_circuit, caller)

def same_number_of_parameters_and_function_arguments(valid_circuit_string,
                                                valid_parameters,
                                                valid_constant_elements):
    """Given the circuit string, its parameters and its constant elements,
    conditions, return wheter the number of parameters and arguments of the
    impedance function are the same. Used for testing

    Parameters
    ----------
    valid_circuit_string : string
        Circuit string given by input
    parameters : list
        List of the parameters given by input
    valid_constant_elements : list
        List of the constant elements condition given by input

    Returns
    -------
    length_equality : bool
        Boolean of the equality length condition
    """
    _, parameters_list, elements_circuit = generate_impedance_function(
        valid_circuit_string, valid_parameters, valid_constant_elements)
    elements_count = 0
    for element in elements_circuit:
        if element.startswith('Q'):
            elements_count += 2
        else:
            elements_count += 1
    length_equality = len(parameters_list)==elements_count
    return length_equality, parameters_list, elements_circuit

def test_generate_impedance_number_of_arguments(valid_circuit_string,
                                                valid_parameters,
                                                valid_constant_elements):
    """Check that the total number of parameters of the functions in the list
    and the number of parameters in list given by generate_cell_impedance is
    the same.

    GIVEN: the description of the initial circuit is valid.
    WHEN: I am taking the initial description of the circuit to have a proper
    impedance function to describe it.
    THEN: the list of parameters and the list of elements have the same
    length.
    """
    (length_equality, parameters_list,
     elements_circuit) = same_number_of_parameters_and_function_arguments(
         valid_circuit_string, valid_parameters, valid_constant_elements)
    assert length_equality, (
        'wrong number of parameters \'' + str(len(parameters_list))
        + '\' with number of elements \'' + str(len(elements_circuit))
        + '\' in output of generate_cell_impedance() \'. It should be 1 '
        + 'parameter for one element')

##############################################################################
#test generate_data.py

def generate_frequencies():
    """Generate the impedance array, used for testing."""
    frequency_vector = set_frequencies()
    return frequency_vector

@pytest.fixture
def frequency_vector():
    return generate_frequencies()

def test_set_frequencies_array(frequency_vector):
    """Check that the output of set_frequencies() is an array.

    WHEN: the function to generate the frequencies is called
    THEN: the frequencies are an array
    """
    assert isinstance(frequency_vector, np.ndarray), (
        'type error in set_frequencies(): the output must be a numpy.ndarray')

def test_set_frequencies_empty_array(frequency_vector):
    """Check that the output of set_frequencies() is not an empty array.

    GIVEN:
    WHEN: the function to generate the frequencies is called
    THEN: the frequencies are a non-empty array
    """
    assert frequency_vector.size>0, (
        'structural error in set_frequencies(): the output cannot be empty')

def find_wrong_elements_set_frequencies(frequency_vector):
    """Find the non-positive elements in the output of set_frequencies(). Used
    for testing.

    Returns
    -------
    wrong_elements : list
        List that contains all the wrong elements
    wrong_element_index : list
        List of indexes of the wrong elements in the array
    """
    wrong_element = []
    wrong_element_index = []
    for i, element in enumerate(frequency_vector):
        if element<=0.:
            wrong_element.append(element)
            wrong_element_index.append(i)
    return wrong_element, wrong_element_index

def test_set_frequencies_value(frequency_vector):
    """Check that the output of set_frequencies() is an array containing only
    positive elements.

    GIVEN: a valid length of the generated signal and that the output of
    generate_random_error_component() is an array (not empty)
    WHEN: the function to generate random numbers to simulate noise is called
    THEN: the random noise contains only valid elements
    """
    (wrong_element,
     wrong_element_index) = find_wrong_elements_set_frequencies(
         frequency_vector)
    assert not wrong_element, (
        'value error in output of set_frequencies(): element(s) '
        + str(wrong_element) + ' in position(s) ' + str(wrong_element_index)
        + ' are not positive')

def generate_file_name_generation():
    """Generate the data file name where the generated data will be written,
    used for testing.
    """
    file_name = set_file_name()
    print (file_name)
    return file_name

@pytest.fixture
def file_name():
    print ('1')
    return generate_file_name_generation()

@pytest.fixture
def caller():
    return 'set_file_name()'

def test_file_name_type(file_name, caller):
    """Check that the data file name is a string.

    WHEN: the function to generate the file name where the data will
    be saved/imported from is called
    THEN: the file name is a string
    """
    assert isinstance(file_name, str), (
        'type error in ' + caller + ': the file name must be a string')

def test_file_name_extention(file_name, caller):
    """Check that the data file name ends with the right extention.

    GIVEN: the file name is a string
    WHEN: the function to generate the file name where the data will
    be saved/imported from is called
    THEN: the file name ends with the right extention
    """
    assert file_name.endswith('.txt'), (
        'structural error in ' + caller + ': invalid file extention. The '
        + 'file name must end with the right extention (.txt)')

def test_file_name_name(file_name, caller):
    """Check that the data file name has at least one character
    before the file extention.

    GIVEN: the file name is a string ending with the right extention
    WHEN: the function to generate the file name where the data will
    be saved/imported from is called
    THEN: the file name has at least one character before the file extention
    """
    assert not file_name.startswith('.txt'), (
        'structural error in ' + caller + ': invalid file name. The file '
        + 'name must have at least one character before the file extention')

@given(signal_length=st.integers(min_value=1, max_value=100))
@settings(max_examples = 10)
def test_generate_random_error_component_array(signal_length):
    """Check that the output of generate_random_error_component() is an array.

    GIVEN: a valid length of the generated signal
    WHEN: the function to generate random numbers to simulate noise is called
    THEN: the random noise is an array
    """
    random_error_component = generate_random_error_component(signal_length)
    assert isinstance(random_error_component, np.ndarray), (
        'type error in generate_random_error_component(): the output must be '
        + 'a numpy.ndarray')

@given(signal_length=st.integers(min_value=1, max_value=100))
@settings(max_examples = 10)
def test_generate_random_error_component_empty_array(signal_length):
    """Check that the output of generate_random_error_component() is not an
    empty array.

    GIVEN: a valid length of the generated signal and that the output of
    generate_random_error_component() is an array
    WHEN: the function to generate random numbers to simulate noise is called
    THEN: the random noise array is not empty
    """
    random_error_component = generate_random_error_component(signal_length)
    assert random_error_component.size>0, (
        'structural error in generate_random_error_component(): the output'
        + 'cannot be empty')

def find_wrong_elements_generate_random_error(signal_length):
    """Given the signal length find the elements in the output of
    generate_random_error_component() that are not within 0 and 1. Used for
    testing.

    Parameters
    ----------
    signal_length : int
        Length of the generated signal

    Returns
    -------
    wrong_elements : list
        List that contains all the wrong elements
    wrong_element_index : list
        List of indexes of the wrong elements in the array
    """
    random_error_component = generate_random_error_component(signal_length)
    wrong_element = []
    wrong_element_index = []
    for i, element in enumerate(random_error_component):
        if (element<0. or element>1.):
            wrong_element.append(element)
            wrong_element_index.append(i)
    return wrong_element, wrong_element_index

@given(signal_length=st.integers(min_value=1, max_value=100))
@settings(max_examples = 10)
def test_generate_random_error_component_value(signal_length):
    """Check that the output of generate_random_error_component() is an array
    containing only elements within 0 and 1.

    GIVEN: a valid length of the generated signal and that the output of
    generate_random_error_component() is an array (not empty)
    WHEN: the function to generate random numbers to simulate noise is called
    THEN: the random noise contains only valid elements
    """
    (wrong_element,
     wrong_element_index) = find_wrong_elements_generate_random_error(
         signal_length)
    assert not wrong_element, (
        'value error in output of generate_random_error_component(): '
        + 'element(s) ' + str(wrong_element) + ' in position(s) '
        + str(wrong_element_index) + ' are not within 0 and 1')

def generate_simulated_signal():
    """Generate a simulated signal vector, with simulated noise, given the
    description of the circuit. Used for testing.
    """
    frequency_vector = set_frequencies()
    circuit_string = generate_circuit()
    parameters = generate_initial_parameters()
    constant_elements = generate_constant_elements_array()
    impedance_function, parameters, _ = generate_impedance_function(
        circuit_string, parameters, constant_elements)
    signal_vector = impedance_function(parameters, frequency_vector)
    simulated_signal = simulate_noise(signal_vector)
    return simulated_signal

@pytest.fixture
def simulated_signal():
    return generate_simulated_signal()

def test_simulate_noise_array(simulated_signal):
    """Check that the output of simulate_noise() is an array.

    GIVEN: a valid generated signal
    WHEN: the function to generate random numbers to simulate noise is called
    THEN: the random noise array is an numpy array
    """
    assert isinstance(simulated_signal, np.ndarray), (
        'type error in simulate_noise(): the output must be a numpy.ndarray')

def test_simulate_noise_empty(simulated_signal):
    """Check that the output of simulate_noise() is not an empty array.

    GIVEN: a valid generated signal
    WHEN: the function to generate random numbers to simulate noise is called
    THEN: the random noise array is not an empty array
    """
    assert simulated_signal.size>0, (
        'type error in simulate_noise(): the output cannot be an empty array')

def test_simulate_noise_one_dimention(simulated_signal):
    """Check that the output of simulate_noise() is one dimentional.

    GIVEN: a valid generated signal
    WHEN: the function to generate random numbers to simulate noise is called
    THEN: the random noise array is one dimentional
    """
    assert simulated_signal.ndim==1, (
        'type error in simulate_noise(): the output must be a one-dimention '
        + 'array, while it is ' + str(simulated_signal.ndim))

def test_simulate_noise_type(simulated_signal):
    """Check that the output of simulate_noise() is a complex
    array.

    GIVEN: a valid generated signal
    WHEN: the function to generate random numbers to simulate noise is called
    THEN: the random noise array is a complex array
    """
    assert simulated_signal.dtype==complex, (
        'type error in simulate_noise(): the output must be a float array, '
        + 'while it is ' + str(simulated_signal.dtype))

def generate_modulus_vector():
    """Generate the modulus of an impedance vector with simulated noise.
    Used for testing.
    """
    impedance_vector = generate_simulated_signal()
    modulus_vector = get_modulus(impedance_vector)
    return modulus_vector

@pytest.fixture
def modulus_vector():
    return generate_modulus_vector()

def test_get_modulus_array(modulus_vector):
    """Check that the output of get_modulus() is an array.

    GIVEN: a valid impedance array
    WHEN: the function to exctract the modulus of the impedance array is
    called
    THEN: the modulus is an array
    """
    assert isinstance(modulus_vector, np.ndarray), (
        'type error in get_modulus(): the output must be a '
        + 'numpy.ndarray')

def test_get_modulus_empty_array(modulus_vector):
    """Check that the output of get_modulus() is not an empty array.

    GIVEN: a valid impedance array and that the output of get_modulus()
    is an array
    WHEN: the function to exctract the modulus of the impedance array is
    called
    THEN: the modulus is a non-empty array
    """
    assert modulus_vector.size>0, (
        'structural error in get_modulus(): the output cannot be empty')

def test_get_modulus_one_dimention(modulus_vector):
    """Check that the output of get_modulus() is one dimentional.

    GIVEN: a valid impedance array and that the output of get_modulus()
    is a non-empty array
    WHEN: the function to exctract the modulus of the impedance array is
    called
    THEN: the modulus is a one-domention array
    """
    assert modulus_vector.ndim==1, (
        'type error in get_modulus(): the output must be a one-dimention '
        + 'array, while it is ' + str(modulus_vector.ndim))

def test_get_modulus_type(modulus_vector):
    """Check that the output of get_modulus() is a float array.

    GIVEN: a valid impedance array and that the output of get_modulus()
    is a non-empty 1D array
    WHEN: the function to exctract the modulus of the impedance array is
    called
    THEN: the modulus is a one-domention float array
    """
    assert modulus_vector.dtype==float, (
        'type error in get_modulus(): the output must be a float array, '
        + 'while it is ' + str(modulus_vector.dtype))

def find_non_positive_values_get_modulus(modulus_vector):
    """Given an impedance array, return modulus that is not positive. Used
    for testing.

    Parameters
    ----------
    impedance_vector : array
        Array of impedances

    Returns
    -------
    wrong_value : list
        List that contains all the invalid modulus
    wrong_value_index : list
        List of indexes of the invalid modulus in the array
    """
    wrong_value = []
    wrong_value_index = []
    for i, element in enumerate(modulus_vector):
        if element<=0:
            wrong_value.append(element)
            wrong_value_index.append(i)
    return wrong_value, wrong_value_index

def test_get_modulus_value(modulus_vector):
    """Check that the output of get_modulus() containes only valid values
    (non-negative values).

    GIVEN: a valid impedance array and that the output of get_modulus()
    is a not empty a one-domention float array
    WHEN: the function to exctract the modulus of the impedance array is
    called
    THEN: the modulus containes non-negative values
    """
    wrong_value, wrong_value_index = find_non_positive_values_get_modulus(
        modulus_vector)
    assert not wrong_value, (
        'value error for modulus ' + str(wrong_value) + ' number '
        + str(wrong_value_index) + ' in get_modulus() output. Modulus must '
        + 'be positive')

def generate_phase_vector():
    """Generate the phase of an impedance vector with simulated noise.
    Used for testing.
    """
    impedance_vector = generate_simulated_signal()
    phase_vector = get_phase(impedance_vector)
    return phase_vector

@pytest.fixture
def phase_vector():
    return generate_phase_vector()

def test_get_phase_array(phase_vector):
    """Check that the output of get_phase() is an array.

    GIVEN: a valid impedance array
    WHEN: the function to exctract the phase of the impedance array is called
    THEN: the phase is an array
    """
    assert isinstance(phase_vector, np.ndarray), (
        'type error in get_phase(): the output must be a numpy.ndarray')

def test_get_phase_empty_array(phase_vector):
    """Check that the output of get_phase() is not an empty array.

    GIVEN: a valid impedance array and that the output of get_phase()
    is an array
    WHEN: the function to exctract the phase of the impedance array is called
    THEN: the phase is a non-empty array
    """
    assert phase_vector.size>0, (
        'structural error in get_phase(): the output cannot be empty')

def test_get_phase_one_dimention(phase_vector):
    """Check that the output of get_phase() is one dimentional.

    GIVEN: a valid impedance array and that the output of get_phase() is a
    non-empty array
    WHEN: the function to exctract the phase of the impedance array is called
    THEN: the phase is a one-domention array
    """
    assert phase_vector.ndim==1, (
        'type error in get_phase(): the output must be a one-dimention '
        + 'array, while it is ' + str(phase_vector.ndim))

def test_get_phase_type(phase_vector):
    """Check that the output of get_phase() is a float array.

    GIVEN: a valid impedance array and that the output of get_phase()
    is a non-empty 1D array
    WHEN: the function to exctract the phase of the impedance array is
    called
    THEN: the phase is a one-domention float array
    """
    assert phase_vector.dtype==float, (
        'type error in get_phase(): the output must be a float array, '
        + 'while it is ' + str(phase_vector.dtype))

##############################################################################
#Tests impedance_analysis.py

@pytest.fixture
def circuit_string_fit():
    return generate_circuit_fit()

@pytest.fixture
def caller():
    return 'generate_circuit_fit()'

def test_circuit_string_fit(circuit_string_fit, caller):
    """Check that the circuit string in the generate_circuit_fit() is a valid
    string.
    """
    test_is_string(circuit_string_fit, caller)
    test_empty_string(circuit_string_fit, caller)
    test_input_string_open_brakets(circuit_string_fit, caller)
    test_input_string_close_brakets(circuit_string_fit, caller)
    test_string_different_number_brackets(circuit_string_fit, caller)
    test_string_consistency_brackets(circuit_string_fit, caller)
    test_no_element(circuit_string_fit, caller)
    test_input_string_characters(circuit_string_fit, caller)
    test_input_string_element_consistency(circuit_string_fit, caller)
    test_input_string_number_sequency(circuit_string_fit, caller)

@pytest.fixture
def circuit_parameters():
    return generate_circuit_parameters()

@pytest.fixture
def caller():
    return 'enerate_circuit_parameters()'

def test_circuit_parameters(circuit_string_fit, circuit_parameters, caller):
    """Check that the circuit parameters in the generate_circuit_fit() are 
    valid parameters.
    """
    test_parameters_is_list(circuit_parameters, caller)
    test_parameters_type(circuit_parameters, caller)
    test_parameters_values(circuit_parameters, caller)
    test_parameters_list_two_elements(circuit_parameters, caller)
    test_parameters_list_type(circuit_parameters, caller)
    test_parameters_list_value(circuit_parameters, caller)
    test_parameters_length(circuit_string_fit, circuit_parameters, caller)
    test_parameters_match(circuit_string_fit, circuit_parameters, caller)

@pytest.fixture
def constant_elements_fit():
    return generate_constant_elements_array_fit()

@pytest.fixture
def caller():
    return 'generate_constant_elements_array_fit()'

def test_constant_elements_fit(circuit_parameters, constant_elements_fit,
                               caller):
    """Check that the circuit parameters in the generate_circuit_fit() are 
    valid parameters.
    """
    test_constant_type(constant_elements_fit, caller)
    test_constant_list_type(constant_elements_fit, caller)
    test_constant_list_value(constant_elements_fit, caller)
    test_constant_length(circuit_parameters, constant_elements_fit, caller)

def generate_file_name_analysis():
    """Generate the data file name from which the data will be read, used for
    testing.
    """
    file_name = get_file_name()
    return file_name

@pytest.fixture
def file_name_analysis():
    return generate_file_name_analysis()

def test_file_name_analysis(file_name_analysis):
    """Check that the data file name for anaysis is valid.

    WHEN: the function to generate the file name where the data will
    be imported from is called
    THEN: the file name is a valid name string witha a valid extention
    """
    caller = 'set_file_name()'
    test_file_name_type(file_name_analysis, caller)
    test_file_name_extention(file_name_analysis, caller)
    test_file_name_name(file_name_analysis, caller)


def generate_number_of_columns():
    file_name = generate_file_name_analysis()
    number_of_columns = get_number_of_columns(file_name)
    return number_of_columns

@pytest.fixture
def number_of_columns():
    return generate_number_of_columns()

def test_get_number_of_columns_type(number_of_columns):
    """Check that the number of columns in get_number_of_columns() is an
    integer.
    
    WHEN: the data file name is read to count the number of data columns
    THEN: number of columns is an integer
    """
    assert isinstance(number_of_columns, int), (
        'type error in get_number_of_columns(): the output must be an '
        + 'integer, while it is ' + str(type(number_of_columns)))
    
def test_get_number_of_columns_value(number_of_columns):
    """Check that the number of columns in get_number_of_columns() is a valid
    number (2 or 3).
    
    WHEN: the data file name is read to count the number of data columns
    THEN: number of columns is 2 or 3
    """
    assert (number_of_columns==2 or number_of_columns==3), (
        'structural error in get_number_of_columns(): the output must be '
        + 'either 2 or 3, while it is ' + str(number_of_columns))
 
def find_non_positive_frequencies_read_data(frequency_vector):
    """Given an frequencies array, return frequencies that is not positive.
    Used for testing.

    Parameters
    ----------
    frequency_vector : array
        Array of frequencies read from data file

    Returns
    -------
    wrong_value : list
        List that contains all the invalid frequencies
    wrong_value_index : list
        List of indexes of the invalid frequencies in the array
    """
    wrong_value = []
    wrong_value_index = []
    for i, element in enumerate(frequency_vector):
        if element<=0:
            wrong_value.append(element)
            wrong_value_index.append(i)
    return wrong_value, wrong_value_index

def test_frequency_read_data(file_name_analysis):
    """Check that the output of read_data() is a valid impedance array as
    second argument.

    GIVEN: a valid file_name and a valid number of columns
    WHEN: the function to read data from a data file is called
    THEN: the second argument is a proper impedance vector: a 1D numpy array
    containing only positive values (floats or integers)
    """
    frequency_vector, _ = read_data(file_name_analysis)
    assert isinstance(frequency_vector, np.ndarray), (
        'type error in the output read_data(): the second argument must be a '
        + 'numpy.ndarray')
    assert frequency_vector.size>0, (
        'structural error in the output read_data(): the second argument '
        + 'cannot be empty')
    assert frequency_vector.ndim==1, (
        'type error in the output read_data(): the second argument must be a '
        + 'one-dimention array, while it is ' + str(frequency_vector.ndim))
    assert (frequency_vector.dtype==float or frequency_vector.dtype==int), (
        'type error in read_data(): the second argument must be a float array, '
        + 'while it is ' + str(frequency_vector.dtype))
    wrong_value, wrong_value_index = find_non_positive_frequencies_read_data(
        frequency_vector)
    assert not wrong_value, (
        'value error for impedance ' + str(wrong_value) + ' number '
        + str(wrong_value_index) + ' in read_data() output. Frequencies must '
        + 'be positive')

def test_impedance_read_data(file_name_analysis):
    """Check that the output of read_data() is a valid impedance array as
    second argument.

    GIVEN: a valid file_name and a valid number of columns
    WHEN: the function to read data from a data file is called
    THEN: the second argument is a proper impedance vector: a 1D numpy complex
    array containing
    """
    _, impedance_data_vector = read_data(file_name_analysis)
    assert isinstance(impedance_data_vector, np.ndarray), (
        'type error in the output read_data(): the second argument must be a '
        + 'numpy.ndarray')
    assert impedance_data_vector.size>0, (
        'structural error in the output read_data(): the second argument '
        + 'cannot be empty')
    assert impedance_data_vector.ndim==1, (
        'type error in the output read_data(): the second argument must be a '
        + 'one-dimention array, while it is '
        + str(impedance_data_vector.ndim))
    assert np.iscomplexobj(impedance_data_vector), (
        'type error in read_data(): the second argument must be a complex '
        + 'array, while it is ' + str(impedance_data_vector.dtype))

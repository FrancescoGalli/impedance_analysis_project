"""This module containes all the test functions (and the function needed for
the tests) for the generate_impedance.py module.
It assesses, for example, that both input data and the output of all the
functions in the module are valid.
"""


import inspect
import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis.extra import numpy as enp
import hypothesis.strategies as st

from generate_data import (
    generate_circuit_string_data, generate_parameters_data,
    generate_constant_elements_data, generate_circuit_data, set_frequencies,
    set_file_name, generate_random_error_component, simulate_noise)
from generate_impedance import Circuit, AnalisysCircuit
from generate_impedance import (
    impedance_resistor, impedance_capacitor, impedance_cpe, add, serial_comb,
    reciprocal, parallel_comb, get_position_opening_bracket,
    list_elements_string)
from plot_and_save import get_modulus, get_phase, get_box_coordinates
from impedance_analysis import (
    generate_circuit_string_fit, generate_circuit_parameters_fit,
    generate_constant_elements_fit, get_file_name, generate_circuit_fit,
    get_number_of_columns, read_data, error_function, get_string,
    bounds_definitions, fit, get_string_constant_parameter,
    get_string_optimized_parameters, get_result_string)


##############################################################################
#String tests of generate_circuit_data() in generate_data.py

def same_number_of_brackets(circuit_string):
    """Given a circuit string, return if the count of open brackets is the
    same of close brackets. Used for testing.

    Parameters
    ----------
    circuit_string : str
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

def wrong_consistency_brackets(circuit_string):
    """Given a circuit string, return if there is a bracket incongruence.
    Used for testing.

    Parameters
    ----------
    circuit_string : str
        String of the circuit given by input

    Returns
    -------
    wrong_brackets : list
        List of all the bracket involbed in the bracket incongruence
    wrong_brackets_index : bool
        Index in the string of all the aforementioned brackets
    """
    wrong_brackets = []
    wrong_brackets_index = ''
    position_of_brackets = [i for i, _ in enumerate(circuit_string)
                            if (circuit_string.startswith(')', i)
                                or circuit_string.startswith(']', i))]
    cut_parameter = 0
    for _ in position_of_brackets:
        for i, char_i in enumerate(circuit_string):
            if char_i in (')', ']'):
                if char_i==')':
                    bracket = '('
                    wrong_bracket = '['
                if char_i==']':
                    bracket = '['
                    wrong_bracket = '('
                found = False
                analyzed_string = circuit_string[:i]
                for j, _ in enumerate(analyzed_string):
                    bracket_index = len(analyzed_string) - 1 - j
                    if (circuit_string[bracket_index]==bracket
                        and not found):
                        found = True
                        relative_index_wrong_bracket = analyzed_string[
                            bracket_index+1:].find(wrong_bracket)
                        if relative_index_wrong_bracket!=-1:
                            wrong_brackets_index += str(
                                relative_index_wrong_bracket + bracket_index
                                + 1 + cut_parameter)
                            wrong_brackets.append(wrong_bracket)
                            circuit_string = (
                                circuit_string[:bracket_index]
                                + circuit_string[bracket_index+1:i]
                                + circuit_string[i+1:])
                            cut_parameter += 2
                            break
                if found:
                    break
    return wrong_brackets, wrong_brackets_index

def list_element_types(circuit_string):
    """Return the list of elements ('C', 'Q' or 'R' ) of a string. Used for
    testing.

    Parameters
    ----------
    circuit_string : str
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

def invalid_characters(circuit_string):
    """Given a circuit string, return any invalid character, i.e. different
    than '(', ')', '[', ']', 'C', 'Q', 'R' or natural numbers. Used for
    testing.

    Parameters
    ----------
    circuit_string : str
        String of the circuit given by input

    Returns
    -------
    wrong_characters : str
        String that contains all the invald characters, separated by a comma
        and a whitespace
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

def inconsistent_elements(circuit_string):
    """Given a circuit string, return any inconsistent element character: each
    element is composed by a capital letter among {'C', 'Q', 'R'} followed
    by a natural number. Used for testing.

    Parameters
    ----------
    circuit_string : str
        String of the circuit given by input

    Returns
    -------
    wrong_elements : str
        String that contains all the inconsistent elements, separated by a
        comma and a whitespace
    wrong_element_index : list
        List of indexes of the inconsistent elements in the string
    """
    wrong_elements = ''
    wrong_element_index = []
    for i, char in enumerate(circuit_string):
        if (char in {'C', 'Q', 'R'} and circuit_string[-1]!=char):
            if not circuit_string[i+1].isnumeric():
                wrong_elements += ('\'' + char + str(circuit_string[i+1])
                                   + '\', ')
                wrong_element_index.append(i)
        elif (char.isnumeric() and circuit_string[0]!=char):
            if not (circuit_string[i-1] in {'C', 'Q', 'R'}):
                wrong_elements += ('\'' + str(circuit_string[i-1]) + char
                                   + '\', ')
                wrong_element_index.append(i-1)
    return wrong_elements, wrong_element_index

def inconsistent_numbers(circuit_string):
    """Given a circuit string, return any inconsistent element number: each
    element has a number that is the same of its order of writing in the
    string. Used for testing.

    Parameters
    ----------
    circuit_string : str
        String of the circuit given by input

    Returns
    -------
    wrong_numbers : str
        String that contains all the inconsistent element number, separated by
        a comma and a whitespace
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

def is_valid_input_string(circuit_string, caller):
    """State if a circuit string is valid. A circuit string is
    made of elements (a letter among {'R', 'C', 'Q'} followed by a single
    digit number) and round and/or square brackets. This means that the
    string must not be empty, and must contain only valid characters. There
    must be a brackets consistency and the first/last character must be an
    open/closed bracket. For the elements, there must be at least a valid
    element, and the digits must represent their order of appearence."""
    assert isinstance(circuit_string, str), (
        'TypeError for circuit scheme in ' + caller
        + '. It must be a string')
    assert circuit_string, 'empty string in ' + caller
    assert (circuit_string.startswith('(')
            or circuit_string.startswith('[')), (
                'StructuralError: no initial open bracket detected in '
                + caller)
    assert (circuit_string.endswith(')') or circuit_string.endswith(']')), (
        'StructuralError: no final close bracket detected' + caller)
    assert same_number_of_brackets(circuit_string), (
        'StructuralError: inconsistent number of open and close brackets in '
        + '\'' + circuit_string + '\' in ' + caller)
    wrong_brackets, wrong_brackets_index = wrong_consistency_brackets(
        circuit_string)
    assert not wrong_brackets, (
        'StructuralError: inconsistent \'' + str(wrong_brackets) + '\' at '
        + wrong_brackets_index + ': ' + circuit_string + ' in ' + caller)
    elements_types = list_element_types(circuit_string)
    assert elements_types, (
        'StructuralError: no element found in ' + circuit_string + ' from '
        + caller + '. An element begins with one of the three letter C, Q '
        + 'or ' + 'R')
    wrong_characters, wrong_characters_index = invalid_characters(
        circuit_string)
    assert not wrong_characters, (
        'StructuralError: invalid character(s) ' + wrong_characters + ' at '
        + str(wrong_characters_index) + ' in ' + circuit_string + 'from '
        + caller + '. Only round and square brackets, C, Q, R and natural '
        + 'numbers are allowed')
    wrong_elements, wrong_element_index = inconsistent_elements(
        circuit_string)
    assert not wrong_elements, (
        'StructuralError: element inconsistency for '+ wrong_elements + ' at '
        + str(wrong_element_index) + ': ' + circuit_string + '. An '
        + 'element is composed by a valid letter followed by a natural '
        + 'number in ' + caller)
    wrong_numbers, wrong_numbers_index = inconsistent_numbers(
        circuit_string)
    assert not wrong_numbers, (
        'StructuralError: wrong number for element(s) '+ wrong_numbers + 'at '
        + str(wrong_numbers_index) + ' in ' + circuit_string + 'from '
        + caller + '. Element numbers must increase of 1 unit per time')

@pytest.fixture
def circuit_string_data():
    return generate_circuit_string_data()

def test_input_string_data(circuit_string_data):
    """Check that the circuit string is a valid string.

    WHEN: when an input circuit string is set
    THEN: the circuit represent a valid circuit
    """
    caller = 'generate_circuit_string_data()'
    is_valid_input_string(circuit_string_data, caller)


##############################################################################
#Parameters tests of generate_parameters_list() in generate_data.py

def invalid_parameters_type(parameters_list):
    """Given a parameters list, return any wrong type parameter: each
    parameter can be an integer, a float or a list. Used for testing.

    Parameters
    ----------
    parameters_list : list
        List of the parameters given by input

    Returns
    -------
    wrong_type : str
        String that contains all the invalid parameters, separated by a comma
        and a whitespace
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

def invalid_parameters_value(parameters_list):
    """Given a parameters list, return any integer of float parameter that has
    a non-positive value, thus invalid. Used for testing.

    Parameters
    ----------
    parameters_list : list
        List of the parameters given by input

    Returns
    -------
    wrong_value : str
        String that contains all the invalid parameters, separated by a comma
        and a whitespace
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

def invalid_parameters_list(parameters_list):
    """Given a parameters list, return any parameter that is a list with a
    length different from 2, thus invalid. Used for testing.

    Parameters
    ----------
    parameters_list : list
        List of the parameters given by input

    Returns
    -------
    wrong_parameters : str
        String that contains all the invalid parameters, separated by a comma
        and a whitespace
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

def invalid_parameters_list_type(parameters_list):
    """Given a parameters list, return any parameter that is a list and does
    not contains floats or integers, thus is invalid. Used for testing.

    Parameters
    ----------
    parameters_list : list
        List of the parameters given by input

    Returns
    -------
    wrong_types : str
        String that contains all the invalid parameters, separated by a comma
        and a whitespace
    wrong_types_index : list
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

def invalid_parameters_list_value(parameters_list):
    """Given a parameters list, return any parameter that is a list of length
    2 of floats or integers with invalid values: the second must be positive,
    the second must be within 0 and 1. Used for testing.

    Parameters
    ----------
    parameters_list : list
        List of the parameters given by input

    Returns
    -------
    wrong_value : str
        String that contains all the invalid parameters, separated by a comma
        and a whitespace
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

def number_of_elements_is_equal_to_number_of_parameters(circuit_string,
                                                        parameters_list):
    """Given the string circuit and its parameters list, return wheter the
    length of the parameters list and the number of elements in the string is
    the same. Used for testing

    Parameters
    ----------
    circuit_string : str
        String of the circuit given by input
    parameters_list : list
        List of the parameters given by input

    Returns
    -------
    length_equality : bool
        Boolean of the equality length condition
    elements_count : str
        Length of the elements list
    """
    elements_types = list_element_types(circuit_string)
    length_equality = len(elements_types)==len(parameters_list)
    elements_count = str(len(elements_types))
    return length_equality, elements_count

def elements_parameters_match(circuit_string, parameters_list):
    """Given the string circuit and its parameters list, return any element
    and parameter that do not match in type: R and C have a float
    or integer type, while Q has a list. Used for testing.

    Parameters
    ----------
    circuit_string : str
        String of the circuit given by input
    parameters_list : list
        List of the parameters given by input

    Returns
    -------
    wrong_match : str
        String that contains all the invalid elements and parameters,
        separated by a comma and a whitespace
    wrong_match_index : list
        List of indexes of the invalid elements in the string
    """
    elements_types = list_element_types(circuit_string)
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

def are_valid_input_parameters(parameters_list, circuit_string, caller):
    """State if a parameter list is valid. Each parameter may be a float,
    an integer or a list itself containing only 2 elements. Each of them can
    be float or integer. There are also value restriction on the float/integer
    variables: if they are parameters they have to be positive.
    If they are inside a list, the first must be positive, the secon must be
    within [0,1].
    Then there must be a match in length and type between the parameters and
    the circuit string: float/int parameters are for 'R' or 'C' elements,
    while lists are for 'Q'.
    """
    assert isinstance(parameters_list, list), (
        'TypeError for parameters in ' + caller + '. It must be a list')
    wrong_type, wrong_type_index = invalid_parameters_type(
        parameters_list)
    assert not wrong_type, (
        'TypeError for parameter(s) number ' + str(wrong_type_index)
        + ' ' + wrong_type + 'in ' + str(parameters_list) + ' in '
        + caller + '. Parameters can only be floats, integers or lists')
    wrong_value, wrong_value_index = invalid_parameters_value(
        parameters_list)
    assert not wrong_value, (
        'ValueError for parameter(s) number ' + str(wrong_value_index) + ' '
        + wrong_value + ' in ' + str(parameters_list) + ' in ' + caller
        + '. Float and integer parameters must be positive')
    wrong_list, wrong_list_index = invalid_parameters_list(
        parameters_list)
    assert not wrong_list, (
        'TypeError for parameter(s) number ' + str(wrong_list_index)
        + ': \'' + wrong_list + '\' in ' + str(parameters_list)
        + ' in ' + caller + '. Lists parameters must contain exactly 2 '
        + 'parameters')
    wrong_list_types, wrong_list_types_index = invalid_parameters_list_type(
        parameters_list)
    assert not wrong_list_types, (
        'TypeError for parameter(s) '+ wrong_list_types  +' in parameter(s) '
        + 'number ' + str(wrong_list_types_index) + ' contained in: \''
        + '\' in ' + str(parameters_list) + ' in ' + caller + '. Lists '
        + 'parameters must only contain floats or integers')
    wrong_list_value, wrong_list_value_index = invalid_parameters_list_value(
        parameters_list)
    assert not wrong_list_value, (
        'ValueError for parameter(s) '+ wrong_list_value
        + wrong_list_value_index + ' parameter(s) contained in: \''
        + str(parameters_list) + ' in ' + caller + '. Lists parameters '
        + 'must contain as first parameter a positive number and as second '
        + 'parameter a number between 0 and 1')

    (length_equality,
     elements_count) = number_of_elements_is_equal_to_number_of_parameters(
        circuit_string, parameters_list)
    assert length_equality, (
        'StructuralError: element count and parameters list size must be '
        + 'the same in ' + caller + '. Element count: ' + elements_count
        + ', parameters size: ' + str(len(parameters_list)))
    wrong_match, wrong_match_index, elements_type = elements_parameters_match(
        circuit_string, parameters_list)
    assert not wrong_match, (
        'StructuralError: bad match for '+ wrong_match + ' in '
        + str(wrong_match_index) + ': elements \'' + str(elements_type)
        + ' with parameters ' + str(parameters_list) + 'from ' + caller
        + '. \'R\' and \'C\' elements must have a float as parameter, \'Q\''
        + 'must have a list')

@pytest.fixture
def parameters_data():
    return generate_parameters_data()

def test_input_parameters_data(parameters_data, circuit_string_data):
    """Check that the parameters are contained in a list.

    GIVEN: input circuit string is a valid circuit string
    WHEN: when a parameters list is set
    THEN: the parameters list represent a valid set of parameters, in accord
    to the circuit string
    """
    caller = 'generate_parameters_data()'
    are_valid_input_parameters(parameters_data, circuit_string_data, caller)

##############################################################################
#Constant elements tests

def invalid_constant_type(constant_elements_list):
    """Given a constant elements condition list, return any wrong type
    constant elements condition: they can only be integers. Used for testing.

    Parameters
    ----------
    constant_elements_list : list
        List of the constant elements condition given by input

    Returns
    -------
    wrong_type : str
        String that contains all the invalid constant elements conditions,
        separated by a comma and a whitespace
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

def invalid_constant_value(constant_elements_list):
    """Given a constant_elements list, return any wrong type constant elements
    condition: each on can only be either 0 or 1. Used for testing.

    Parameters
    ----------
    constant_elements_list : list
        List of the constant elements condition given by input

    Returns
    -------
    wrong_value : str
        String that contains all the invalid constant elements conditions,
        separated by a comma and a whitespace
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

def are_valid_constant_elements(constant_elements_list, parameters_list,
                                caller):
    """States if a constant element list is valid. Each value has to be int,
    and can be 0 or 1. The constant element list has to be of the same length
    of the parameter list.
    """
    assert isinstance(constant_elements_list, list), (
        'TypeError for circuit scheme in ' + caller + '. It must be a '
        + 'list')
    wrong_types, wrong_types_index = invalid_constant_type(
        constant_elements_list)
    assert not wrong_types, (
        'TypeError for constant element(s) ' + str(wrong_types) + ' number '
        + str(wrong_types_index) + ' in ' + str(constant_elements_list)
        + ' from ' + caller + '. Constant element must be an integer')
    wrong_value, wrong_value_index = invalid_constant_value(
        constant_elements_list)
    assert not wrong_value, (
        'ValueError for constant element(s) '+ wrong_value + 'at '
        + str(wrong_value_index) + ' in \'' + str(constant_elements_list)
        + '\' from ' + caller + '. Constant array must contain only 0 or '
        + '1')

    assert number_of_parameters_is_equal_to_number_of_const_elements(
        parameters_list, constant_elements_list), (
        'StructuralError: error from ' + caller + ': parameters and '
        + 'constant array list size must be the same. Parameters size: '
        + str(len(parameters_list)) + ', constant array size: '
        + str(len(constant_elements_list)))

def return_constant_elements_data():
    """Generate an array of constant element conditions. Used for tests."""
    parameters_data = generate_parameters_data()
    constant_elements_data = generate_constant_elements_data(
        parameters_data)
    return constant_elements_data

@pytest.fixture
def constant_elements_data():
    return return_constant_elements_data()

def test_constant_elements_data(constant_elements_data, parameters_data):
    """Check that the constant elements list is valid.

    GIVEN: the parameters list is a valid parameters list, related to the
    correspondant circuit string.
    WHEN: the constant list generation function is called
    THEN: the constant elements list is a valid list of constant elements
    condition
    """
    caller = 'generate_constant_elements_data()'
    are_valid_constant_elements(constant_elements_data, parameters_data, caller)


##############################################################################
#Test valid initial circuit

def invalid_elements_type(element_list):
    """Given the elements in the circuit that will figure in the fit, return
    any character that is not a string. Used for testing.

    Parameters
    ----------
    elements_circuit : list
        List of the elements in the circuit that will figure in the fit

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
    return wrong_char, wrong_char_index

def elements_duplicate(elements_circuit):
    """Given the elements in the circuit that will figure in the fit, return
    any element that has the same number of a previous one. Used for testing.

    Parameters
    ----------
    elements_circuit : list
        List of the elements in the circuit that will figure in the fit

    Returns
    -------
    wrong_char : str
        String that contains all the duplictaes elements, separated by a comma
        and a whitespace
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

def valid_elements(elements_list, caller):
    """States if an element list is valid. Each element is a 2-char string,
    beginning with 'R', 'C' or 'Q', and followed by a numeric char. No
    duplicates with the same number are permitted.
    """
    assert isinstance(elements_list, list), (
        'TypeError for output in ' + caller + '. It must be a list')
    wrong_types, wrong_types_index = invalid_elements_type(elements_list)
    assert not wrong_types, (
        'TypeError for element(s) number ' + str(wrong_types_index) + ' '
        + wrong_types + ' in ' + str(elements_list) + ' in ' + caller
        + '. Elements (here dictionary keys) can only be strings')
    wrong_length, wrong_length_index = invalid_elements_length(elements_list)
    assert not wrong_length, (
        'LengthError for element(s) number ' + str(wrong_length_index)
        + ' ' + wrong_length + ' in ' + str(elements_list) + ' in '
        + caller + '. Elements must all be of length 2')
    (wrong_char_letter,
        wrong_char_letter_index) = invalid_elements_char_letter(elements_list)
    assert not wrong_char_letter, (
        'StructuralError for element(s) number '
        + str(wrong_char_letter_index) + ' ' + wrong_char_letter + ' in '
        + str(elements_list) + ' in ' + caller + '. All elements must begin '
        + 'with a letter among \'C\', \'R\' ' + 'and \'Q\'')
    (wrong_char_number,
        wrong_char_number_index) = invalid_elements_char_number(elements_list)
    assert not wrong_char_number, (
        'StructuralError for element(s) number '
        + str(wrong_char_number_index) + ' ' + wrong_char_number + ' in '
        + str(elements_list) + ' in ' + caller + '. All elements must end '
        + 'with a natural number')
    wrong_char_dupe, wrong_char_dupe_index = elements_duplicate(elements_list)
    assert not wrong_char_dupe, (
        'StructuralError for element(s). Found duplicate of number '
        + wrong_char_dupe + ' in positions ' + str(wrong_char_dupe_index)
        + ' in ' + str(elements_list) + ' in ' + caller + '. Each element '
        + 'number must be unique')

def wrong_tuples_circuit(parameters_map):
    """Return any element inside a dictionary that has not a tuple as a value.

    Parameters
    ----------
    parameters_map : dict
        Dictionary representing the elements with their parameters and
        constant conditions

    Returns
    -------
    wrong_tuples : str
        Elements string with a value in the dictionary that is not a tuple
    """
    wrong_tuples = ''
    for element in parameters_map.keys():
        tuple_ = parameters_map[element]
        if not isinstance(tuple_, tuple):
            wrong_tuples += '\'' + element + '\', '
    return wrong_tuples

def valid_circuit(input_circuit, input_circuit_string, input_parameters,
                  input_constant_elements, caller):
    """States if a Circuit instance is valid. Each instance has a valid
    circuit string, valid elements as keys of the parameters_map attribute
    and valid parameters and constant conditions in tuples as valus of the
    dictionary.
    """
    assert isinstance(input_circuit, Circuit), (
        'TyperError for output of ' + caller + ' method. It must be an '
        + 'instance of the \'Circuit\' class')

    circuit_string = input_circuit.circuit_string
    is_valid_input_string(circuit_string, caller)
    assert circuit_string==input_circuit_string, (
        'StructuralError for attribute \'circuit_string\' output of '
        + caller + '. It must be the same of the output of '
        + 'generate_circuit_string_data()')

    parameters_map = input_circuit.parameters_map
    assert isinstance(parameters_map, dict), (
        'TypeError for attribute \'parameters_map\' in output of '
        + caller + '. It must be a dictionary')
    elements_list = list(parameters_map.keys())
    valid_elements(elements_list, caller)
    assert elements_list==list_elements_string(input_circuit_string), (
        'StructuralError for elements in attribute \'parameters_map\' in '
        + 'output of ' + caller + '. The elements must be the same that '
        + 'compose the output of generate_circuit_string_data()')

    wrong_tuples = wrong_tuples_circuit(parameters_map)
    assert not wrong_tuples, (
        'TypeError in output of get_impedance_const_input_element_type() '
        + 'for element \'' + wrong_tuples + '\'. Its value in the dictionary '
        + ' have to be a tuple')
    parameters_list = list(parameters_map.values())
    parameters_data_circuit = [parameter[0] for parameter in parameters_list]
    are_valid_input_parameters(parameters_data_circuit, input_circuit_string,
                               caller)
    assert parameters_data_circuit==input_parameters, (
        'StructuralError for parameters in attribute \'parameters_map\' in '
        + 'output of ' + caller + '. It must be the same of the output of '
        + 'generate_parameters_data()')
    constant_elements_data_circuit = [ce[1] for ce in parameters_list]
    are_valid_constant_elements(constant_elements_data_circuit,
                                input_parameters, caller)
    assert constant_elements_data_circuit==input_constant_elements, (
        'StructuralError for constant elements in attribute '
        + '\'parameters_map\' in output of ' + caller + '. It must be the '
        + 'same of the output of return_constant_elements_data()')

def generate_initial_circuit_data():
    """Generate an array of constant element conditions. Used for tests."""
    circuit_string_data = generate_circuit_string_data()
    parameters_data = generate_parameters_data()
    initial_circuit_data = generate_circuit_data(circuit_string_data,
                                                 parameters_data)
    return initial_circuit_data

@pytest.fixture
def initial_circuit_data():
    return generate_initial_circuit_data()

def test_generate_circuit_data(initial_circuit_data, circuit_string_data,
                               parameters_data, constant_elements_data):
    """Check that the initial_circuit_data is a valid circuit.

    GIVEN: the circuit string, the parameters list and the constant elements
    list are valid
    WHEN: the initial circuit generation function is called
    THEN: the initial circuit is valid
    """
    caller = 'generate_circuit_data()'
    valid_circuit(initial_circuit_data, circuit_string_data,
                               parameters_data, constant_elements_data, caller)

#Test for generate_impedance.py

###################################
#Test for AnalisysCircuit Class

def generate_example_input_elements():
    """Generate a list of Element obejects, one for each type. Used for
    testing.
    """
    element_strings = (['R', 'C', 'Q'])
    element_parameters = ([10, 3e-6, [2e-6, 0.5]])
    example_input_elements = {}
    for i, element_type in enumerate(element_strings):
        example_input_elements[element_type+str(1)] = element_parameters[i]
        example_input_elements[element_type+str(2)] = element_parameters[i]
    return example_input_elements

@pytest.fixture
def example_input_elements():
    return generate_example_input_elements()

def generate_base_analyzed_circuits():
    """Generate a possible list of already analyzed circuits."""
    element_strings = (['R', 'C', 'Q'])
    base_analyzed_circuits = []
    for element in element_strings:
        analyzed_circuit_empty = AnalisysCircuit('('+element+str(1)+')')
        base_analyzed_circuits.append(analyzed_circuit_empty)
        analyzed_circuit = AnalisysCircuit('(R1'+element+str(2)+')')
        analyzed_circuit.get_impedance_non_const_element('R1', 100)
        base_analyzed_circuits.append(analyzed_circuit)
    return base_analyzed_circuits

def wrong_dictionary_get_impedance_single_element(
        example_input_elements, example_analyzed_circuits):
    """Find for which element the impedance-parameter map of the
    AnalysisCircuit is not a dictionary. Used for testing.

    Parameters
    ----------
    example_input_elements : list
        List of the dictionaries containing the elements analyzed
    example_analyzed_circuits : list
        List of the AnalysisCircuit objects of the analyzed circuit


    Returns
    -------
    wrong_dictionaries : str
        String that contains all the wrong elements with bad dictionaries,
        separated by a comma and a whitespace
    """
    wrong_dictionaries = ''
    for element in example_input_elements.keys():
        index = list(example_input_elements).index(element)
        analyzed_circuit = example_analyzed_circuits[index]
        impedance_parameters_map = analyzed_circuit.impedance_parameters_map
        if not isinstance(impedance_parameters_map, dict):
            wrong_dictionaries += '\'' + element + '\', '
    return wrong_dictionaries

def wrong_tuples_get_impedance_single_element(example_input_elements,
                                              example_analyzed_circuits):
    """Find for which element the impedance-parameter map of the
    AnalysisCircuit has not a tuple as a value. Used for testing.

    Parameters
    ----------
    example_input_elements : list
        List of the dictionaries containing the elements analyzed
    example_analyzed_circuits : list
        List of the AnalysisCircuit objects of the analyzed circuit

    Returns
    -------
    wrong_tuples : str
        String that contains all the wrong elements with bad tuples,
        separated by a comma and a whitespace
    """
    wrong_tuples = ''
    for element in example_input_elements.keys():
        index = list(example_input_elements).index(element)
        analyzed_circuit = example_analyzed_circuits[index]
        tuple_ = analyzed_circuit.impedance_parameters_map[element]
        if not isinstance(tuple_, tuple):
            wrong_tuples += '\'' + element + '\', '
    return wrong_tuples

def wrong_impedance_get_impedance_single_element(example_input_elements,
                                                 example_analyzed_circuits):
    """Find for which element the impedance-parameter map of the
    AnalysisCircuit has an invalid function as the first element of the tuple.
    Used for testing.

    Parameters
    ----------
    example_input_elements : list
        List of the dictionaries containing the elements analyzed
    example_analyzed_circuits : list
        List of the AnalysisCircuit objects of the analyzed circuit

    Returns
    -------
    wrong_functions : str
        String that contains all the wrong elements with bad functions,
        separated by a comma and a whitespace
    """
    wrong_functions = ''
    for element in example_input_elements.keys():
        index = list(example_input_elements).index(element)
        analyzed_circuit = example_analyzed_circuits[index]
        impedance_element = analyzed_circuit.impedance_parameters_map[
            element][0]
        if not inspect.isfunction(impedance_element):
            wrong_functions += '\'' + element + '\', '
    return wrong_functions

def wrong_parameter_get_impedance_constant_element(
    example_input_elements, example_analyzed_circuits_constant):
    """Find for which element the impedance-parameter map of the
    AnalysisCircuit has an invalid parameter (i.e. a 'const' atring since it
    is constant) as the second element of the tuple. Used for testing.

    Parameters
    ----------
    example_input_elements : list
        List of the dictionaries containing the elements analyzed
    example_analyzed_circuits : list
        List of the AnalysisCircuit objects of the analyzed circuit

    Returns
    -------
    wrong_parameters : str
        String that contains all the wrong elements with bad parameter,
        separated by a comma and a whitespace
    """
    wrong_parameters = ''
    for element in example_input_elements.keys():
        index = list(example_input_elements).index(element)
        analyzed_circuit = example_analyzed_circuits_constant[index]
        parameter_ = analyzed_circuit.impedance_parameters_map[element][1]
        if (not isinstance(parameter_, str)
            or not parameter_.startswith('const')):
            wrong_parameters += '\'' + element + '\', '
    return wrong_parameters

def generate_analized_circuits_constant():
    """Generate a possible list of analyzed circuits with a constat element
    analysis.
    """
    example_input_elements = generate_example_input_elements()
    base_analyzed_circuits = generate_base_analyzed_circuits()
    example_analyzed_circuits_constant = base_analyzed_circuits.copy()
    for element, parameter in example_input_elements.items():
        index = list(example_input_elements).index(element)
        analyzed_circuit_constant = example_analyzed_circuits_constant[index]
        analyzed_circuit_constant.get_impedance_constant_element(element,
                                                                 parameter)
    return example_analyzed_circuits_constant

@pytest.fixture
def example_analyzed_circuits_constant():
    return generate_analized_circuits_constant()

def test_get_impedance_constant_element(example_input_elements,
                                        example_analyzed_circuits_constant):
    """Check that get_impedance_constant_element() sets a valid
    impedance-parameter map (dictionary) for each type of constant element.

    GIVEN: a valid set of input parameters.
    WHEN: I am analyzing a constant input element.
    THEN: the impedance-parameter map is set correctely for each element type
    if constant.
    """
    caller = 'get_impedance_constant_element()'
    wrong_dictionaries = wrong_dictionary_get_impedance_single_element(
         example_input_elements, example_analyzed_circuits_constant)
    assert not wrong_dictionaries, (
        'TypeError in output of ' + caller + ' for element type(s) \''
        + wrong_dictionaries + '\'. It must be a dictionary')

    for element in example_input_elements.keys():
        index = list(example_input_elements).index(element)
        analyzed_circuit = example_analyzed_circuits_constant[index]
        elements_list = list(analyzed_circuit.impedance_parameters_map.keys())
        valid_elements(elements_list, caller)

    wrong_tuples = wrong_tuples_get_impedance_single_element(
         example_input_elements, example_analyzed_circuits_constant)
    assert not wrong_tuples, (
        'TypeError in output of ' + caller + ' for element \''
        + wrong_tuples + '\'. Its value in the dictionary have to be a tuple')

    wrong_functions = wrong_impedance_get_impedance_single_element(
        example_input_elements, example_analyzed_circuits_constant)
    assert not wrong_functions, (
        'TypeError in output of get_impedance_const_input_element_type() '
        + 'for element type(s) ' + ' \'' + wrong_functions + '\'. Its first '
        + 'element of the tuple must be a function')
    wrong_parameters = wrong_parameter_get_impedance_constant_element(
         example_input_elements, example_analyzed_circuits_constant)
    assert not wrong_parameters, (
        'TypeError in output of get_impedance_const_input_element_type() '
        + 'for element type(s)' + ' \'' + wrong_parameters + '\'. Its second '
        + 'element of the tuple must be a \'const\' string')


def generate_analized_circuits_non_constant():
    """Generate a possible list of analyzed circuits with a non-constat
    element analysis.
    """
    base_analyzed_circuits = generate_base_analyzed_circuits()
    example_input_elements = generate_example_input_elements()
    example_analyzed_circuits_non_constant = base_analyzed_circuits.copy()
    for element, parameter in example_input_elements.items():
        index = list(example_input_elements).index(element)
        analyzed_circuit_non_constant = example_analyzed_circuits_non_constant[
            index]
        analyzed_circuit_non_constant.get_impedance_non_const_element(
            element,  parameter)
    return example_analyzed_circuits_non_constant

@pytest.fixture
def example_analyzed_circuits_non_constant():
    return generate_analized_circuits_non_constant()

def test_get_impedance_non_const_element(
        example_input_elements, example_analyzed_circuits_non_constant):
    """Check that get_impedance_non_const_element() sets a valid impedance-parameter
    map (dictionary) for each type of non-constant element.

    GIVEN: a valid set of input parameters
    WHEN: I am analyzing a non-constant input element.
    THEN: the impedance-parameter map is set correctely for each element type
    if non-constant.
    """
    caller = 'get_impedance_non_const_element()'
    wrong_dictionaries = wrong_dictionary_get_impedance_single_element(
         example_input_elements, example_analyzed_circuits_non_constant)
    assert not wrong_dictionaries, (
        'TypeError in output of ' + caller + ' for element type(s) \''
        + wrong_dictionaries + '\'. It must be a dictionary')

    for element in example_input_elements.keys():
        index = list(example_input_elements).index(element)
        analyzed_circuit = example_analyzed_circuits_non_constant[index]
        elements_list = list(analyzed_circuit.impedance_parameters_map.keys())
        valid_elements(elements_list, caller)

    wrong_tuples = wrong_tuples_get_impedance_single_element(
         example_input_elements, example_analyzed_circuits_non_constant)
    assert not wrong_tuples, (
        'TypeError in output of ' + caller + ' for element \''
        + wrong_tuples + '\'. Its value in the dictionary have to be a tuple')

    wrong_functions = wrong_impedance_get_impedance_single_element(
        example_input_elements, example_analyzed_circuits_non_constant)
    assert not wrong_functions, (
        'TypeError in output of ' + caller + ' for element type(s) \''
        + wrong_functions + '\'. Its first element of the tuple must be a '
        + 'function')

    for element in example_input_elements.keys():
        index = list(example_input_elements).index(element)
        analyzed_circuit_ = example_analyzed_circuits_non_constant[index]
        parameters_list = list(analyzed_circuit_.impedance_parameters_map.values())
        parameters = [par[1] for par in parameters_list]
        circuit_string = analyzed_circuit_.circuit_string
        are_valid_input_parameters(parameters, circuit_string, caller)


def wrong_tuples_get_impedance_element(circuit_get_impedance,
                                       analyzed_circuit_get_impedance):
    """Find for which element in a AnalysisCircuit, given by the
    get_impedance(), the values of the dictionary are not a tuple. Used for
    testing.

    Parameters
    ----------
    circuit_get_impedance : Circuit
        Input circuit to be analyzed
    analyzed_circuit_get_impedance : AnalysisCircuit
        analyzed counterpart

    Returns
    -------
    wrong_tuples : str
        String that contains all the wrong elements with bad tuples,
        separated by a comma and a whitespace
    """
    wrong_tuples = ''
    for element in circuit_get_impedance.parameters_map.keys():
        tuple_ = analyzed_circuit_get_impedance.impedance_parameters_map[
            element]
        if not isinstance(tuple_, tuple):
            wrong_tuples += '\'' + element + '\', '
    return wrong_tuples

def wrong_impedance_get_impedance_element(circuit_get_impedance,
                                          analyzed_circuit_get_impedance):
    """Find for which element in a AnalysisCircuit, given by the
    get_impedance(), the values of the dictionary are not a tuple. Used for
    testing.

    Parameters
    ----------
    circuit_get_impedance : Circuit
        Input circuit to be analyzed
    analyzed_circuit_get_impedance : AnalysisCircuit
        analyzed counterpart

    Returns
    -------
    wrong_functions : str
        String that contains all the wrong elements with bad functions,
        separated by a comma and a whitespace
    """
    wrong_functions = ''
    for element in circuit_get_impedance.parameters_map.keys():
        impedance_element = analyzed_circuit_get_impedance.impedance_parameters_map[
            element][0]
        if not inspect.isfunction(impedance_element):
            wrong_functions += '\'' + element + '\', '
    return wrong_functions

def check_parameters_get_impedance_element(circuit_get_impedance,
                                           analyzed_circuit_get_impedance,
                                           caller):
    """Check that for each element in a AnalysisCircuit, given by the
    get_impedance(), the values of the parameter in the tuple is set to the
    string 'const' if the constant condition is true, while if the parameter
    is valid in the condition is false. Used for testing.

    Parameters
    ----------
    circuit_get_impedance : Circuit
        Input circuit to be analyzed
    analyzed_circuit_get_impedance : AnalysisCircuit
        analyzed counterpart
    """
    parameters_list = list(
        analyzed_circuit_get_impedance.impedance_parameters_map.values())
    parameters = [par[1] for par in parameters_list]
    circuit_elements = list_elements_string(
        analyzed_circuit_get_impedance.circuit_string)
    parameters_cc_list = list(circuit_get_impedance.parameters_map.values())
    constant_conditions = [c_c[1] for c_c in parameters_cc_list]
    for i, c_c in enumerate(constant_conditions):
        if c_c:
            assert parameters[i] == 'const'
        else:
            parameter = ([parameters[i]])
            are_valid_input_parameters(parameter, circuit_elements[i], caller)

def generate_circuit_get_impedance():
    """Generate a circuit consisting in a cell with two elements: a constant
    one and a non-constant one.
    """
    circuit_string = '(R1C2)'
    parameters = ([10, 3e-6])
    circuit_get_impedance = generate_circuit_data(circuit_string,
                                                 parameters)
    parameter_value = circuit_get_impedance.parameters_map['C2'][0]
    circuit_get_impedance.parameters_map['C2'] = (parameter_value, 0)
    return circuit_get_impedance

@pytest.fixture
def circuit_get_impedance():
    return generate_circuit_get_impedance()

def generate_analized_circuit_get_impedance():
    """Generate an AnalysisCircuit instance consisting in a cell with two
    elements: a constant one and a non-constant one.
    """
    circuit_get_impedance = generate_circuit_get_impedance()
    analyzed_circuit_get_impedance = AnalisysCircuit('(R1C2)')
    circuit_elements = (['R1', 'C2'])
    for element in circuit_elements:
        analyzed_circuit_get_impedance.get_impedance_element(
            element, circuit_get_impedance)
    return analyzed_circuit_get_impedance

@pytest.fixture
def analyzed_circuit_get_impedance():
    return generate_analized_circuit_get_impedance()

def test_get_impedance(circuit_get_impedance, analyzed_circuit_get_impedance):
    """Check that get_impedance() sets the correct analysis on the
    AnalysisCircuit instance.

    GIVEN: a valid input circuit
    WHEN: I am analyzing a generic input element.
    THEN: the AnalysisCircuit instance contains all the correct analysis
    """
    caller = 'get_impedance_element()'
    impedance_parameters_map = analyzed_circuit_get_impedance.impedance_parameters_map
    assert isinstance(impedance_parameters_map, dict), (
        'TypeError in output of ' + caller + 'for \''
        + analyzed_circuit_get_impedance.circuit_string + '\'. It must be a '
        + ' dictionary')

    elements_list = list(
        analyzed_circuit_get_impedance.impedance_parameters_map.keys())
    valid_elements(elements_list, caller)

    wrong_tuples = wrong_tuples_get_impedance_element(
         circuit_get_impedance, analyzed_circuit_get_impedance)
    assert not wrong_tuples, (
        'TypeError in output of ' + caller + ' for element \'' + wrong_tuples
        + '\'. Its value in the dictionary have to be a tuple')

    wrong_functions = wrong_impedance_get_impedance_element(
        circuit_get_impedance, analyzed_circuit_get_impedance)
    assert not wrong_functions, (
        'TypeError in output of ' + caller + ' for element type(s) ' + ' \''
        + wrong_functions + '\'. Its first element of the tuple must be a '
        + 'function')

    check_parameters_get_impedance_element(circuit_get_impedance,
                                           analyzed_circuit_get_impedance,
                                           caller)

def generate_i_end():
    """Generate an index of the end of the cell."""
    i_end = 5
    return i_end

def generate_analized_circuit_cell_impedance():
    """Generate an analyzed circuit for a cell."""
    circuit_get_impedance = generate_circuit_get_impedance()
    circuit_string = circuit_get_impedance.circuit_string
    analyzed_circuit_cell_impedance = AnalisysCircuit(circuit_string, {})
    i_end = generate_i_end()
    i_start = get_position_opening_bracket(circuit_string, i_end)
    _ = analyzed_circuit_cell_impedance.generate_cell_impedance(
                    circuit_get_impedance, i_start, i_end)
    return analyzed_circuit_cell_impedance

@pytest.fixture
def analyzed_circuit_cell_impedance():
    return generate_analized_circuit_cell_impedance()

def test_analized_circuit_generate_cell_impedance(
        circuit_get_impedance, analyzed_circuit_cell_impedance):
    """Check that generate_cell_impedance() sets the correct analysis
    information about the analyzed cell inside the AnalysisCircuit instance.

    GIVEN: a correct initial circuit.
    WHEN: I am analyzing a whole cell.
    THEN: the AnalysisCircuit instance is updated with the analysis of the
    cell.
    """
    caller = 'get_cell_impedance()'
    impedance_parameters_map = analyzed_circuit_cell_impedance.impedance_parameters_map
    assert isinstance(impedance_parameters_map, dict), (
        'TypeError in output of ' + caller + ' for \''
        + analyzed_circuit_cell_impedance.circuit_string + '\'. It must be a '
        + ' dictionary')

    elements_list = list(
        analyzed_circuit_cell_impedance.impedance_parameters_map.keys())
    valid_elements(elements_list, caller)

    wrong_tuples = wrong_tuples_get_impedance_element(
         circuit_get_impedance, analyzed_circuit_cell_impedance)
    assert not wrong_tuples, (
        'TypeError in output of ' + caller + 'for element \'' + wrong_tuples
        + '\'. Its value in the dictionary have to be a tuple')

    wrong_functions = wrong_impedance_get_impedance_element(
        circuit_get_impedance, analyzed_circuit_cell_impedance)
    assert not wrong_functions, (
        'TypeError in output of ' + caller + 'for element type(s) \''
        + wrong_functions + '\'. Its first element of the tuple must be a '
        + 'function')

def wrong_impedance_generate_cell_impedance(impedance_cell):
    """Find any invalid function inside the iimpedance_cell. Used for testing.

    Parameters
    ----------
    impedance_cell : list
        List of the impedance functions inside the cell

    Returns
    -------
    wrong_functions_index : list
        List of indexes of the wrong functions in the string
    """
    wrong_functions_index = []
    for i, impedance_function in enumerate(impedance_cell):
        if not inspect.isfunction(impedance_function):
            wrong_functions_index.append(i)
    return wrong_functions_index

def circuit_string_impedance_cell_same_length(cell_string, impedance_cell):
    """Return if the a string circuit's element count and the length of the
    impedance_cell is the same.

    Parameters
    ----------
    cell_string : str
        Circuit string of the cell

    Returns
    -------
    equality_condition : bool
        Boolean condition for the length equality
    """
    element_list = list_elements_string(cell_string)
    equality_condition = (len(element_list)==len(impedance_cell))
    return equality_condition

def generate_impedance_cell():
    """Generate an impedance_cell list containing all the impedance functions
    of the elements of a cell.
    """
    circuit_get_impedance = generate_circuit_get_impedance()
    cell_string = circuit_get_impedance.circuit_string
    analyzed_circuit_cell_impedance_ = AnalisysCircuit(cell_string, {})
    i_end = generate_i_end()
    i_start = get_position_opening_bracket(cell_string, i_end)
    impedance_cell = analyzed_circuit_cell_impedance_.generate_cell_impedance(
                    circuit_get_impedance, i_start, i_end)
    return impedance_cell

@pytest.fixture
def impedance_cell():
    return generate_impedance_cell()

def test_impedance_list_cell_impedance(circuit_get_impedance, impedance_cell):
    """Check that get_impedance_const_input_element_type function returns a
    function.

    GIVEN: example_input_elements is a valid list of Element objects (they
    have a correct element string and a correct parameter).
    WHEN: I am calculating the correspondant impedance function while keeping
    the parameter(s) of this element constant.
    THEN: the impedance funtion is a function.
    """
    caller = 'generate_cell_impedance()'
    circuit_string = circuit_get_impedance.circuit_string
    assert isinstance(impedance_cell, list), (
        'TypeError in output of ' + caller + 'for \'' + circuit_string
        + '\'. It must be a list')

    wrong_functions_index = wrong_impedance_generate_cell_impedance(
        impedance_cell)
    assert not wrong_functions_index, (
        'TypeError in output of ' + caller
        + ' for element number(s) ' + ' \'' + str(wrong_functions_index)
        + '\'. The output must contain ony funtions')

    assert circuit_string_impedance_cell_same_length(
        circuit_string, impedance_cell), (
        'StructuralError in output of ' + caller + ' with cell '
        + circuit_string + '. The length of the output must be the same of '
        + 'the number of the element of the cell')


def invalid_characters_updated_string(updated_circuit_string):
    """Given a valid circuit string, a valid position of the start and end of
    the string substitution, find the invalid characters in the updated
    string. The obly valid characters are (, ), [, ], Z, R, C, Q and numbers.
    Used for testing.

    Parameters
    ----------
    updated_circuit_string : str
        Updated string

    Returns
    -------
    wrong_characters : str
        String that contains all the invald characters, separated by a comma
        and a whitespace
    wrong_characters_index : list
        List of indexes of the invalid characters in the string
    updated_circuit_string : str
        Updated string
    """
    wrong_characters = ''
    wrong_characters_index = []
    for i, char in enumerate(updated_circuit_string):
        if (char not in {'(', ')', '[', ']', 'Z', 'C', 'Q', 'R'}
                and not char.isnumeric()):
            wrong_characters += '\'' + char + '\', '
            wrong_characters_index.append(i)
    return wrong_characters, wrong_characters_index, updated_circuit_string

def inconsistent_elements_updated_string(updated_circuit_string):
    """Given a valid circuit string, a valid position of the start and end of
    the string substitution, find the inconsistent element in the updated
    string. Each element has a number that is the same of its order of writing
    in the string. Used for testing.

    Parameters
    ----------
    updated_circuit_string : str
        Updated string

    Returns
    -------
    wrong_elements : str
        String that contains all the inconsistent elements, separated by a
        comma and a whitespace
    wrong_element_index : list
        List of indexes of the inconsistent elements in the updated string
    updated_circuit_string : str
        Updated string
    """
    wrong_elements = ''
    wrong_element_index = []
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

def generate_updated_circuit_string():
    """Generate the updated circuit string given the previous circuit string
    and the start and end of the analyzed cell.
    """
    circuit_updated_circuit_string = generate_circuit_get_impedance()
    circuit_string = circuit_updated_circuit_string.circuit_string
    analyzed_circuit_update_string = AnalisysCircuit(circuit_string, {})
    i_end = generate_i_end()
    i_start = get_position_opening_bracket(circuit_string, i_end)
    cell_count = 1
    _ = analyzed_circuit_update_string.update_string(i_start, i_end,
                                                     cell_count)
    update_circuit_string = analyzed_circuit_update_string.circuit_string
    return update_circuit_string

@pytest.fixture
def updated_circuit_string():
    return generate_updated_circuit_string()

def test_update_string_valid_string(updated_circuit_string):
    """Check that update_string() method returns a valid string.

    GIVEN: a valid circuit string, a valid position of the start and end of
    the string substitution.
    WHEN: I am substituting the old string with the updated string, acording
    to the analysis done so far.
    THEN: the updated string is valid, except for the characters and the
    element consistency.
    """
    caller = 'update_string()'
    assert isinstance(updated_circuit_string, str), (
        'TypeError for circuit scheme in ' + caller+ '. It must be a string')
    assert updated_circuit_string, ('StructuralError: empty string in '
                                    + caller)
    assert same_number_of_brackets(updated_circuit_string), (
        'StructuralError: inconsistent number of open and close brackets in '
        + '\'' + updated_circuit_string + '\' in ' + caller)
    wrong_bracket, index_wrong_bracket = wrong_consistency_brackets(
        updated_circuit_string)
    assert not index_wrong_bracket, (
        'StructuralError: inconsistent \'' + str(wrong_bracket)+ '\' at '
        + index_wrong_bracket + ': ' + updated_circuit_string + ' in '
        + caller)
    (wrong_characters, wrong_characters_index,
     updated_circuit_string) = invalid_characters_updated_string(
         updated_circuit_string)
    assert not wrong_characters, (
        'Invalid character(s) ' + wrong_characters + ' at '
        + str(wrong_characters_index) + ' in ' + updated_circuit_string
        + ' in update_string(). Only round and square brackets, C, Q, R and '
        + 'natural numbers are valid characters')
    (wrong_elements, wrong_element_index,
     updated_circuit_string) = inconsistent_elements_updated_string(
         updated_circuit_string)
    assert not wrong_elements, (
        'element inconsistency for '+ wrong_elements + ' at '
        + str(wrong_element_index) + ' in updated string: '
        + updated_circuit_string + '. An element is composed by a valid '
        + 'letter followed by a natural number')

def generate_new_element():
    """Generate the updated circuit string given the previous circuit string
    and the start and end of the analyzed cell.
    """
    circuit_updated_circuit_string = generate_circuit_get_impedance()
    circuit_string = circuit_updated_circuit_string.circuit_string
    analyzed_circuit_update_string = AnalisysCircuit(circuit_string, {})
    i_end = generate_i_end()
    i_start = get_position_opening_bracket(circuit_string, i_end)
    cell_count = 1
    new_element = analyzed_circuit_update_string.update_string(
        i_start, i_end, cell_count)
    return new_element

@pytest.fixture
def new_element():
    return generate_new_element()

def test_update_string_new_element(new_element):
    """Check that update_string returns a valid string.

    GIVEN: a valid circuit string, a valid position of the start and end of
    the string substitution.
    WHEN: I am substituting the old string with the updated string, acording
    to the analysis done so far.
    THEN: the updated string is valid, except for the characters and the
    element consistency.
    """
    caller = 'update_string()'
    assert isinstance(new_element, str), (
        'TypeError for circuit scheme in ' + caller+ '. It must be a string')
    assert updated_circuit_string, ('StructuralError: empty string in '
                                    + caller)
    assert len(new_element)==2, (
        'Invalid length for ' + new_element + ' in ' + caller + '. It has to '
        + 'be of length 2')
    assert new_element.startswith('Z'), (
        'StrcuturalError for '+ new_element + ' in ' + caller + '. A  new '
        + 'element must begin with a \'Z\'')
    last_element = new_element[-1]
    assert last_element.isnumeric(), (
        'StrcuturalError for '+ new_element + ' in ' + caller + '. A  new '
        + 'element must end with a numeric char')

def generate_analyzed_circuit_final_results():
    """Generate an analyzed circuit with the final results attribuyes set."""
    circuit_get_results = generate_circuit_get_impedance()
    circuit_string = circuit_get_results.circuit_string
    analyzed_circuit_final_results = AnalisysCircuit(circuit_string, {})
    i_end = generate_i_end()
    i_start = get_position_opening_bracket(circuit_string, i_end)
    impedance_cell = analyzed_circuit_final_results.generate_cell_impedance(
        circuit_get_results, i_start, i_end)
    impedance_cell_equivalent = serial_comb(impedance_cell)
    cell_count = 1
    new_element = analyzed_circuit_final_results.update_string(i_start, i_end,
                                                             cell_count)
    analyzed_circuit_final_results.impedance_parameters_map[
        new_element] = (impedance_cell_equivalent, 'equivalent')
    analyzed_circuit_final_results.get_final_results()
    return analyzed_circuit_final_results

@pytest.fixture
def analyzed_circuit_final_results():
    return generate_analyzed_circuit_final_results()

def generate_final_impedance():
    """Generate the final impedance of an analyzed circuit."""
    analyzed_circuit = generate_analyzed_circuit_final_results()
    final_impedance = analyzed_circuit.impedance
    return final_impedance

@pytest.fixture
def final_impedance():
    return generate_final_impedance()

def test_impedance_get_final_results(final_impedance):
    """Check that the final impedance is a function.

    GIVEN: a valid analyzed circuit.
    WHEN: I am setting the final results in the analyzed circuit.
    THEN: the final impedance is a function.
    """
    assert inspect.isfunction(final_impedance), (
        'TypeError for the final impedance of the AnalysisCircuit. It must '
        + 'be a function')

def generate_final_parameters_map():
    """Generate the final parameters_map of an analyzed circuit."""
    analyzed_circuit = generate_analyzed_circuit_final_results()
    final_parameters_map = analyzed_circuit.parameters_map
    return final_parameters_map

@pytest.fixture
def final_parameters_map():
    return generate_final_parameters_map()

def wrong_match_element_initial_circuit_final_parameters(final_parameters_map,
                                                         initial_parameters):
    """Find any non-constant element in the initial circuit that is missing
    in the final parameters_map.

    Parameters
    ----------
    final_parameters_map : dict
        Final parameters map
    initial_parameters : Circuit
        Initial circuit, object of the analysis

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

def wrong_match_parameter_initial_circuit_final_parameters(
        final_parameters_map, initial_parameters):
    """Find any non-constant parameter in the initial circuit that is missing
    in the final parameters_map.

    Parameters
    ----------
    final_parameters_map : dict
        Final parameters map
    initial_parameters : Circuit
        Initial circuit, object of the analysis

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

def test_parameters_get_final_results(final_parameters_map,
                                      circuit_get_impedance):
    """Check that the final parameters_map has all the non-constant elements
    in the initial circuit.

    GIVEN: a valid analyzed circuit.
    WHEN: I am setting the final results in the analyzed circuit.
    THEN: the final parameters_map matches the one in the initial circuit.
    """
    initial_parameters = circuit_get_impedance.parameters_map

    wrong_elements = wrong_match_element_initial_circuit_final_parameters(
        final_parameters_map, initial_parameters)
    assert not wrong_elements, (
        'Bad match between non constant elements of the initial circuit and '
        + 'the final analysis parameter. ' + wrong_elements + 'not found')

    wrong_parameters = wrong_match_parameter_initial_circuit_final_parameters(
        final_parameters_map, initial_parameters)
    assert not wrong_parameters, (
        'Bad match between parameters of the initial circuit and the final '
        + 'analysis parameter. Parameter of element ' + wrong_elements
        + 'not found')


def wrong_match_element_final_parameters_list_elements(final_elements_list,
                                                       final_parameters_map):
    """Find any non-constant element in the final parameters map that is
    missing in the element_list given by the list_elements() method.

    Parameters
    ----------
    final_elements_list : list
        Elements list (non-constant)
    final_parameters_map : dict
        Dictionary containing all the non-constant elements as keys

    Returns
    -------
    wrong_elements : str
        String that contains all the absent elements, separated by a comma
        and a whitespace
    """
    wrong_elements = ''
    for element in final_parameters_map.keys():
        if not element in final_elements_list:
            wrong_elements += '\'' + element + '\', '
    return wrong_elements

def generate_final_elements_list():
    """Generate final elements list out of the final parameters_map."""
    analyzed_circuit = generate_analyzed_circuit_final_results()
    final_elements_list = analyzed_circuit.list_elements()
    return final_elements_list

@pytest.fixture
def final_elements_list():
    return generate_final_elements_list()

def test_list_elements(final_elements_list, analyzed_circuit_final_results):
    """Check that the list_elements() method return a list containing all the
    non-constant element strings, with all the element inside the
    parameters_map and of the same length of its list of keys.

    GIVEN: a valid analyzed circuit with the final results set.
    WHEN: I am extracting the final element list.
    THEN: the final element list is a valid list containg all and only the
    non-constant elements.
    """
    caller = 'list_elements()'
    assert isinstance(final_elements_list, list), (
        'TypeError for ' + caller + '. The output must be a list')
    final_parameters_map = analyzed_circuit_final_results.parameters_map
    assert len(final_elements_list)==len(list(final_parameters_map.keys())), (
        'StructuralError for ' + caller + ' between final elements of the '
        + 'analyzed circuit and its list of elements. They have to be of the '
        + 'same length')

    wrong_elements = wrong_match_element_final_parameters_list_elements(
        final_elements_list, final_parameters_map)
    assert not wrong_elements, (
        'Bad match for ' + caller + ' between final elements of the analyzed circuit and '
        + 'its list of elements. ' + wrong_elements + 'not found')


def wrong_match_parameter_final_parameters_list_parameters(
        final_parameters_list, final_parameters_map):
    """Find any non-constant parameter in the final parameters map that is
    missing in the element_list given by the list_parameters() method.

    Parameters
    ----------
    final_parameters_list : list
        Elements list (non-constant)
    final_parameters_map : dict
        Dictionary containing all the non-constant elements as keys

    Returns
    -------
    wrong_elements : str
        String that contains all the absent parameters, separated by a comma
        and a whitespace
    """
    wrong_parameters = ''
    for parameter in final_parameters_map.values():
        if not parameter in final_parameters_list:
            wrong_parameters += '\'' + str(parameter) + '\', '
    return wrong_parameters

def generate_final_parameters_list():
    """Generate final parameters list out of the final parameters_map."""
    analyzed_circuit = generate_analyzed_circuit_final_results()
    final_parameters_list = analyzed_circuit.list_parameters()
    return final_parameters_list

@pytest.fixture
def final_parameters_list():
    return generate_final_parameters_list()

def test_list_parameters(final_parameters_list, analyzed_circuit_final_results):
    """Check that the list_parameters() method return a list containing all the
    non-constant parameters, with all the parameters inside the
    parameters_map and of the same length of its list of values.

    GIVEN: a valid analyzed circuit with the final results set.
    WHEN: I am extracting the final parameters list.
    THEN: the final parameters list is a valid list containg all and only the
    non-constant parameters.
    """
    caller = 'list_parameters()'
    assert isinstance(final_parameters_list, list), (
        'TypeError for ' + caller + '. The output must be a list')
    analyzed_circuit_final_results.get_final_results()
    final_parameters_map = analyzed_circuit_final_results.parameters_map
    assert len(final_parameters_list)==len(list(
        final_parameters_map.values())), (
        'StructuralError for ' + caller + ' between final parameters of the '
        + 'analyzed circuit and its list of parameters. They have to be of '
        + 'the same length')
    wrong_parameters = wrong_match_parameter_final_parameters_list_parameters(
        final_parameters_list, final_parameters_map)
    assert not wrong_parameters, (
        'Bad match for ' + caller + ' between final parameters of the '
        + 'analyzed circuit and its list of parameters. ' + wrong_parameters
        + 'not found')

################################
#Test mischellanous functions

@given(frequency=enp.arrays(dtype=float, shape=10, elements=st.floats(1, 1e4),
                            unique=True),
       resistance=st.floats(min_value=10, max_value=1e5))
@settings(max_examples=10)
def test_impedance_resistor(resistance, frequency):
    """Check that the definition of the impedance of resistors returns a
    valid impedance vector.

    GIVEN: the value of resistance and frequencies are valid
    WHEN: every time the impedance of a resisitor is needed
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


@given(frequency=enp.arrays(dtype=float, shape=10, elements=st.floats(1, 1e4),
                            unique=True),
       capacitance=st.floats(min_value=1e-9, max_value=1e-5))
@settings(max_examples=10)
def test_impedance_capacitor(capacitance, frequency):
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


@given(frequency=enp.arrays(dtype=float, shape=10, elements=st.floats(1, 1e4),
                            unique=True),
       q_parameter=st.floats(min_value=1e-9, max_value=1e-5),
       ideality_factor=st.floats(min_value=0., max_value=1.))
@settings(max_examples=10)
def test_impedance_cpe(q_parameter, ideality_factor, frequency):
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


def generate_first_function():
    """Generate a function."""
    first_function = lambda x, y: x + y
    return first_function

@pytest.fixture
def first_function():
    return generate_first_function()

def generate_second_function():
    """Generate a function."""
    second_function = lambda x, y: x*y
    return second_function

@pytest.fixture
def second_function():
    return generate_second_function()

def test_add(first_function, second_function):
    """Check that the add function returns a function.

    GIVEN: first_function, second_function are functions.
    WHEN: I want the sum function of them.
    THEN: the sum function is a function.
    """
    assert inspect.isfunction(add(first_function, second_function)),(
        'TypeError in output of add(). It must be a function')


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

    GIVEN: function_list is a list of functions.
    WHEN: I want the equivalent function of a serial comb of them.
    THEN: the equivalent function is a function.
    """
    assert inspect.isfunction(serial_comb(function_list)), (
        'TypeError in output of serial_comb(). It must be a function')


@pytest.fixture
def function_():
    return generate_first_function()

def test_reciprocal(function_):
    """Check that the add function returns a function.

    GIVEN: function_ is a funtion.
    WHEN: I want the inverse function of function_.
    THEN: the inverse function is a function.
    """
    assert inspect.isfunction(reciprocal(function_)), (
        'TypeError in output of reciprical(). It must be a function')


def test_parallel_comb(function_list):
    """Check that the serial_comb function returns a function.

    GIVEN: function_list is a list of functions.
    WHEN: I want the equivalent function of a parallel comb of them.
    THEN: the equivalent function is a function.
    """
    assert inspect.isfunction(parallel_comb(function_list)), (
        'TypeError in output of parallelComb(). It must be a function')


def generate_last_opening_bracket_position():
    """Return a valid last opening bracket in a circuit string."""
    circuit_get_impedance = generate_circuit_get_impedance()
    circuit_string = circuit_get_impedance.circuit_string
    i_end = generate_i_end()
    last_opening_bracket_position = get_position_opening_bracket(
        circuit_string, i_end)
    return last_opening_bracket_position

@pytest.fixture
def last_opening_bracket_position():
    return generate_last_opening_bracket_position()

def test_get_position_opening_bracket(last_opening_bracket_position):
    """Check that get_position_opening_bracket() returns an integer.

    GIVEN: a valid circuit string and i_end that is the position of a closed
    bracket.
    WHEN: the function to divide the circuit string in cell i called
    THEN: the index of the start of the cell is a positive integer
    """
    assert isinstance(last_opening_bracket_position, int), (
        'TypeError in output of get_position_opening_bracket(). Last '
        + 'opening bracket position must be an integer')
    assert last_opening_bracket_position>=0, ('ValueError in output of '
        + 'get_position_opening_bracket(). Last opening bracket position '
        + 'must be non-negative')

def generate_string_():
    """Generate a string vector of two elements."""
    list_string = ['first element', 'second element']
    string_ = get_string(list_string)
    return string_

@pytest.fixture
def string_():
    return generate_string_()

def test_get_string(string_):
    """Check that the output of get_string() is a valid string.

    GIVEN: a list of strings
    WHEN: the function to concatenate a list of strings is called
    THEN: the output of get_string() is a string
    """
    assert isinstance(string_, str), ('TypeError for output of get_string(): '
        + 'the output must be a string, not a ' + str(type(string_)))

##########################
#Test Circuit Class

def wrong_match_constant_element(parameters_map, initial_parameters_map):
    """Find any constant element in the initial circuit that is also present
    in the final parameters_map of the analyzed circuit.

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
            if element in parameters_map.keys():
                wrong_const_elements += '\'' + element + '\', '
    return wrong_const_elements

def wrong_non_existent_element(parameters_map, initial_parameters_map):
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
    for element in parameters_map.keys():
        if element not in initial_parameters_map.keys():
            wrong_non_e_elements += '\'' + element + '\', '
    return wrong_non_e_elements

def generate_non_const_initial_circuit():
    """Generate an initial circuit that has the first two elements non
    constant.
    """
    non_const_initial_circuit = generate_initial_circuit_data()
    parameter_value_r1 = non_const_initial_circuit.parameters_map['R1'][0]
    non_const_initial_circuit.parameters_map['R1'] = (parameter_value_r1, 0)
    parameter_value_c2 = non_const_initial_circuit.parameters_map['C2'][0]
    non_const_initial_circuit.parameters_map['C2'] = (parameter_value_c2, 0)
    return non_const_initial_circuit

@pytest.fixture
def non_const_initial_circuit():
    return generate_non_const_initial_circuit()

def generate_full_analyzed_circuit():
    """Generate a generic full analyzed circuit."""
    non_const_initial_circuit = generate_non_const_initial_circuit()
    full_analyzed_circuit = non_const_initial_circuit.generate_analyzed_circuit()
    return full_analyzed_circuit

@pytest.fixture
def full_analyzed_circuit():
    return generate_full_analyzed_circuit()

def test_generate_analyzed_circuit(full_analyzed_circuit,
                                   non_const_initial_circuit):
    """Check that the generate_analyzed_circuit() method return a
    valid AnalysisCircuit instance.

    GIVEN: a initial circuit.
    WHEN: I am creating the analyzed circuit.
    THEN: the output is a valid AnalysisCircuit instance.
    """
    caller = 'generate_analyzed_circuit()'
    assert isinstance(full_analyzed_circuit, AnalisysCircuit), (
        'TyperError for output of ' + caller + ' method. It must be an '
        + 'instance of the \'AnalisysCircuit\' class')

    string_analyzed_circuit = full_analyzed_circuit.circuit_string
    assert isinstance(string_analyzed_circuit, str), (
        'TypeError for the circuit string of the output of ' + caller + ' It '
        + 'must be a string')
    assert inspect.isfunction(full_analyzed_circuit.impedance), (
        'TypeError for the final impedance of the output of ' + caller
        + '. It must be a function')

    parameters_map = full_analyzed_circuit.parameters_map
    assert isinstance(parameters_map, dict), (
        'TypeError for the parameters map of the output of ' + caller
        + '. It must be a dictionary')
    initial_parameters_map = non_const_initial_circuit.parameters_map
    wrong_elements = wrong_match_element_initial_circuit_final_parameters(
        parameters_map, initial_parameters_map)
    assert not wrong_elements, (
        'Bad match between non constant elements of the initial circuit and '
        + 'the final analysis parameter. ' + wrong_elements + 'not found')
    wrong_parameters = wrong_match_parameter_initial_circuit_final_parameters(
        parameters_map, initial_parameters_map)
    assert not wrong_parameters, (
        'Bad match between parameters of the initial circuit and the final '
        + 'analysis parameter. Parameter of element '+ wrong_elements
        + 'not found')
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


def generate_parameters_string():
    """Generate an example of initial parameters string."""
    initial_circuit_with_error = generate_non_const_initial_circuit()
    initial_circuit_with_error.error = 225.8
    parameters_string = initial_circuit_with_error.get_initial_parameters()
    return parameters_string

@pytest.fixture
def parameters_string():
    return generate_parameters_string()

def test_get_initial_parameters(parameters_string):
    """Check that the output of get_initial_parameters() is a valid string.

    GIVEN: a valid inital circuit.
    WHEN: the initial parametrs string is created.
    THEN: the output is a string.
    """
    assert isinstance(parameters_string, str), ('TypeError for output of '
        + 'get_string(): the output must be a string, not a '
        + str(type(parameters_string)))


def generate_list_of_elements():
    """Generate an example of string elements list of a circuit."""
    circuit_string = generate_circuit_string_data()
    string_elements = list_elements_string(circuit_string)
    return string_elements

@pytest.fixture
def string_elements():
    return generate_list_of_elements()

def test_list_elements_string(string_elements):
    """Check that the output of get_initial_parameters() is a valid string.

    GIVEN: a valid circuit string.
    WHEN: the list of all the string element is needed.
    THEN: the output is a string.
    """
    caller = 'list_elements_string()'
    valid_elements(string_elements, caller)


#########################################################################
#Test Generate_data.py


def generate_frequencies():
    """Generate the impedance array, used for testing."""
    frequency_vector = set_frequencies()
    return frequency_vector

@pytest.fixture
def frequency_vector():
    return generate_frequencies()

def wrong_elements_set_frequencies(frequency_vector):
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

def test_set_frequencies(frequency_vector):
    """Check that the output of set_frequencies() is an array.

    WHEN: the function to generate the frequencies is called
    THEN: the frequencies are an array
    """
    assert isinstance(frequency_vector, np.ndarray), (
        'TypeError in set_frequencies(): the output must be a numpy.ndarray')
    assert frequency_vector.size>0, (
        'StructuralError in set_frequencies(): the output cannot be empty')
    wrong_element, wrong_element_index = wrong_elements_set_frequencies(
        frequency_vector)
    assert not wrong_element, (
        'ValueError in output of set_frequencies(): element(s) '
        + str(wrong_element) + ' in position(s) ' + str(wrong_element_index)
        + ' are not positive')


def generate_file_name_generation():
    """Generate the data file name where the generated data will be written,
    used for testing.
    """
    file_name = set_file_name()
    return file_name

@pytest.fixture
def file_name():
    return generate_file_name_generation()

def test_file_name(file_name):
    """Check that the data file name is a string.

    WHEN: the function to generate the file name where the data will
    be saved/imported from is called
    THEN: the file name is a string
    """
    caller = 'set_file_name()'
    assert isinstance(file_name, str), (
        'TypeError in ' + caller + ': the file name must be a '
        + ' string')
    assert file_name.endswith('.txt'), (
        'StructuralError in ' + caller + ': invalid file '
        + 'extention. The file name must end with the right extention (.txt)')
    assert not file_name.startswith('.txt'), (
        'StructuralError in ' + caller + ': invalid file '
        + 'name. The file name must have at least one character before the '
        + 'file extention')


def wrong_elements_generate_random_error(random_error_component):
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
    wrong_element = []
    wrong_element_index = []
    for i, element in enumerate(random_error_component):
        if abs(element)>1.:
            wrong_element.append(element)
            wrong_element_index.append(i)
    return wrong_element, wrong_element_index

@given(signal_length=st.integers(min_value=1, max_value=100))
@settings(max_examples=10)
def test_generate_random_error_component_array(signal_length):
    """Check that the output of generate_random_error_component() is an array.

    GIVEN: a valid length of the generated signal
    WHEN: the function to generate random numbers to simulate noise is called
    THEN: the random noise is an array
    """
    random_error_component = generate_random_error_component(signal_length)
    assert isinstance(random_error_component, np.ndarray), (
        'TypeError in generate_random_error_component(): the output must be '
        + 'a numpy.ndarray')
    assert random_error_component.size>0, (
        'StructuralError in generate_random_error_component(): the output'
        + 'cannot be empty')
    (wrong_element,
     wrong_element_index) = wrong_elements_generate_random_error(
         random_error_component)
    assert not wrong_element, (
        'ValueError in output of generate_random_error_component(): '
        + 'element(s) ' + str(wrong_element) + ' in position(s) '
        + str(wrong_element_index) + ' are not within 0 and 1')


def generate_simulated_signal():
    """Generate a simulated signal vector, with simulated noise, given the
    description of the circuit. Used for testing.
    """
    frequency_vector = set_frequencies()
    initial_circuit = generate_initial_circuit_data()
    analyzed_circuit_data = initial_circuit.generate_analyzed_circuit()
    impedance_function = analyzed_circuit_data.impedance

    parameters = analyzed_circuit_data.list_parameters()
    signal_vector = impedance_function(parameters,
                                       frequency_vector)
    simulated_signal = simulate_noise(signal_vector)
    return simulated_signal

@pytest.fixture
def simulated_signal():
    return generate_simulated_signal()

def test_simulate_noise(simulated_signal):
    """Check that the output of simulate_noise() is an array.

    GIVEN: a valid generated signal
    WHEN: the function to generate random numbers to simulate noise is called
    THEN: the random noise array is an numpy array
    """
    assert isinstance(simulated_signal, np.ndarray), (
        'TypeError in simulate_noise(): the output must be a numpy.ndarray')
    assert simulated_signal.size>0, (
        'TypeError in simulate_noise(): the output cannot be an empty array')
    assert simulated_signal.ndim==1, (
        'TypeError in simulate_noise(): the output must be a one-dimention '
        + 'array, while it is ' + str(simulated_signal.ndim))
    assert simulated_signal.dtype==complex, (
        'TypeError in simulate_noise(): the output must be a float array, '
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

def non_positive_values_get_modulus(modulus_vector):
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

def test_get_modulus(modulus_vector):
    """Check that the output of get_modulus() is an array.

    GIVEN: a valid impedance array
    WHEN: the function to exctract the modulus of the impedance array is
    called
    THEN: the modulus is an array
    """
    assert isinstance(modulus_vector, np.ndarray), (
        'TypeError in get_modulus(): the output must be a numpy.ndarray')
    assert modulus_vector.size>0, (
        'StructuralError in get_modulus(): the output cannot be empty')
    assert modulus_vector.ndim==1, (
        'TypeError in get_modulus(): the output must be a one-dimention '
        + 'array, while it is ' + str(modulus_vector.ndim))
    assert modulus_vector.dtype==float, (
        'TypeError in get_modulus(): the output must be a float array, '
        + 'while it is ' + str(modulus_vector.dtype))
    wrong_value, wrong_value_index = non_positive_values_get_modulus(
        modulus_vector)
    assert not wrong_value, (
        'ValueError for modulus ' + str(wrong_value) + ' number '
        + str(wrong_value_index) + ' in get_modulus() output. Modulus must '
        + 'be positive')


def generate_phase_vector():
    """Generate the phase of an impedance vector with simulated noise."""
    impedance_vector = generate_simulated_signal()
    phase_vector = get_phase(impedance_vector)
    return phase_vector

@pytest.fixture
def phase_vector():
    return generate_phase_vector()

def test_get_phase(phase_vector):
    """Check that the output of get_phase() is an array.

    GIVEN: a valid impedance array
    WHEN: the function to exctract the phase of the impedance array is called
    THEN: the phase is an array
    """
    assert isinstance(phase_vector, np.ndarray), (
        'TypeError in get_phase(): the output must be a numpy.ndarray')
    assert phase_vector.size>0, (
        'StructuralError in get_phase(): the output cannot be empty')
    assert phase_vector.ndim==1, (
        'TypeError in get_phase(): the output must be a one-dimention array, '
        + 'while it is ' + str(phase_vector.ndim))
    assert phase_vector.dtype==float, (
        'TypeError in get_phase(): the output must be a float array, while '
        + 'it is ' + str(phase_vector.dtype))

###################################################################
#Test Impedance_anaysis.py

##################
#Test generation

@pytest.fixture
def circuit_string_fit():
    return generate_circuit_string_fit()

def test_input_string_fit(circuit_string_fit):
    """Check that the input circuit string in the fit module is a valid
    string.

    WHEN: when an input circuit string is set
    THEN: the circuit represent a valid circuit
    """
    caller = 'generate_circuit_string_fit()'
    is_valid_input_string(circuit_string_fit, caller)

@pytest.fixture
def parameters_fit():
    return generate_circuit_parameters_fit()

def test_input_parameters_fit(parameters_fit, circuit_string_fit):
    """Check that the input parameters in the fit module are valid and
    contained in a list.

    GIVEN: input circuit string is a valid circuit string.
    WHEN: when an input parameters list is set.
    THEN: the parameters list represent a valid set of parameters, in accord
    to the circuit string.
    """
    caller = 'generate_circuit_parameters_fit()'
    are_valid_input_parameters(parameters_fit, circuit_string_fit, caller)

@pytest.fixture
def constant_elements_fit():
    return generate_constant_elements_fit()

def test_input_constant_elements_fit(constant_elements_fit, parameters_fit):
    """Check that the input constant conditions in the fit module are valid.
    
    GIVEN: the parameters list is a valid parameters list, related to the
    correspondant circuit string.
    WHEN: the constant element condition list generation function is called.
    THEN: the constant elements condition list is valid.
    """
    caller = 'generate_constant_elements_data()'
    are_valid_constant_elements(constant_elements_fit, parameters_fit, caller)


def generate_initial_circuit_fit():
    """Generate an initial circuit in the fit module."""
    circuit_string_fit = generate_circuit_string_fit()
    parameters_fit = generate_circuit_parameters_fit()
    constant_elements_fit = generate_constant_elements_fit()
    initial_circuit_fit = generate_circuit_fit(
        circuit_string_fit, parameters_fit, constant_elements_fit)
    return initial_circuit_fit

@pytest.fixture
def initial_circuit_fit():
    return generate_initial_circuit_fit()

def test_generate_circuit_fit(initial_circuit_fit, circuit_string_fit,
                               parameters_fit, constant_elements_fit):
    """Check that the initial circuit in the fit module is valid.

    GIVEN: the input circuit string, parameters list and constant cinditions
    are valid.
    WHEN: the initial circuit generation is called.
    THEN: the output is a valid initial circuit.
    """
    caller = 'generate_circuit_fit()'
    valid_circuit(initial_circuit_fit, circuit_string_fit, parameters_fit,
                  constant_elements_fit, caller)

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
    assert isinstance(file_name_analysis, str), (
        'TypeError in ' + caller + ': the file name must be a '
        + ' string')
    assert file_name_analysis.endswith('.txt'), (
        'StructuralError in ' + caller + ': invalid file '
        + 'extention. The file name must end with the right extention (.txt)')
    assert not file_name_analysis.startswith('.txt'), (
        'StructuralError in ' + caller + ': invalid file '
        + 'name. The file name must have at least one character before the '
        + 'file extention')


def generate_number_of_columns():
    """Geneerate the number of columns of an impedance data file. Must
    generate a file first.
    """
    file_name = generate_file_name_analysis()
    number_of_columns = get_number_of_columns(file_name)
    return number_of_columns

@pytest.fixture
def number_of_columns():
    return generate_number_of_columns()

def test_get_number_of_columns(number_of_columns):
    """Check that the number of columns in get_number_of_columns() is an
    integer.

    WHEN: the data file name is read to count the number of data columns
    THEN: number of columns is an integer
    """
    assert isinstance(number_of_columns, int), (
        'TypeError in get_number_of_columns(): the output must be an '
        + 'integer, while it is ' + str(type(number_of_columns)))
    assert (number_of_columns in (2, 3)), (
        'StructuralError in get_number_of_columns(): the output must be '
        + 'either 2 or 3, while it is ' + str(number_of_columns))


def generate_frequency_vector_analysis():
    """Generate the frequency vector imported from data"""
    file_name = get_file_name()
    frequency_vector_analysis, _ = read_data(file_name)
    return frequency_vector_analysis

@pytest.fixture
def frequency_vector_analysis():
    return generate_frequency_vector_analysis()

def non_positive_frequencies_read_data(frequency_vector):
    """Return the frequencies in a frequency_vector that are not positive.
    Used for testing.

    Parameters
    ----------
    frequency_vector : array
        Array of frequencies read from data file.

    Returns
    -------
    wrong_value : list
        List that contains all the invalid frequencies.
    wrong_value_index : list
        List of indexes of the invalid frequencies in the array.
    """
    wrong_value = []
    wrong_value_index = []
    for i, element in enumerate(frequency_vector):
        if element<=0:
            wrong_value.append(element)
            wrong_value_index.append(i)
    return wrong_value, wrong_value_index

def test_read_data_frequency(frequency_vector_analysis):
    """Check that the output of read_data() is a valid impedance array as
    second argument.

    GIVEN: a valid file_name and a valid number of columns
    WHEN: the function to read data from a data file is called
    THEN: the second argument is a proper impedance vector: a 1D numpy array
    containing only positive values (floats or integers)
    """
    frequency = frequency_vector_analysis
    assert isinstance(frequency, np.ndarray), (
        'TypeError in the output read_data(): the the first argument must be a '
        + 'numpy.ndarray')
    assert frequency.size>0, (
        'StructuralError in the output read_data(): the the first argument '
        + 'cannot be empty')
    assert frequency.ndim==1, (
        'TypeError in the output read_data(): the the first argument must be a '
        + 'one-dimention array, while it is '
        + str(frequency.ndim))
    assert (frequency.dtype==float or frequency.dtype==int), (
        'TypeError in read_data(): the the first argument must be a float '
        + ' array, while it is ' + str(frequency_vector_analysis.dtype))
    wrong_value, wrong_value_index = non_positive_frequencies_read_data(
        frequency)
    assert not wrong_value, (
        'ValueError for impedance ' + str(wrong_value) + ' number '
        + str(wrong_value_index) + ' in read_data() output. Frequencies must '
        + 'be positive')


def generate_impedance_data_vector_analysis():
    """Generate the impedance data."""
    file_name = get_file_name()
    _, impedance_data_vector_analysis = read_data(file_name)
    return impedance_data_vector_analysis

@pytest.fixture
def impedance_data_vector_analysis():
    return generate_impedance_data_vector_analysis()

def test_read_data_impedance(impedance_data_vector_analysis):
    """Check that the output of read_data() is a valid impedance array as
    second argument.

    GIVEN: a valid file_name and a valid number of columns
    WHEN: the function to read data from a data file is called
    THEN: the second argument is a proper impedance vector: a 1D numpy complex
    array containing
    """
    impedance = impedance_data_vector_analysis
    assert isinstance(impedance, np.ndarray), (
        'TypeError in the output read_data(): the second argument must be a '
        + 'numpy.ndarray')
    assert impedance.size>0, (
        'StructuralError in the output read_data(): the second argument '
        + 'cannot be empty')
    assert impedance.ndim==1, (
        'TypeError in the output read_data(): the second argument must be a '
        + 'one-dimention array, while it is '
        + str(impedance.ndim))
    assert np.iscomplexobj(impedance), (
        'TypeError in read_data(): the second argument must be a complex '
        + 'array, while it is ' + str(impedance.dtype))

def generate_error():
    """Generate the error from the error function, given a typical data
    example. Used for testing.
    """
    initial_circuit = generate_initial_circuit_fit()
    analyzed_circuit = initial_circuit.generate_analyzed_circuit()
    impedance_function = analyzed_circuit.impedance
    file_name = get_file_name()
    frequency_vector, impedance_data_vector = read_data(file_name)

    parameters = analyzed_circuit.list_parameters()
    error = error_function(parameters, impedance_data_vector,
                           impedance_function, frequency_vector)
    return error

@pytest.fixture
def error():
    return generate_error()

def test_error_function(error):
    """Check that the output of error_function() is a valid error (a positive
    float).

    GIVEN: a valid imported data and a valid correspondant impedance function.
    WHEN: the function to calculate the error between the impedance function
    (with given parameters) and the data is called.
    THEN: the error is a positive float or int.
    """
    assert isinstance(error, (float, int)), (
        'TypeError for output of error_function(): the output must be a '
        + 'float or an integer, not a ' + str(type(error)))
    assert error>0, ('StructuralError in output of error_function(): the '
        + 'output must be positive')


def wrong_element_type_bound_definitions(bounds_list):
    """Find the invalid elements type (any but tuples) inside the bounds list.
    Used for testing

    Parameters
    ----------
    bounds_list : list
        List of all the bounds (numeric/None tuples).

    Returns
    -------
    wrong_element_index : list
        List of indexes of the wrong bounds in the list.
    """
    wrong_element_type_index = []
    for i, bound in enumerate(bounds_list):
        if not isinstance(bound, tuple):
            wrong_element_type_index.append(i)
        elif len(bound)!=2:
            wrong_element_type_index.append(i)
    return wrong_element_type_index

def wrong_element_value_bound_definitions(bounds_list):
    """Find the invalid elements values (any but tuples) inside the bounds
    list. Used for testing.

    Parameters
    ----------
    bounds_list : list
        List of all the bounds (numeric tuples)

    Returns
    -------
    wrong_element_index : str
        String of indexes of the wrong elements in the list
    """
    wrong_element_value_index = ''
    for i, bound in enumerate(bounds_list):
        if not isinstance(bound[0], (float, int)):
            wrong_element_value_index += '[' + str(i) + '] (first element), '
        elif isinstance(bound[0], (float, int)):
            if bound[0]<0:
                wrong_element_value_index += ('[' + str(i) + '] (first '
                                              + 'element), ')
        if not (isinstance(bound[1], (float, int)) or bound[1] is None):
            wrong_element_value_index += '[' + str(i) + '] (second element), '
        elif isinstance(bound[1], (float, int)):
            if (bound[1]<bound[0] or bound[1]<0):
                wrong_element_value_index += ('[' + str(i) + '] (second '
                + 'element), ')
    return wrong_element_value_index

def count_q(elements_bound, i_element):
    """Count howm many Q elements there are before a certain element.

    Parameters
    ----------
    elements : list
        List of elements string of the fitting parameters.
    i_element : int
        Index of the element of interest.

    Returns
    -------
    number_of_q : int
        Number of Q elements present before a certain element.
    """
    number_of_q = 0
    for element in elements_bound[:i_element]:
        number_of_q += element.count('Q')
    return number_of_q

def bound_definitions_same_length_elements_list(elements_bound, bounds_list):
    """Return whether there is a consistent correspondance between the length
    of elements and bounds_list. For each element but for Q 1 element is equal
    to 1 bound. For Q case is 1 element to 2 bounds. Used for testing

    Parameters
    ----------
    elements : list
        List of elements string of the fitting parameters
    bounds_list : list
        List of all the bounds (numeric tuples)

    Returns
    -------
    consistent_condition : bool
        Boolean condition for length equality
    """
    number_of_q = count_q(elements_bound, len(elements_bound)+1)
    consistent_condition = ((len(elements_bound)+number_of_q)==len(
        bounds_list))
    return consistent_condition

def bad_match_bound_definitions_elements_list(elements_bound, bounds_list):
    """Find the invalid correspondance between a single element and its bound.
    Used for testing

    Parameters
    ----------
    elements : list
        List of elements string of the fitting parameters
    bounds_list : list
        List of all the bounds (numeric tuples)

    Returns
    -------
    wrong_match_index : str
        String of indexes of the wrong matches in the list
    """
    wrong_match_index = ''
    for i, element in enumerate(elements_bound):
        if not element.startswith('Q'):
            number_of_q = count_q(elements_bound, i)
            if bounds_list[i+number_of_q][0]==0:
                wrong_match_index += '[' + str(i) + '] (first element), '
        if element.startswith('Q'):
            number_of_q = count_q(elements_bound, i)
            if bounds_list[i+number_of_q][0]==0:
                wrong_match_index += '[' + str(i) + '] (first element), '
            if bounds_list[i+number_of_q+1][1]>1:
                wrong_match_index += '[' + str(i) + '] (second element), '
    return wrong_match_index

def generate_elements_bound():
    """Generate an element list from the inital description of the circuit.
    Used for testing.
    """
    initial_circuit = generate_initial_circuit_fit()
    analyzed_circuit = initial_circuit.generate_analyzed_circuit()
    elements = analyzed_circuit.list_elements()
    return elements

@pytest.fixture
def elements_bound():
    return generate_elements_bound()

def generate_bounds_list():
    """Generate a bound list from the element list. Used for testing."""
    elements = generate_elements_bound()
    bounds_list = bounds_definitions(elements)
    return bounds_list

@pytest.fixture
def bounds_list():
    return generate_bounds_list()

def test_bound_definitions(elements_bound, bounds_list):
    """Check that the output of bound_definitions() is a valid list of tuple
    for bound conditions.

    GIVEN: a valid list of elements
    WHEN: the function to get the bounds defintiion is called during the fit
    THEN: the output is a proper list of tuples for elements
    """
    assert isinstance(bounds_list, list), (
        'TypeError in bound_definitions(): the output must be a list, '
        + 'not a ' + str(type(bounds_list)))
    wrong_element_type_index = wrong_element_type_bound_definitions(
        bounds_list)
    assert not wrong_element_type_index, (
        'TypeError in output of bound_definitions(): the output must '
        + 'be a list of tuples of length 2')
    wrong_element_value_index = wrong_element_value_bound_definitions(
        bounds_list)
    assert not wrong_element_value_index, (
        'StructuralError for ' + wrong_element_value_index + 'in output of '
        + 'bound_definitions(): each element of the output must be a tuple '
        + 'with as first element a non-negative number, and as a second '
        + 'element either \'None\' or a non-negative number bigger than the '
        + 'first element')
    assert bound_definitions_same_length_elements_list(elements_bound,
                                                       bounds_list), (
        'StructuralError in output of bound_definitions(): the list of '
        + 'bounds must have a proper length related to the elements list. '
        + 'For each element but for Q 1 element is equal to 1 bound. For Q '
        + 'case is 1 element to 2 bounds.')
    wrong_match_index = bad_match_bound_definitions_elements_list(
        elements_bound, bounds_list)
    assert not wrong_match_index, (
        'StructuralError for elements ' + wrong_match_index + 'in output of '
        + 'bound_definitions(): the must be a correspondace between each '
        + 'element of the element list \'' + str(elements_bound) + '\' and '
        + 'the correspective bound. Bound for R, C or Q must have a positive '
        + 'number as first element, while for n the second parameter must '
        + 'not be bigger than 1')


def same_length_elements_parameters_map(elements_pre_fit, elements_post_fit):
    """Return whether there is a length equality between the elemnts list
    before and after the fit.

    Parameters
    ----------
    elements_pre_fit : list
        List of elements string of the fitting parameters before the fit
    elements_post_fit : list
        List of elements string of the fitting parameters after the fit

    Returns
    -------
    length_equality : bool
        Boolean condition for length equality
    """
    length_equality = (len(elements_pre_fit)==len(elements_post_fit))
    return length_equality

def wrong_elements_parameters_map(elements_pre_fit, elements_post_fit):
    """Find any missing element in the post fit element list.

    Parameters
    ----------
    elements_pre_fit : list
        List of elements string of the fitting parameters before the fit
    elements_post_fit : list
        List of elements string of the fitting parameters after the fit

    Returns
    -------
    wrong_elements : str
        String that contains all the wrong elements, separated by a comma and
        a whitespace
    """
    wrong_element = ''
    for i, element in enumerate(elements_pre_fit):
        if element!=elements_post_fit[i]:
            wrong_element += '\'' + element + '\', '
    return wrong_element

def wrong_parameters_parameters_map(pre_fit_parameters_map,
                                    post_fit_parameters_map):
    """Find any missing parameters in the post fit element list.

    Parameters
    ----------
    pre_fit_parameters_map : dict
        Parameters map of the fitting parameters before the fit
    post_fit_parameters_map : dict
        Parameters map of the fitting parameters after the fit

    Returns
    -------
    wrong_elements : str
        String that contains all the wrong elements' parameter, separated by
        a comma and a whitespace
    wrong_parameters : str
        String that contains all the wrong parameters, separated by a comma and
        a whitespace
    """
    wrong_elements = ''
    wrong_parameters = ''
    for element, parameter in pre_fit_parameters_map.items():
        if isinstance(parameter, list):
            if not isinstance(post_fit_parameters_map[element], list):
                wrong_elements += '\'' + element + '\', '
                wrong_parameters += '\'' + parameter + '\', '
        if isinstance(parameter, (int, float)):
            if not isinstance(post_fit_parameters_map[element], (int, float)):
                wrong_elements += '\'' + element + '\', '
                wrong_parameters += '\'' + parameter + '\', '
    return wrong_elements, wrong_parameters

def generate_analyzed_circuit_pre_fit():
    """Generate the analyzed circuit before a fit."""
    initial_circuit = generate_initial_circuit_fit()
    analyzed_circuit_pre_fit = initial_circuit.generate_analyzed_circuit()
    return analyzed_circuit_pre_fit

@pytest.fixture
def analyzed_circuit_pre_fit():
    return generate_analyzed_circuit_pre_fit()

def generate_analyzed_circuit_post_fit():
    """Generate the analyzed circuit after a fit."""
    analyzed_circuit_post_fit = generate_analyzed_circuit_pre_fit()
    file_name = get_file_name()
    frequency_vector, impedance_data_vector = read_data(file_name)
    _ = fit(frequency_vector, impedance_data_vector,
                      analyzed_circuit_post_fit)
    return analyzed_circuit_post_fit

@pytest.fixture
def analyzed_circuit_post_fit():
    return generate_analyzed_circuit_post_fit()

def test_fit_analyzed_circuit_parameters(analyzed_circuit_pre_fit,
                                         analyzed_circuit_post_fit):
    """Check that the parameters map of post fit is congruent with the one
    of pre fit: same elements, same types of the parameters.

    GIVEN: a valid parameters pre fit and fitted parameters
    WHEN: the fit function is called
    THEN: the parameters map of post fit is congruent with the one of pre fit
    """
    assert isinstance(analyzed_circuit_post_fit.parameters_map, dict), (
        'TypeError for post fit parameters map. It must be a dictionary')
    assert same_length_elements_parameters_map(
        analyzed_circuit_pre_fit.list_elements(),
        analyzed_circuit_post_fit.list_elements()), (
            'StructuralError between elements list in parameter map pre and '
            + 'post fit. They must have the same length')
    wrong_element = wrong_elements_parameters_map(
        analyzed_circuit_pre_fit.list_elements(),
        analyzed_circuit_post_fit.list_elements())
    assert not wrong_element, (
            'StructuralError between elements list in parameter map pre and '
            + 'post fit. ' + wrong_element + ' of pre fit elements not found '
            + 'in post fit elements ')
    wrong_elements, wrong_parameters = wrong_parameters_parameters_map(
        analyzed_circuit_pre_fit.parameters_map,
        analyzed_circuit_post_fit.parameters_map)
    assert not wrong_elements, (
            'StructuralError between parameter(s) in parameter map pre and '
            + 'post fit. Parameter(s) ' + wrong_parameters + 'of element'
            + wrong_elements + ' of pre fit elements has a different type of'
            + 'the counterpart in the post fit parameters_map')


def analyzed_circuit_parameters_and_optimized_parameters_same_length(
        analyzed_circuit_parameters, optimized_parameters):
    """Given the string circuit and its parameters list, return wheter the
    length of the parameters list and the number of elements in the string is
    the same. Used for testing

    Parameters
    ----------
    initial_parameters_fit : list
        List of initial parameters of the fit given by input
    optimized_parameters : list
        List of final parameters given by the fit

    Returns
    -------
    length_equality : bool
        Boolean of the equality length condition
    """
    length_equality = (len(analyzed_circuit_parameters)==len(
        optimized_parameters))
    return length_equality

def wrong_match_analyzed_circuit_parameters_optimized_parameters(
        analyzed_circuit_parameters, optimized_parameters):
    """Find any missing parameters in the post fit element list given the
    optmized parameters list.

    Parameters
    ----------
    optimized_parameters : list
        List of optmized parameters given by the fit.
    analyzed_circuit_parameters : list
        List of parameters of the fitting parameters after the fit in the
        analyzed object.

    Returns
    -------
    missing_parameter : str
        String that contains all the missing parameters, separated by a comma and
        a whitespace.
    """
    missing_parameter = ''
    for parameter in analyzed_circuit_parameters:
        if parameter not in optimized_parameters:
            missing_parameter += '\'' + str(parameter) + '\', '
    return missing_parameter

def outside_bound_optimized_parameters(optimized_parameters, bounds_list):
    """Find the optimized parameters that are outside the correspondant
    bounds. Used for testing

    Parameters
    ----------
    optimized_parameters : list
        List of final parameters given by the fit
    bounds_list : list
        List of the parameters bounds for the fit

    Returns
    -------
    outside_bound_index : str
        String of indexes of the optimized parameters outside the bound
    """
    outside_bound_index = ''
    for i, parameter in enumerate(optimized_parameters):
        if isinstance(bounds_list[i][0], (float, int)):
            if parameter<bounds_list[i][0]:
                outside_bound_index += '[' + str(i) + '] (first element), '
        if isinstance(bounds_list[i][1], (float, int)):
            if parameter>bounds_list[i][1]:
                outside_bound_index += '[' + str(i) + '] (second element), '
    return outside_bound_index

def generate_fit_results():
    """Generate the fit results list from a valid data, initial parameters,
    element list and impedance function. Used for testing."""
    analyzed_circuit = generate_analyzed_circuit_pre_fit()
    file_name = get_file_name()
    frequency_vector, impedance_data_vector = read_data(file_name)
    fit_results = fit(frequency_vector, impedance_data_vector,
                      analyzed_circuit)
    return fit_results

@pytest.fixture
def fit_results():
    return generate_fit_results()

def test_fit_optimized_parameters(fit_results, bounds_list,
                                  analyzed_circuit_post_fit):
    """Check that the first argument of the output of fit() is a valid
    parameter
    list, with a correspondance in length and type with the initial
    parameters, and within the bounds.

    GIVEN: a valid data, initial parameters, element list and impedance
    function
    WHEN: the fit function is called
    THEN: the first argument of the output of fit() is a proper parameter list
    """
    caller = 'fit()'
    optimized_parameters = fit_results[0]
    assert isinstance(optimized_parameters, np.ndarray), (
        'TypeError for parameters in ' + caller + ' . It must be a list')
    assert analyzed_circuit_parameters_and_optimized_parameters_same_length(
        analyzed_circuit_post_fit.list_parameters(), optimized_parameters), (
        'StructuralError: wrong number of optimized parameters \''
        + str(len(optimized_parameters)) + '\' (with number of initial '
        + 'parameters \'' + str(len(
            analyzed_circuit_post_fit.list_parameters())) + '\') in output '
        + 'of ' + caller + ' . They must be the same')
    missing_parameter = wrong_match_analyzed_circuit_parameters_optimized_parameters(
        analyzed_circuit_post_fit.list_parameters(), optimized_parameters)
    assert not missing_parameter, (
        'StructuralError in ' + caller + ': missing parameter for '
        + 'optimization ' + missing_parameter)
    outside_bound_index = outside_bound_optimized_parameters(
        optimized_parameters, bounds_list)
    assert not outside_bound_index, (
        'StructuralError for optimized parametrs with bound(s) '
        + outside_bound_index + 'in output of ' + caller + ': the optimized '
        + 'parameters must be within their bounds: ' + str(bounds_list))

def test_fit_success_flag(fit_results):
    """Check that second argument of the output of fit() is a string.

    GIVEN: a valid data, initial parameters, element list and impedance
    function
    WHEN: the fit function is called
    THEN: second argument of the output of fit() is a string
    """
    success_flag = fit_results[1]
    assert isinstance(success_flag, str), ('TypeError for output of '
        + 'fit(): the output must be a string, not a '
        + str(type(success_flag)))


def generate_example_element_info_const():
    """Generate example of constant element info strings for all the element
    types.
    """
    example_elements = (['R1', 'C1', 'Q1'])
    example_parameters = ([(1000, 1), (2e-6, 1), (([1e-6, 0.6]), 1)])
    example_element_info_const = []
    for i, element in enumerate(example_elements):
        example_element_info_const.append(get_string_constant_parameter(
            element, example_parameters[i]))
    return example_element_info_const

@pytest.fixture
def example_element_info_const():
    return generate_example_element_info_const()

def test_generate_get_string_constant_parameter(example_element_info_const):
    """Check that element info of a constant parameter for the result string
    is a string.

    GIVEN: a example elements and constant parameters
    WHEN: the function to get the info of a constant element is called
    THEN: the element info is a string
    """
    for example in example_element_info_const:
        assert isinstance(example, str), (
            'TypeError for output of '
            + 'generate_get_string_constant_parameter(). It has to be a '
            + 'string.')


def generate_example_element_info():
    """Generate example of non-constant element info strings for all the
    element types.
    """
    example_elements = (['R1', 'C1', 'Q1'])
    example_parameters = ([1000, 2e-6, ([1e-6, 0.6])])
    example_element_info = []
    for i, element in enumerate(example_elements):
        example_element_info.append(get_string_optimized_parameters(
            element, example_parameters[i]))
    return example_element_info

@pytest.fixture
def example_element_info():
    return generate_example_element_info()

def test_generate_get_string_optimized_parameter(example_element_info):
    """Check that element info of an optimized parameter for the result string
    is a string.

    GIVEN: a example elements and optimized parameters
    WHEN: the function to get the info of a constant element is called
    THEN: the element info is a string
    """
    for example in example_element_info:
        assert isinstance(example, str), (
            'TypeError for output of '
            + 'generate_get_string_optimized_parameter(). It has to be a '
            + 'string.')


def generate_result_string():
    """Generate an example of a result string."""
    initial_circuit = generate_initial_circuit_fit()
    final_error = 0.25
    analyzed_circuit_post_fit = generate_analyzed_circuit_post_fit()
    result_string = get_result_string(analyzed_circuit_post_fit, final_error,
                                      initial_circuit)
    return result_string

@pytest.fixture
def result_string():
    return generate_result_string()

def test_result_string(result_string):
    """Check that the result string is a string.

    GIVEN: a valid set of elements and parameters.
    WHEN: the function to get the result string is called.
    THEN: the result string is a string.
    """
    assert isinstance(result_string, str), (
        'TypeError for output of get_result_string(). It has to be a string.')


def generate_box_coordinates():
    """Generate the box coordinates fot the result string."""
    file_name_analysis = generate_file_name_analysis()
    frequency_vector, impedance_data_vector = read_data(file_name_analysis)
    modulus_vector = get_modulus(impedance_data_vector)
    box_coordinates = get_box_coordinates(frequency_vector, modulus_vector)
    return box_coordinates

@pytest.fixture
def box_coordinates():
    return generate_box_coordinates()

def test_get_box_coordinates(box_coordinates, frequency_vector,
                             modulus_vector):
    """Check that the box coordinates are a float and within the data.

    GIVEN: a valid set of data to be plotted in logarithmic scale
    WHEN: the function to plot the fit result is called
    THEN: the coordinates are a proper x, y set
    """
    box_x, box_y = box_coordinates
    caller = 'get_box_coordinates()'
    assert isinstance(box_x, float), (
        'TypeError for box x coordinate in ' + caller +'. It must be a float'
        + 'number.')
    assert (np.min(frequency_vector)<box_x<np.max(frequency_vector)), (
            'ValueError for box x coordinate in ' + caller +'. It must be '
            + 'within the range defined by the frequency vector (x vector).')
    assert isinstance(box_y, float), (
        'TypeError for box y coordinate in ' + caller +'. It must be a float'
        + 'number.')
    assert (np.min(modulus_vector)<box_y<np.max(modulus_vector)), (
            'ValueError for box y coordinate in ' + caller +'. It must be '
            + 'within the range defined by the modulus vector (y vector).')

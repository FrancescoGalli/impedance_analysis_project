"""This module containes all the test functions (and the function needed for
the tests) for the AnalysisCircuit class of the generate_impedance.py module.
It assesses, for example, that both input data and the output of all the
functions in the class are valid.
"""


import inspect
import pytest

import sys
from pathlib import Path
sys.path.append(str(Path.cwd().parent))

from generate_impedance import Circuit, AnalisysCircuit
from generate_impedance import add, list_elements_circuit


####################################
#Tests for AnalysisCircuit class

def wrong_tuples_impedance_parameters_map(impedance_parameters_map):
    """Return any element inside a dictionary that has not a tuple of length
    2 as a value. Used for testing.

    Parameters
    ----------
    impedance_parameters_map : dict
        Dictionary that links the elements with his own impedance function
        and related parameters

    Returns
    -------
    wrong_tuples : str
        Elements string with a value in the dictionary that is not a tuple of
        legth 2, separated by a whitespace
    """
    wrong_tuples = ''
    for element, tuple_ in impedance_parameters_map.items():
        if not isinstance(tuple_, tuple):
            wrong_tuples += element + ' '
        elif len(tuple_)!=2:
            wrong_tuples += element + ' '
    return wrong_tuples

def test_wrong_tuples_circuit_no_element():
    """Check that the help function that returns any item in a dictionary that
    is not a tuple of length 2 works on an empty dictionary.
    If no invalid value is detected, the returned string given by the function
    under test is empty.

    GIVEN: an empty dictionary
    WHEN: I check if there are invalid values inside the dictionary (any that
    is not a tuple of length 2)
    THEN: no invalid value is found
    """
    no_element = {}
    wrong_tuples = wrong_tuples_impedance_parameters_map(no_element)

    assert not wrong_tuples, (
        'TypeError in output of get_impedance_const_input_element_type() '
        + 'for an element in the empty dicitonary. No invalid value of the '
        + 'dictionary should be found since there is None')

def test_wrong_tuples_circuit_single_element():
    """Check that the help function that returns any item in a dictionary that
    is not a tuple of length 2 works on a dictionary with one (valid) object
    inside.
    If no invalid value is detected, the returned string given by the function
    under test is empty.

    GIVEN: a dictionary with one tuple of length 2 as a value
    WHEN: I check if there are invalid values inside the dictionary (any that
    is not a tuple of length 2)
    THEN: no invalid value is found
    """
    single_element = {'C1': (1e-6, 0)}
    wrong_tuples = wrong_tuples_impedance_parameters_map(single_element)

    assert not wrong_tuples, (
        'TypeError in output of get_impedance_const_input_element_type() '
        + 'for ' + wrong_tuples + ' in ' + str(single_element) + '. All the '
        + 'values in the dictionary have to be a tuple')

def test_wrong_tuples_circuit_two_elements():
    """Check that the help function that returns any item in a dictionary that
    is not a tuple of length 2 works on a dictionary with two (valid) objects
    inside.
    If no invalid value is detected, the returned string given by the function
    under test is empty.

    GIVEN: a dictionary with two tuples of length 2 as values
    WHEN: I check if there are invalid values inside the dictionary (any that
    is not a tuple of length 2)
    THEN: no invalid value is found
    """
    two_elements = {'Q1': ([1e-6, 0.5], 1), 'R2': ('100', 22.4)}
    wrong_tuples = wrong_tuples_impedance_parameters_map(two_elements)

    assert not wrong_tuples, (
        'TypeError in output of get_impedance_const_input_element_type() '
        + 'for ' + wrong_tuples + ' in ' + str(two_elements) + '. All the '
        + 'values in the dictionary have to be a tuple')

def test_wrong_tuples_circuit_wrong_elements():
    """Check that the help function that returns any item in a dictionary that
    is not a tuple of length 2 works on a dictionary with three objects inside,
    where only the last one is valid.
    If invalid value are detected, the returned string given by the function
    under test contains the elements (keys) of the invalid values.

    GIVEN: a dictionary with only as second value a tuple of length 2
    WHEN: I check if there are invalid values inside the dictionary (any that
    is not a tuple of length 2)
    THEN: only the first two values are detected as wrong
    """
    wrong_elements = {'Q1': ([1e-6, 0.5]), 'C1': (1e-6, 3, 0.5),
                      'R1': (1e-6, 1)}
    wrong_tuples = wrong_tuples_impedance_parameters_map(wrong_elements)
    expected_result = 'Q1 C1 '

    assert wrong_tuples==expected_result, (
        'TypeError in output of get_impedance_const_input_element_type() '
        + 'for ' + wrong_tuples + ' in ' + str(wrong_elements) + '. the '
        + 'values detected differs from the expected ones:' + expected_result)


def wrong_function_impedance_parameters_map(impedance_parameters_map):
    """Find for which element the impedance-parameter map of the
    AnalysisCircuit has an invalid function as the first element of the tuple.
    Used for testing.

    Parameters
    ----------
    impedance_parameters_map : dict
        Dictionary that links the elements with his own impedance function
        and related parameters

    Returns
    -------
    wrong_functions : str
        String that contains all the wrong elements with bad functions,
        separated by a whitespace
    """
    wrong_functions = ''
    for element, tuple_ in impedance_parameters_map.items():
        if not inspect.isfunction(tuple_[0]):
            wrong_functions += element + ' '
    return wrong_functions

def test_wrong_function_impedance_parameters_map_no_element():
    """Check that the help function that returns any tuple in a dictionary
    that has not a function as first argument works on an empty dictionary.
    If no invalid tuple is detected, the returned string given by the function
    under test is empty.

    GIVEN: an empty dictionary
    WHEN: I check if there are invalid impedance functions as first elements of
    the tuple, that are values of a dictionary
    THEN: no invalid impedance function is found
    """
    no_element = {}
    wrong_functions = wrong_function_impedance_parameters_map(no_element)

    assert not wrong_functions, (
        'TypeError in output of wrong_function_impedance_parameters_map() '
        + 'for an element in the empty dicitonary. No invalid impedance '
        + 'function of the dictionary should be found since there is None')

def test_wrong_function_impedance_parameters_map_single_element():
    """Check that the help function that returns any tuple in a dictionary
    that has not a function as first argument works on a dictionary with
    one (valid) function inside (a constant one).
    If no invalid tuple is detected, the returned string given by the function
    under test is empty.

    GIVEN: a dictionary with one tuple containing a valid impedance function
    (a constant one) as first element
    WHEN: I check if there are invalid impedance functions as first elements
    of the tuple, that are values of a dictionary
    THEN: no invalid impedance function is found
    """
    function_ = lambda x, y: 1000.
    single_element = {'R1': (function_, 'const')}
    wrong_functions = wrong_function_impedance_parameters_map(single_element)

    assert not wrong_functions, (
        'TypeError in output of wrong_function_impedance_parameters_map() '
        + 'for ' + wrong_functions + ' in ' + str(single_element)
        + '. All the first value of the tuples of the dictionary have to be '
        + 'a function')

def test_wrong_function_impedance_parameters_map_two_elements():
    """Check that the help function that returns any tuple in a dictionary
    that has not a function as first argument works on a dictionary with
    two (valid) functions inside, a constant one and a non constant one.
    If no invalid tuple is detected, the returned string given by the function
    under test is empty.

    GIVEN: a dictionary with two tuples containing two valid impedance
    function  (a constant one and a non constant one) as first elements
    WHEN: I check if there are invalid impedance functions as first elements of
    the tuple, that are values of a dictionary
    THEN: no invalid impedance function is found
    """
    function_1 = lambda x, y: y
    function_2 = lambda x, y: 1/(x*y)
    two_elements = {'R1': (function_1, 1000.), 'R2': (function_2, 'const')}
    wrong_functions = wrong_function_impedance_parameters_map(two_elements)

    assert not wrong_functions, (
        'TypeError in output of wrong_function_impedance_parameters_map() '
        + 'for ' + wrong_functions + ' in ' + str(two_elements) + '. All the '
        + 'values in the dictionary have to be a tuple')

def test_wrong_function_impedance_parameters_map_wrong_element():
    """Check that the help function that returns any tuple in a dictionary
    that has not a function a first argument works on a dictionary with
    an invalid onject inside (a string).
    If invalid tuples are detected, the returned string given by the function
    under test contains the elements (keys) of the invalid functions in the
    tuples.

    GIVEN: a dictionary with a tuple containing an invalid impedance
    function as first element
    WHEN: I check if there are invalid impedance functions as first elements of
    the tuple, that are values of a dictionary
    THEN: the invalid impedance function is detected
    """
    wrong_elements = {'R1': ('x', 1000.)}
    wrong_functions = wrong_function_impedance_parameters_map(wrong_elements)
    expected_result = 'R1 '

    assert wrong_functions==expected_result, (
        'TypeError in output of wrong_function_impedance_parameters_map() '
        + 'for ' + wrong_functions + ' in ' + str(wrong_elements) + '. '
        + 'Invalid functions detecetd are different from the expected ones: '
        + expected_result)


def wrong_parameter_impedance_parameters_map_const(impedance_parameters_map):
    """Find for which element the impedance-parameter map has an invalid
    constant parameter (i.e. a 'const' string) as the second element of the
    tuple, that are the dictionary values. Used for testing.

    Parameters
    ----------
    impedance_parameters_map : dict
        Dictionary that links the elements with his own impedance function
        and related parameters

    Returns
    -------
    wrong_parameters : str
        String that contains all the wrong elements with bad parameter,
        separated by a whitespace
    """
    wrong_parameters = ''
    for element, tuple_ in impedance_parameters_map.items():
        parameter_ = tuple_[1]
        if (not isinstance(parameter_, str)
            or not parameter_.startswith('const')):
            wrong_parameters += element + ' '
    return wrong_parameters

def test_wrong_parameter_impedance_parameters_map_const_no_elements():
    """Check that the help function that returns any element in a dictionary
    that has not a 'const' string a second argument of a tuple works on an
    empty dictionary.
    If no invalid tuple is detected, the returned string given by the function
    under test is empty.

    GIVEN: an empty dictionary
    WHEN: I check if there are invalid 'const' strings as second elements of
    the tuple, that are values of a dictionary
    THEN: no invalid 'const' strings is found
    """
    no_elements = {}
    wrong_parameters = wrong_parameter_impedance_parameters_map_const(
        no_elements)

    assert not wrong_parameters, (
        'TypeError for element type(s)' + wrong_parameters + 'from '
        + 'wrong_parameter_impedance_parameters_map_const(). '
        + 'Cannot have a wrong parameter because there are no parameters')

def test_wrong_parameter_impedance_parameters_map_const_single_element():
    """Check that the help function that returns any element in a dictionary
    that has not a 'const' string a second argument of a tuple works on a
    dictionary with one (valid) 'const' string.
    If no invalid tuple is detected, the returned string given by the function
    under test is empty.

    GIVEN: a dictionary with one tuple containing a 'const' string as second
    element
    WHEN: I check if there are invalid 'const' strings as second elements of
    the tuple, that are values of a dictionary
    THEN: no invalid 'const' strings is found
    """
    function_ = lambda x, y: 1000.
    single_element = {'R1': (function_, 'const')}
    wrong_parameters = wrong_parameter_impedance_parameters_map_const(
        single_element)

    assert not wrong_parameters, (
        'TypeError for element type(s)' + wrong_parameters + 'from '
        + 'wrong_parameter_impedance_parameters_map_const(). '
        + 'All the second ojects of the tuples of the dictionary have to be '
        + 'a \'const\' string')

def test_wrong_parameter_impedance_parameters_map_const_two_elements():
    """Check that the help function that returns any element in a dictionary
    that has not a 'const' string a second argument of a tuple works on a
    dictionary with two (valid) 'const' string.
    If no invalid tuple is detected, the returned string given by the function
    under test is empty.

    GIVEN: a dictionary with two tuples containing a 'const' string as second
    element
    WHEN: I check if there are invalid 'const' strings as second elements of
    the tuple, that are values of a dictionary
    THEN: no invalid 'const' strings is found
    """
    function_1 = lambda x, y: y
    function_2 = lambda x, y: 1/(x*y)
    two_elements = {'R1': (function_1, 'const'), 'C2': (function_2, 'const')}
    wrong_parameters = wrong_parameter_impedance_parameters_map_const(
        two_elements)

    assert not wrong_parameters, (
        'TypeError for element type(s)' + wrong_parameters + 'from '
        + 'wrong_parameter_impedance_parameters_map_const(). '
        + 'All the second ojects of the tuples of the dictionary have to be '
        + 'a \'const\' string')

def test_wrong_parameter_impedance_parameters_map_const_wrong_elements():
    """Check that the help function that returns any element in a dictionary
    that has not a 'const' string a second argument of a tuple works on a
    dictionary with two parameters, but only the second one is a 'const'
    string (valid). The first one is invalid.
    If invalid tuples are detected, the returned string given by the function
    under test contains the elements (keys) of the invalud tuples.

    GIVEN: a dictionary with two tuples containing an invalid object (first
    element) and a valid 'const' string as second element
    WHEN: I check if there are invalid 'const' strings as second elements of
    the tuple, that are values of a dictionary
    THEN: the second tuple is detected as invalid
    """
    function_1 = lambda x, y: 2000.
    function_2 = lambda x, y: 1/(x*y)
    two_elements = {'R1': (function_1, 2000.), 'C2': (function_2, 'const')}
    wrong_parameters = wrong_parameter_impedance_parameters_map_const(
        two_elements)
    expected_result = 'R1 '

    assert wrong_parameters==expected_result, (
        'TypeError for element type(s)' + wrong_parameters + 'from '
        + 'wrong_parameter_impedance_parameters_map_const(). Invalid '
        + 'parameters detecetd are different from the expected ones: '
        + expected_result)


def test_set_impedance_constant_element_resistor():
    """Check that set_impedance_constant_element() sets a valid function and
    'const' as parameter in an impedance-parameter map (dictionary)
    for the resistor element type.

    GIVEN: a valid AnalysisCircuit object with a circuit diagram that contains
    a resistor type, the corresponding element name (resistor type) and a
    valid parameter for the resistor.
    WHEN: I call the function to set the impedance of a constant element in an
    AnalysisCircuit
    THEN: the impedance-parameter map is set correctly for the resistor
    element type: the set parameter has a 'const' string value
    """
    element_name_input = 'R1'
    resistor_circuit = AnalisysCircuit('(R1)')
    resistor_circuit.set_impedance_constant_element(element_name_input, 1000.)

    impedance_map = resistor_circuit.impedance_parameters_map
    assert isinstance(impedance_map, dict), (
        'TypeError for impedance_map of ' + element_name_input
        + '. It must be a dictionary')

    elements_impedance_map = list(impedance_map.keys())
    assert element_name_input in elements_impedance_map, (
        'ValueError for ' + element_name_input + '. None of the element '
        + 'names in the dictionary match the input one')

    wrong_tuples = wrong_tuples_impedance_parameters_map(impedance_map)
    assert not wrong_tuples, (
        'TypeError for element \'' + wrong_tuples + '\'. Its value in the '
        + ' dictionary have to be a tuple')
    wrong_functions = wrong_function_impedance_parameters_map(impedance_map)
    assert not wrong_functions, (
        'TypeError for element type(s) ' + ' \'' + wrong_functions
            + '\'. Its first element of the tuple must be a function')
    wrong_parameters = wrong_parameter_impedance_parameters_map_const(
        impedance_map)
    assert not wrong_parameters, (
        'TypeError for element type(s)' + ' \'' + wrong_parameters
        + '\'. Its second element of the tuple must be a \'const\' string')


def test_set_impedance_constant_element_capacitor():
    """Check that set_impedance_constant_element() sets a valid function and
    'const' as parameter in an impedance-parameter map (dictionary) for the
    capacitor element type, even after the resistor type has already been
    added.

    GIVEN: a valid AnalysisCircuit object with a circuit diagram that contains
    a capacitor type, the corresponding element name (capacitor type) and a
    valid parameter for the capacitor. Furthermore, a resistor element has
    already been set correctly
    WHEN: I call the function to set the impedance of a constant element in an
    AnalysisCircuit
    THEN: the impedance-parameter map is set correctly for the capacitor
    element type: the set parameter has a 'const' string value
    """
    element_name_input = 'C2'
    capacitor_circuit = AnalisysCircuit('(R1C2)')
    capacitor_circuit.set_impedance_constant_element('R1', 100.)
    capacitor_circuit.set_impedance_constant_element(element_name_input, 1e-4)

    impedance_map = capacitor_circuit.impedance_parameters_map
    assert isinstance(impedance_map, dict), (
        'TypeError for impedance_map of ' + element_name_input
        + '. It must be a dictionary')

    elements_impedance_map = list(impedance_map.keys())
    assert element_name_input in elements_impedance_map, (
        'ValueError for ' + element_name_input + '. None of the element '
        + 'names in the dictionary match the input one')

    wrong_tuples = wrong_tuples_impedance_parameters_map(impedance_map)
    assert not wrong_tuples, (
        'TypeError for element \'' + wrong_tuples + '\'. Its value in the '
        + ' dictionary have to be a tuple')
    wrong_functions = wrong_function_impedance_parameters_map(impedance_map)
    assert not wrong_functions, (
        'TypeError for element type(s) ' + ' \'' + wrong_functions
        + '\'. Its first element of the tuple must be a function')
    wrong_parameters = wrong_parameter_impedance_parameters_map_const(
        impedance_map)
    assert not wrong_parameters, (
        'TypeError for element type(s)' + ' \'' + wrong_parameters
        + '\'. Its second element of the tuple must be a \'const\' string')

def test_set_impedance_constant_element_cpe():
    """Check that set_impedance_constant_element() sets a valid function and
    'const' as parameter in an impedance-parameter map (dictionary) for the
    cpe element type.

    GIVEN: a valid AnalysisCircuit object with a circuit diagram that contains
    a cpe type, the corresponding element name (cpe type) and a
    valid parameter for the cpe.
    WHEN: I call the function to set the impedance of a constant element in an
    AnalysisCircuit
    THEN: the impedance-parameter map is set correctly for the cpe
    element type: the set parameter has a 'const' string value
    """
    element_name_input = 'Q2'
    cpe_circuit = AnalisysCircuit('(R1Q2)')
    cpe_circuit.set_impedance_constant_element(element_name_input, [1e-6, 0.6])

    impedance_map = cpe_circuit.impedance_parameters_map
    assert isinstance(impedance_map, dict), (
        'TypeError for impedance_map of ' + element_name_input
        + '. It must be a dictionary')

    elements_impedance_map = list(impedance_map.keys())
    assert element_name_input in elements_impedance_map, (
        'ValueError for ' + element_name_input + '. None of the element '
        + 'names in the dictionary match the input one')

    wrong_tuples = wrong_tuples_impedance_parameters_map(impedance_map)
    assert not wrong_tuples, (
        'TypeError for element \'' + wrong_tuples + '\'. Its value in the '
        + ' dictionary have to be a tuple')
    wrong_functions = wrong_function_impedance_parameters_map(impedance_map)
    assert not wrong_functions, (
        'TypeError for element type(s) ' + ' \'' + wrong_functions
            + '\'. Its first element of the tuple must be a function')

    wrong_parameters = wrong_parameter_impedance_parameters_map_const(
        impedance_map)
    assert not wrong_parameters, (
        'TypeError for element type(s)' + ' \'' + wrong_parameters
        + '\'. Its second element of the tuple must be a \'const\' string')

def test_set_impedance_constant_element_wrong_type():
    """Check that set_impedance_constant_element() raises an Exception
    with a certain message for any element type that is not among the valid
    ones ('C', 'Q', 'R').

    GIVEN: a AnalysisCircuit object with a circuit diagram that contains
    an invalid element type, the corresponding element name (invalid by type)
    and a valid parameter for the resistor.
    WHEN: I call the function to set the impedance of a constant element in an
    AnalysisCircuit
    THEN: the set function raises an Exception with a message that states the
    non-validity of the element type, which makes impossible the desired
    setting
    """
    element_name_input = 'S1' #S is not a valid element type
    wrong_circuit = AnalisysCircuit('(S1)')

    with pytest.raises(Exception) as excinfo:
        wrong_circuit.set_impedance_constant_element(element_name_input,
                                                     1000.0)
    message = excinfo.value.args[0]
    assert message==('FatalError: Invalid constant element name for the '
                     + 'setting of impedance function')


def wrong_parameter_impedance_parameters_map_non_constant(
        element_name, parameter, impedance_parameters_map):
    """Find if an input non-constant element and its parameter has
    been set correctly in a dictionary (here called impedance-parameter map),
    in particuralry in the second element of a tuple, that is one of the
    dictionary's values. Used for testing.

    Parameters
    ----------
    element_name : str
        Names of the input element of which we wanto to test the parameter
        value
    parameter : float or list
        Parameter of which we want to test if it has been correctly set the
        value in the dictionary
    impedance_parameters_map : dict
        Dictionary that links the elements with his own impedance function
        and related parameters

    Returns
    -------
    wrong_parameter : str
        String that contains the unsuccessufully set element (with an invalid
        parameter, i.e. different from the input one) follow by a whitespace
    """
    wrong_parameter = ''
    if element_name in impedance_parameters_map.keys():
        parameter_dictionary = impedance_parameters_map[element_name][1]
        if parameter_dictionary!=parameter:
            wrong_parameter = element_name + ' '
    return wrong_parameter

def test_wrong_parameter_impedance_parameters_map_non_constant_no_elements():
    """Check that the help function that returns any element in a dictionary
    that has not as a second argument of a tuple the relative input parameter
    works on an empty dictionary.
    If no invalid parameter is detected, the returned string given by the
    function under test is empty.

    GIVEN: a None parameter/element and an empty dictionary
    WHEN: I check if there are invalid parameters as second elements of
    the tuple, that are values of a dictionary
    THEN: no invalid parameter is found
    """
    parameter = None
    element = None
    no_elements = {}
    wrong_parameters = wrong_parameter_impedance_parameters_map_non_constant(
        element, parameter, no_elements)

    assert not wrong_parameters, (
        'TypeError for element type(s)' + wrong_parameters + ' in empty '
        + 'dictionary from '
        + 'wrong_parameter_impedance_parameters_map_non_constant(). '
        + 'Cannot have a wrong parameter because there are no parameters')

def test_wrong_parameter_impedance_parameters_map_non_constant_single_element():
    """Check that the help function that returns any element in a dictionary
    that has not as a second argument of a tuple the relative input parameter
    works on a dictionary with one valid parameter.
    If no invalid parameter is detected, the returned string given by the
    function under test is empty.

    GIVEN: a valid parameter and element name and a dictionary with the same
    (valid) parameter
    WHEN: I check if there are invalid parameters as second elements of
    the tuple, that are values of a dictionary
    THEN: no invalid parameter is found
    """
    parameter = 1e-4
    element_name = 'C1'
    function_1 = lambda x, y: 1/(x*y)
    single_element = {'R1': (function_1, 1e-4)}
    wrong_parameters = wrong_parameter_impedance_parameters_map_non_constant(
        element_name, parameter, single_element)

    assert not wrong_parameters, (
        'TypeError for element type(s)' + wrong_parameters + ' in '
        + str(single_element) + ' from '
        + 'wrong_parameter_impedance_parameters_map_non_const(). '
        + 'The parameter inside the dictionary must be the same of the '
        + ' input one')

def test_wrong_parameter_impedance_parameters_map_non_constant_two_elements():
    """Check that the help function that returns any element in a dictionary
    that has not as a second argument of a tuple the relative input parameter
    works on a dictionary with two valid parameters.
    If no invalid parameter is detected, the returned string given by the
    function under test is empty.

    GIVEN: a valid input parameter and element name and a dictionary with
    two valid parameters, of which one is same of the (valid) input parameter
    WHEN: I check if there are invalid parameters as second elements of
    the tuple, that are values of a dictionary
    THEN: no invalid parameter is found
    """
    parameter = [1e-4, 0.2]
    element_name = 'Q2'
    function_1 = lambda x, y: y
    function_2 = lambda x, y: 1/(x*y)
    two_elements = {'R1': (function_1, 2000.), 'Q2': (function_2, [1e-4, 0.2])}
    wrong_parameters = wrong_parameter_impedance_parameters_map_non_constant(
        element_name, parameter, two_elements)

    assert not wrong_parameters, (
        'TypeError for element type(s)' + wrong_parameters + ' for '
        + element_name + ' from '
        + 'wrong_parameter_impedance_parameters_map_non_const(). '
        + 'One of the parameters inside the dictionary must be the same of '
        + 'the input one')

def test_wrong_parameter_impedance_parameters_map_non_constant_wrong_element():
    """Check that the help function that returns any element in a dictionary
    that has not as a second argument of a tuple the relative input parameter
    works on a dictionary with an valid parameter.
    If invalid parameters are detected, the returned string given by the
    function under test contains the elements (keys) of the invalid parameters.

    GIVEN: a valid parameter and element name and a dictionary with an invalid
    parameter (a 'const' string)
    WHEN: I check if there are invalid parameters as second elements of
    the tuple, that are values of a dictionary
    THEN: the invalid parameter is detected
    """
    parameter = 1e-5
    element_name = 'C1'
    function_1 = lambda x, y: 1/(x*y)
    wrong_element = {'C1': (function_1, 'const')}
    expected_result = 'C1 '
    wrong_parameters = wrong_parameter_impedance_parameters_map_non_constant(
        element_name, parameter, wrong_element)

    assert wrong_parameters==expected_result, (
        'TypeError for element type(s)' + wrong_parameters + ' in '
        + element_name + ' from '
        + 'wrong_parameter_impedance_parameters_map_non_const(). '
        + 'The invalid parameters detected are different from the expected '
        + 'one: ' + expected_result)


def test_set_impedance_non_const_element_resistor():
    """Check that set_impedance_constant_element() sets a valid function and
    the proper input parameter in an impedance-parameter map (dictionary)
    for the resistor element type.

    GIVEN: a valid AnalysisCircuit object with a circuit diagram that contains
    a resistor type, the corresponding element name (resistor type) and a
    valid parameter for the resistor.
    WHEN: I call the function to set the impedance of a non-constant element
    in an AnalysisCircuit object
    THEN: the impedance-parameter map is set correctly for the resistor
    element type: the set parameter has the same value of the input parameter
    """
    element_name_input = 'R1'
    parameter_input = 1000.
    resistor_circuit = AnalisysCircuit('(R1)')
    resistor_circuit.set_impedance_non_const_element(element_name_input,
                                                      parameter_input)

    impedance_map = resistor_circuit.impedance_parameters_map
    assert isinstance(impedance_map, dict), (
        'TypeError for impedance_map of ' + element_name_input
        + '. It must be a dictionary')

    elements_impedance_map = list(impedance_map.keys())
    assert element_name_input in elements_impedance_map, (
        'ValueError for ' + element_name_input + '. None of the element '
        + 'names in the dictionary match the input one')

    wrong_tuples = wrong_tuples_impedance_parameters_map(impedance_map)
    assert not wrong_tuples, (
        'TypeError for element \'' + wrong_tuples + '\'. Its value in the '
        + ' dictionary have to be a tuple')
    wrong_functions = wrong_function_impedance_parameters_map(
        impedance_map)
    assert not wrong_functions, (
        'TypeError for element type(s) ' + ' \'' + wrong_functions
            + '\'. Its first element of the tuple must be a function')

    wrong_parameters = wrong_parameter_impedance_parameters_map_non_constant(
        element_name_input, parameter_input, impedance_map)
    assert not wrong_parameters, (
        'TypeError for element type(s)' + ' \'' + wrong_parameters
        + '\'. The parameters inside the dictionary must be the same of '
        + 'the input one')

def test_set_impedance_non_const_element_capacitor():
    """Check that set_impedance_constant_element() sets a valid function and
    the proper input parameter in an impedance-parameter map (dictionary)
    for the capacitor element type, even after the resistor type has already
    been added.

    GIVEN: a valid AnalysisCircuit object with a circuit diagram that contains
    a capacitor type, the corresponding element name (capacitor type) and a
    valid parameter for the capacitor. Furthermore, a resistor element has
    already been set correctly
    WHEN: I call the function to set the impedance of a non-constant element
    in an AnalysisCircuit object
    THEN: the impedance-parameter map is set correctly for the capacitor
    element type: the set parameter has the same value of the input parameter
    """
    element_name_input = 'C2'
    parameter_input = 22e-6
    capacitor_circuit = AnalisysCircuit('(R1C2)')
    capacitor_circuit.set_impedance_non_const_element('R1', 1000.)
    capacitor_circuit.set_impedance_non_const_element(element_name_input,
                                                      parameter_input)

    impedance_map = capacitor_circuit.impedance_parameters_map
    assert isinstance(impedance_map, dict), (
        'TypeError for impedance_map of ' + element_name_input
        + '. It must be a dictionary')

    elements_impedance_map = list(impedance_map.keys())
    assert element_name_input in elements_impedance_map, (
        'ValueError for ' + element_name_input + '. None of the element '
        + 'names in the dictionary match the input one')

    wrong_tuples = wrong_tuples_impedance_parameters_map(impedance_map)
    assert not wrong_tuples, (
        'TypeError for element \'' + wrong_tuples + '\'. Its value in the '
        + ' dictionary have to be a tuple')
    wrong_functions = wrong_function_impedance_parameters_map(
        impedance_map)
    assert not wrong_functions, (
        'TypeError for element type(s) ' + ' \'' + wrong_functions
            + '\'. Its first element of the tuple must be a function')

    wrong_parameters = wrong_parameter_impedance_parameters_map_non_constant(
        element_name_input, parameter_input, impedance_map)
    assert not wrong_parameters, (
        'TypeError for element type(s)' + ' \'' + wrong_parameters
        + '\'. The parameters inside the dictionary must be the same of '
        + 'the input one')

def test_set_impedance_non_const_element_cpe():
    """Check that set_impedance_constant_element() sets a valid function and
    the proper input parameter in an impedance-parameter map (dictionary)
    for the cpe element type.

    GIVEN: a valid AnalysisCircuit object with a circuit diagram that contains
    a cpe type, the corresponding element name (cpe type) and a
    valid parameter for the cpe.
    WHEN: I call the function to set the impedance of a non-constant element
    in an AnalysisCircuit object
    THEN: the impedance-parameter map is set correctly for the cpe
    element type: the set parameter has the same value of the input parameter
    """
    element_name_input = 'Q1'
    parameter_input = 22e-6
    capacitor_circuit = AnalisysCircuit('(Q1)')
    capacitor_circuit.set_impedance_non_const_element(element_name_input,
                                                      parameter_input)

    impedance_map = capacitor_circuit.impedance_parameters_map
    assert isinstance(impedance_map, dict), (
        'TypeError for impedance_map of ' + element_name_input
        + '. It must be a dictionary')

    elements_impedance_map = list(impedance_map.keys())
    assert element_name_input in elements_impedance_map, (
        'ValueError for ' + element_name_input + '. None of the element '
        + 'names in the dictionary match the input one')

    wrong_tuples = wrong_tuples_impedance_parameters_map(impedance_map)
    assert not wrong_tuples, (
        'TypeError for element \'' + wrong_tuples + '\'. Its value in the '
        + ' dictionary have to be a tuple')
    wrong_functions = wrong_function_impedance_parameters_map(
        impedance_map)
    assert not wrong_functions, (
        'TypeError for element type(s) ' + ' \'' + wrong_functions
            + '\'. Its first element of the tuple must be a function')

    wrong_parameters = wrong_parameter_impedance_parameters_map_non_constant(
        element_name_input, parameter_input, impedance_map)
    assert not wrong_parameters, (
        'TypeError for element type(s)' + ' \'' + wrong_parameters
        + '\'. The parameters inside the dictionary must be the same of '
        + 'the input one')

def test_set_impedance_non_constant_element_wrong_type():
    """Check that set_impedance_non_const_element() raises an
    Exception with a certain message for any element type that is not among
    the valid ones ('C', 'Q', 'R').

    GIVEN: a AnalysisCircuit object with a circuit diagram that contains
    an invalid element type, the corresponding element name (invalid by type)
    and a valid parameter for the resistor.
    WHEN: I call the function to set the impedance of a non constant element
    in an AnalysisCircuit
    THEN: the set function raises an Exception with a message that states the
    non-validity of the element type, which makes impossible the desired
    setting
    """
    element_name_input = 'F1' #F is not a valid element type
    wrong_circuit = AnalisysCircuit('(F1)')

    with pytest.raises(Exception) as excinfo:
        wrong_circuit.set_impedance_non_const_element(element_name_input, 1e-6)
    message = excinfo.value.args[0]
    assert message==('FatalError: Invalid non-constant element name for the '
                     + 'setting of impedance function')


def wrong_parameter_impedance_parameters_map(
        element_name, input_parameter, constant_condition,
        impedance_parameters_map):
    """Find if an input element (either non-constant o constant) and its
    parameter has been set correctly in a dictionary (here called
    impedance-parameter map), in particularly in the second element of a
    tuple, that is one of the dictionary's values. Used for testing.

    Parameters
    ----------
    element_name : str
        Names of the input element of which we wanto to test the parameter
        value
    parameter : float or list
        Parameter of which we want to test if it has been correctly set the
        value in the dictionary
    constant_conditions : int
        Constant condition for the input value to be tested
    impedance_parameters_map : dict
        Dictionary that links the elements with his own impedance function
        and related parameters

    Returns
    -------
    wrong_parameters : str
        String that contains all the wrong elements with bad parameter,
        separated by a whitespace
    """
    wrong_parameters = ''
    if element_name in impedance_parameters_map.keys():
        parameter_dictionary = impedance_parameters_map[element_name][1]
        if constant_condition:
            if not isinstance(parameter_dictionary, str):
                wrong_parameters += element_name + ' '
            elif not parameter_dictionary.startswith('const'):
                wrong_parameters += element_name + ' '
        elif parameter_dictionary!=input_parameter:
            wrong_parameters += element_name + ' '
    return wrong_parameters

def test_wrong_parameter_impedance_parameters_map_no_elements():
    """Check that the help function that returns any element (constant or not)
    in a dictionary that has not as a second argument of the tuple the
    relative input parameter works on an empty dictionary. If the parameter is
    constant, the valid parameter inside the dictionary is a 'const' string.
    If no invalid parameter is detected, the returned string given by the
    function under test is empty.

    GIVEN: an empty list of parameters and an empty dictionary
    WHEN: I check if there are invalid parameters as second elements of
    the tuple, that are values of a dictionary
    THEN: no invalid parameter is found
    """
    parameter = None
    element = None
    constant_condition = 0
    no_elements = {}
    wrong_parameters = wrong_parameter_impedance_parameters_map(
        element, parameter, constant_condition, no_elements)

    assert not wrong_parameters, (
        'TypeError for element type(s)' + wrong_parameters + ' in empty '
        + 'dictionary from wrong_parameter_impedance_parameters_map(). '
        + 'Cannot have a wrong parameter because there are no parameters')

def test_wrong_parameter_impedance_parameters_map_single_element():
    """Check that the help function that returns any element (constant or not)
    in a dictionary that has not as a second argument of the tuple the
    relative input parameter works on an empty dictionary. If the parameter is
    constant, the valid parameter inside the dictionary is a 'const' string.
    If no invalid parameter is detected, the returned string given by the
    function under test is empty.

    GIVEN: a valid parameter and element name, a valid (False) constant
    condition and a dictionary with the same (valid) parameter
    WHEN: I check if there are invalid parameters as second elements of
    the tuple, that are values of a dictionary
    THEN: no invalid parameter is found
    """
    parameter = 1000.
    element_name = 'R1'
    constant_condition = 0
    function_1 = lambda x, y: y
    single_element = {'R1': (function_1, 1000.)}
    wrong_parameters = wrong_parameter_impedance_parameters_map(
        element_name, parameter, constant_condition, single_element)

    assert not wrong_parameters, (
        'TypeError for element type(s)' + wrong_parameters + ' in '
        + str(single_element) + ' from '
        + 'wrong_parameter_impedance_parameters_map(). The parameter inside '
        + 'the dictionary must be the same of the input one')

def test_wrong_parameter_impedance_parameters_map_two_elements():
    """Check that the help function that returns any element (constant or not)
    in a dictionary that has not as a second argument of a tuple the relative
    input parameter works on a dictionary with two valid parameters: the first
    one is non-constant, the second one is constant.
    If invalid parameters are detected, the returned string given by the
    function under test contains the elements (keys) of the invalid parameters.

    GIVEN: two valid input parameters (a non-constant resistor and a constant
    capacitor) with their valid element names and a dictionary with
    the same parameters, set correctly
    WHEN: I check if there are invalid parameters as second elements of
    the tuple, that are values of a dictionary
    THEN: no invalid parameter is found
    """
    input_parameter_non_const = 1000.
    element_name_non_const = 'R2'
    input_parameter_const = 1e-4
    element_name_const = 'C2'
    constant_condition = 0
    function_1 = lambda x, y: 1/(x*y)
    function_2 = lambda x, y: y
    two_elements = {'R1': (function_1, 1000.), 'C1': (function_2, 'const'), }
    wrong_parameters = wrong_parameter_impedance_parameters_map(
        element_name_non_const, input_parameter_non_const, constant_condition,
        two_elements)

    assert not wrong_parameters, (
        'TypeError for element type(s)' + wrong_parameters + ' for '
        + element_name_non_const + ' from '
        + 'wrong_parameter_impedance_parameters_map(). The parameter inside '
        + 'the dictionary must be the same of the input one')

    wrong_parameters = wrong_parameter_impedance_parameters_map(
        element_name_const, input_parameter_const, 1, two_elements)
    assert not wrong_parameters, (
        'TypeError for element type(s)' + wrong_parameters + ' for '
        + element_name_const + ' from '
        + 'wrong_parameter_impedance_parameters_map(). The parameter inside '
        + 'the dictionary must be the same of the input one')

def test_wrong_parameter_impedance_parameters_map_wrong_element():
    """Check that the help function that returns any element (constant or not)
    in a dictionary that has not as a second argument of a tuple the relative
    input parameter works on a dictionary with an invalid parameters: the input
    constant condition is False but in the dictionary it has been set as if
    it was True.
    If invalid parameters are detected, the returned string given by the
    function under test contains the elements (keys) of the invalid parameters.

    GIVEN: a valid parameter and element name with a False constant condition
    and a dictionary with an invalid parameter (a 'const' string, as if the
    constant condition was True)
    WHEN: I check if there are invalid parameters as second elements of
    the tuple, that are values of a dictionary
    THEN: the invalid parameter is detected
    """
    parameter = 1e-5
    element_name = 'C1'
    constant_condition = 0
    function_1 = lambda x, y: 1/(x*y)
    wrong_element = {'C1': (function_1, 'const')}
    wrong_parameters = wrong_parameter_impedance_parameters_map(
        element_name, parameter, constant_condition, wrong_element)
    expected_result = 'C1 '

    assert wrong_parameters==expected_result, (
        'TypeError for element type(s)' + wrong_parameters + ' in '
        + element_name + ' from '
        + 'wrong_parameter_impedance_parameters_map_non_const(). '
        + 'The invalid parameters detected are different from the expected '
        + 'one: ' + expected_result)


def generate_analysis_circuit_resistor():
    """Generate an AnalysisCircuit object of a circuit with one resistor.
    This resistor has its own valid parameter and a valid (False) constant
    condition. Thus, to set the element, set_impedance_element() method of
    the AnalysisCircuit class is called. Used for testing.
    """
    diagram = '(R1)'
    input_element = 'R1'
    input_parameter_value = 1000.
    input_constant_condition_value = 0
    parameter_map = {input_element: (input_parameter_value,
                                     input_constant_condition_value)}
    resistor_circuit = Circuit(diagram, parameter_map)
    resistor_analyzed_circuit = AnalisysCircuit(diagram)
    resistor_analyzed_circuit.set_impedance_element(input_element,
                                                    resistor_circuit)
    return resistor_analyzed_circuit

def test_set_impedance_resistor():
    """Check that set_impedance() sets a resistor element in the correct way
    on a AnalysisCircuit object in the case the element is non-constant.

    GIVEN: a valid input Circuit with a valid resistor element (constant
    condition False) and an AnalysisCircuit initialized with the same circuit
    diagram
    WHEN: I set the resistor element of the input Circuit in the
    AnalysisCircuit
    THEN: the AnalysisCircuit has the same resistor element set correctly,
    i.e. the parameter is set as non-constant
    """
    input_element = 'R1'
    input_parameter_value = 1000.
    input_constant_condition_value = 0
    resistor_circuit = generate_analysis_circuit_resistor()

    impedance_map = resistor_circuit.impedance_parameters_map
    assert isinstance(impedance_map, dict), (
        'TypeError for impedance_map of ' + input_element + '. It must be a '
        + 'dictionary')

    elements_impedance_map = list(impedance_map.keys())
    assert input_element in elements_impedance_map, (
        'ValueError for ' + input_element + '. None of the element names in '
        + ' the dictionary match the input one')

    wrong_tuples = wrong_tuples_impedance_parameters_map(impedance_map)
    assert not wrong_tuples, (
        'TypeError for element \'' + wrong_tuples + '\'. Its value in the '
        + ' dictionary have to be a tuple')
    wrong_functions = wrong_function_impedance_parameters_map(impedance_map)
    assert not wrong_functions, (
        'TypeError for element type(s) ' + ' \'' + wrong_functions
            + '\'. Its first element of the tuple must be a function')

    wrong_parameters = wrong_parameter_impedance_parameters_map(
        input_element, input_parameter_value, input_constant_condition_value,
        impedance_map)
    assert not wrong_parameters, (
        'TypeError for element type(s)' + ' \'' + wrong_parameters
        + '\'. The parameters inside the dictionary must be the same of the '
        + 'input one')

def generate_analysis_circuit_capacitor():
    """Generate an AnalysisCircuit object of a circuit with one resistor
    and one capacitor.
    This capacitor has its own valid parameter and a valid (True) constant
    condition. Thus, to set the element, set_impedance_element() method of
    the AnalysisCircuit class is called. The capacitor has already being set
    correctly first. Used for testing.
    """
    diagram = '(R1C2)'
    input_element = 'C2'
    input_parameter_value = 1e-6
    input_constant_condition_value = 1
    parameter_map = {'R1': (1000., 0),
                     input_element: (input_parameter_value,
                                     input_constant_condition_value)}
    capacitor_circuit = Circuit(diagram, parameter_map)
    capacitor_analyzed_circuit = AnalisysCircuit(diagram)
    capacitor_analyzed_circuit.set_impedance_element('R1', capacitor_circuit)

    capacitor_analyzed_circuit.set_impedance_element(input_element,
                                                     capacitor_circuit)
    return capacitor_analyzed_circuit

def test_set_impedance_capacitor():
    """Check that set_impedance() sets a capacitor element in the correct way
    on a AnalysisCircuit object in the case the element is constant, even
    after another valid resistor element has been successfully set.

    GIVEN: a valid input Circuit with a valid resistor element (constant
    condition False) and a valid resistor element (constant condition True)
    and an AnalysisCircuit initialized with the same circuit diagram
    WHEN: I set the capacitor element of the input Circuit in the
    AnalysisCircuit after being successfully set the reisitor element
    THEN: the AnalysisCircuit has the same capacitor element set correctly,
    i.e. the parameter is set as constant
    """
    input_element = 'C2'
    input_parameter_value = 1e-6
    input_constant_condition_value = 1
    capacitor_circuit = generate_analysis_circuit_capacitor()

    impedance_map = capacitor_circuit.impedance_parameters_map
    assert isinstance(impedance_map, dict), (
        'TypeError for impedance_map of ' + input_element + '. It must be a '
        + 'dictionary')

    elements_impedance_map = list(impedance_map.keys())
    assert input_element in elements_impedance_map, (
        'ValueError for ' + input_element + '. None of the element names in '
        + 'the dictionary match the input one')

    wrong_tuples = wrong_tuples_impedance_parameters_map(impedance_map)
    assert not wrong_tuples, (
        'TypeError for element \'' + wrong_tuples + '\'. Its value in the '
        + ' dictionary have to be a tuple')
    wrong_functions = wrong_function_impedance_parameters_map(impedance_map)
    assert not wrong_functions, (
        'TypeError for element type(s) ' + ' \'' + wrong_functions
        + '\'. Its first element of the tuple must be a function')

    wrong_parameters = wrong_parameter_impedance_parameters_map(
        input_element, input_parameter_value, input_constant_condition_value,
        impedance_map)
    assert not wrong_parameters, (
        'TypeError for element type(s)' + ' \'' + wrong_parameters
        + '\'. The parameters inside the dictionary must be the same of the '
        + 'input one')

def generate_analysis_circuit_cpe():
    """Generate an AnalysisCircuit object of a circuit with one cpe.
    This cpe has its own valid parameter and a valid (True) constant
    condition. Thus, to set the element, set_impedance_element() method of
    the AnalysisCircuit class is called. Used for testing.
    """
    diagram = '(Q1)'
    input_element = 'Q1'
    input_parameter_value = [1e-5, 0.55]
    input_constant_condition_value = 0
    parameter_map = {input_element: (input_parameter_value,
                                     input_constant_condition_value)}
    cpe_circuit = Circuit(diagram, parameter_map)
    cpe_analyzed_circuit = AnalisysCircuit(diagram)
    cpe_analyzed_circuit.set_impedance_element(input_element, cpe_circuit)
    return cpe_analyzed_circuit

def test_set_impedance_cpe():
    """Check that set_impedance() sets a cpe element in the correct way
    on a AnalysisCircuit object in the case the element is non-constant.

    GIVEN: a valid input Circuit with a valid cpe element (constant condition
    False) and an AnalysisCircuit initialized with the same circuit diagram
    WHEN: I set the cpe element of the input Circuit in the AnalysisCircuit
    THEN: the AnalysisCircuit has the same cpe element set correctly, i.e. the
    parameter is set as non-constant
    """
    input_element = 'Q1'
    input_parameter_value = [1e-5, 0.55]
    input_constant_condition_value = 0
    cpe_circuit = generate_analysis_circuit_cpe()

    impedance_map = cpe_circuit.impedance_parameters_map
    assert isinstance(impedance_map, dict), (
        'TypeError for impedance_map of ' + input_element + '. It must be a '
        + 'dictionary')

    elements_impedance_map = list(impedance_map.keys())
    assert input_element in elements_impedance_map, (
        'ValueError for ' + input_element + '. None of the element names in '
        + 'the dictionary match the input one')

    wrong_tuples = wrong_tuples_impedance_parameters_map(impedance_map)
    assert not wrong_tuples, (
        'TypeError for element \'' + wrong_tuples + '\'. Its value in the '
        + 'dictionary have to be a tuple')
    wrong_functions = wrong_function_impedance_parameters_map(impedance_map)
    assert not wrong_functions, (
        'TypeError for element type(s) ' + ' \'' + wrong_functions
        + '\'. Its first element of the tuple must be a function')

    wrong_parameters = wrong_parameter_impedance_parameters_map(
        input_element, input_parameter_value, input_constant_condition_value,
        impedance_map)
    assert not wrong_parameters, (
        'TypeError for element type(s)' + ' \'' + wrong_parameters
        + '\'. The parameters inside the dictionary must be the same of the '
        + 'input one')

def generate_wrong_circuit_resistor():
    """Generate an AnalysisCircuit object of a circuit with one invalid
    resistor (invalid by element type in the name).
    This resistor has a valid parameter and a valid (True) constant condition.
    Thus, to set the element, set_impedance_element() method of the
    AnalysisCircuit class is called. Used for testing.
    """
    diagram = '(F1)'
    input_element = 'F1'
    input_parameter_value = 1000.
    input_constant_condition_value = 1
    parameter_map = {input_element: (input_parameter_value,
                                     input_constant_condition_value)}
    resistor_circuit = Circuit(diagram, parameter_map)
    return resistor_circuit

def test_set_impedance_wrong_type():
    """Check that set_impedance_element() raises an Exception with a
    certain message for any element type that is not among the valid ones
    ('C', 'Q', 'R'). The message Exception depends on weather the constant
    conditions are True or not.

    GIVEN: an input Circuit with an invalid element name (by element type)
    with a constant condition True) and an AnalysisCircuit initialized with
    the same circuit diagram
    WHEN: I call the function to set the impedance of a non constant element
    in an AnalysisCircuit
    THEN: the set function raises an Exception with a message that states the
    non-validity of the element type, which makes impossible the desired
    setting
    """
    wrong_resistor_circuit = generate_wrong_circuit_resistor()
    element_name_input = 'F1'
    wrong_circuit = AnalisysCircuit('(F1)')
    with pytest.raises(Exception) as excinfo:
        wrong_circuit.set_impedance_element(element_name_input,
                                            wrong_resistor_circuit)
    message = excinfo.value.args[0]
    assert message==('FatalError: Invalid constant element name for the '
                     + 'setting of impedance function')

def generate_valid_circuit_resistor():
    """Generate an AnalysisCircuit object of a circuit with one valid resistor
    element.
    """
    diagram = '(R1)'
    input_element = 'R1'
    input_parameter_value = 1000.
    input_constant_condition_value = 1
    parameter_map = {input_element: (input_parameter_value,
                                     input_constant_condition_value)}
    resistor_circuit = Circuit(diagram, parameter_map)
    return resistor_circuit

def test_set_impedance_non_existent_element_name():
    """Check that set_impedance_element() raises an Exception with a
    certain message if the element name is not among the element names of the
    parameters_map of the initial circuit.

    GIVEN: an input Circuit with an valid element name and an AnalysisCircuit
    initialized with the same circuit diagram. But the element name of the
    set_impedance_element() is different from the one in the circuits.
    WHEN: I call the function to set the impedance of a non constant element
    in an AnalysisCircuit
    THEN: the set function raises an Exception with a message that states the
    non-validity of the element type, which makes impossible the desired
    setting
    """
    resistor_circuit = generate_valid_circuit_resistor()
    wrong_element_name_input = 'C1'
    wrong_circuit = AnalisysCircuit('(R1)')

    with pytest.raises(Exception) as excinfo:
        wrong_circuit.set_impedance_element(wrong_element_name_input,
                                            resistor_circuit)
    message = excinfo.value.args[0]
    assert message==('FatalError: Invalid element name for the constant '
                     + 'conditions')


def wrong_impedance_generate_cell_impedance(impedance_cell):
    """Find any invalid function inside the impedance_cell (a list). Used for
    testing. Used for testing.

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

def test_wrong_impedance_generate_cell_impedance_no_functions():
    """Check that the help function that returns any object in a list that has
    is not a function works on an empty list.
    If no invalid function is detected, the returned list given by the
    function under test is empty.

    GIVEN: an empty list
    WHEN: I check if there are invalid functions inside the impedance_cell
    THEN: no invalid function is found
    """
    empty_list = []
    wrong_functions_index = wrong_impedance_generate_cell_impedance(empty_list)

    assert not wrong_functions_index, (
        'TypeError for element number(s) ' + str(wrong_functions_index)
        + 'for the empty list. Cannot find a wrong function because there are '
        + 'no function')

def test_wrong_impedance_generate_cell_impedance_single_function():
    """Check that the help function that returns any object in a list that has
    is not a function works on a list containing one valid function.
    If no invalid function is detected, the returned list given by the
    function under test is empty.

    GIVEN: a list containing one valid function
    WHEN: I check if there are invalid functions inside the impedance_cell
    THEN: no invalid function is found
    """
    function_r = lambda x, y : y
    single_function = [function_r]
    wrong_functions_index = wrong_impedance_generate_cell_impedance(
        single_function)

    assert not wrong_functions_index, (
        'TypeError for element number(s) ' + str(wrong_functions_index)
        + 'for the single function list. The output must contain ony funtions')

def test_wrong_impedance_generate_cell_impedance_two_functions():
    """Check that the help function that returns any object in a list that has
    is not a function works on a list containing two valid functions.
    If no invalid function is detected, the returned list given by the
    function under test is empty.

    GIVEN: a list containing two valid function
    WHEN: I check if there are invalid functions inside the impedance_cell
    THEN: no invalid function is found
    """
    function_r = lambda x, y : y
    function_c = lambda x, y : 1/(x*y)
    two_functions = [function_r, function_c]
    wrong_functions_index = wrong_impedance_generate_cell_impedance(
        two_functions)

    assert not wrong_functions_index, (
        'TypeError for element number(s) ' + str(wrong_functions_index)
        + 'for the single function list. The output must contain ony funtions')

def test_wrong_impedance_generate_cell_impedance_wrong_functions():
    """Check that the help function that returns any object in a list that has
    is not a function works on a list containing three objects, but only the
    last one is a valid function.
    If invalid functions are detected, the returned list given by the
    function under test contains the indexes of the invalid functions.

    GIVEN: a list containing three objects, but only the last one is a valid
    function
    WHEN: I check if there are invalid functions inside the impedance_cell
    THEN: only the first two are detected as invalid functions
    """
    function_r = lambda x, y : y
    wrong_functions = ['1/x', 1000., function_r]
    expected_result = [0, 1] #Position in the array of the wrong functions
    wrong_functions_index = wrong_impedance_generate_cell_impedance(
        wrong_functions)

    assert wrong_functions_index==expected_result, (
        'TypeError for element number(s) ' + str(wrong_functions_index)
        + 'for the single function list. The detected invalid functions are '
        + 'different from the expected ones: ' + str(expected_result))


def generate_impedance_cell_single_element():
    """Generate the impedance cell of a cell containing a single resistor
    element using the generate_cell_impedance() function.
    """
    diagram = '(R1)'
    parameter_value = 100.
    constant_conditions_value = 0
    parameters_map = {'R1': (parameter_value, constant_conditions_value)}
    circuit = Circuit(diagram, parameters_map)
    analyzed_circuit = AnalisysCircuit(diagram)
    impedance_cell_single = analyzed_circuit.generate_cell_impedance(
        circuit, i_start=0, i_end=3)
    return impedance_cell_single

def test_generate_cell_impedance_single_element():
    """Check that generate_cell_impedance() function returns a proper list of
    functions in the case of a cell containing a single resistor element.
    If no invalid function is detected, the returned list given by the
    function under test is empty.

    GIVEN:  a valid input circuit with a cell that contains one valid element
    and valid delimiters in the circuit diagram of the cell to be analyzed
    WHEN: I call the method to analyze a whole cell of the circuit
    THEN: the list of the impedance functions of the elements of the cell is
    valid.
    """
    impedance_cell_single = generate_impedance_cell_single_element()
    circuit_cell_diagram = '(R1)'

    caller = 'generate_cell_impedance()'
    assert isinstance(impedance_cell_single, list), (
        'TypeError in output of ' + caller + 'for \'' + circuit_cell_diagram
        + '\'. It must be a list')

    wrong_functions_index = wrong_impedance_generate_cell_impedance(
        impedance_cell_single)
    assert not wrong_functions_index, (
        'TypeError in output of ' + caller
        + ' for element number(s) ' + ' \'' + str(wrong_functions_index)
        + '\'. The output must contain ony funtions')

    element_list = list_elements_circuit(circuit_cell_diagram)
    equality_condition = len(element_list)==len(impedance_cell_single)
    assert equality_condition, (
        'StructuralError in output of ' + caller + ' with cell '
        + circuit_cell_diagram + '. The length of the output must be the '
        + 'same of the number of the element of the cell')

def generate_impedance_cell_two_elements():
    """Generate the impedance cell of a cell containing a resistor and a
    capacitor elements using the generate_cell_impedance() function.
    """
    diagram = '(R1C2)'
    resistor_parameter_value = 100.
    capacitor_parameter_value = 1e-6
    constant_condition_value = 0
    parameters_map = {'R1': (resistor_parameter_value,
                             constant_condition_value),
                      'C2': (capacitor_parameter_value,
                             constant_condition_value)}
    circuit = Circuit(diagram, parameters_map)
    analyzed_circuit = AnalisysCircuit(diagram)
    impedance_cell__two_elements = analyzed_circuit.generate_cell_impedance(
        circuit, i_start=0, i_end=5)
    return impedance_cell__two_elements

def test_generate_cell_impedance_two_elements():
    """Check that generate_cell_impedance() function returns a proper list of
    functions in the case of a cell containing a resistor and a capacitor
    elements.

    GIVEN: a valid input circuit with a cell that contains two valid elements
    (a resistor and a capacitor) and valid delimiters in the circuit
    diagram of the cell to be analyzed
    WHEN: I call the method to analyze a whole cell of the circuit
    THEN: the list of the impedance functions of the elements of the cell is
    valid.
    """
    impedance_cell_two = generate_impedance_cell_two_elements()
    circuit_cell_diagram = '(R1C2)'

    caller = 'generate_cell_impedance()'
    assert isinstance(impedance_cell_two, list), (
        'TypeError in output of ' + caller + 'for \'' + circuit_cell_diagram
        + '\'. It must be a list')

    wrong_functions_index = wrong_impedance_generate_cell_impedance(
        impedance_cell_two)
    assert not wrong_functions_index, (
        'TypeError in output of ' + caller + ' for element number(s) \''
        + str(wrong_functions_index) + '\'. The output must contain only '
        + 'funtions')

    element_list = list_elements_circuit(circuit_cell_diagram)
    equality_condition = len(element_list)==len(impedance_cell_two)
    assert equality_condition, (
        'StructuralError in output of ' + caller + ' with cell '
        + circuit_cell_diagram + '. The length of the output must be the '
        + 'same of the number of the element of the cell')

def generate_impedance_cell_many_elements():
    """Generate the impedance cell of a cell containing a resistor and a
    cpe elements using the generate_cell_impedance() function in a circuit
    with two nested cells, where the one being analyzed is the most nested
    one.
    """
    diagram = '(R1C2[R3Q4])'
    resistor_1_parameter_value = 100.
    capacitor_parameter_value = 1e-6
    resistor_3_parameter_value = 1000.
    cpe_parameter_value = [1e-6, 0.6]
    constant_condition_value = 0
    constant_condition_R3_value = 1
    parameters_map = {'R1': (resistor_1_parameter_value,
                             constant_condition_value),
                      'C2': (capacitor_parameter_value,
                             constant_condition_value),
                      'R3': (resistor_3_parameter_value,
                             constant_condition_R3_value),
                      'Q4': (resistor_1_parameter_value,
                             cpe_parameter_value)}
    circuit = Circuit(diagram, parameters_map)
    analyzed_circuit = AnalisysCircuit(diagram)
    impedance_cell_many_elements = analyzed_circuit.generate_cell_impedance(
        circuit, i_start=5, i_end=10)
    return impedance_cell_many_elements

def test_generate_cell_impedance_many_elements():
    """Check that generate_cell_impedance() function returns a proper list of
    functions in the case of a diagram with two nested cells. The analyzed one
    will be the most nested one, that contains a resistor and a cpe
    elements.

    GIVEN: a valid input circuit with two nested cells. The analyzed one
    will be the most nested one, that contains a valid resistor and a valid
    cpe. Also valid delimiters of the analyzed cell in the circuit diagram
    WHEN: I call the method to analyze a whole cell of the circuit
    THEN: the list of the impedance functions of the elements of the cell is
    valid.
    """
    impedance_cell_many = generate_impedance_cell_many_elements()
    circuit_cell_diagram = '[R3Q4]'

    caller = 'generate_cell_impedance()'
    assert isinstance(impedance_cell_many, list), (
        'TypeError in output of ' + caller + 'for \'' + circuit_cell_diagram
        + '\'. It must be a list')

    wrong_functions_index = wrong_impedance_generate_cell_impedance(
        impedance_cell_many)
    assert not wrong_functions_index, (
        'TypeError in output of ' + caller + ' for element number(s) \''
        + str(wrong_functions_index) + '\'. The output must contain only '
        + 'funtions')

    element_list = list_elements_circuit(circuit_cell_diagram)
    equality_condition = len(element_list)==len(impedance_cell_many)
    assert equality_condition, (
        'StructuralError in output of ' + caller + ' with cell '
        + circuit_cell_diagram + '. The length of the output must be the same '
        + 'of the number of the element of the cell')

def test_generate_cell_impedance_wrong_element():
    """Check that generate_cell_impedance() raises an Exception with a
    certain message for any element type in the analyzed cell that is not
    among the valid ones ('C', 'Q', 'R'). The message Exception depends on
    weather the constant conditions are True or not.

    GIVEN: an invalid input circuit with a cell that contain an invalid
    element type. The delimiters of the analyzed cell in the circuit diagram
    are valid
    WHEN: I call the method to analyze a whole cell of the circuit
    THEN: the function raises an Exception with a message that states the
    non-validity of the element type, which makes impossible the desired
    impedance function.
    """
    diagram = '(G1)' #G is an invalid element type
    parameter_value = 100.
    constant_conditions_value = 1
    parameters_map = {'G1': (parameter_value, constant_conditions_value)}
    wrong_circuit = Circuit(diagram, parameters_map)
    wrong_analyzed_circuit = AnalisysCircuit(diagram)

    with pytest.raises(Exception) as excinfo:
        _ = wrong_analyzed_circuit.generate_cell_impedance(
            wrong_circuit, i_start=0, i_end=3)
    message = excinfo.value.args[0]
    assert message==('FatalError: Invalid constant element name for the '
                     + 'setting of impedance function')

def test_generate_cell_impedance_wrong_delimiter():
    """Check that generate_cell_impedance() raises an Exception with a
    certain message if the delimiter of the analyzed cell are invalid (thus
    creating invalid cells, with invalid elements). The message Exception
    depends on weather the constant conditions of the original elements in the
    cell are True or not.

    GIVEN: an valid input circuit with a cell that contain a single valid
    element. However The delimiters of the analyzed cell in the circuit
    diagram are invalid for the single cell
    WHEN: I call the method to analyze a whole cell of the circuit
    THEN: the function raises an Exception with a message that states the
    non-validity of the element type, which makes impossible the desired
    impedance function.
    """
    resistor_circuit = generate_valid_circuit_resistor()
    analyzed_circuit = AnalisysCircuit('(R1)')

    with pytest.raises(Exception) as excinfo:
        _ = analyzed_circuit.generate_cell_impedance(
            resistor_circuit, i_start=1, i_end=3) #Incorrect delimiters,
                                                  #should be 0 and 3
    message = excinfo.value.args[0]
    assert message==('FatalError: Invalid element name for the constant '
                     + 'conditions')


def consistency_brackets(circuit_diagram):
    """Given a circuit diagram, return if there is a bracket incongruence.
    Used for testing.

    Parameters
    ----------
    circuit_diagram : str
        String of the circuit given by input

    Returns
    -------
    wrong_brackets : list
        List of all the bracket involbed in the bracket incongruence
    wrong_brackets_index : str
        Index in the string of all the aforementioned brackets
    """
    wrong_brackets = ''
    wrong_brackets_index = ''

    equality_count = (
        circuit_diagram.count('(')==circuit_diagram.count(')')
        and circuit_diagram.count('[')==circuit_diagram.count(']'))
    if not equality_count:
        error_msg = 'number of brackets'
        wrong_brackets += error_msg
    else:
        position_of_brackets = [i for i, _ in enumerate(circuit_diagram)
                                if (circuit_diagram.startswith(')', i)
                                    or circuit_diagram.startswith(']', i))]
        cut_parameter = 0
        for _ in position_of_brackets:
            for i, char_i in enumerate(circuit_diagram):
                if char_i in (')', ']'):
                    if char_i==')':
                        bracket = '('
                        wrong_bracket = '['
                    if char_i==']':
                        bracket = '['
                        wrong_bracket = '('
                    found = False
                    analyzed_string = circuit_diagram[:i]
                    for j, _ in enumerate(analyzed_string):
                        bracket_index = len(analyzed_string) - 1 - j
                        if (circuit_diagram[bracket_index]==bracket
                            and not found):
                            found = True
                            relative_index_wrong_bracket = analyzed_string[
                                bracket_index+1:].find(wrong_bracket)
                            if relative_index_wrong_bracket!=-1:
                                wrong_brackets_index += str(
                                    relative_index_wrong_bracket
                                    + bracket_index + 1 + cut_parameter)
                                wrong_brackets += (str(wrong_bracket)
                                                   + '\'')
                                circuit_diagram = (
                                    circuit_diagram[:bracket_index]
                                    + circuit_diagram[bracket_index+1:i]
                                    + circuit_diagram[i+1:])
                                cut_parameter += 2
                                break
                    if found:
                        break
    return wrong_brackets, wrong_brackets_index

def test_consistency_brackets_single_pair():
    """Check that the help function to test if a string has brackets
    consistency works on a single pair of brackets.
    If no inconsistency is detected, the returned strings given by the
    function under test are empty.

    GIVEN: the circuit diagram as a pair of round brackets
    WHEN: I check if there is a brackets inconsistency
    THEN: there is no inconsistency
    """
    pair_brackets = '()' #A single pair of round brackets with obvious
                         #consistency
    wrong_brackets, wrong_brackets_index = consistency_brackets(pair_brackets)

    assert not wrong_brackets, (
        'StructuralError: inconsistent ' + str(wrong_brackets) + ' at '
        + wrong_brackets_index + ': ' + pair_brackets + ' from '
        + 'consistency_brackets()')

def test_consistency_brackets_with_two_pairs():
    """Check that the help function to test if a string has brackets
    consistency works on a string with two pairs of (consistent) brackets.
    If no inconsistency is detected, the returned strings given by the
    function under test are empty.

    GIVEN: the circuit diagram as two pairs of consistent brackets
    WHEN: I check if there is a brackets inconsistency
    THEN: there is no inconsistency
    """
    two_pairs = '([])' #Two pairs of bracket with obvious consistency
    wrong_brackets, wrong_brackets_index = consistency_brackets(two_pairs)

    assert not wrong_brackets, (
        'StructuralError: inconsistent ' + str(wrong_brackets) + ' at '
        + wrong_brackets_index + ': ' + two_pairs + ' from '
        + 'consistency_brackets()')

def test_consistency_brackets_complex():
    """Check that the help function to test if a string has brackets
    consistency works on a string with many pairs of (consistent) brackets,
    with elements inside.
    If no inconsistency is detected, the returned strings given by the
    function under test are empty.

    GIVEN: the circuit diagram with many pairs of consistent brackets
    WHEN: I check if there is a brackets inconsistency
    THEN: there is no inconsistency
    """
    complex_pairs = '[(R1C2)[(R3Q4)R5]]' #Many consistent pairs of brackets
    wrong_brackets, wrong_brackets_index = consistency_brackets(complex_pairs)

    assert not wrong_brackets, (
        'StructuralError: inconsistent ' + str(wrong_brackets) + ' at '
        + wrong_brackets_index + ': ' + complex_pairs + ' from '
        + 'consistency_brackets()')

def test_consistency_brackets_inconsistent_pairs():
    """Check that the help function to test if a string has brackets
    consistency works on a string with inconsistent brackets.
    If an inconsistency is detected, the returned strings given by the
    function under test are contains the inconsistent group and their index in
    the input string.

    GIVEN: the circuit diagram as four brackets that are inconsistent
    WHEN: I check if there is a brackets inconsistency
    THEN: the inconsistency is detected
    """
    complex_pairs = '[(])' #an evident example of inconsistent brackets
    wrong_brackets, _ = consistency_brackets(complex_pairs)

    assert wrong_brackets, (
        'StructuralError: inconsistent brackets inside ' + complex_pairs
        + 'not detected by from consistency_brackets()')


def invalid_characters_updated_diagram(circuit_diagram):
    """Given a valid circuit diagram, a valid position of the start and end of
    the string substitution, find the invalid characters in the updated
    string. The obly valid characters are (, ), [, ], Z, R, C, Q and numbers.
    Used for testing.

    Parameters
    ----------
    circuit_diagram : str
        Updated diagram after a cycle of analysis

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
    for i, char in enumerate(circuit_diagram):
        if (char not in {'(', ')', '[', ']', 'Z', 'C', 'Q', 'R'}
            and not char.isnumeric()):
            wrong_characters += char + ' '
            wrong_characters_index.append(i)
    return wrong_characters, wrong_characters_index

def test_invalid_characters_updated_diagram_no_element():
    """Check that the help function to find invalid characters in an update
    diagram works on a pair of round brackets diagram.
    If no invalid character is detected, the returned string and list given
    by the function under test are empty.

    GIVEN: the updated circuit diagram is an empty string
    WHEN: I check if there are invalid characters inside the diagram
    THEN: no invalid character is detected
    """
    empty_string_diagram = ''
    (wrong_characters,
     wrong_characters_index) = invalid_characters_updated_diagram(
        empty_string_diagram)

    assert not wrong_characters, (
        'StructuralError: invalid character(s) ' + wrong_characters
        + ' at ' + str(wrong_characters_index) + ' in ' + empty_string_diagram
        + 'from invalid_characters_updated_diagram(). Cannot have invalid '
        + 'characters because the string is empty')

def test_invalid_characters_updated_diagram_single_element():
    """Check that the help function to find invalid characters in a an update
    diagram works on a diagram with a single element and a pair of round
    brackets.
    If no invalid character is detected, the returned string and list given
    by the function under test are empty.

    GIVEN: the updated circuit diagram as a single element inside a pair
    of brackets (all valid characters)
    WHEN: I check if there are invalid characters inside the diagram
    THEN: no invalid character is detected
    """
    single_element_diagram = '(R1)'
    (wrong_characters,
     wrong_characters_index) = invalid_characters_updated_diagram(
        single_element_diagram)

    assert not wrong_characters, (
        'StructuralError: invalid character(s) ' + wrong_characters
        + ' at ' + str(wrong_characters_index) + ' in '
        + single_element_diagram + ' from invalid_characters_updated_diagram(). '
        + 'Only round and square brackets, Z, C, Q, R and natural numbers '
        + 'are allowed')

def test_invalid_characters_updated_diagram_many_element():
    """Check that the help function to find invalid characters in an updated
    diagram works on a diagram with all element types and brackets.
    If no invalid character is detected, the returned string and list given
    by the function under test are empty.

    GIVEN: the updated circuit diagram with all element types possible and
    with both types of brackets (with all valid characters)
    WHEN: I check if there are invalid characters inside the diagram
    THEN: no invalid character is detected
    """
    many_element_diagram = '([C1Q2]R3Z4)'
    (wrong_characters,
     wrong_characters_index) = invalid_characters_updated_diagram(
        many_element_diagram)

    assert not wrong_characters, (
        'StructuralError: invalid character(s) ' + wrong_characters
        + ' at ' + str(wrong_characters_index) + ' in '
        + many_element_diagram + 'from invalid_characters_updated_diagram(). '
        + 'Only round and square brackets, Z C, Q, R and natural numbers are '
        + 'allowed')

def test_invalid_characters_updated_diagram_invalid_characters():
    """Check that the help function to find invalid characters in an updated
    diagram works on a diagram with multiple invalid characters.
    If invalid characters are detected, the returned string contains the
    invalid characters, while the returned list contains their index in the
    string.

    GIVEN: the circuit diagram with multiple invalid characters and some valid
    characters
    WHEN: I check if there are invalid characters inside the diagram
    THEN: all and only the invalid characters are reported as such
    """
    invalid_characters_diagram = '(TZ1R3G2)' #T and G are not valid characters
    (wrong_characters,
     wrong_characters_index) = invalid_characters_updated_diagram(
        invalid_characters_diagram)
    expected_result = 'T G '

    assert wrong_characters==expected_result, (
        'StructuralError: invalid character(s) ' + wrong_characters + ' at '
        + str(wrong_characters_index) + ' in ' + invalid_characters_diagram
        + 'from invalid_characters_updated_diagram() are not the ones expected '
        + expected_result + '. Only round and square brackets, Z, C, Q, R '
        + 'and natural numbers are allowed')


def inconsistent_elements_updated_diagram(circuit_diagram):
    """Given a valid circuit string, a valid position of the start and end of
    the string substitution, find the inconsistent element in the updated
    string. Each element has a number that is the same of its order of writing
    in the string. Used for testing.

    Parameters
    ----------
    circuit_diagram : str
        Updated diagram after a cycle of analysis

    Returns
    -------
    wrong_elements : str
        String that contains all the inconsistent elements, separated by a
        comma and a whitespace
    wrong_element_index : list
        List of indexes of the inconsistent elements in the updated string
    """
    wrong_elements = ''
    wrong_element_index = []
    for i, char in enumerate(circuit_diagram):
        if (char in {'Z', 'C', 'Q', 'R'} and circuit_diagram[-1]!=char):
            if not circuit_diagram[i+1].isnumeric():
                wrong_elements += char + str(circuit_diagram[i+1]) + ' '
                wrong_element_index.append(i)
        elif (char.isnumeric() and circuit_diagram[0]!=char):
            if not (circuit_diagram[i-1] in {'Z','C', 'Q', 'R'}):
                wrong_elements += str(circuit_diagram[i-1]) + char + ' '
                wrong_element_index.append(i-1)
    return wrong_elements, wrong_element_index

def test_inconsistent_elements_updated_diagram_no_element():
    """Check that the help function to find inconsistent elements in an
    updated diagram works on a diagram with a no element but only a pair of
    round brackets.
    If no invalid element is detected, the returned string and list given
    by the function under test are empty.

    GIVEN: the updated circuit diagram is just a pair of round brackets, with
    no (invalid) element
    WHEN: I check if there are invalid elements inside the diagram
    THEN: no invalid element is detected
    """
    no_element_diagram = '()'
    (wrong_elements,
     wrong_element_index) = inconsistent_elements_updated_diagram(
        no_element_diagram)

    assert not wrong_elements, (
        'StructuralError: element inconsistency for '+ wrong_elements
        + ' at ' + str(wrong_element_index) + ': ' + no_element_diagram
        + 'from inconsistent_elements(). An element is composed by a valid '
        + 'letter followed by a natural number')

def test_inconsistent_elements_updated_diagram_single_element():
    """Check that the help function to find invalid characters in an
    updated diagram works on a diagram with a single element and a pair of
    round brackets.
    If no invalid element is detected, the returned string and list given
    by the function under test are empty.

    GIVEN: the updated circuit diagram as a single (valid) element inside a
    pair of brackets
    WHEN: I check if there are invalid elements inside the diagram
    THEN: no invalid element is detected
    """
    single_element_diagram = '(Z1)'
    (wrong_elements,
     wrong_element_index) = inconsistent_elements_updated_diagram(
        single_element_diagram)

    assert not wrong_elements, (
        'StructuralError: element inconsistency for '+ wrong_elements
        + ' at ' + str(wrong_element_index) + ': ' + single_element_diagram
        + 'from inconsistent_elements(). An element is composed by a valid '
        + 'letter followed by a natural number')

def test_inconsistent_elements_updated_diagram_many_element():
    """Check that the help function to find invalid characters in an
    updated diagram works on a diagram with multiple elements and a many
    brackets.
    If no invalid element is detected, the returned string and list given
    by the function under test are empty.

    GIVEN: the updated circuit diagram as a three (valid) element inside two
    sets of brackets
    WHEN: I check if there are invalid elements inside the diagram
    THEN: no invalid element is detected
    """
    many_element_diagram = '[(R1Q2)[C3(R4Z5)]'
    (wrong_elements,
     wrong_element_index) = inconsistent_elements_updated_diagram(
        many_element_diagram)

    assert not wrong_elements, (
        'StructuralError: element inconsistency for '+ wrong_elements
        + ' at ' + str(wrong_element_index) + ': ' + many_element_diagram
        + 'from inconsistent_elements(). An element is composed by a valid '
        + 'letter followed by a natural number')

def test_inconsistent_elements_updated_diagram_invalid_element():
    """Check that the help function to find invalid elements in an
    updated diagram works on a diagram with multiple invalid elements.
    If invalid elements are detected, the returned string contains the invalid
    elements, while the returned list contains their indexes in the string.

    GIVEN: the updated circuit diagram with two invalid elements and a valid
    element
    WHEN: I check if there are invalid elements inside the diagram
    THEN: all and only the invalid characters are reported as such
    """
    invalid_element_diagram = '([Z1R]S3)' #R has no number and S is an invalid
                                          #element type
    expected_result = 'R] S3 '
    (wrong_elements,
     wrong_element_index) = inconsistent_elements_updated_diagram(
        invalid_element_diagram)

    assert wrong_elements==expected_result, (
        'StructuralError: element inconsistency for '+ wrong_elements
        + ' at ' + str(wrong_element_index) + ' in ' + invalid_element_diagram
        + 'from inconsistent_elements(). An element is composed by a valid '
        + 'letter followed by a natural number')


def test_update_diagram_valid_diagram_single_cell():
    """Check that update_diagram() method does the right substiturion to set
    a valid diagram (still a string) when there is only a cell with a single
    element.
    Every element inside the specified cell (through delimiters), brackets
    included, must be replaced with a 'Z' followed by the number of the cell
    count. No character outside the substituted cell must be changed.
    If no invalid element is detected, the returned string and list given
    by the function under test are empty.

    GIVEN: a valid circuit diagram with a cell containing a single element,
    valid delimiters for the string substitution
    WHEN: I apply the function to update a diagram at the end of an analysis
    cycle
    THEN: the updated diagram is valid, i.e. the delimited cell is correctly
    updated
    """
    starting_diagram = '(R1)'
    expected_result = 'Z1'
    i_starts = 0
    i_end = 3
    cell_count = 1
    circuit_ = AnalisysCircuit(starting_diagram)
    _ = circuit_.update_diagram(i_starts, i_end, cell_count)
    diagram = circuit_.circuit_diagram

    caller = 'update_diagram()'
    assert isinstance(diagram, str), (
        'TypeError for circuit diagram in ' + caller + '. It must be a string')
    assert diagram, ('StructuralError: empty string in ' + caller)
    wrong_brackets, wrong_brackets_index = consistency_brackets(diagram)
    assert not wrong_brackets, (
        'StructuralError: inconsistent \'' + str(wrong_brackets)
        + '\' at ' + wrong_brackets_index + ': ' + diagram + ' in ' + caller)
    (wrong_characters,
    wrong_characters_index) = invalid_characters_updated_diagram(diagram)
    assert not wrong_characters, (
        'Invalid character(s) ' + wrong_characters + ' at '
        + str(wrong_characters_index) + ' in ' + diagram + ' from ' + caller
        + '. Only round and square brackets, Z, C, Q, R and natural numbers '
        + 'are valid characters')
    (wrong_elements,
        wrong_element_index) = inconsistent_elements_updated_diagram(diagram)
    assert not wrong_elements, (
        'StrucutuaError: element inconsistency for '+ wrong_elements + ' at '
        + str(wrong_element_index) + ' from ' + caller + ': ' + diagram
        + '. An element is composed by a valid letter followed by a natural '
        + 'number')

    assert diagram==expected_result, (
        'StrucutuaError: the updated diagram ' + diagram + 'differs from the '
        + 'expected one: ' + expected_result)

def test_update_diagram_valid_diagram_two_cells():
    """Check that update_diagram() method does the right substiturion to set
    a valid diagram (still a string) when there are two nested cells with two
    elements per cell.
    Every element inside the specified cell (through delimiters), brackets
    included, must be replaced with a 'Z' followed by the number of the cell
    count. No character outside the substituted cell must be changed.

    GIVEN: a valid circuit diagram with two nested cells with two elements
    per cell and valid delimiters of the most nested cell for the string
    substitution
    WHEN: I apply the function to update a diagram at the end of an analysis
    cycle
    THEN: the updated diagram is valid, i.e. the delimited cell is correctly
    updated
    """
    starting_diagram = '(R1C2[R3Q4])'
    expected_result = '(R1C2Z1)'
    i_starts = 5
    i_end = 10
    cell_count = 1
    circuit_ = AnalisysCircuit(starting_diagram)
    _ = circuit_.update_diagram(i_starts, i_end, cell_count)
    diagram = circuit_.circuit_diagram

    caller = 'update_diagram()'
    assert isinstance(diagram, str), (
        'TypeError for circuit diagram in ' + caller + '. It must be a string')
    assert diagram, ('StructuralError: empty string in ' + caller)
    wrong_brackets, wrong_brackets_index = consistency_brackets(diagram)
    assert not wrong_brackets, (
        'StructuralError: inconsistent \'' + str(wrong_brackets)
        + '\' at ' + wrong_brackets_index + ': ' + diagram + ' in ' + caller)
    (wrong_characters,
    wrong_characters_index) = invalid_characters_updated_diagram(diagram)
    assert not wrong_characters, (
        'Invalid character(s) ' + wrong_characters + ' at '
        + str(wrong_characters_index) + ' in ' + diagram + ' from ' + caller
        + '. Only round and square brackets, Z, C, Q, R and natural numbers '
        + 'are valid characters')
    (wrong_elements,
        wrong_element_index) = inconsistent_elements_updated_diagram(diagram)
    assert not wrong_elements, (
        'StrucutuaError: element inconsistency for '+ wrong_elements + ' at '
        + str(wrong_element_index) + ' from ' + caller + ': ' + diagram
        + '. An element is composed by a valid letter followed by a natural '
        + 'number')

    assert diagram==expected_result, (
        'StrucutuaError: the updated diagram ' + diagram + 'differs from the '
        + 'expected one: ' + expected_result)

def test_update_diagram_valid_diagram_many_cells():
    """Check that update_diagram() method does the right substiturion to set
    a valid diagram (still a string) when there are many cells with a variable
    number of elements per cell.
    Every element inside the specified cell (through delimiters), brackets
    included, must be replaced with a 'Z' followed by the number of the cell
    count. No character outside the substituted cell must be changed.

    GIVEN: a valid circuit diagram with many cells with a variable
    number of elements per cell, and valid delimiters of the first closed cell
    for the string substitution
    WHEN: I apply the function to update a diagram at the end of an analysis
    cycle
    THEN: the updated diagram is valid, i.e. the delimited cell is correctly
    updated
    """
    starting_diagram = '[(Z1Q2)[C3(R4Q5)]]'
    expected_result = '[Z2[C3(R4Q5)]]'
    i_starts = 1
    i_end = 6
    cell_count = 2
    circuit_ = AnalisysCircuit(starting_diagram)
    _ = circuit_.update_diagram(i_starts, i_end, cell_count)
    diagram = circuit_.circuit_diagram

    caller = 'update_diagram()'
    assert isinstance(diagram, str), (
        'TypeError for circuit diagram in ' + caller + '. It must be a string')
    assert diagram, ('StructuralError: empty string in ' + caller)
    wrong_brackets, wrong_brackets_index = consistency_brackets(diagram)
    assert not wrong_brackets, (
        'StructuralError: inconsistent \'' + str(wrong_brackets)
        + '\' at ' + wrong_brackets_index + ': ' + diagram + ' in ' + caller)
    (wrong_characters,
    wrong_characters_index) = invalid_characters_updated_diagram(diagram)
    assert not wrong_characters, (
        'Invalid character(s) ' + wrong_characters + ' at '
        + str(wrong_characters_index) + ' in ' + diagram + ' from ' + caller
        + '. Only round and square brackets, Z, C, Q, R and natural numbers '
        + 'are valid characters')
    (wrong_elements,
        wrong_element_index) = inconsistent_elements_updated_diagram(diagram)
    assert not wrong_elements, (
        'StrucutuaError: element inconsistency for '+ wrong_elements + ' at '
        + str(wrong_element_index) + ' from ' + caller + ': ' + diagram
        + '. An element is composed by a valid letter followed by a natural '
        + 'number')

    assert diagram==expected_result, (
        'StrucutuaError: the updated diagram ' + diagram + 'differs from the '
        + 'expected one: ' + expected_result)

def test_update_diagram_valid_diagram_empty_cell():
    """Check that update_diagram() method return an illogical string during
    the update of a diagram when the starting diagram is just a pair of round
    barckets, with no element.

    GIVEN: an invalid circuit diagram with only a pair of round brackets, and
    no element, valid delimiters of this cell for the string substitution
    WHEN: I apply the function to update a diagram at the end of an analysis
    cycle
    THEN: the updated diagram is invalid, i.e. a fictitious new element is
    created in the diagram
    """
    invalid_starting_diagram = '()'
    expected_result = 'Z1'
    i_starts = 0
    i_end = 1
    cell_count = 1
    circuit_ = AnalisysCircuit(invalid_starting_diagram)
    _ = circuit_.update_diagram(i_starts, i_end, cell_count)
    diagram = circuit_.circuit_diagram

    caller = 'update_diagram()'
    assert isinstance(diagram, str), (
        'TypeError for circuit diagram in ' + caller + '. It must be a string')
    assert diagram, ('StructuralError: empty string in ' + caller)
    wrong_brackets, wrong_brackets_index = consistency_brackets(diagram)
    assert not wrong_brackets, (
        'StructuralError: inconsistent \'' + str(wrong_brackets) + '\' at '
        + wrong_brackets_index + ': ' + diagram + ' in ' + caller)
    (wrong_characters,
    wrong_characters_index) = invalid_characters_updated_diagram(diagram)
    assert not wrong_characters, (
        'Invalid character(s) ' + wrong_characters + ' at '
        + str(wrong_characters_index) + ' in ' + diagram + ' from ' + caller
        + '. Only round and square brackets, Z, C, Q, R and natural numbers '
        + 'are valid characters')
    (wrong_elements,
        wrong_element_index) = inconsistent_elements_updated_diagram(diagram)
    assert not wrong_elements, (
        'StrucutuaError: element inconsistency for '+ wrong_elements + ' at '
        + str(wrong_element_index) + ' from ' + caller + ': ' + diagram
        + '. An element is composed by a valid letter followed by a natural '
        + 'number')

    assert diagram==expected_result, (
        'StrucutuaError: the updated diagram ' + diagram + 'differs from the '
        + 'expected one: ' + expected_result)

def test_update_diagram_valid_diagram_wrong_delimiters():
    """Check that update_diagram() method return an illogical string during
    the update of a diagram when the delimiters of the cell to be updated are
    wrong, even if the starting diagram is valid.

    GIVEN: a valid circuit diagram with two nested cells that contain two
    elements each, but invalid delimiters of this cell for the string
    substitution
    WHEN: I apply the function to update a diagram at the end of an analysis
    cycle
    THEN: the updated diagram is invalid, i.e. there are invalid elements in
    the updated cell
    """
    starting_diagram = '(R1C2[R3Q4])'
    expected_diagram = '(R1CZ1)' #Invalid diagram with that stand-alone C
    invalid_i_starts = 4
    i_end = 10
    cell_count = 1
    circuit_ = AnalisysCircuit(starting_diagram)
    _ = circuit_.update_diagram(invalid_i_starts, i_end, cell_count)
    diagram = circuit_.circuit_diagram
    expected_result_inconsistent_elements = 'CZ '

    caller = 'update_diagram()'
    assert isinstance(diagram, str), (
        'TypeError for circuit diagram in ' + caller + '. It must be a string')
    assert diagram, ('StructuralError: empty string in ' + caller)
    wrong_brackets, wrong_brackets_index = consistency_brackets(diagram)
    assert not wrong_brackets, (
        'StructuralError: inconsistent \'' + str(wrong_brackets)
        + '\' at ' + wrong_brackets_index + ': ' + diagram + ' in ' + caller)
    (wrong_characters,
    wrong_characters_index) = invalid_characters_updated_diagram(diagram)
    assert not wrong_characters, (
        'Invalid character(s) ' + wrong_characters + ' at '
        + str(wrong_characters_index) + ' in ' + diagram + ' from ' + caller
        + '. Only round and square brackets, Z, C, Q, R and natural numbers '
        + 'are valid characters')

    (wrong_elements,
        wrong_element_index) = inconsistent_elements_updated_diagram(diagram)
    assert wrong_elements==expected_result_inconsistent_elements, (
        'StrucutuaError: element inconsistency for '+ wrong_elements + ' at '
        + str(wrong_element_index) + ' from ' + caller + ': ' + diagram
        + '. The invalid elements detected differ from the expected ones: '
        + expected_result_inconsistent_elements)

    assert diagram==expected_diagram, (
        'StrucutuaError: the updated diagram ' + diagram + 'differs from the '
        + 'expected one: ' + expected_diagram)


def test_update_diagram_new_element_single_cell():
    """Check that update_diagram() returns a valid new element after the update
    of the diagram when there is only a cell with a single element.
    Every new element have to be a string starting with 'Z' followed by the
    number of the cell count (a numeric char).

    GIVEN: a valid circuit diagram with a cell containing a single element,
    valid delimiters for the string substitution and valid cell count
    WHEN: I apply the function to update a diagram at the end of an analysis
    cycle
    THEN: the new element is a valid element
    """
    starting_diagram = '(R1)'
    expected_result = 'Z1'
    i_starts = 0
    i_end = 3
    cell_count = 1
    circuit_ = AnalisysCircuit(starting_diagram)
    new_element = circuit_.update_diagram(i_starts, i_end, cell_count)

    caller = 'update_diagram()'
    assert isinstance(new_element, str), (
        'TypeError for circuit diagram in ' + caller + '. It must be a string')
    assert new_element, ('StructuralError: empty string in ' + caller)
    assert len(new_element)==2, ('Invalid length for ' + new_element + ' in '
                                 + caller + '. It has to be of length 2')
    assert new_element.startswith('Z'), (
        'StructuralError for '+ new_element + ' in ' + caller + '. A new '
        + 'element must begin with a \'Z\'')
    last_element = new_element[-1]
    assert last_element.isnumeric(), (
        'StructuralError for '+ new_element + ' in ' + caller + '. A new '
        + 'element must end with a numeric char')

    assert new_element==expected_result, (
    'StrucutuaError: the new element ' + new_element + 'differs from the '
    + 'expected one: ' + expected_result)

def test_update_diagram_new_element_two_cells():
    """Check that update_diagram() returns a valid new element after the update
    of the diagram when there are two nested cells with two elements per cell.
    One cycle of substitution has already happened.
    Every new element have to be a string starting with 'Z' followed by the
    number of the cell count (a numeric char).

    GIVEN: a valid circuit diagram with two nested cells with two
    elements per cell, valid delimiters for the string substitution and
    valid cell count
    WHEN: I apply the function to update a diagram at the end of an analysis
    cycle
    THEN: the new element is a valid element
    """
    starting_diagram = '(R1C2[Z1Q5])'
    expected_result = 'Z2'
    i_starts = 5
    i_end = 10
    cell_count = 2
    circuit_ = AnalisysCircuit(starting_diagram)
    new_element = circuit_.update_diagram(i_starts, i_end, cell_count)

    caller = 'update_diagram()'
    assert isinstance(new_element, str), (
        'TypeError for circuit diagram in ' + caller + '. It must be a string')
    assert new_element, ('StructuralError: empty string in ' + caller)
    assert len(new_element)==2, ('Invalid length for ' + new_element + ' in '
                                 + caller + '. It has to be of length 2')
    assert new_element.startswith('Z'), (
        'StructuralError for '+ new_element + ' in ' + caller + '. A new '
        + 'element must begin with a \'Z\'')
    last_element = new_element[-1]
    assert last_element.isnumeric(), (
        'StructuralError for '+ new_element + ' in ' + caller + '. A new '
        + 'element must end with a numeric char')

    assert new_element==expected_result, (
    'StrucutuaError: the new element ' + new_element + 'differs from the '
    + 'expected one: ' + expected_result)

def test_update_diagram_new_element_many_cells():
    """Check that update_diagram() returns a valid new element after the update
    of the diagram when there are many cells with a variable number of
    elements per cell.
    Every new element have to be a string starting with 'Z' followed by the
    number of the cell count (a numeric char).

    GIVEN: a valid circuit diagram with many cells with a variable number of
    elements per cell, valid delimiters for the string substitution and valid
    cell count.
    WHEN: I apply the function to update a diagram at the end of an analysis
    cycle
    THEN: the new element is a valid element
    """
    starting_diagram = '[(R1Q2)[C3(R4Q5)]]'
    expected_result = 'Z1'
    i_starts = 1
    i_end = 6
    cell_count = 1
    circuit_ = AnalisysCircuit(starting_diagram)
    new_element = circuit_.update_diagram(i_starts, i_end, cell_count)

    caller = 'update_diagram()'
    assert isinstance(new_element, str), (
        'TypeError for circuit diagram in ' + caller + '. It must be a string')
    assert new_element, ('StructuralError: empty string in ' + caller)
    assert len(new_element)==2, ('Invalid length for ' + new_element + ' in '
                                 + caller + '. It has to be of length 2')
    assert new_element.startswith('Z'), (
        'StructuralError for '+ new_element + ' in ' + caller + '. A new '
        + 'element must begin with a \'Z\'')
    last_element = new_element[-1]
    assert last_element.isnumeric(), (
        'StructuralError for '+ new_element + ' in ' + caller + '. A new '
        + 'element must end with a numeric char')

    assert new_element==expected_result, (
    'StrucutuaError: the new element ' + new_element + 'differs from the '
    + 'expected one: ' + expected_result)

def test_update_diagram_new_element_invalid_cell_count():
    """Check that update_diagram() returns an invalid new element after the
    update of the diagram when the cell count is invalid, even if the starting
    diagram was valid.

    GIVEN: a valid circuit diagram with two nested cells with two
    elements per cell, valid delimiters for the string substitution but an
    invalid cell count (a letter char).
    WHEN: I apply the function to update a diagram at the end of an analysis
    cycle
    THEN: the new element is an invalid element
    """
    starting_diagram = '[(R1C2)[C3R4]]'
    expected_result = 'Ze' #Invalid element: its second character is not
                           #numerical but a letter
    i_starts = 1
    i_end = 6
    invalid_cell_count = 'e'
    circuit_ = AnalisysCircuit(starting_diagram)
    new_element = circuit_.update_diagram(i_starts, i_end, invalid_cell_count)

    caller = 'update_diagram()'
    assert isinstance(new_element, str), (
        'TypeError for circuit diagram in ' + caller + '. It must be a string')
    assert new_element, ('StructuralError: empty string in ' + caller)
    assert len(new_element)==2, ('Invalid length for ' + new_element + ' in '
                                 + caller + '. It has to be of length 2')
    assert new_element.startswith('Z'), (
        'StructuralError for '+ new_element + ' in ' + caller + '. A new '
        + 'element must begin with a \'Z\'')
    last_element = new_element[-1]
    assert not last_element.isnumeric(), (
        'StructuralError for '+ new_element + ' in ' + caller + '. The new '
        + 'element is expected to have an invalid second character i.e. a '
        + 'letter')

    assert new_element==expected_result, (
    'StrucutuaError: the new element ' + new_element + 'differs from the '
    + 'expected one: ' + expected_result)


def generate_analyzed_circuit_resistor():
    """Generate a full analyzed circuit of a single resistor, after the
    set_final_results() method is used.
    """
    function_r = lambda x, y: y
    impedance_map = {'R1': (function_r, 1000.)}
    analyzed_circuit = AnalisysCircuit('Z1', impedance_map)
    analyzed_circuit.set_final_results()
    return analyzed_circuit

def test_set_final_results_impedance_resistor():
    """Check that the final impedance of an analyzed circuit, set through
    the set_final_results() method, is a function in the case of a valid
    diagram with a single element.

    GIVEN: a valid analyzed circuit with a single element, after the
    set_final_results() method is used
    WHEN: I apply the set_final_results() on the AnalysisCircuit object at the
    end of the analysis
    THEN: the set final impedance is a function
    """
    analyzed_circuit = generate_analyzed_circuit_resistor()
    final_impedance = analyzed_circuit.impedance

    assert inspect.isfunction(final_impedance), (
        'TypeError for the final impedance of the AnalysisCircuit. It must '
        + 'be a function')

def generate_analyzed_circuit_capacitor():
    """Generate a full analyzed circuit of a constant capacitor, after the
    set_final_results() method is used.
    """
    function_c = lambda x, y: 1/(x*y)
    impedance_map = {'C1': (function_c, 'const')}
    analyzed_circuit = AnalisysCircuit('Z1', impedance_map)
    analyzed_circuit.set_final_results()
    return analyzed_circuit

def test_set_final_results_impedance_capacitor():
    """Check that the final impedance of an analyzed circuit, set through
    the set_final_results() method, is a function in the case of a valid
    diagram with a single constant capacitor element.

    GIVEN: a valid analyzed circuit with a capcitor element, after the
    set_final_results() method is used
    WHEN: I apply the set_final_results() on the AnalysisCircuit object at the
    end of the analysis
    THEN: the set final impedance is a function
    """
    analyzed_circuit = generate_analyzed_circuit_capacitor()
    final_impedance = analyzed_circuit.impedance

    assert inspect.isfunction(final_impedance), (
        'TypeError for the final impedance of the AnalysisCircuit. It must '
        + 'be a function')

def generate_analyzed_circuit_two_elements():
    """Generate a full analyzed circuit of a resistor and a capacitor in
    series, after the set_final_results() method is used.
    """
    function_r = lambda x, y: y
    function_q = lambda x, y: 1/((x*y[0])**y[1])
    impedance_map = {'R1': (function_r, 1000.),
                     'Q2': (function_q, [1e-6, 0.1]),
                     'Z1': (add(function_r, function_r), 'equivalent')}
    analyzed_circuit = AnalisysCircuit('Z1', impedance_map)
    analyzed_circuit.set_final_results()
    return analyzed_circuit

def test_set_final_results_impedance_two_elements():
    """Check that the final impedance of an analyzed circuit, set through
    the set_final_results() method, is a function in the case of a valid
    diagram with two elements.

    GIVEN: a valid analyzed circuit with two elements, after the
    set_final_results() method is used
    WHEN: I apply the set_final_results() on the AnalysisCircuit object at the
    end of the analysis
    THEN: the set final impedance is a function
    """
    analyzed_circuit = generate_analyzed_circuit_two_elements()
    final_impedance = analyzed_circuit.impedance

    assert inspect.isfunction(final_impedance), (
        'TypeError for the final impedance of the AnalysisCircuit. It must '
        + 'be a function')

def generate_analyzed_circuit_invalid():
    """Generate a full invalid analyzed circuit of a resistor, with an invalid
    impedance function and an valid constant parameter, after the
    set_final_results() method is used.
    """
    impedance_map = {'R1': ('f(x)', 'const')}
    analyzed_circuit = AnalisysCircuit('Z1', impedance_map)
    analyzed_circuit.set_final_results()
    return analyzed_circuit

def test_set_final_results_impedance_invalid():
    """Check that the final impedance of an analyzed circuit, set through
    the set_final_results() method, is an invalid function in the case of an
    invalid input function in the circuit.

    GIVEN: an invalid analyzed circuit with in ainvalid function, after the
    set_final_results() method is used
    WHEN: I apply the set_final_results() on the AnalysisCircuit object at the
    end of the analysis
    THEN: the set final impedance is an invalid function
    """
    invalid_analyzed_circuit = generate_analyzed_circuit_invalid()
    invalid_impedance = invalid_analyzed_circuit.impedance

    assert not inspect.isfunction(invalid_impedance), (
        'TypeError for the final impedance of the AnalysisCircuit. It should '
        + 'not be a function')


def wrong_match_element_analyzed_circuit_final_parameters(
        impedance_parameters_map, final_parameters):
    """Find any incongruence between the elements of impedance_parameters_map
    and final_parameters: all the non-constant elements of the
    impedance_parameters_map must be present in the final parameters_map with
    the same element name a key. No constant element of the
    impedance_parameters_map must be present in the final parameters_map and
    no element that is not present in the analyzed parameters must be present
    in the final parameters map. Used for testing.

    Parameters
    ----------
    impedance_parameters_map : dict
        Analyzed parameters map
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
    if not set(final_elements).issubset(impedance_parameters_map.keys()):
        wrong_elements += 'Extra element in the final parameters '
    else:
        for element, parameter in impedance_parameters_map.items():
            if not isinstance(parameter[1], str):
                if not element in final_elements:
                    wrong_elements += element + ' '
            else:
                if element in final_elements:
                    wrong_elements += element + ' '
    return wrong_elements

def test_wrong_match_element_analyzed_final_parameters_no_element():
    """Check that the help function that finds the element mismatch between
    impedance_parameters_map and final parameters dictionary works in the case
    of two empty dictionaries.
    All and only the impedance_parameters_map elements that are not constant
    must be in the final parameters elements.
    If no invalid match is detected, the returned string given by the function
    under test is empty.

    GIVEN: two empty dictionaries
    WHEN: I check if the final parameters elements are correctly set from the
    impedance_parameters_map elements
    THEN: no invalid final parameters elements detected
    """
    input_parameters_map = {}
    final_parameters_map = {}
    wrong_elements = wrong_match_element_analyzed_circuit_final_parameters(
        input_parameters_map, final_parameters_map)

    assert not wrong_elements, (
        'Bad match between non constant elements of the analyzed circuit '
        + 'and the final analysis parameter. ' + wrong_elements + 'not found. '
        + 'Cannot find any bad match because the dictionaries are both empty')

def test_wrong_match_element_analyzed_final_parameters_single_element():
    """Check that the help function that finds the element mismatch between
    impedance_parameters_map and final parameters dictionary works in the case
    of a non constant element in the impedance_parameters_map and the same
    element in the final dictionary.
    All and only the analyzed parameters elements that are not constant must
    be in the final parameters elements.
    If no invalid match is detected, the returned string given by the function
    under test is empty.

    GIVEN: a non constant element in the impedance_parameters_map and the same
    element in the final dictionary
    WHEN: I check if the final parameters elements are correctly set from the
    analyzed parameters elements
    THEN: no invalid final parameters elements detected
    """
    function_r = lambda x, y: y
    input_parameters_map = {'R1': (function_r, 1000.)}
    final_parameters_map = {'R1': 1000.}
    wrong_elements = wrong_match_element_analyzed_circuit_final_parameters(
        input_parameters_map, final_parameters_map)

    assert not wrong_elements, (
        'Bad match between non constant elements of the analyzed circuit and '
        + 'the final analysis parameter. ' + wrong_elements + 'not found. ')

def test_wrong_match_element_analyzed_final_parameters_two_elements():
    """Check that the help function that finds the element mismatch between
    impedance_parameters_map and final parameters dictionary works in the case
    of both a non constant element a constant element in the
    impedance_parameters_map and only the non constant element in the final
    dictionary.
    All and only the analyzed parameters elements that are not constant must
    be in the final parameters elements.
    If no invalid match is detected, the returned string given by the function
    under test is empty.

    GIVEN: a non constant element  and a constant element in the
    impedance_parameters_map and only the non constant element in the final
    dictionary
    WHEN: I check if the final parameters elements are correctly set from the
    analyzed parameters elements
    THEN: no invalid final parameters elements detected
    """
    function_c = lambda x, y: 1/(x*y)
    function_q = lambda x, y: 1/((x*y[0])**y[1])
    input_parameters_map = {'C1': (function_c, 1e-6),
                            'Q2': (function_q, 'const')}
    final_parameters_map = {'C1': 1e-6}
    wrong_elements = wrong_match_element_analyzed_circuit_final_parameters(
        input_parameters_map, final_parameters_map)

    assert not wrong_elements, (
        'Bad match between non constant elements of the analyzed circuit '
        + 'and the final analysis parameter. ' + wrong_elements + 'not '
        + 'found. ')

def test_wrong_match_element_analyzed_final_parameters_missing_element():
    """Check that the help function that finds the element mismatch between
    impedance_parameters_map and final parameters dictionary works in the case
    of two non constant elements in the impedance_parameters_map and only one
    of them in the final dictionary.
    All and only the analyzed parameters elements that are not constant must
    be in the final parameters elements.
    If invalid matches are detected, the returned string given by the function
    under test contains the elements of the bad matches.

    GIVEN: a non constant element and a constant element in the
    impedance_parameters_map and only one of them in the final dictionary
    WHEN: I check if the final parameters elements are correctly set from the
    analyzed parameters elements
    THEN: the missing element in the final parameters elements is detected
    """
    function_r = lambda x, y: y
    input_parameters_map = {'R1': (function_r, 300.), 'R2': (function_r, 100.)}
    final_parameters_map = {'R1': 200.}
    wrong_elements = wrong_match_element_analyzed_circuit_final_parameters(
        input_parameters_map, final_parameters_map)
    expected_result = 'R2 '

    assert wrong_elements==expected_result, (
        'Bad match between non constant elements of the analyzed circuit '
        + 'and the final analysis parameter. ' + wrong_elements + 'not '
        + 'found. Different invalid elements than the one expeted: '
        + expected_result)

def test_wrong_match_element_analyzed_final_parameters_extra_element():
    """Check that the help function that finds the element mismatch between
    impedance_parameters_map and final parameters dictionary works in the case
    of one non constant elements and a constant one in the
    impedance_parameters_map, while the final dictionary has the same
    non-constant element but also an entirely new element.
    All and only the analyzed parameters elements that are not constant must
    be in the final parameters elements.
    If invalid matches are detected, the returned string given by the function
    under test contains the elements of the bad matches.

    GIVEN: one non constant element and a constant one in the
    impedance_parameters_map, while the final dictionary has the same
    non-constant element but also and an entirely new element
    WHEN: I check if the final parameters elements are correctly set from the
    analyzed parameters elements
    THEN: the extra element in the final parameters elements is detected as
    invalid
    """
    function_r = lambda x, y: y
    input_parameters_map = {'R1': (function_r, 300.), 'R2': (function_r, 100.)}
    final_parameters_map = {'R1': 300., 'C2': 1e-6}
    wrong_elements = wrong_match_element_analyzed_circuit_final_parameters(
        input_parameters_map, final_parameters_map)
    expected_result = 'Extra element in the final parameters '

    assert wrong_elements==expected_result, (
        'Bad match between non constant elements of the analyzed circuit '
        + 'and the final analysis parameter. ' + wrong_elements + 'not '
        + 'found. Different invalid elements than the one expeted: '
        + expected_result)

def test_wrong_match_element_analyzed_final_parameters_bad_match():
    """Check that the help function that finds the element mismatch between
    impedance_parameters_map and final parameters dictionary works in the case
    of one non constant elements and a constant one in the analyzed dictionary,
    while the final dictionary has the same non-constant element but also an
    entirely new element.
    All and only the analyzed parameters elements that are not constant must
    be in the final parameters elements.
    If invalid matches are detected, the returned string given by the function
    under test contains the elements of the bad matches.

    GIVEN: one non constant element and a constant one in the
    impedance_parameters_map while the final dictionary has the the same
    elements (though only the non constant one should be there)
    WHEN: I check if the final parameters elements are correctly set from the
    analyzed parameters elements
    THEN: the constant element in the final parameters element is detected as
    invalid
    """
    function_r = lambda x, y: y
    function_c = lambda x, y: 1/(x*y)
    input_parameters_map = {'R1': (function_r, 300.),
                            'C2': (function_c, 'const')}
    final_parameters_map = {'R1': 300., 'C2': 1e-6}
    wrong_elements = wrong_match_element_analyzed_circuit_final_parameters(
        input_parameters_map, final_parameters_map)
    expected_result = 'C2 '

    assert wrong_elements==expected_result, (
        'Bad match between non constant elements of the analyzed circuit '
        + 'and the final analysis parameter. ' + wrong_elements + 'not '
        + 'found. Different invalid elements than the one expeted: '
        + expected_result)


def wrong_match_parameter_analyzed_circuit_final_parameters(
        impedance_parameters_map, final_parameters):
    """Find any incongruence between the analyzed parameters and
    final_parameters: all the non-constant parameter of the
    impedance_parameters_map must be present in the final parameters_map
    with the same element name a key. No constant parameter of the
    impedance_parameters_map must be present in the final parameters_map and
    no parameter that is not present in the analyzed parameter must be present
    in the final parameters map. Used for testing.

    Parameters
    ----------
    impedance_parameters_map : dict
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
    #'set()' does not accept nested lists, (Q's parameter case), so a
    # convertion to tuple is needed
    impedance_parameters_map_values = [
        tuple(parameter[1]) if isinstance(parameter[1], list) else parameter[1]
        for parameter in impedance_parameters_map.values()]
    final_parameters_values = [
        tuple(parameter) if isinstance(parameter, list) else parameter
        for parameter in final_parameters.values()]

    if not set(final_parameters_values).issubset(impedance_parameters_map_values):
        wrong_parameters += 'Extra parameter in the final parameters '
    else:
        for element, parameter in impedance_parameters_map.items():
            if not isinstance(parameter[1], str):
                if parameter[1] not in list(final_parameters.values()):
                    wrong_parameters += element + ' '
                elif parameter[1]!=final_parameters[element]:
                    wrong_parameters += element + ' '
    return wrong_parameters

def test_wrong_match_parameter_analyzed_final_parameters_no_element():
    """Check that the help function that finds the parameter mismatch between
    impedance_parameters_map and final parameters dictionary works in
    the case of two empty dictionaries.
    All and only the analyzed parameters that are not constant must be in the
    final parameters.
    If no invalid match is detected, the returned string given by the function
    under test is empty.

    GIVEN: two empty dictionaries
    WHEN: I check if the final parameters are correctly set from the
    impedance_parameters_map
    THEN: no invalid final parameters detected
    """
    input_parameters_map = {}
    final_parameters_map = {}
    wrong_parameter = wrong_match_parameter_analyzed_circuit_final_parameters(
        input_parameters_map, final_parameters_map)

    assert not wrong_parameter, (
        'Bad match between non constant parameters of the analyzed circuit '
        + 'and the final analysis parameter. ' + wrong_parameter + 'not '
        + 'found. Cannot find any bad match because the dictionaries are both '
        + 'empty')

def test_wrong_match_parameter_analyzed_final_parameters_single_element():
    """Check that the help function that finds the parameter mismatch between
    impedance_parameters_map and final parameters dictionary works in the case
    of a non constant parameter in the impedance_parameters_map and the
    same parameter in the final dictionary.
    All and only the analyzed parameters that are not constant must be
    in the final parameters.
    If no invalid match is detected, the returned string given by the function
    under test is empty.

    GIVEN: a non constant parameter in the impedance_parameters_map and the
    same parameter (with the same element name) in the final dictionary
    WHEN: I check if the final parameters are correctly set from the
    analyzed parameters
    THEN: no invalid final parameters detected
    """
    function_r = lambda x, y: y
    input_parameters_map = {'R1': (function_r, 1000.)}
    final_parameters_map = {'R1': 1000.}
    wrong_parameter= wrong_match_parameter_analyzed_circuit_final_parameters(
        input_parameters_map, final_parameters_map)

    assert not wrong_parameter, (
        'Bad match between non constant parameters of the analyzed circuit '
        + 'and the final analysis parameter. ' + wrong_parameter + 'not '
        + 'found. ')

def test_wrong_match_parameter_analyzed_final_parameters_two_elements():
    """Check that the help function that finds the parameter mismatch between
    impedance_parameters_map and final parameters dictionary works in
    the case of both a non constant parameter a constant parameter in the
    impedance_parameters_map and only the non constant parameter in the final
    dictionary.
    All and only the analyzed parameters that are not constant must be
    in the final parameters.
    If no invalid match is detected, the returned string given by the function
    under test is empty.

    GIVEN: a non constant parameter and a constant parameter in the
    impedance_parameters_map and only the non constant parameter in the final
    dictionary (with the same element names)
    WHEN: I check if the final parameters are correctly set from the
    analyzed parameters
    THEN: no invalid final parameters detected
    """
    function_c = lambda x, y: 1/(x*y)
    function_q = lambda x, y: 1/((x*y[0])**y[1])
    input_parameters_map = {'Q1': (function_q, [1e-5, 0.76]),
                            'C2': (function_c, 'const')}
    final_parameters_map = {'Q1': [1e-5, 0.76]}
    wrong_parameter = wrong_match_parameter_analyzed_circuit_final_parameters(
        input_parameters_map, final_parameters_map)

    assert not wrong_parameter, (
        'Bad match between non constant parameters of the analyzed circuit '
        + 'and the final analysis parameter. ' + wrong_parameter + 'not '
        + 'found. ')

def test_wrong_match_parameter_analyzed_final_parameters_missing_parameter():
    """Check that the help function that finds the parameter mismatch between
    impedance_parameters_map and final parameters dictionary works in
    the case of two non constant parameters in the impedance_parameters_map
    and only one of them in the final dictionary.
    All and only the analyzed parameters that are not constant must be
    in the final parameters.
    If invalid matches (by element) are detected, the returned string given
    by the function under test contains the elements of the bad matches.

    GIVEN: a non constant parameter and a constant parameter in the
    impedance_parameters_map and only one of them in the final dictionary
    (with the same element name)
    WHEN: I check if the final parameters are correctly set from the
    analyzed parameters
    THEN: the missing parameter in the final parameters is detected
    """
    function_r = lambda x, y: y
    input_parameters_map = {'R1': (function_r, 300.), 'R2': (function_r, 100.)}
    final_parameters_map = {'R1': 300.}
    wrong_parameters = wrong_match_parameter_analyzed_circuit_final_parameters(
        input_parameters_map, final_parameters_map)
    expected_result = 'R2 '

    assert wrong_parameters==expected_result, (
        'Bad match between non constant parameters of the analyzed circuit '
        + 'and the final analysis parameter. ' + wrong_parameters + 'not '
        + 'found. Different invalid parameters than the one expeted: '
        + expected_result)

def test_wrong_match_parameter_analyzed_final_parameters_extra_parameter():
    """Check that the help function that finds the parameter mismatch between
    input parameters dictionaries and final parameters dictionaries works in
    the case of one non constant parameters and a constant one in the
    impedance_parameters_map, while the final dictionary has the same
    non-constant parameter but also an entirely new parameter (with the same
    element of the constant element).
    All and only the analyzed parameters that are not constant must be
    in the final parameters.
    If invalid matches (by parameter) are detected, the returned string given
    by the function under test states that there is an extra parameter.

    GIVEN: one non constant parameter and a constant one in the
    impedance_parameters_map, while the final dictionary has the same
    non-constant parameter (with the same element name) but also and an
    entirely new parameter (with the same element of the constant element)
    WHEN: I check if the final parameters are correctly set from the
    analyzed parameters
    THEN: the extra parameter in the final parameters is detected as
    invalid
    """
    function_r = lambda x, y: y
    input_parameters_map = {'R1': (function_r, 300.), 'R2': (function_r, 100.)}
    final_parameters_map = {'R1': 300., 'R2': 200.}
    wrong_parameters = wrong_match_parameter_analyzed_circuit_final_parameters(
        input_parameters_map, final_parameters_map)
    expected_result = 'Extra parameter in the final parameters '

    assert wrong_parameters==expected_result, (
        'Bad match between non constant parameters of the analyzed circuit '
        + 'and the final analysis parameter. ' + wrong_parameters + 'not '
        + 'found. Different invalid parameters than the one expeted: '
        + expected_result)

def test_wrong_match_parameter_analyzed_final_parameters_bad_match():
    """Check that the help function that finds the parameter mismatch between
    impedance_parameters_map and final parameters dictionary works in
    the case of one non constant parameter and a constant one in the
    impedance_parameters_map, while the final dictionary has the same
    non-constant parameter but also an entirely new parameter.
    All and only the analyzed parameters that are not constant must be
    in the final parameters.
    If invalid matches (by parameter) are detected, the returned string given
    by the function under test states that there is an extra parameter.

    GIVEN: one non constant parameter and a constant one in the analyzed
    dictionary, while the final dictionary has the the same parameters (though
    only the non constant one should be there)
    WHEN: I check if the final parameters are correctly set from the
    analyzed parameters
    THEN: the constant parameter in the final parameters is detected as
    invalid
    """
    function_r = lambda x, y: y
    input_parameters_map = {'R1': (function_r, 'const'),
                            'R2': (function_r, 100.)}
    final_parameters_map = {'R1': 300., 'R2': 100.}
    wrong_parameters = wrong_match_parameter_analyzed_circuit_final_parameters(
        input_parameters_map, final_parameters_map)
    expected_result = 'Extra parameter in the final parameters '

    assert wrong_parameters==expected_result, (
        'Bad match between non constant parameters of the analyzed circuit '
        + 'and the final analysis parameters. ' + wrong_parameters + 'not '
        + 'found. Different invalid parameters than the one expeted: '
        + expected_result)

def test_wrong_match_parameter_analyzed_final_parameters_duplicates():
    """Check that the help function that finds the parameter mismatch between
    impedance_parameters_map dictionary and final parameters dictionaries
    works in the case of two non constant parameters in the
    impedance_parameters_map and two parameters in the final dictionary, bu
    even tough the elements are correct, the parameters in the final
    parameters are both the valid parameter of the first analyzed parameters,
    thus leaving the second parameters (that should be in the final parameters
    too since it is not constant) behind.
    All and only the analyzed parameters that are not constant must be
    in the final parameters.
    If invalid matches (by element) are detected, the returned string given
    by the function under test contains the elements of the bad matches.

    GIVEN: two non constant parameters in the analyzed dictionary and two
    parameters in the final dictionary, but even tough the elements are correct,
    the parameters in the final parameters are both the valid parameter of
    the first analyzed parameters
    WHEN: I check if the final parameters are correctly set from the
    analyzed parameters
    THEN: the second parameter in the final parameters is detected as invalid
    """
    function_c = lambda x, y: 1/(x*y)
    impedance_parameters_map = {'C1': (function_c, 1e-6),
                                'C2': (function_c, 2e-6)}
    final_parameters_map = {'C1': 1e-6, 'C2': 1e-6}
    wrong_parameter = wrong_match_parameter_analyzed_circuit_final_parameters(
        impedance_parameters_map, final_parameters_map)
    expected_result = 'C2 '

    assert wrong_parameter==expected_result, (
        'Bad match between non constant parameters of the analyzed circuit '
        + 'and the final analysis parameter. ' + wrong_parameter + 'not '
        + 'found. Different invalid parameters than the one expeted: '
        + expected_result)


def test_get_final_results_parameters_resistor():
    """Check that the final parameters_map of an analyzed circuit, set through
    the set_final_results() method, corresponds to the correct
    impedance_parameters_map from the analyzed Circuit in the case of a
    non-constant single resistor analyzed circuit.
    The final parameters_map must contain all and only the non-constant
    element names with their relative parameter value.

    GIVEN: a valid analyzed circuit of a single resistor with correct
    impedance_parameters_map and parameters_map
    WHEN: I check if the final parameters elements are correctly set from the
    impedance_parameters_map
    THEN: the set final parameters_map matches the input ones
    """
    analyzed_circuit = generate_analyzed_circuit_resistor()
    final_parameters_map = analyzed_circuit.parameters_map
    function_r = lambda x, y: y
    impedance_parameters_map = {'R1': (function_r, 1000.)}

    wrong_elements = wrong_match_element_analyzed_circuit_final_parameters(
        impedance_parameters_map, final_parameters_map)
    assert not wrong_elements, (
        'Bad match between non constant elements of the analyzed circuit and '
        + 'the final analysis parameter. ' + wrong_elements + 'not found')

    wrong_parameters = wrong_match_parameter_analyzed_circuit_final_parameters(
        impedance_parameters_map, final_parameters_map)
    assert not wrong_parameters, (
        'Bad match between parameters of the initial circuit and the final '
        + 'analysis parameter. Parameter of element ' + wrong_parameters
        + 'not found')

def test_get_final_results_parameters_capacitor():
    """Check that the final parameters_map of an analyzed circuit, set through
    the set_final_results() method, corresponds to the correct
    impedance_parameters_map from the analyzed Circuit in the case of a
    constant single capacitor analyzed circuit.
    The final parameters_map must contain all and only the non-constant
    element names with their relative parameter value.

    GIVEN: a valid analyzed circuit of a single resistor with correct
    impedance_parameters_map and parameters_map
    WHEN: I check if the final parameters elements are correctly set from the
    impedance_parameters_map
    THEN: the set final parameters_map matches the input ones
    """
    analyzed_circuit = generate_analyzed_circuit_capacitor()
    final_parameters_map = analyzed_circuit.parameters_map
    function_c = lambda x, y: 1/(x*y)
    impedance_parameters_map = {'C1': (function_c, 'const')}

    wrong_elements = wrong_match_element_analyzed_circuit_final_parameters(
        impedance_parameters_map, final_parameters_map)
    assert not wrong_elements, (
        'Bad match between non constant elements of the analyzed circuit and '
        + 'the final analysis parameter. ' + wrong_elements + 'not found')

    wrong_parameters = wrong_match_parameter_analyzed_circuit_final_parameters(
        impedance_parameters_map, final_parameters_map)
    assert not wrong_parameters, (
        'Bad match between parameters of the initial circuit and the final '
        + 'analysis parameter. Parameter of element ' + wrong_parameters
        + 'not found')

def test_get_final_results_parameters_two_elements():
    """Check that the final parameters_map of an analyzed circuit, set through
    the set_final_results() method, corresponds to the correct
    impedance_parameters_map from the analyzed Circuit in the case of a
    a non-constant resistor and non-constant cpe analyzed circuit.
    The final parameters_map must contain all and only the non-constant
    element names with their relative parameter value.

    GIVEN: a valid analyzed circuit of a single resistor with correct
    impedance_parameters_map and parameters_map
    WHEN: I check if the final parameters elements are correctly set from the
    impedance_parameters_map
    THEN: the set final parameters_map matches the input ones
    """
    analyzed_circuit = generate_analyzed_circuit_two_elements()
    final_parameters_map = analyzed_circuit.parameters_map
    function_r = lambda x, y: y
    function_q = lambda x, y: 1/(x*y)
    impedance_parameters_map = {'R1': (function_r, 1000.),
                                'Q2': (function_q, [1e-6, 0.1])}

    wrong_elements = wrong_match_element_analyzed_circuit_final_parameters(
        impedance_parameters_map, final_parameters_map)
    assert not wrong_elements, (
        'Bad match between non constant elements of the analyzed circuit and '
        + 'the final analysis parameter. ' + wrong_elements + 'not found')

    wrong_parameters = wrong_match_parameter_analyzed_circuit_final_parameters(
        impedance_parameters_map, final_parameters_map)
    assert not wrong_parameters, (
        'Bad match between parameters of the initial circuit and the final '
        + 'analysis parameter. Parameter of element ' + wrong_parameters
        + 'not found')


def test_list_parameters_resistor():
    """Check that the list_parameters() method return a list containing all
    the non-constant parameters inside the parameters_map, (in order of
    apparition in the parameters_map) in the case of a non-constant resistor
    analyzed circuit.

    GIVEN: a valid analyzed circuit with only a non-constant resistor and the
    final results set
    WHEN: I call the function to list the non-constant parameters of the
    analysis
    THEN: the final parameters list is a valid list containg all and only the
    non-constant parameters (in this case just one).
    """
    analyzed_circuit = generate_analyzed_circuit_resistor()
    parameters = analyzed_circuit.list_parameters()
    expected_result = [1000.] #Parameters in order of apparition in the
                              #parameters_map

    caller = 'list_parameters()'
    assert isinstance(parameters, list), (
        'TypeError for ' + caller + '. The output must be a list')
    assert parameters==expected_result, (
        'Bad match for ' + caller + ' between final parameters of the '
        + 'analyzed circuit and its list of parameters.')

def test_list_parameters_capacitor():
    """Check that the list_parameters() method return a list containing all
    the non-constant parameters inside the parameters_map, (in order of
    apparition in the parameters_map) in the case of a constant capacitor
    analyzed circuit

    GIVEN: a valid analyzed circuit with only a constant capacitor and the
    final results set.
    WHEN: I call the function to list the non-constant parameters of the
    analysis
    THEN: the final parameters list is a valid list containg all and only the
    non-constant parameters (in this case the list is empty because the only
    parameter is set constant)
    """
    analyzed_circuit = generate_analyzed_circuit_capacitor()
    parameters = analyzed_circuit.list_parameters()
    expected_result = [] #No parameters since the only present is set constant

    caller = 'list_parameters()'
    assert isinstance(parameters, list), (
        'TypeError for ' + caller + '. The output must be a list')
    assert parameters==expected_result, (
        'Bad match for ' + caller + ' between final parameters of the '
        + 'analyzed circuit and its list of parameters.')

def test_list_parameters_two_elements():
    """Check that the list_parameters() method return a list containing all
    the non-constant parameters inside the parameters_map, (in order of
    apparition in the parameters_map) in the case of a two non-constant
    element analyzed circuit

    GIVEN: a valid analyzed circuit with a non-constant resisitor and a
    non-constant cpe, and the final results set
    WHEN: I call the function to list the non-constant parameters of the
    analysis
    THEN: the final parameters list is a valid list containg all and only the
    non-constant parameters, in order of apparition in the parameters_map.
    """
    analyzed_circuit = generate_analyzed_circuit_two_elements()
    parameters = analyzed_circuit.list_parameters()
    expected_result = [1000., 1e-6, 0.1] #Parameters in order of apparition
                                         #in the parameters_map

    caller = 'list_parameters()'
    assert isinstance(parameters, list), (
        'TypeError for ' + caller + '. The output must be a list')
    assert parameters==expected_result, (
        'Bad match for ' + caller + ' between final parameters of the '
        + 'analyzed circuit and its list of parameters.')

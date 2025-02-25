"""This module containes all the test functions (and the tested help functions
for the tests) of the impedance_analysis.py module.
"""

import pytest
import numpy as np

import sys
from pathlib import Path
sys.path.append(str(Path.cwd().parent))

from generate_impedance import Circuit, AnalisysCircuit
from impedance_analysis import (
    error_function, bounds_definitions, fit, get_constant_parameter_info,
    get_optimized_parameter_info, get_results_info)



def test_error_function_resistor():
    """Check that the output of error_function() is a valid error (a non
    negative float, almost zero if the parameters are correct) if the
    parameters and function are perfectly matching the data of a resistor.

    GIVEN: valid data, correct function and parameters of a resistor. The
    parameters and function match the data
    WHEN: I call the the function to calculate the error between the impedance
    function (with given parameters) and the data
    THEN: the error is a non-negative float, smaller than 1 (thus small).
    """
    impedance = np.array([complex(100,0), complex(100,0), complex(100,0),
                          complex(100,0)])
    frequency = np.array([10, 100, 1000, 10000])
    function_r = lambda x, y: (x[0]+0j) * np.ones(len(y))
    parameters = [100.]
    error = error_function(parameters, impedance, function_r, frequency)
    expected_result = 0.

    assert isinstance(error, float), (
        'TypeError for output of error_function(): the output must be a '
        + 'float, not a ' + str(type(error)))
    assert error>=0, ('ValueError for output of error_function(): the output '
                      + 'must be non-negative')
    assert error<1, ('ValueError output of error_function(): given the '
                     + 'examples, the parameters are set to have a small '
                     + 'error')
    assert error==expected_result, ('ValueError output of error_function(): '
                                    + 'the error is incorrect')

def test_error_function_capacitor():
    """Check that the output of error_function() is a valid error (a non
    negative float, almost zero if the parameters are correct) if the
    parameters and function are correct even if they do not match in value the
    data of a capacitor.

    GIVEN: valid data, correct function and non matching parameters of a
    capacitor
    WHEN: I call the the function to calculate the error between the impedance
    function (with given parameters) and the data
    THEN: the error is a non-negative float, bigger than 1 (thus big)
    """
    impedance = np.array([complex(0,-1000), complex(0,-100), complex(0,-10),
                         complex(0,-1)])
    frequency = np.array([10, 100, 1000, 10000])
    function_c = lambda x, y: 1./(1j*y*2*np.pi*x[0])
    parameters = [2.e-4/(2*np.pi)]
    error = error_function(parameters, impedance, function_c, frequency)
    expected_result = 2.

    assert isinstance(error, float), (
        'TypeError for output of error_function(): the output must be a float, '
        + 'not a ' + str(type(error)))
    assert error>=0, ('ValueError for output of error_function(): the output '
                      + 'must be non-negative')
    assert error>1, ('ValueError output of error_function(): given the '
                     + 'examples, the parameters are set to have'
                     + 'a big error')
    assert error==expected_result, ('ValueError output of error_function(): '
                                    + 'the error is incorrect')

def test_error_function_rc():
    """Check that the output of error_function() is a valid error (a non
    negative float, almost zero if the parameters are correct) if the
    parameters and function are perfectly matching the data of an rc circuit.

    GIVEN: valid data, correct function and parameters of an rc circuit. The
    parameters and functions match the data
    WHEN: I call the the function to calculate the error between the impedance
    function (with given parameters) and the data
    THEN: the error is a non-negative float, smaller than 1 (thus small).
    """
    impedance = np.array([complex(500,-1000), complex(500,-100),
                          complex(500,-10), complex(500,-1)])
    frequency = np.array([10, 100, 1000, 10000])
    function_rc = lambda x, y: ((x[0]+0j) * np.ones(len(y))
                                + 1./(1j*y*2*np.pi*x[1]))
    parameters = [500, 1e-4/(2*np.pi)]
    error = error_function(parameters, impedance, function_rc, frequency)
    expected_result = 0.

    assert isinstance(error, float), (
        'TypeError for output of error_function(): the output must be a '
        + 'float, not a ' + str(type(error)))
    assert error>=0, ('ValueError for output of error_function(): the output '
                      + 'must be non-negative')
    assert error<1, ('ValueError output of error_function(): given the '
                     + 'examples, the parameters are set to have a small '
                     + 'error')
    assert error==expected_result, ('ValueError output of error_function(): '
                                    + 'the error is incorrect')

def test_error_function_zero_q():
    """Check that the output of error_function() raises an Exception with a
    certain message if the circuit contains a divergent point in the function.

    GIVEN: an invalid (zero) q and a valid n in the paramters, and valid data
    WHEN: I call the the function to calculate the error between the impedance
    function (with given parameters) and the data
    THEN: the error function raises an Exception with a message that states
    the division by 0
    """
    impedance = np.array([complex(0,-1000), complex(0,-100),
                          complex(0,-10), complex(0,-1)])
    frequency = np.array([10, 100, 1000, 10000])
    function_q = lambda x, y: 1./(
        x[0]*(y*2*np.pi)**x[1]*np.exp(np.pi/2*x[1]*1j))
    parameters = [0, 1] #First parameter (q) cannot be 0
    with pytest.raises(SystemExit) as excinfo:
        _ = error_function(parameters, impedance, function_q, frequency)
    message = excinfo.value.args[0]

    assert message==('FatalError: FloatingPointError(\'divide by zero '
                     + 'encountered in true_divide\')')


def wrong_element_type_bound_definitions(bounds_list):
    """Return any element inside a dictionary that has not a tuple of length
    2 as a value. Used for testing.

    Parameters
    ----------
    bounds_list : list
        List of all the bounds (tuples).

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

def test_wrong_element_type_bound_empty_list():
    """Check that the the help function to find objects that are not a
    2-length tuples works if there are no bounds.
    If no invalid tuple is detected, the returned list given by the function
    under test is empty.

    GIVEN: an empty list
    WHEN: I check if there are any invalid elements in a list
    THEN: no invalid element is found
    """
    empty_list = []
    wrong_element_type_index = wrong_element_type_bound_definitions(
        empty_list)

    assert not wrong_element_type_index, (
        'TypeError in output of bound_definitions(): the output must be'
        + ' a list of tuples of length 2. Cannot find invalid elements '
        + 'because there are no elements')

def test_wrong_element_type_bound_single_tuple():
    """Check that the the help function to find objects that are not a
    2-length tuples works if there is a valid tuples of bounds.
    If no invalid tuple is detected, the returned list given by the function
    under test is empty.

    GIVEN: a list with one valid tuple
    WHEN: I check if there are any invalid elements in a list
    THEN: no invalid element is found
    """
    one_tuple = [(100., None)]
    wrong_element_type_index = wrong_element_type_bound_definitions(one_tuple)

    assert not wrong_element_type_index, (
        'TypeError in output of bound_definitions(): the output must be'
        + ' a list of tuples of length 2.')

def test_wrong_element_type_bound_many_tuples():
    """Check that the the help function to find objects that are not a
    2-length tuples works if there are many tuples of bounds.
    If no invalid tuple is detected, the returned list given by the function
    under test is empty.

    GIVEN: a list with many valid tuples
    WHEN: I check if there are any invalid elements in a list
    THEN: no invalid element is found
    """
    many_tuples = [(100., None), (1e-10, 1e-4), (1e-10, 1e-6), (0, 1)]
    wrong_element_type_index = wrong_element_type_bound_definitions(
        many_tuples)

    assert not wrong_element_type_index, (
        'TypeError in output of bound_definitions(): the output must be'
        + ' a list of tuples of length 2.')

def test_wrong_element_type_bound_invalid_tuples():
    """Check that the the help function to find objects that are not a
    2-length tuples works if there are three invalid elements in a list of
    four elements.
    If invalid tuples are detected, the returned list contains the position
    of the invalid tuples.

    GIVEN: a list with four elements. Only the last one is a valid tuples
    WHEN: I check if there are any invalid elements in a list
    THEN: the first three invalid elements are the only ones to be detected as
    invalid
    """
    many_tuples = ['(100., None)', 1e-10, (1e-2, 1e3, 1e4), (1e-8, 1e-6)]
    expected_result = [0, 1, 2] #Index of invalid tuples
    wrong_element_type_index = wrong_element_type_bound_definitions(
        many_tuples)

    assert wrong_element_type_index==expected_result, (
        'TypeError in output of bound_definitions(): the output differs from '
        + 'the expected one: ' + expected_result)


def wrong_element_value_bound_definitions(bounds_list):
    """Find the invalid values of the tuples inside the bounds list. Used for
    testing.

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

def test_wrong_element_value_bound_no_elements():
    """Check that the the help function to find objects inside of tuples that
    are not valid bounds works for an empty list.
    If no invalid tuple is detected, the returned string given by the function
    under test is empty.

    GIVEN: an empty list
    WHEN: I check if all the value of the bounds are correct
    THEN: no invalid value is found
    """
    empty_list = []
    wrong_element_value_index = wrong_element_value_bound_definitions(
            empty_list)

    assert not wrong_element_value_index, (
        'StructuralError for ' + wrong_element_value_index + 'of output of '
        + 'bound_definitions(): each element of the output must be a tuple '
        + 'with as first element a non-negative number, and as a second '
        + 'element either \'None\' or a non-negative number bigger than the '
        + 'first element. Cannot find an invalid element because there are no'
        + 'elements')

def test_wrong_element_value_bound_single_element():
    """Check that the the help function to find objects inside of tuples that
    are not valid bounds works for a list with one valid element.
    Each tuple must have as first element a non-negative number, and as a
    second element either None-type or a non-negative number bigger than the '
    first element.
    If no invalid tuple is detected, the returned string given by the function
    under test is empty.

    GIVEN: a list with valid tuple
    WHEN: I check if all the value of the bounds are correct
    THEN: no invalid value is found
    """
    single_element = [(10, 1e5)]
    wrong_element_value_index = wrong_element_value_bound_definitions(
            single_element)

    assert not wrong_element_value_index, (
        'StructuralError for ' + wrong_element_value_index + 'of output of '
        + 'bound_definitions(): each element of the output must be a tuple '
        + 'with as first element a non-negative number, and as a second '
        + 'element either \'None\' or a non-negative number bigger than the '
        + 'first element')

def test_wrong_element_value_bound_many_elements():
    """Check that the the help function to find objects inside of tuples that
    are not valid bounds works for a list with three valid elements.
    Each tuple must have as first element a non-negative number, and as a
    second element either None-type or a non-negative number bigger than the '
    first element.
    If no invalid tuple is detected, the returned string given by the function
    under test is empty.

    GIVEN: a list with three valid tuples
    WHEN: I check if all the value of the bounds are correct
    THEN: no invalid value is found
    """
    many_elements = [(22, 345), (1., 10), (1e-2, 1e3)]
    wrong_element_value_index = wrong_element_value_bound_definitions(
            many_elements)

    assert not wrong_element_value_index, (
        'StructuralError for ' + wrong_element_value_index + 'of output of '
        + 'bound_definitions(): each element of the output must be a tuple '
        + 'with as first element a non-negative number, and as a second '
        + 'element either \'None\' or a non-negative number bigger than the '
        + 'first element')

def test_wrong_element_value_bound_invalid_elements():
    """Check that the the help function to find objects inside of tuples that
    are not valid bounds works for a list with four invalid elements.
    Each tuple must have as first element a non-negative number, and as a
    second element either None-type or a non-negative number bigger than the '
    first element.
    If invalid tuples are detected, the returned string contains the positions
    of the invalid values.

    GIVEN: a list with four invalid tuples
    WHEN: I check if all the value of the bounds are correct
    THEN: all the tuples are detected as invalid
    """
    many_elements = [('a', None), #Invalid for the string object
                     (1., 1j), #Invalid for the comples second object
                     (10., 1), #Invalid because first number is bigger than
                               #the second one
                     (-1, 10)] #Invalid because first number is negative
    expected_result = ('[0] (first element), [1] (second element), '
                       + '[2] (second element), [3] (first element), ')
    wrong_element_value_index = wrong_element_value_bound_definitions(
            many_elements)

    assert wrong_element_value_index==expected_result, (
        'StructuralError for ' + wrong_element_value_index + 'of output of '
        + 'bound_definitions(): the output differs from the expected one: '
        + str(expected_result))


def count_q(elements_bound, i_element):
    """Count how many Q elements there are before a certain element. Used for
    testing.

    Parameters
    ----------
    elements_bound : list
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

def test_count_Q_no_q_elements():
    """Check that the the help function to find how many Q elements there are
    in a element list before a certain element works if there are only non-Q
    elements.

    GIVEN: a valid list of three elements. None of them is a Q elements
    WHEN: I call the help function to count the number of Q elements
    THEN: count of Q is 0, as it should be
    """
    no_q = ['R1', 'C2', 'R3']
    counting_element = 2 #I.e. R3
    number_of_q = count_q(no_q, counting_element)
    expected_result = 0

    assert number_of_q==expected_result, ('Value error for the q_count() '
                                          + 'function: incorrect result')

def test_count_Q_one_q_elements():
    """Check that the the help function to find how many Q elements there are
    in a element list before a certain element works if there is one Q element
    (and it is before the certain element).

    GIVEN: a valid list of three elements and index of the counting element.
    One of them is a Q elements
    WHEN: I call the help function to count the number of Q elements
    THEN: count of Q is 1, as it should be
    """
    no_q = ['R1', 'Q2', 'R3']
    counting_element = 2 #I.e. R3
    number_of_q = count_q(no_q, counting_element)
    expected_result = 1

    assert number_of_q==expected_result, ('Value error for the q_count() '
                                          + 'function: incorrect result')

def test_count_Q_two_q_elements():
    """Check that the the help function to find how many Q elements there are
    in a element list before a certain element works if there are three
    Q elements, but only two are before the certain element.

    GIVEN: a valid list of three elements and index of the counting element.
    None of them is a Q elements
    WHEN: I call the help function to count the number of Q elements
    THEN: count of Q is 2, as it should be
    """
    no_q = ['R1', 'Q2', 'Q3', 'C4', 'R5', 'Q6']
    counting_element = 3 #I.e. C4
    number_of_q = count_q(no_q, counting_element)
    expected_result = 2

    assert number_of_q==expected_result, ('Value error for the q_count() '
                                          + 'function: incorrect result')

def test_count_Q_one_q_element_after():
    """Check that the the help function to find how many Q elements there are
    in a element list before a certain element works if there is a Q element,
    but is after the certain element.

    GIVEN: a valid list of three elements, but the index of the counting
    element is before the one of the Q element
    WHEN: I call the help function to count the number of Q elements
    THEN: count of Q is 0, as it should be
    """
    no_q = ['R1', 'R2', 'Q3']
    counting_element = 1
    number_of_q = count_q(no_q, counting_element)
    expected_result = 0

    assert number_of_q==expected_result, ('Value error for the q_count() '
                                          + 'function: incorrect result')


def bad_match_bound_definitions_elements_list(elements_bound, bounds_list):
    """Find the invalid correspondance between a single element and its bound.
    Used for testing.

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
                wrong_match_index += '[' + str(i+1) + '] (second element), '
    return wrong_match_index

def test_bad_match_bound_no_elements():
    """Check that the the help function to find if the elements lists and the
    bound list have a bad match works on two empty lists.
    Bound for R, C or Q must have a positive umber as first element, while
    for n the second parameter must not be bigger than 1.
    If no invalid match is detected, the returned string given by the function
    under test is empty.

    GIVEN: two empty lists
    WHEN: I call the help function to find if there is a bad match between
    bounds and elements
    THEN: no bad match is found
    """
    element_list = []
    bound_list = []
    wrong_match_index = bad_match_bound_definitions_elements_list(
        element_list, bound_list)

    assert not wrong_match_index, (
        'StructuralError for elements ' + wrong_match_index + ' there must '
        + 'be a correspondace between each element of the element list and '
        + 'the correspective bound. Bound for R, C or Q must have a positive '
        + 'unber as first element, while for n the second parameter must not '
        + 'be bigger than 1. CAnnot find bad match because there are no '
        + 'elements')

def test_bad_match_bound_one_element():
    """Check that the the help function to find if the elements lists and the
    bound list have a bad match works on a single element list.
    Bound for R, C or Q must have a positive umber as first element, while
    for n the second parameter must not be bigger than 1.
    If no invalid match is detected, the returned string given by the function
    under test is empty.

    GIVEN: an element list and a bound list with one valid tuple each
    WHEN: I call the help function to find if there is a bad match between
    bounds and elements
    THEN: no bad match is found
    """
    element_list = ['R1']
    bound_list = [(1, 1000)]
    wrong_match_index = bad_match_bound_definitions_elements_list(
        element_list, bound_list)

    assert not wrong_match_index, (
        'StructuralError for elements ' + wrong_match_index + ' there must '
        + 'be a correspondace between each element of the element list and '
        + 'the correspective bound. Bound for R, C or Q must have a positive '
        + 'unber as first element, while for n the second parameter must not '
        + 'be bigger than 1. CAnnot find bad match because there are no '
        + 'elements')

def test_bad_match_bound_many_element():
    """Check that the the help function to find if the elements lists and the
    bound list have a bad match works on many elements.
    Bound for R, C or Q must have a positive umber as first element, while
    for n the second parameter must not be bigger than 1.
    If no invalid match is detected, the returned string given by the function
    under test is empty.

    GIVEN: an element list and a bound list with three and four valid tuples,
    respectively, which are also matching
    WHEN: I call the help function to find if there is a bad match between
    bounds and elements
    THEN: no bad match is found
    """
    element_list = ['R1', 'Q2', 'C3']
    bound_list = [(1, 10), (1e-6, 1), (0.1, 0.5), (1e-10, 1e-3)]
    wrong_match_index = bad_match_bound_definitions_elements_list(
        element_list, bound_list)

    assert not wrong_match_index, (
        'StructuralError for elements ' + wrong_match_index + ' there must '
        + 'be a correspondace between each element of the element list and '
        + 'the correspective bound. Bound for R, C or Q must have a positive '
        + 'unber as first element, while for n the second parameter must not '
        + 'be bigger than 1. CAnnot find bad match because there are no '
        + 'elements')

def test_bad_match_bound_bad_match():
    """Check that the the help function to find if the elements lists and the
    bound list have a bad match works on lists with two bad matches.
    Bound for R, C or Q must have a positive umber as first element, while
    for n the second parameter must not be bigger than 1.
    If no invalid match is detected, the returned string given by the function
    under test is empty.

    GIVEN: an element list and a bound list with three and four valid elements
    each, but ony one each is matching (the second ones)
    WHEN: I call the help function to find if there is a bad match between
    bounds and elements
    THEN: the two bad match are detected
    """
    element_list = ['R1', 'R2', 'Q3']
    bound_list = [(0, 1), (10, 1000), (0, 100), (0-5, 10)]
    expected_result = ('[0] (first element), [2] (first element), [3] (second '
                      + 'element), ')
    wrong_match_index = bad_match_bound_definitions_elements_list(
        element_list, bound_list)

    assert wrong_match_index==expected_result, (
        'StructuralError for elements ' + wrong_match_index + ' there must '
        + 'be a correspondace between each element of the element list and '
        + 'the correspective bound. Bound for R, C or Q must have a positive '
        + 'unber as first element, while for n the second parameter must not '
        + 'be bigger than 1. CAnnot find bad match because there are no '
        + 'elements')


def test_bound_definitions_single_element():
    """Check that the output of bound_definitions() is a valid list of tuple
    for bound conditions in the case of a single resistor element.

    GIVEN: a valid list of elements containing just one resistor-like element
    WHEN: I call the function to get the bounds definition of a list of
    elements
    THEN: the output is a proper list of tuples for the input element
    """
    element_list = ['R1']
    bounds_list = bounds_definitions(element_list)

    assert isinstance(bounds_list, list), (
        'TypeError in the output: it must be a list,  not a '
        + str(type(bounds_list)))
    assert bounds_list, ('StructuralError in the output: it cannot be empty')
    wrong_element_type_index = wrong_element_type_bound_definitions(
        bounds_list)
    assert not wrong_element_type_index, ('TypeError: the output must be a '
                                          + 'list of tuples of length 2')
    wrong_element_value_index = wrong_element_value_bound_definitions(
        bounds_list)
    assert not wrong_element_value_index, (
        'StructuralError for ' + wrong_element_value_index + ': each element '
        + 'of the output must be a tuple with as first element a non-negative'
        + 'number, and as a second element either \'None\' or a non-negative '
        + 'number bigger than the first element')

    number_of_q = count_q(element_list, len(element_list)+1)
    consistent_condition = ((len(element_list)+number_of_q)==len(bounds_list))
    assert consistent_condition, (
        'StructuralError: the list of bounds must have a proper length related '
        + 'to the elements list. For each element but for Q 1 element is '
        + 'equal to bound. For Q case is 1 element to 2 bounds.')
    wrong_match_index = bad_match_bound_definitions_elements_list(
        element_list, bounds_list)
    assert not wrong_match_index, (
        'StructuralError for elements ' + wrong_match_index + ': there must '
        + 'be a correspondace between each element of the element list \''
        + str(element_list) + '\' and the correspective bound. Bound for R, '
        + 'C or Q must have a positive number as first element, while for n'
        + 'the second parameter must not be bigger than 1')

def test_bound_definitions_two_elements():
    """Check that the output of bound_definitions() is a valid list of tuple
    for bound conditions in the case of a resistor and capacitor elements.

    GIVEN: a valid list of elements containing one resistor-like element and
    one capacitor-like element
    WHEN: I call the function to get the bounds definition of a list of
    elements
    THEN: the output is a proper list of tuples for the input elements
    """
    element_list = ['R1', 'C2']
    bounds_list = bounds_definitions(element_list)

    assert isinstance(bounds_list, list), (
        'TypeError in the output: it must be a list,  not a '
        + str(type(bounds_list)))
    assert bounds_list, ('StructuralError in the output: it cannot be empty')
    wrong_element_type_index = wrong_element_type_bound_definitions(
        bounds_list)
    assert not wrong_element_type_index, ('TypeError: the output must be a '
                                          + 'list of tuples of length 2')
    wrong_element_value_index = wrong_element_value_bound_definitions(
        bounds_list)
    assert not wrong_element_value_index, (
        'StructuralError for ' + wrong_element_value_index + ': each element '
        + 'of the output must be a tuple with as first element a non-negative'
        + 'number, and as a second element either \'None\' or a non-negative '
        + 'number bigger than the first element')

    number_of_q = count_q(element_list, len(element_list)+1)
    consistent_condition = ((len(element_list)+number_of_q)==len(bounds_list))
    assert consistent_condition, (
        'StructuralError: the list of bounds must have a proper length related '
        + 'to the elements list. For each element but for Q 1 element is '
        + 'equal to bound. For Q case is 1 element to 2 bounds')
    wrong_match_index = bad_match_bound_definitions_elements_list(
        element_list, bounds_list)
    assert not wrong_match_index, (
        'StructuralError for elements ' + wrong_match_index + ': there must '
        + 'be a correspondace between each element of the element list \''
        + str(element_list) + '\' and the correspective bound. Bound for R, '
        + 'C or Q must have a positive number as first element, while for n'
        + 'the second parameter must not be bigger than 1')

def test_bound_definitions_many_elements():
    """Check that the output of bound_definitions() is a valid list of tuple
    for bound conditions in the case of many elements.

    GIVEN: a valid list of elements containing all types of elements
    WHEN: I call the function to get the bounds definition of a list of
    elements
    THEN: the output is a proper list of tuples for the input elements
    """
    element_list = ['R1', 'C2', 'Q3', 'R4']
    bounds_list = bounds_definitions(element_list)

    assert isinstance(bounds_list, list), (
        'TypeError in the output: it must be a list,  not a '
        + str(type(bounds_list)))
    assert bounds_list, ('StructuralError in the output: it cannot be empty')
    wrong_element_type_index = wrong_element_type_bound_definitions(
        bounds_list)
    assert not wrong_element_type_index, ('TypeError: the output must be a '
                                          + 'list of tuples of length 2')
    wrong_element_value_index = wrong_element_value_bound_definitions(
        bounds_list)
    assert not wrong_element_value_index, (
        'StructuralError for ' + wrong_element_value_index + ': each element '
        + 'of the output must be a tuple with as first element a non-negative'
        + 'number, and as a second element either \'None\' or a non-negative '
        + 'number bigger than the first element')

    number_of_q = count_q(element_list, len(element_list)+1)
    consistent_condition = ((len(element_list)+number_of_q)==len(bounds_list))
    assert consistent_condition, (
        'StructuralError: the list of bounds must have a proper length related '
        + 'to the elements list. For each element but for Q 1 element is '
        + 'equal to bound. For Q case is 1 element to 2 bounds.')
    wrong_match_index = bad_match_bound_definitions_elements_list(
        element_list, bounds_list)
    assert not wrong_match_index, (
        'StructuralError for elements ' + wrong_match_index + ': there must '
        + 'be a correspondace between each element of the element list \''
        + str(element_list) + '\' and the correspective bound. Bound for R, '
        + 'C or Q must have a positive number as first element, while for n'
        + 'the second parameter must not be bigger than 1')

def test_bound_definitions_no_elements():
    """Check that the output of bound_definitions() is a valid list of tuple
    for bound conditions in the case of an invalid list of zero elements.

    GIVEN: an invalid empty list of elements
    WHEN: I call the function to get the bounds definition of a list of
    elements
    THEN: the output is an invalid list of bounds: an empty one
    """
    element_list = []
    bounds_list = bounds_definitions(element_list)

    assert isinstance(bounds_list, list), (
        'TypeError in the output: it must be a list,  not a '
        + str(type(bounds_list)))
    assert not bounds_list, ('StructuralError in the output: it is expected '
                             + 'to be empty')
    wrong_element_type_index = wrong_element_type_bound_definitions(
        bounds_list)
    assert not wrong_element_type_index, ('TypeError: the output must be a '
                                          + 'list of tuples of length 2')
    wrong_element_value_index = wrong_element_value_bound_definitions(
        bounds_list)
    assert not wrong_element_value_index, (
        'StructuralError for ' + wrong_element_value_index + ': each element '
        + 'of the output must be a tuple with as first element a non-negative'
        + 'number, and as a second element either \'None\' or a non-negative '
        + 'number bigger than the first element')

    number_of_q = count_q(element_list, len(element_list)+1)
    consistent_condition = ((len(element_list)+number_of_q)==len(bounds_list))
    assert consistent_condition, (
        'StructuralError: the list of bounds must have a proper length related '
        + 'to the elements list. For each element but for Q 1 element is '
        + 'equal to bound. For Q case is 1 element to 2 bounds.')
    wrong_match_index = bad_match_bound_definitions_elements_list(
        element_list, bounds_list)
    assert not wrong_match_index, (
        'StructuralError for elements ' + wrong_match_index + ': there must '
        + 'be a correspondace between each element of the element list \''
        + str(element_list) + '\' and the correspective bound. Bound for R, '
        + 'C or Q must have a positive number as first element, while for n'
        + 'the second parameter must not be bigger than 1')


def outside_bound_optimized_parameters(optimized_parameters, bounds_list):
    """Find the optimized parameters that are outside the correspondant
    bounds. Used for testing.

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

def test_outside_bounds_empty():
    """Check that the the help function to find if there are optimized
    parameters outside the fi bounds (tuples) works for a no parameters or
    bounds case.
    If no invalid value is detected, the returned string given by the function
    under test is empty.

    GIVEN: two empty lists
    WHEN: I call the function to chek if any optimized parameters are outside
    their own bounds
    THEN: no invalid parameter is found
    """
    optimized_parameters = []
    bounds = []
    outside_bound_index = outside_bound_optimized_parameters(
        optimized_parameters, bounds)

    assert not outside_bound_index, (
        'StructuralError for optimized parametrs with bound(s) '
        + outside_bound_index + ': the optimized parameters must be within '
        + 'their bounds: ' + str(bounds))

def test_outside_bounds_one_parameter():
    """Check that the help function to find if there are optimized parameters
    outside the bounds (tuples) works for a resistor-like parameter with
    proper bounds.
    If no invalid value is detected, the returned string given by the function
    under test is empty.

    GIVEN: a valid optimized parameter for a resistor within the bounds
    WHEN: I call the function to chek if any optimized parameters are outside
    their own bounds
    THEN: no invalid parameter is found
    """
    optimized_parameters = [1229.3]
    bounds = [(10, 1e5)]
    outside_bound_index = outside_bound_optimized_parameters(
        optimized_parameters, bounds)

    assert not outside_bound_index, (
        'StructuralError for optimized parametrs with bound(s) '
        + outside_bound_index + ': the optimized parameters must be within '
        + 'their bounds: ' + str(bounds))

def test_outside_bounds_many_parameters():
    """Check that the help function to find if there are optimized
    parameters outside the bounds (tuples) works for four parameters with
    proper bounds.
    If no invalid value is detected, the returned string given by the function
    under test is empty.

    GIVEN: four valid optimized parameters within the bounds
    WHEN: I call the function to chek if any optimized parameters are outside
    their own bounds
    THEN: no invalid parameter is found
    """
    optimized_parameters = [1.2e-7, 11297.45, 7.8e-6, 0.89]
    bounds = [(1e-10, 1e-4), (100., None), (1e-10, 1e-4), (0, 1)]
    outside_bound_index = outside_bound_optimized_parameters(
        optimized_parameters, bounds)

    assert not outside_bound_index, (
        'StructuralError for optimized parametrs with bound(s) '
        + outside_bound_index + ': the optimized parameters must be within '
        + 'their bounds: ' + str(bounds))

def test_outside_bounds_invalid_parameters():
    """Check that the help function to find if there are optimized
    parameters outside the bounds (tuples) works for three parameters with
    proper bounds, of which only two are within the bounds.
    If invalid values are detected, the returned string contains the positions
    of the parameters out of bound.

    GIVEN: three valid optimized parameters, of which the second one is the
    only one otside the bounds (lower than the lower bound)
    WHEN: I call the function to chek if any optimized parameters are outside
    their own bounds
    THEN: no invalid parameter is found
    """
    optimized_parameters = [8.4e-7, 0.002, 3950.5] #Second element invalid
                                                   #because lower than its
                                                   #lower bound
    bounds = [(1e-10, 1e-4), (1., None), (100., None)]
    expected_result = '[1] (first element), '
    outside_bound_index = outside_bound_optimized_parameters(
        optimized_parameters, bounds)

    assert outside_bound_index==expected_result, (
        'StructuralError for optimized parametrs with bound(s) '
        + outside_bound_index + ': the optimized parameters must be within '
        + 'their bounds: ' + str(bounds))


def generate_pre_fit_circuit_resistor():
    """Generate an analyzed circuit of a resistor before a fit."""
    diagram = '(R1)'
    function_r = lambda x, y: (x[0]+0j) * np.ones(len(y))
    parameters = {'R1': 200.}
    circuit_resistor = AnalisysCircuit(diagram, impedance=function_r,
                                       parameters_map=parameters)
    return circuit_resistor

@pytest.fixture
def pre_fit_circuit_resistor():
    """Fixture for a pre-fit resistor-like AnalisysCircuit instance."""
    return generate_pre_fit_circuit_resistor()

def generate_post_fit_circuit_resistor():
    """Generate a data set of a resistor and fit them using a proper analyzed
    circuit. Return the analyzed circuit after the fit
    """
    signal = np.array([complex(100,0), complex(100,0), complex(100,0),
                       complex(100,0)])
    frequency = np.array([10, 100, 1000, 10000])
    analyzed_circuit = generate_pre_fit_circuit_resistor()
    _ = fit(frequency, signal, analyzed_circuit)
    return analyzed_circuit

@pytest.fixture
def post_fit_circuit_resistor():
    """Fixture for a post-fit resistor-like AnalisysCircuit instance."""
    return generate_post_fit_circuit_resistor()

def generate_fit_results_resistor():
    """Generate a data set of a resistor and fit them using a proper analyzed
    circuit. Return the fit results.
    """
    signal = np.array([complex(100,0), complex(100,0), complex(100,0),
                        complex(100,0)])
    frequency = np.array([10, 100, 1000, 10000])
    analyzed_circuit = generate_pre_fit_circuit_resistor()
    fit_results = fit(frequency, signal, analyzed_circuit)
    return fit_results

@pytest.fixture
def fit_results_resistor():
    """Fixture for the fit results of a resistor-like Circuit."""
    return generate_fit_results_resistor()

def test_fit_resistor(pre_fit_circuit_resistor, post_fit_circuit_resistor,
                      fit_results_resistor):
    """Check that the fit() function returns proper values of the fit, given
    a resistor-like analyzed circuit and the correspective data. The initial
    parameter in the circuit is twice the 'true' one (that is the one that
    would properly describe the data).
    Have proper values means that all the non-constant element names in the
    analyzed circuit before and after the fit are the same, and that the
    optimized parameters are the same of the ones in the post fit analyzed
    circuit. At last, the parameters must be inside the fit bounds.

    GIVEN: a valid analyzed circuit (resistor-like) and valid data initial
    parameters, element list and impedance function
    WHEN: I call the fit function to get the optimized parameters
    THEN: the optimized parameters are all the expected ones, that well fit
    the data
    """
    bounds = [(10, None)]
    optimized_parameters = fit_results_resistor[0]
    expected_parameters = [100.] #Expected value of the fitted resistance

    assert isinstance(optimized_parameters, np.ndarray), (
        'TypeError for parameters in fit() . It must be a list')
    assert isinstance(post_fit_circuit_resistor.parameters_map, dict), (
        'TypeError for post fit parameters map. It must be a dictionary')

    pre_fit_elements = list(pre_fit_circuit_resistor.parameters_map.keys())
    post_fit_elements = list(post_fit_circuit_resistor.parameters_map.keys())
    assert np.all(pre_fit_elements==post_fit_elements), (
        'StructuralError between elements list in parameter map pre and post '
        + 'fit.')

    optimized_parameters_circuit = post_fit_circuit_resistor.list_parameters()
    length_equality = (len(optimized_parameters_circuit)==len(
        optimized_parameters))
    assert length_equality, (
        'StructuralError: wrong number of optimized parameters \''
        + str(len(optimized_parameters)) + '\' (with number of initial '
        + 'parameters ' + str(len(post_fit_circuit_resistor.list_parameters()))
        + ') in output of fit(). They must be the same')
    assert set(optimized_parameters_circuit)==set(optimized_parameters), (
        'StructuralError in fit(): different optimized parameters between '
        + 'the ones set into the analyzed circuit and given from the fit() '
        + 'function')

    outside_bound_index = outside_bound_optimized_parameters(
        optimized_parameters, bounds)
    assert not outside_bound_index, (
        'StructuralError for optimized parametrs with bound(s) '
        + outside_bound_index + 'in output of fit(): the optimized parameters '
        + 'must be within their bounds: ' + str(bounds))
    assert np.all(optimized_parameters==expected_parameters), (
        'ValueError: optimized parameters differ from the expected ones')

def generate_pre_fit_circuit_rc():
    """Generate an analyzed circuit of a resistor and a capacitor in series
    before a fit.
    """
    diagram = '(R1C2)'
    function_rc_series = lambda x, y: ((x[0]+0j) * np.ones(len(y))
                                      + 1./(1j*y*2*np.pi*x[1]))
    parameters = {'R1': 200., 'C2': 1e-7}
    circuit_rc = AnalisysCircuit(diagram, impedance=function_rc_series,
                                 parameters_map=parameters)
    return circuit_rc

@pytest.fixture
def pre_fit_circuit_rc():
    """Fixture for a pre-fit RC-like AnalisysCircuit instance."""
    return generate_pre_fit_circuit_rc()

def generate_post_fit_circuit_rc():
    """Generate a data set of a resistor and a capacitor in series and fit
    them using a proper analyzed circuit. Return the analyzed circuit after
    the fit
    """
    signal = np.array([complex(1398.2675,-30597.282), complex(1183,-3053.53),
                       complex(1212.,-304.15), complex(1196.5468,-35.643)])
    frequency = np.array([10, 100, 1000, 10000])
    analyzed_circuit = generate_pre_fit_circuit_rc()
    _ = fit(frequency, signal, analyzed_circuit)
    return analyzed_circuit

@pytest.fixture
def post_fit_circuit_rc():
    """Fixture for a post-fit RC-like AnalisysCircuit instance."""
    return generate_post_fit_circuit_rc()

def generate_fit_results_rc():
    """Generate a data set of a resistor and a capacitor in series and fit
    them using a proper analyzed circuit. Return the fit results.
    """
    signal = np.array([complex(1398.2675,-30597.282), complex(1183,-3053.53),
                       complex(1212.,-304.15), complex(1196.5468,-35.643)])
    frequency = np.array([10, 100, 1000, 10000])
    analyzed_circuit = generate_pre_fit_circuit_rc()
    fit_results = fit(frequency, signal, analyzed_circuit)
    return fit_results

@pytest.fixture
def fit_results_rc():
    """Fixture for the fit results of an RC-like Circuit."""
    return generate_fit_results_rc()

def test_fit_rc_series(pre_fit_circuit_rc, post_fit_circuit_rc,
                       fit_results_rc):
    """Check that the fit() function returns proper values of the fit, given
    a rc-series-like analyzed circuit and the correspective data. The initial
    parameters in the circuit are abount one order of magnitude different of
    'true' ones (that is the one that would properly describe the data).
    Have a proper values means that all the non-constant element names in the
    analyzed circuit before and after the fit are the same, and that the
    optimized parameters are the same of the ones in the post fit analyzed
    circuit. At last, the parameters must be inside the fit bounds.

    GIVEN: a valid analyzed circuit (RC-series-like) and valid data initial
    parameters, element list and impedance function
    WHEN: I call the fit function to get the optimized parameters
    THEN: the optimized parameters are all the expected ones, that well fit
    the data
    """
    bounds = [(10, None), (1e-9, None)]
    optimized_parameters = fit_results_rc[0]
    expected_parameters = [1200.6, 5.2e-7] #Expected value of the fitted rc

    assert isinstance(optimized_parameters, np.ndarray), (
        'TypeError for parameters in fit() . It must be a list')
    assert isinstance(post_fit_circuit_rc.parameters_map, dict), (
        'TypeError for post fit parameters map. It must be a dictionary')

    pre_fit_elements = list(pre_fit_circuit_rc.parameters_map.keys())
    post_fit_elements = list(post_fit_circuit_rc.parameters_map.keys())
    assert np.all(pre_fit_elements==post_fit_elements), (
        'StructuralError between elements list in parameter map pre and post '
        + 'fit.')

    optimized_parameters_circuit = post_fit_circuit_rc.list_parameters()
    length_equality = (len(optimized_parameters_circuit)==len(
        optimized_parameters))
    assert length_equality, (
        'StructuralError: wrong number of optimized parameters \''
        + str(len(optimized_parameters)) + '\' (with number of initial '
        + 'parameters ' + str(len(post_fit_circuit_rc.list_parameters()))
        + ') in output of fit(). They must be the same')
    assert set(optimized_parameters_circuit)==set(optimized_parameters), (
        'StructuralError in fit(): different optimized parameters between the '
        + 'ones set into the analyzed circuit and given from the fit() '
        + 'function ')

    outside_bound_index = outside_bound_optimized_parameters(
        optimized_parameters, bounds)
    assert not outside_bound_index, (
        'StructuralError for optimized parametrs with bound(s) '
        + outside_bound_index + 'in output of fit(): the optimized parameters '
        + 'must be within their bounds: ' + str(bounds))
    optimized_parameters_rounded = [round(optimized_parameters[0], 1),
                                    round(optimized_parameters[1], 8)]
    assert np.all(optimized_parameters_rounded==expected_parameters), (
        'ValueError: optimized parameters differ from the expected ones')

def generate_pre_fit_circuit_rq():
    """Generate an analyzed circuit of a resistor and a cpe in parallel before
    a fit.
    """
    diagram = '[R1Q2]'
    function_rq_parallel = lambda x, y: 1./(1./((500.+0j) * np.ones(len(y))) +
        (x[0]*(y*2*np.pi)**x[1]*np.exp(np.pi/2*x[1]*1j)))
    parameters = {'Q2': [5e-6, 0.95]}
    circuit_rq = AnalisysCircuit(diagram, impedance=function_rq_parallel,
                                 parameters_map=parameters)
    return circuit_rq

@pytest.fixture
def pre_fit_circuit_rq():
    """Fixture for a pre-fit RQ-like AnalisysCircuit instance."""
    return generate_pre_fit_circuit_rq()

def generate_post_fit_circuit_rq():
    """Generate a data set of a resistor and a cpe in parallel and fit
    them using a proper analyzed circuit. Return the analyzed circuit after
    the fit
    """
    signal = np.array([
        complex(499.93298,2.91446593), complex(497.440942,-4.6390736),
        complex(499.67858,-13.8646), complex(452.5068562,-108.554184),
        complex(120.7550,-177.1707253), complex(6.985519494,-31.0678),
        complex(0.6873635497,-3.97560), complex(0.08247718,-0.5019773)])
    frequency = np.array([0.1, 1, 10, 100, 1000, 1e4, 1e5, 1e6])
    analyzed_circuit = generate_pre_fit_circuit_rq()
    _ = fit(frequency, signal, analyzed_circuit)
    return analyzed_circuit

@pytest.fixture
def post_fit_circuit_rq():
    """Fixture for a post-fit RQ-like AnalisysCircuit instance."""
    return generate_post_fit_circuit_rq()

def generate_fit_results_rq():
    """Generate a data set of a resistor and cpe in parallel and fit them
    using a proper analyzed circuit. Return the fit results.
    """
    signal = np.array([
        complex(499.93298,2.91446593), complex(497.440942,-4.6390736),
        complex(499.67858,-13.8646), complex(452.5068562,-108.554184),
        complex(120.7550,-177.1707253), complex(6.985519494,-31.0678),
        complex(0.6873635497,-3.97560), complex(0.08247718,-0.5019773)])
    frequency = np.array([0.1, 1, 10, 100, 1000, 1e4, 1e5, 1e6])
    analyzed_circuit = generate_pre_fit_circuit_rq()
    fit_results = fit(frequency, signal, analyzed_circuit)
    return fit_results

@pytest.fixture
def fit_results_rq():
    """Fixture for the fit results of an RQ-like Circuit."""
    return generate_fit_results_rq()

def test_fit_rq_parallel(pre_fit_circuit_rq, post_fit_circuit_rq,
                         fit_results_rq):
    """Check that the fit() function returns proper values of the fit, given
    an rq-parallel-like analyzed circuit and the correspective data. The
    parameter of the resistor is set constant (at the correct value), while
    the initial parameters of the cpe are 5 times the correct one for q and
    5% more for the ideality factor.
    Have a proper values means that all the non-constant element names in the
    analyzed circuit before and after the fit are the same, and that the
    optimized parameters are the same of the ones in the post fit analyzed
    circuit. At last, the parameters must be inside the fit bounds.

    GIVEN: a valid analyzed circuit (RQ-like) and valid data initial
    parameters, element list and impedance function
    WHEN: the fit function is called
    THEN: the first argument of the output of fit() is a proper parameter list
    """
    bounds = [(1e-9, None), (0, 1)]
    optimized_parameters = fit_results_rq[0]
    expected_parameters = [1.5e-6, 0.9] #Expected value of the fitted rc

    assert isinstance(optimized_parameters, np.ndarray), (
        'TypeError for parameters in fit() . It must be a list')
    assert isinstance(post_fit_circuit_rq.parameters_map, dict), (
        'TypeError for post fit parameters map. It must be a dictionary')

    pre_fit_elements = list(pre_fit_circuit_rq.parameters_map.keys())
    post_fit_elements = list(post_fit_circuit_rq.parameters_map.keys())
    assert np.all(pre_fit_elements==post_fit_elements), (
        'StructuralError between elements list in parameter map pre and post '
        + 'fit.')

    optimized_parameters_circuit = post_fit_circuit_rq.list_parameters()
    length_equality = (len(optimized_parameters_circuit)==len(
        optimized_parameters))
    assert length_equality, (
        'StructuralError: wrong number of optimized parameters \''
        + str(len(optimized_parameters)) + '\' (with number of initial '
        + 'parameters ' + str(len(post_fit_circuit_rq.list_parameters()))
        + ') in output of fit(). They must be the same')
    assert set(optimized_parameters_circuit)==set(optimized_parameters), (
        'StructuralError in fit(): different optimized parameters between the '
        + 'ones set into the analyzed circuit and given from the fit() '
        + 'function')

    outside_bound_index = outside_bound_optimized_parameters(
        optimized_parameters, bounds)
    assert not outside_bound_index, (
        'StructuralError for optimized parametrs with bound(s) '
        + outside_bound_index + 'in output of fit(): the optimized parameters '
        + 'must be within their bounds: ' + str(bounds))
    optimized_parameters_rounded = [round(optimized_parameters[0], 7),
                                    round(optimized_parameters[1], 1)]
    assert np.all(optimized_parameters_rounded==expected_parameters), (
        'ValueError: optimized parameters differ from the expected ones')

def generate_fit_results_bad_parameters():
    """Generate a data set of a resistor and a capacitor in series and fit
    them using an analyzed circuit with correct circuit diagram but parameters
    that differs too much. Return the fit results.
    """
    signal = np.array([complex(60.05,-1591.), complex(48.912082,-158.71475),
                       complex(50.29982,-15.8523), complex(49.6478,-1.79834)])
    frequency = np.array([10, 100, 1000, 10000])
    analyzed_circuit = generate_pre_fit_circuit_rc()
    fit_results = fit(frequency, signal, analyzed_circuit)
    return fit_results

@pytest.fixture
def fit_results_bad_parameters():
    """Fixture for the fit results of an RC-like Circuit with parameters too
    much different.
    """
    return generate_fit_results_bad_parameters()

def test_fit_bad_parameters(fit_results_bad_parameters):
    """Check that the fit() function fails to return proper values of the fit
    if there are few points and the initial parameters are too far from the
    'true' ones.

    GIVEN: a valid analyzed circuit (RC-series-like) but data that belongs to
    a circuit with parameters of few order of magnitude different. Also the
    data points are not many (just 4)
    WHEN: I call the fit function to get the optimized parameters
    THEN: there is one optimized parameter that do not fit the data
    """
    bounds = [(10, None), (1e-9, None)]
    optimized_parameters = fit_results_bad_parameters[0]
    expected_parameters = [10.0, 1e-5] #Expected value of the fitted rc. The
                                       #first one is different from the
                                       #correct one (that fits the data): 50.0

    assert isinstance(optimized_parameters, np.ndarray), (
        'TypeError for parameters in fit() . It must be a list')
    outside_bound_index = outside_bound_optimized_parameters(
        optimized_parameters, bounds)
    assert not outside_bound_index, (
        'StructuralError for optimized parametrs with bound(s) '
        + outside_bound_index + 'in output of fit(): the optimized parameters '
        + 'must be within their bounds: ' + str(bounds))
    optimized_parameters_rounded = [round(optimized_parameters[0], 1),
                                    round(optimized_parameters[1], 6)]
    assert np.all(optimized_parameters_rounded==expected_parameters), (
        'ValueError: optimized parameters differ from the expected ones')

def generate_fit_results_bad_representation():
    """Generate a data set of a resistor and fit them using an analyzed
    circuit with an incorrect circuit diagram (an rc parallel). Return the fit
    results.
    """
    signal = np.array([complex(6770, 0), complex(6770, 0),
                       complex(6770, 0), complex(6770, 0)])
    frequency = np.array([10, 100, 1000, 10000])
    analyzed_circuit = generate_pre_fit_circuit_rc()
    fit_results = fit(frequency, signal, analyzed_circuit)
    return fit_results

@pytest.fixture
def fit_results_bad_representation():
    """Fixture for the fit results of an RC-like Circuit with wrong fitting
    diagram.
    """
    return generate_fit_results_bad_representation()

def test_fit_bad_representation(fit_results_bad_representation):
    """Check that the fit() function fails to return proper values of the fit
    if there data and the analyzed circuit describe two different circuits.

    GIVEN: a valid analyzed circuit (rc-series-like) but data that belongs to
    a resistor-like circuit.
    WHEN: I call the fit function to get the optimized parameters
    THEN: there optimized parameters have a the capacitor parameters that does
    not represent anything in the data, in fact is just insanely large to
    account for the absence of an impedance contribution given by a capacitor
    (if the capacitance is huge the impedance is almsot zero). The resistor
    parameter instead is accurate
    """
    bounds = [(10, None), (1e-9, None)]
    optimized_parameters = fit_results_bad_representation[0]
    expected_parameter_resistor = [6770.0] #Expected value of the fitted data.
                                           #But there is also a second
                                           #parameter that has no meaning

    assert isinstance(optimized_parameters, np.ndarray), (
        'TypeError for parameters in fit() . It must be a list')
    outside_bound_index = outside_bound_optimized_parameters(
        optimized_parameters, bounds)
    assert not outside_bound_index, (
        'StructuralError for optimized parametrs with bound(s) '
        + outside_bound_index + 'in output of fit(): the optimized parameters '
        + 'must be within their bounds: ' + str(bounds))
    assert optimized_parameters[0]==expected_parameter_resistor, (
        'ValueError: the optimized parameter for the resistor differ from '
        + 'the expected one')
    assert optimized_parameters[1]>1, (
        'ValueError: the optimized parameter for the cacitor is not as big as '
        + 'expected')


def test_generate_get_constant_parameter_info_resistor():
    """Check that element info of a constant parameter for the result string
    is a string with the element and the value of the constant parameter of a
    resistor.

    GIVEN: a resistor element and an input parameter map element
    WHEN: I call the function to get the info of a constant element
    THEN: the element info is a proper string for the results
    """
    element = 'R1'
    parameter = (1000.0, 1)
    expected_result = 'R1: 1000.0 (constant)'
    constant_info_string = get_constant_parameter_info(element, parameter)

    assert isinstance(constant_info_string, str), (
        'TypeError for output of get_constant_parameter_info(). It has to be '
        + 'a string')
    assert constant_info_string==expected_result, (
        'StructuralError for output of get_constant_parameter_info(). The '
        + 'output string is different from the expected one')

def test_generate_get_constant_parameter_info_capacitor():
    """Check that element info of a constant parameter for the result string
    is a string with the element and the value of the constant parameter of a
    capacitor.

    GIVEN: a capacitor element and an input parameter map element
    WHEN: I call the function to get the info of a constant element
    THEN: the element info is a proper string for the results
    """
    element = 'C2'
    parameter = (1e-06, 1)
    expected_result = 'C2: 1e-06 (constant)'
    constant_info_string = get_constant_parameter_info(element, parameter)

    assert isinstance(constant_info_string, str), (
        'TypeError for output of get_constant_parameter_info(). It has to be '
        + 'a string')
    assert constant_info_string==expected_result, (
        'StructuralError for output of get_constant_parameter_info(). The '
        + 'output string is different from the expected one')

def test_generate_get_constant_parameter_info_cpe():
    """Check that element info of the constant parameters for the result
    string is a string with the element and the value of the constant
    parameters of a cpe.

    GIVEN: a cpe element and the input parameter map element
    WHEN: I call the function to get the info of a constant element
    THEN: the element info is a proper string for the results
    """
    element = 'Q5'
    parameters = ([1e-07, 0.5], 1)
    expected_result = 'Q5: 1e-07, 0.5 (constant)'
    constant_info_string = get_constant_parameter_info(element, parameters)

    assert isinstance(constant_info_string, str), (
        'TypeError for output of get_constant_parameter_info(). It has to be '
        + 'a string')
    assert constant_info_string==expected_result, (
        'StructuralError for output of get_constant_parameter_info(). The '
        + 'output string is different from the expected one')


def test_generate_get_optimized_parameter_info_resistor():
    """Check that element info of a optimized parameter for the result string
    is a string with the element and the value of the optimized parameter of a
    resistor.

    GIVEN: a resistor element and the optimized parameter
    WHEN: I call the function to get the info of a optimized element
    THEN: the element info is a proper string for the results where the
    parameter is rounded
    """
    element = 'R1'
    parameter = 1034.66735
    expected_result = 'R1: 1034.667'
    optimized_info_string = get_optimized_parameter_info(element, parameter)

    assert isinstance(optimized_info_string, str), (
        'TypeError for output of get_optimized_parameter_info(). It has to '
        + 'be a string')
    assert optimized_info_string==expected_result, (
        'StructuralError for output of get_optimized_parameter_info(). The '
        + 'output string is different from the expected one')

def test_generate_get_optimized_parameter_info_capacitor():
    """Check that element info of a optimized parameter for the result string
    is a string with the element and the value of the optimized parameter of a
    capacitor.

    GIVEN: a capacitor element and the optimized parameter
    WHEN: I call the function to get the info of a optimized element
    THEN: the element info is a proper string for the results where the
    parameter is rounded
    """
    element = 'C4'
    parameter = 1.252574e-07
    expected_result = 'C4: 1.2526e-07'
    optimized_info_string = get_optimized_parameter_info(element, parameter)

    assert isinstance(optimized_info_string, str), (
        'TypeError for output of get_optimized_parameter_info(). It has to be '
        + 'a string')
    assert optimized_info_string==expected_result, (
        'StructuralError for output of get_optimized_parameter_info(). The '
        + 'output string is different from the expected one')

def test_generate_get_optimized_parameter_info_cpe():
    """Check that element info of the optimized parameters for the result
    string is a string with the element and the value of the optimized
    parameters of a cpe.

    GIVEN: a cpe element and the optimized parameters
    WHEN: I call the function to get the info of a optimized element
    THEN: the element info is a proper string for the results, where the
    parameters are rounded
    """
    element = 'Q8'
    parameter = [1.2e-06, 0.474]
    expected_result = 'Q8: 1.2e-06, 0.474'
    optimized_info_string = get_optimized_parameter_info(element, parameter)

    assert isinstance(optimized_info_string, str), (
        'TypeError for output of get_optimized_parameter_info(). It has to '
        + 'be a string')
    assert optimized_info_string==expected_result, (
        'StructuralError for output of get_optimized_parameter_info(). The '
        + 'output string is different from the expected one')


def test_results_info_resistor(post_fit_circuit_resistor):
    """Check that the results info of a fitted circuit of a resistor (i.e.
    with the parameter set as non-constant) is a proper result string.

    GIVEN: a valid initial circuit of a resistor, its analyzed circuit after
    the fit and the final error
    WHEN: I call the function to get the result string of a circuit
    THEN: the result info is a proper string for the results, where all the
    parameters are present (both constant and non-constant). The optimized
    parameters are rounded
    """
    diagram = '(R1)'
    parameters = {'R1': (100., 0)}
    initial_circuit = Circuit(diagram, parameters)
    final_errors = 0.0254
    result_string = get_results_info(post_fit_circuit_resistor, final_errors,
                                     initial_circuit)
    expected_result = 'R1: 100.0\nError: 0.0254'

    assert isinstance(result_string, str), (
        'TypeError for output of get_results_info(). It has to be a string.')
    assert result_string==expected_result, (
        'StructuralError for output of get_results_info(). It differs from '
        + 'the expected one')

def test_results_info_rc(post_fit_circuit_rc):
    """Check that the results info of a fitted circuit of an rc in series
    (with the parameter set as non-constant) is a proper result string.

    GIVEN: a valid initial circuit of an rc in series, its analyzed circuit
    after the fit and the final error
    WHEN: I call the function to get the result string of a circuit
    THEN: the result info is a proper string for the results, where all the
    parameters are present (both constant and non-constant). The optimized
    parameters are rounded
    """
    diagram = '(R1C2)'
    parameters = {'R1': (100., 0), 'C2': (1e-6, 0)}
    initial_circuit = Circuit(diagram, parameters)
    final_errors = 0.174
    result_string = get_results_info(post_fit_circuit_rc, final_errors,
                                     initial_circuit)
    expected_result = 'R1: 1200.642\nC2: 5.2072e-07\nError: 0.1740'

    assert isinstance(result_string, str), (
        'TypeError for output of get_results_info(). It has to be a string.')
    assert result_string==expected_result, (
        'StructuralError for output of get_results_info(). It differs from '
        + 'the expected one')

def test_results_info_rq(post_fit_circuit_rq):
    """Check that the results info of a fitted circuit of an rq in parallel
    (with the resistor parameter set as constant and the cpe parameters as
    non-constant) is a proper result string.

    GIVEN: a valid initial circuit of an rq in parallel, its analyzed circuit
    after the fit and the final error
    WHEN: I call the function to get the result string of a circuit
    THEN: the result info is a proper string for the results, where all the
    parameters are present (both constant and non-constant). The optimized
    parameters are rounded
    """
    diagram = '[R1Q2]'
    parameters = {'R1': (500., 1), 'Q2': ([1e-6, 0.5], 0)}
    initial_circuit = Circuit(diagram, parameters)
    final_errors = 0.0037
    result_string = get_results_info(post_fit_circuit_rq, final_errors,
                                     initial_circuit)
    expected_result = ('R1: 500.0 (constant)\nQ2: 1.49755e-06, 0.9\nError: '
                       + '0.0037')

    assert isinstance(result_string, str), (
        'TypeError for output of get_results_info(). It has to be a string.')
    assert result_string==expected_result, (
        'StructuralError for output of get_results_info(). It differs from '
        + 'the expected one')

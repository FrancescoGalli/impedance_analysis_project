import pytest
import numpy as np

import sys
from pathlib import Path
sys.path.append(str(Path.cwd().parent)) 

from generate_impedance import Circuit, AnalisysCircuit

from impedance_analysis import (
    error_function, bounds_definitions, fit,
    get_constant_parameter_info, get_optimized_parameters_info,
    get_results_info)




def generate_examples_error():
    """Generate examples of errors from the error function, for the error test.
    Only the last one is incorrect, where the parameters is set as incorrect
    """
    signals = [np.array([complex(100,0), complex(100,0), complex(100,0),
                         complex(100,0)]),
               np.array([complex(0,-1000), complex(0,-100), complex(0,-10),
                         complex(0,-1)]),
               np.array([complex(500,-1000), complex(500,-100),
                         complex(500,-10), complex(500,-1)]),
               np.array([complex(200,0), complex(200,0), complex(200,0),
                         complex(200,0)]),]
    frequency = np.array([10, 100, 1000, 10000])
    function_r = lambda x, y: (x[0]+0j) * np.ones(len(y))
    function_c = lambda x, y: 1./(1j*y*2*np.pi*x[0])
    function_rc = lambda x, y: ((x[0]+0j) * np.ones(len(y))
                                + 1./(1j*y*2*np.pi*x[1]))
    functions_ = [function_r, function_c, function_rc, function_r]
    parameters = [[100.], [1e-4/(2*np.pi)], [500, 1e-4/(2*np.pi)], [50.]]
    examples_errors = []
    for i, signal in enumerate(signals):
        error = error_function(parameters[i], signal, functions_[i],
                               frequency)
        examples_errors.append(error)
    return examples_errors

@pytest.fixture
def examples_error():
    return generate_examples_error()

def test_error_function(examples_error):
    """Check that the output of error_function() is a valid error (a 
    non negative float, almost zero if the parameters are correct).

    GIVEN: valid data, functions and parameters.
    WHEN: the function to calculate the error between the impedance function
    (with given parameters) and the data is called.
    THEN: the error is a non-negative positive float.
    """
    for i, error in enumerate(examples_error):
        assert isinstance(error, float), (
            'TypeError for ' + str(i+1) + 'th example of error_function(): '
            + 'the output must be a float, not a ' + str(type(error)))
        assert error>=0, ('ValueError for ' + str(i+1) + ' of '
                          + 'error_function(): the output must be '
                          + 'non-negative')
        assert error<1, ('ValueError ' + str(i+1) + ' of error_function(): '
                          + 'given the examples, the parameters are set to '
                          + 'have almost zero error')


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

def generate_examples_tuple_list_type():
    """Generate examples of tuples, for the wrong_element_value_bound test.
    Only the last one is incorrect.
    """
    examples_tuples_list = [[('a', 1)], [(22, 345), (10, 1e5)], [(1., 1j)],
                            [(1e-2, 1e3, 1e4)]]
    return examples_tuples_list

@pytest.fixture
def examples_tuple_list_type():
    return generate_examples_tuple_list_type()

def test_wrong_element_type_bound(examples_tuple_list_type):
    """Check that the the help function to find objects that are not a 2-lengt
    tuples works 

    GIVEN: valid list of bounds.
    WHEN: the help function to test the bound definitions is called
    THEN: the function works.
    """
    for i, bounds_list in enumerate(examples_tuple_list_type):
        wrong_element_type_index = wrong_element_type_bound_definitions(
            bounds_list)
        assert not wrong_element_type_index, (
            'TypeError in ' + str(i+1) + 'th example of bound_definitions(): '
            + 'the output must be a list of tuples of length 2')


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

def generate_examples_tuple_list_value():
    """Generate examples of tuples, for the wrong_element_value_bound test.
    Only the last one is incorrect (multiple times).
    """
    examples_tuples_list = [[(22, 345), (10, 1e5)], [(1., 10)], [(1e-2, 1e3)],
                            [('a', None), (1., 1j), (10., 1), (-1, 10)]]
    return examples_tuples_list

@pytest.fixture
def examples_tuple_list_value():
    return generate_examples_tuple_list_value()

def test_wrong_element_value_bound(examples_tuple_list_value):
    """Check that the the help function to find objects inside of tuples that
    are not valid bounds works.

    GIVEN: valid list of bounds.
    WHEN: the help function to test the bound definitions is called
    THEN: the function works.
    """
    for i, bounds_list in enumerate(examples_tuple_list_value):
        wrong_element_value_index = wrong_element_value_bound_definitions(
            bounds_list)
        assert not wrong_element_value_index, (
            'StructuralError for ' + wrong_element_value_index + 'of the '
            + str(i+1) + 'th example of bound_definitions(): each element '
            + 'of the output must be a tuple with as first element a '
            + 'non-negative number, and as a second element either \'None\' '
            + 'or a non-negative number bigger than the  first element')

def count_q(elements_bound, i_element):
    """Count how many Q elements there are before a certain element.

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

def generate_examples_Q_count():
    """Generate examples of Qcounts for the count_q test."""
    elements_list = [['R1', 'C2', 'R3'], ['R1', 'Q2', 'R3'],
                              ['R3', 'Q4', 'R1', 'C2']]
    example_Q_count = []
    for list_ in elements_list:
        example_Q_count.append(count_q(list_, 2))
    return example_Q_count

@pytest.fixture
def examples_Q_count():
    return generate_examples_Q_count()

def generate_examples_Q_count_results():
    """Generate examples of Q counts for the count_q test."""
    results = [0, 1, 1]
    return results

@pytest.fixture
def examples_Q_count_results():
    return generate_examples_Q_count_results()

def test_count_Q(examples_Q_count, examples_Q_count_results):
    """Check that the the help function to find how many Q elements there are
    in a element list works.

    GIVEN: valid list of bounds.
    WHEN: the help function to test the bound definitions is called
    THEN: the function works.
    """
    for i, q_count in enumerate(examples_Q_count):
        assert q_count==examples_Q_count_results[i], (
            'Value error for the q_count() function: incorrect result')


def bound_definitions_same_length_elements_list(elements_bound, bounds_list):
    """Return whether there is a consistent correspondance between the length
    of elements and bounds_list. For each element but for Q 1 element is equal
    to 1 bound. For Q case is 1 element to 2 bounds. Used for testing

    Parameters
    ----------
    elements_bound : list
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

def generate_examples_same_length():
    """Generate examples of result of length equality between elements lists
    and bound lists.
    """
    examples_elements_list = [['R1'], ['R1', 'Q2'], ['R3', 'R1', 'C2'], ['C1']]
    examples_bounds_list = [[(1, 2)], [(1, 10), (0.1, 100), (1, 2, 3)],
                            [(1, 10), (0.1, 100), (1, 2, 3)],
                            [(1, 10), (0.1, 100)]]
    boolean_conditions = []
    for i, element_list in enumerate(examples_elements_list):
        condition = bound_definitions_same_length_elements_list(
            element_list, examples_bounds_list[i])
        boolean_conditions.append(condition)
    return boolean_conditions

@pytest.fixture
def examples_same_length():
    return generate_examples_same_length()

def test_same_length(examples_same_length):
    """Check that the the help function to find if the elements lists and the
    bound list are consistent in length works.

    GIVEN: valid list of bounds and elements.
    WHEN: the help function to test the bound definitions is called
    THEN: the function works.
    """
    for i, result in enumerate(examples_same_length):
        assert result, (
            'StructuralError for the ' + str(i+1) + 'th example of '
            + 'bound_definitions(): the list of bounds must have a proper '
            + 'length related to the elements list. For each element but for '
            + 'Q 1 element is equal to 1 bound. For Q case is 1 element to 2 '
            + 'bounds.')


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

def generate_examples_elements_list_bounds():
    """Generate examples of elements lists for the bad_match test."""
    examples_elements_list = [['R1'], ['R1', 'Q2'], ['R3', 'R1', 'C2'], ['C1']]
    return examples_elements_list

@pytest.fixture
def examples_elements_list_bounds():
    return generate_examples_elements_list_bounds()

def generate_examples_bounds_list_bad_match():
    """Generate examples of elements lists for the bad_match test."""
    examples_bounds_list = [[(1, 1000)], [(1, 10), (0.1, 100), (0.2, 0.7)],
                            [(1, 10), (0.1, 100), (1e-6, 1)], [(0, 10)]]
    return examples_bounds_list

@pytest.fixture
def examples_bounds_list_bad_match():
    return generate_examples_bounds_list_bad_match()

def test_bad_match_bound(examples_elements_list_bounds,
                         examples_bounds_list_bad_match):
    """Check that the the help function to find if the elements lists and the
    bound list have a bad match works.

    GIVEN: valid list of bounds and elements.
    WHEN: the help function to test the bound definitions is called
    THEN: the function works.
    """
    for i, elements_list in enumerate(examples_elements_list_bounds):
        wrong_match_index = bad_match_bound_definitions_elements_list(
            elements_list, examples_bounds_list_bad_match[i])
        assert not wrong_match_index, (
            'StructuralError for elements ' + wrong_match_index + 'in the '
            + str(i+1) + 'th example: there must be a correspondace between '
            + 'each element of the element list and the correspective bound.'
            + 'Bound for R, C or Q must have a positive umber as first '
            + 'element, while for n the second parameter must not be bigger '
            + 'than 1')


def generate_example_bounds_list():
    """Generate examples of bound list from the element list."""
    element_lists = generate_examples_elements_list_bounds()
    example_bounds = []
    for element_list in element_lists:
        bounds_list = bounds_definitions(element_list)
        example_bounds.append(bounds_list)
    return example_bounds

@pytest.fixture
def example_bounds_list():
    return generate_example_bounds_list()

def test_bound_definitions(examples_elements_list_bounds, example_bounds_list):
    """Check that the output of bound_definitions() is a valid list of tuple
    for bound conditions.

    GIVEN: a valid list of elements
    WHEN: the function to get the bounds defintiion is called during the fit
    THEN: the output is a proper list of tuples for elements
    """
    for i, bounds_list in enumerate(example_bounds_list):
        assert isinstance(bounds_list, list), (
            'TypeError in the ' + str(i+1) + 'th example: the output must '
            + 'be a list,  not a ' + str(type(bounds_list)))
        wrong_element_type_index = wrong_element_type_bound_definitions(
            bounds_list)
        assert not wrong_element_type_index, (
            'TypeError in the '
            + str(i+1) + 'th example: the output must '
            + 'be a list of tuples of length 2')
        wrong_element_value_index = wrong_element_value_bound_definitions(
            bounds_list)
        assert not wrong_element_value_index, (
            'StructuralError for ' + wrong_element_value_index + 'in the '
            + str(i+1) + 'th example: each element of the output must be a '
            + 'tuple with as first element a non-negative number, and as a '
            + 'second element either \'None\' or a non-negative number '
            + 'bigger than the first element')
        elements_bound = examples_elements_list_bounds[i]
        assert bound_definitions_same_length_elements_list(
            elements_bound, bounds_list), (
            'StructuralError in the '
            + str(i+1) + 'th example: the list of '
            + 'bounds must have a proper length related to the elements '
            + 'list. For each element but for Q 1 element is equal to '
            + 'bound. For Q case is 1 element to 2 bounds.')
        wrong_match_index = bad_match_bound_definitions_elements_list(
            elements_bound, bounds_list)
        assert not wrong_match_index, (
            'StructuralError for elements ' + wrong_match_index + 'in the '
            + str(i+1) + 'th example: there must be a correspondace between '
            + 'each element of the element list \'' + str(elements_bound)
            + '\' and the correspective bound. Bound for R, C or Q must have '
            + 'a positive number as first element, while for n the second '
            + 'parameter must not be bigger than 1')



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

def generate_example_elements_pre_fit_length():
    """Generate examples of element lists pre fit."""
    element_lists = [['R1'], ['C1'], ['R1', 'C1'], ['R1']]
    return element_lists

@pytest.fixture
def example_elements_pre_fit_length():
    return generate_example_elements_pre_fit_length()

def generate_example_elements_post_fit_length():
    """Generate examples of element lists post fit."""
    element_lists = [['R1'], ['C1'], ['R1', 'C1'], ['R1', 'C1']]
    return element_lists

@pytest.fixture
def example_elements_post_fit_length():
    return generate_example_elements_post_fit_length()

def test_same_length_elements_fit(example_elements_pre_fit_length,
                                  example_elements_post_fit_length):
    """Check that the the help function to find if the elements lists before
    and after fit are of the same length works.

    GIVEN: valid elements lists.
    WHEN: the help function to test the fit function
    THEN: the function works.
    """
    for i, elements_list in enumerate(example_elements_pre_fit_length):
        assert same_length_elements_parameters_map(
            elements_list, example_elements_post_fit_length[i]), (
            'StructuralError for the '+ str(i+1) + 'th example between '
            + 'elements list in parameter map pre and post fit. They must '
            + 'have the same length')


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

def generate_example_elements_pre_fit_match():
    """Generate examples of element lists pre fit."""
    element_lists = [['R1'], ['C1'], ['R1', 'C1'], ['R1']]
    return element_lists

@pytest.fixture
def example_elements_pre_fit_match():
    return generate_example_elements_pre_fit_match()

def generate_example_elements_post_fit_match():
    """Generate examples of element lists post fit."""
    element_lists = [['R1'], ['C1'], ['R1', 'C1'], ['C1']]
    return element_lists

@pytest.fixture
def example_elements_post_fit_match():
    return generate_example_elements_post_fit_match()

def test_match_elements_fit(example_elements_pre_fit_match,
                            example_elements_post_fit_match):
    """Check that the the help function to find if the elements lists before
    and after fit matches in element names works.

    GIVEN: valid elements lists.
    WHEN: the help function to test the fit function
    THEN: the function works.
    """
    for i, elements_list in enumerate(example_elements_pre_fit_match):
        wrong_element = wrong_elements_parameters_map(
            elements_list, example_elements_post_fit_match[i])
        assert not wrong_element, (
                'StructuralError for the '+ str(i+1) + 'th example: '
                + wrong_element + ' of pre fit elements not found in post fit'
                + 'elements')


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

def generate_example_parameters_pre_fit_match():
    """Generate examples of parameters lists pre fit."""
    parameters_lists = [[200.], [1e-6], [100., 3e-6], [1000.]]
    return parameters_lists

@pytest.fixture
def example_parameters_pre_fit_match():
    return generate_example_parameters_pre_fit_match()

def generate_example_parameters_post_fit_match():
    """Generate examples of parameters lists post fit."""
    parameters_lists = [[300.], [3.5e-6], [175., 4.554e-6], ['1236']]
    return parameters_lists

@pytest.fixture
def example_parameters_post_fit_match():
    return generate_example_parameters_post_fit_match()

def test_match_parameters_fit(example_parameters_pre_fit_match,
                              example_parameters_post_fit_match):
    """Check that the the help function to find if the elements lists before
    and after fit matches in element names works.

    GIVEN: valid elements lists.
    WHEN: the help function to test the fit function
    THEN: the function works.
    """
    for i, parameters_lists in enumerate(example_parameters_pre_fit_match):
        wrong_elements, wrong_parameters = wrong_parameters_parameters_map(
            parameters_lists, example_parameters_post_fit_match[i])
        assert not wrong_elements, (
                'StructuralError for the '+ str(i+1) + 'th example. '
                + 'Parameter(s) ' + wrong_parameters + 'of element'
                + wrong_elements + ' of pre fit elements has a different type of'
                + 'the counterpart in the post fit parameters_map')


def generate_examples_analyzed_circuit_pre_fit():
    """Generate examples of analyzed circuit before a fit for the fit test."""
    function_r = lambda x, y: (x[0]+0j) * np.ones(len(y))
    function_c = lambda x, y: 1./(1j*y*2*np.pi*x[0])
    function_rc = lambda x, y: ((x[0]+0j) * np.ones(len(y))
                                + 1./(1j*y*2*np.pi*x[1]))
    functions_ = [function_r, function_c, function_rc]
    parameters = [{'R1': 200.}, {'C1': 7e-4}, {'R1': 330., 'C2': 5e-4}]
    diagrams = ['(R1)', '(C1)', '(R1C2)']
    examples_circuits = []
    for i, diagram in enumerate(diagrams):
        circuit_ = AnalisysCircuit(diagram, impedance=functions_[i],
                                   parameters_map=parameters[i])
        examples_circuits.append(circuit_)
    return examples_circuits

@pytest.fixture
def examples_analyzed_circuit_pre_fit():
    return generate_examples_analyzed_circuit_pre_fit()

def generate_examples_analyzed_circuit_post_fit():
    """Generate examples of analyzed circuit after a fit for the fit test."""
    example_analyzed_circuit_pre_fit = generate_examples_analyzed_circuit_pre_fit()
    signals = [np.array([complex(100,0), complex(100,0), complex(100,0),
                        complex(100,0)]),
               np.array([complex(0,-1000), complex(0,-100), complex(0,-10),
                        complex(0,-1)]),
               np.array([complex(500,-1000), complex(500,-100),
                        complex(500,-10), complex(500,-1)])]
    frequency = np.array([10, 100, 1000, 10000])
    example_analyzed_circuit_post_fit = []
    for i, signal in enumerate(signals):
        circuit_ = example_analyzed_circuit_pre_fit[i]
        _ = fit(frequency, signal, circuit_)
        example_analyzed_circuit_post_fit.append(circuit_)
    return example_analyzed_circuit_post_fit

@pytest.fixture
def examples_analyzed_circuit_post_fit():
    return generate_examples_analyzed_circuit_post_fit()

def test_fit_analyzed_circuit_parameters(examples_analyzed_circuit_pre_fit,
                                         examples_analyzed_circuit_post_fit):
    """Check that the parameters map of post fit is congruent with the one
    of pre fit: same elements, same types of the parameters.

    GIVEN: a valid pre fit analyzed circuit
    WHEN: the fit function is called
    THEN: the parameters map of post fit is congruent with the one of pre fit
    """
    for i, post_circuit in enumerate(examples_analyzed_circuit_post_fit):
        pre_circuit = examples_analyzed_circuit_pre_fit[i]
        assert isinstance(post_circuit.parameters_map, dict), (
            'TypeError for post fit parameters map. It must be a dictionary')
        assert same_length_elements_parameters_map(
            pre_circuit.list_elements(), post_circuit.list_elements()), (
                'StructuralError between elements list in parameter map pre '
                + 'and post fit. They must have the same length')
        wrong_element = wrong_elements_parameters_map(
            pre_circuit.list_elements(),
            post_circuit.list_elements())
        assert not wrong_element, (
                'StructuralError between elements list in parameter map pre '
                + 'and post fit. ' + wrong_element + ' of pre fit elements '
                + 'not found in post fit elements ')
        wrong_elements, wrong_parameters = wrong_parameters_parameters_map(
            pre_circuit.parameters_map,
            post_circuit.parameters_map)
        assert not wrong_elements, (
                'StructuralError between parameter(s) in parameter map pre '
                + 'and post fit. Parameter(s) ' + wrong_parameters + 'of element'
                + wrong_elements + ' of pre fit elements has a different '
                + 'type of the counterpart in the post fit parameters_map')



def analyzed_circuit_parameters_and_optimized_parameters_same_length(
        analyzed_circuit_parameters, optimized_parameters):
    """Given the analyzed parameters list in the analysis circuit and the
    optimized parameters list given by the fit, return wheter they have the
    same length or not. Used for testing

    Parameters
    ----------
    analyzed_circuit_parameters : list
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

def generate_example_parameters_analyzed():
    """Generate examples of parameters lists of the analyzed circuit after the
    fit. Only the last one is incorrect.
    """
    parameters_lists = [[200.], [1e-6], [100., 3e-6], [1000.]]
    return parameters_lists

@pytest.fixture
def example_parameters_analyzed():
    return generate_example_parameters_analyzed()

def generate_example_parameters_optimized():
    """Generate examples of optimized parameters lists after the fit."""
    parameters_lists = [[200.], [1e-6], [100., 3e-6], [1e14]]
    return parameters_lists

@pytest.fixture
def example_parameters_optimized():
    return generate_example_parameters_optimized()

def test_parameters_same_length(example_parameters_analyzed,
                                example_parameters_optimized):
    """Check that the the help function to find if the parameters lists before
    and after fit have the same length works.

    GIVEN: valid parameters lists.
    WHEN: the help function to test the fit function
    THEN: the function works.
    """
    for i, parameters_lists in enumerate(example_parameters_analyzed):
        assert analyzed_circuit_parameters_and_optimized_parameters_same_length(
            parameters_lists, example_parameters_optimized[i]), (
            'StructuralError: wrong number of optimized parameters \''
            + str(len(example_parameters_optimized[i]))
            + '\' (with number of initial parameters \''
            + str(len(parameters_lists)) + '\'). They must be the same')


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

def test_parameters_wrong_match(example_parameters_analyzed,
                                example_parameters_optimized):
    """Check that the the help function to find if the parameters lists before
    and after fit have the same length works.

    GIVEN: valid parameters lists.
    WHEN: the help function to test the fit function
    THEN: the function works.
    """
    for i, parameters_lists in enumerate(example_parameters_analyzed):
        missing_parameter = wrong_match_analyzed_circuit_parameters_optimized_parameters(
            parameters_lists, example_parameters_optimized[i])
        assert not missing_parameter, (
            'StructuralError in ' + str(i+1) + 'th example: missing parameter '
            + 'for optimization ' + missing_parameter)


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

def generate_example_bounds_fit():
    """Generate examples of bounds for the fit. Only the last one is incorrect.
    """
    bounds_lists = [[(1., 1e7)], [(1e-9, 1e-2)], [(1., 1e7),(1e-9, 1e-2)],
                    [(1., 1e7)]]
    return bounds_lists

@pytest.fixture
def example_bounds_fit():
    return generate_example_bounds_fit()

def test_outside_bounds(example_parameters_optimized, example_bounds_fit):
    """Check that the the help function to find if the parameters lists before
    and after fit have the same length works.

    GIVEN: valid parameters lists.
    WHEN: the help function to test the fit function
    THEN: the function works.
    """
    for i, optimized_parameters in enumerate(example_parameters_optimized):
        outside_bound_index = outside_bound_optimized_parameters(
            optimized_parameters, example_bounds_fit[i])
        assert not outside_bound_index, (
            'StructuralError for optimized parametrs with bound(s) '
            + outside_bound_index + 'in ' + str(i+1) + 'th example: the '
            + 'optimized parameters must be within their bounds: '
            + str(example_bounds_fit[i]))


def generate_examples_fit_results():
    """Generate examples of fit results list from a valid data,
    initial parameters, element list and impedance function, for the fit test.
    """
    example_analyzed_circuit_pre_fit = generate_examples_analyzed_circuit_pre_fit()
    signals = [np.array([complex(100,0), complex(100,0), complex(100,0),
                        complex(100,0)]),
               np.array([complex(0,-1000), complex(0,-100), complex(0,-10),
                        complex(0,-1)]),
               np.array([complex(500,-1000), complex(500,-100),
                        complex(500,-10), complex(500,-1)])]
    frequency = np.array([10, 100, 1000, 10000])
    example_fit_results = []
    for i, signal in enumerate(signals):
        circuit_ = example_analyzed_circuit_pre_fit[i]
        fit_results = fit(frequency, signal, circuit_)
        example_fit_results.append(fit_results)
    return example_fit_results

@pytest.fixture
def examples_fit_results():
    return generate_examples_fit_results()

def test_fit_optimized_parameters(examples_fit_results, example_bounds_fit,
                                  examples_analyzed_circuit_post_fit):
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
    for i, results in enumerate(examples_fit_results):
        optimized_parameters = results[0] 
        assert isinstance(optimized_parameters, np.ndarray), (
            'TypeError for parameters in ' + caller + ' . It must be a list')
        assert analyzed_circuit_parameters_and_optimized_parameters_same_length(
            examples_analyzed_circuit_post_fit[i].list_parameters(),
            optimized_parameters), (
            'StructuralError: wrong number of optimized parameters \''
            + str(len(optimized_parameters)) + '\' (with number of initial '
            + 'parameters \'' + str(len(
                examples_analyzed_circuit_post_fit[i].list_parameters()))
                + '\') in output of ' + caller + ' . They must be the same')
        missing_parameter = wrong_match_analyzed_circuit_parameters_optimized_parameters(
            examples_analyzed_circuit_post_fit[i].list_parameters(),
            optimized_parameters)
        assert not missing_parameter, (
            'StructuralError in ' + caller + ': missing parameter for '
            + 'optimization ' + missing_parameter)
        outside_bound_index = outside_bound_optimized_parameters(
            optimized_parameters, example_bounds_fit[i])
        assert not outside_bound_index, (
            'StructuralError for optimized parametrs with bound(s) '
            + outside_bound_index + 'in output of ' + caller + ': the '
            + 'optimized parameters must be within their bounds: '
            + str(example_bounds_fit[i]))


def test_fit_success_flag(examples_fit_results):
    """Check that second argument of the output of fit() is a string.

    GIVEN: a valid data, initial parameters, element list and impedance
    function
    WHEN: the fit function is called
    THEN: second argument of the output of fit() is a string
    """
    for results in examples_fit_results:
        success_flag = results[1]
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
        example_element_info_const.append(get_constant_parameter_info(
            element, example_parameters[i]))
    return example_element_info_const

@pytest.fixture
def example_element_info_const():
    return generate_example_element_info_const()

def test_generate_get_constant_parameter_info(example_element_info_const):
    """Check that element info of a constant parameter for the result string
    is a string.

    GIVEN: a example elements and constant parameters
    WHEN: the function to get the info of a constant element is called
    THEN: the element info is a string
    """
    for example in example_element_info_const:
        assert isinstance(example, str), (
            'TypeError for output of '
            + 'generate_get_constant_parameter_info(). It has to be a '
            + 'string.')


def generate_example_element_info():
    """Generate example of non-constant element info strings for all the
    element types.
    """
    example_elements = (['R1', 'C1', 'Q1'])
    example_parameters = ([1000, 2e-6, ([1e-6, 0.6])])
    example_element_info = []
    for i, element in enumerate(example_elements):
        example_element_info.append(get_optimized_parameters_info(
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


def generate_example_result_string():
    """Generate an example of a result string."""
    analyzed_circuits = generate_examples_analyzed_circuit_pre_fit()
    final_errors = [0.0, 0.1, 1e-5]
    
    diagrams = ['(R1)', '(C1)', '(R1C2)']
    parameters = [{'R1': (100., 0)}, {'C1': (5e-4, 0)}, 
                  {'R1': (30., 0), 'C2': (4e-4, 0)}]
    errors = [234.24, 112.55, 45.4]
    examples_result_string = []
    for i, diagram in enumerate(diagrams):
        circuit_ = Circuit(diagram, parameters_map=parameters[i], 
                           error=errors[i])
        result_string = get_results_info(analyzed_circuits[i], final_errors[i],
                                         circuit_)
        examples_result_string.append(result_string)
    return result_string

@pytest.fixture
def example_result_string():
    return generate_example_result_string()

def test_result_string(example_result_string):
    """Check that the result string is a string.

    GIVEN: a valid set of elements and parameters.
    WHEN: the function to get the result string is called.
    THEN: the result string is a string.
    """
    for result_string in example_result_string:
        assert isinstance(result_string, str), (
            'TypeError for output of get_results_info(). It has to be a '
            + 'string.')

"""This module containes all the test functions (and the function needed for
the tests) for the AnalysisCircuit class of the generate_impedance.py module.
It assesses, for example, that both input data and the output of all the
functions in the class are valid.

Note: of all the group of examples, only the fourth one is meant to fail
"""


import inspect
import pytest

import sys
from pathlib import Path
sys.path.append(str(Path.cwd().parent)) 

from generate_impedance import AnalisysCircuit
from generate_impedance import generate_circuit, add, list_elements_circuit


def wrong_tuples_impedance_parameters_map(impedance_parameters_map):
    """Find for which element the impedance-parameter map of the
    AnalysisCircuit has not a tuple as a value. Used for testing.

    Parameters
    ----------
    impedance_parameters_map : dict 
        Dictionary that links the elements with his own impedance function
        and related parameters

    Returns
    -------
    wrong_tuples : str
        String that contains all the elements that are not tuples,
        separated by a comma and a whitespace
    """
    wrong_tuples = ''
    for tuple_ in impedance_parameters_map.values():
        if not isinstance(tuple_, tuple):
            wrong_tuples += '\'' + str(tuple_) + '\', '
    return wrong_tuples

def generate_example_impedance_map_tuples():
    """Generate examples for the tuples of the impedance_parameters map test.
    Only the last one is incorrect.
    """
    function_ = lambda x, y: 1000.
    impedance_maps = [{'R1': (function_, 'const')},
                      {'R1': (function_, 1000.)},
                      {'R1': (function_, 1000.), 'R2': (function_, 'const')},
                      {'R1': 1000.}]
    return impedance_maps

@pytest.fixture
def example_impedance_map_tuples():
    return generate_example_impedance_map_tuples()

def test_wrong_tuples_impedance_parameters_map(example_impedance_map_tuples):
    """Check that the function to find dictionaries that have not tuples as
    values works.

    GIVEN: a valid list of impedance_parameters_map of input parameters.
    WHEN: the setting of a impedance_parameters_map is tested
    THEN: the impedance-parameter map has the correct type for the values
    """
    for impedance_map in example_impedance_map_tuples:
        wrong_tuples = wrong_tuples_impedance_parameters_map(impedance_map)
        assert not wrong_tuples, (
        'TypeError for element \'' + wrong_tuples + '\'. Its value in the '
        + ' dictionary have to be a tuple')


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
        separated by a comma and a whitespace
    """
    wrong_functions = ''
    for element, tuple_ in impedance_parameters_map.items():
        if not inspect.isfunction(tuple_[0]):
            wrong_functions += '\'' + element + '\', '
    return wrong_functions

def generate_example_impedance_map_function():
    """Generate examples for the impedance of the impedance_parameters map
    test. Only the last one is incorrect.
    """
    function_ = lambda x, y: 1000.
    impedance_maps = [{'R1': (function_, 'const')},
                      {'R1': (function_, 1000.)},
                      {'R1': (function_, 1000.), 'R2': (function_, 'const')},
                      {'R1': ('x', 1000.)}]
    return impedance_maps

@pytest.fixture
def example_impedance_map_function():
    return generate_example_impedance_map_function()

def test_wrong_function_impedance_parameters_map(
        example_impedance_map_function):
    """Check that the function to find dictionaries that have not a function
    as the first element of the tuple works.

    GIVEN: a valid list of impedance_parameters_map of input parameters.
    WHEN: the setting of a impedance_parameters_map is tested
    THEN: the impedance-parameter map has the correct type for the values
    """
    for impedance_map in example_impedance_map_function:
        wrong_functions = wrong_function_impedance_parameters_map(
            impedance_map)
        assert not wrong_functions, (
            'TypeError for element type(s) ' + ' \'' + wrong_functions
            + '\'. Its first element of the tuple must be a function')


def wrong_parameter_impedance_parameters_map_const(element_name_list,
                                                   impedance_parameters_map):
    """Find for which element the impedance-parameter map of the
    AnalysisCircuit has an invalid parameter (i.e. a 'const' atring since it
    is constant) as the second element of the tuple. Used for testing.

    Parameters
    ----------
    element_name_list : list
        List of names (key of the dictionary) of the impedance_map to be
        tested
    impedance_parameters_map : dict 
        Dictionary that links the elements with his own impedance function
        and related parameters

    Returns
    -------
    wrong_parameters : str
        String that contains all the wrong elements with bad parameter,
        separated by a comma and a whitespace
    """
    wrong_parameters = ''
    for element_name in element_name_list:
        tuple_ = impedance_parameters_map[element_name]
        parameter_ = tuple_[1]
        if (not isinstance(parameter_, str)
            or not parameter_.startswith('const')):
            wrong_parameters += '\'' + element_name + '\', '
    return wrong_parameters

def generate_example_impedance_map_const():
    """Generate examples of impedance_parameters map for the 'const' string
    of the impedance_parameters map test. Only the last one is incorrect.
    """
    function_r = lambda x, y: 1000.
    function_c = lambda x, y: 1/(x*y)
    impedance_maps = [{'R1': (function_r, 'const'),
                       'C2': (function_c, 'const')},
                      {'C1': (function_c, 1e-6)},
                      {'R1': (function_r, 1000.),
                       'C2': (function_c, 'const')},
                      {'C1': (function_c, 1e-6)}]
    return impedance_maps

@pytest.fixture
def example_impedance_map_const():
    return generate_example_impedance_map_const()

def generate_example_element_names():
    """Generate examples of element names for the 'const' string of the
    impedance_parameters map test. Only the last one is incorrect.
    """
    element_names = [['R1', 'C2'], [], ['C2'], ['C1']]
    return element_names

@pytest.fixture
def example_element_names():
    return generate_example_element_names()

def test_wrong_parameter_impedance_parameters_map_const(
        example_element_names, example_impedance_map_const):
    """Check that the function to find parameters of the tuple that are just
    a 'const' string  works.

    GIVEN: a valid list of impedance_parameters_map of input parameters.
    WHEN: the setting of a impedance_parameters_map is tested
    THEN: the impedance-parameter map has the correct type for the const
    parameters
    """
    for i, impedance_map in enumerate(example_impedance_map_const):
        wrong_parameters = wrong_parameter_impedance_parameters_map_const(
            example_element_names[i], impedance_map)
        assert not wrong_parameters, (
            'TypeError for element type(s)' + ' \'' + wrong_parameters
            + '\'. Its second element of the tuple must be a \'const\' '
            + 'string')

def generate_example_set_impedance_constants():
    """Generate a possible list of analyzed circuits with a constat element
    analysis.
    """
    first_example = AnalisysCircuit('(R1)')
    first_example.set_impedance_constant_element('R1', 1000.0)
    second_example = AnalisysCircuit('(Q1)')
    second_example.set_impedance_constant_element('Q1', ([1e-6, 0.3]))
    third_example = AnalisysCircuit('(R1C2)')
    third_example.set_impedance_constant_element('C2', 1e-6)
    example_set_impedance_constants = ([first_example, second_example,
                                        third_example])
    return example_set_impedance_constants

@pytest.fixture
def example_set_impedance_constants():
    return generate_example_set_impedance_constants()

def generate_example_names_set_impedance_constants():
    """Generate the list of the element names for the example of the analyzed 
    circuits with a constant element.
    """
    example_names = [['R1'], ['Q1'], ['C2']]
    return example_names

@pytest.fixture
def example_names_set_impedance_constants():
    return generate_example_names_set_impedance_constants()

def test_set_impedance_constant_element(example_names_set_impedance_constants,
                                        example_set_impedance_constants):
    """Check that set_impedance_constant_element() sets a valid
    impedance-parameter map (dictionary) for each type of constant element.

    GIVEN: a valid set of input parameters.
    WHEN: the function to set the impedance of a constant element in the
    AnalysisCircuit
    THEN: the impedance-parameter map is set correctely for each element type
    if constant.
    """
    for i, analyzed_circuit in enumerate(example_set_impedance_constants):
        impedance_map = analyzed_circuit.impedance_parameters_map
        assert isinstance(impedance_map, dict), (
            'TypeError for example number \'' + str(i) + '\'. It must be a '
            + 'dictionary')

        elements_example = list(impedance_map.keys())
        elements_input = example_names_set_impedance_constants[i]
        assert set(elements_example)==set(elements_input), (
            'ValueError for example number \'' + str(i) + '\'. The element '
            + 'names in the dictionary do not match the input ones')

        wrong_tuples = wrong_tuples_impedance_parameters_map(impedance_map)
        assert not wrong_tuples, (
            'TypeError for element \'' + wrong_tuples + '\'. Its value in the '
            + ' dictionary have to be a tuple')
        wrong_functions = wrong_function_impedance_parameters_map(
            impedance_map)
        assert not wrong_functions, (
            'TypeError for element type(s) ' + ' \'' + wrong_functions
             + '\'. Its first element of the tuple must be a function')
        wrong_parameters = wrong_parameter_impedance_parameters_map_const(
            elements_example, impedance_map)
        assert not wrong_parameters, (
            'TypeError for element type(s)' + ' \'' + wrong_parameters
            + '\'. Its second element of the tuple must be a \'const\' string')


def wrong_parameter_impedance_parameters_map_non_constant(
        element_name_list, parameters_list, impedance_parameters_map):
    """Find for which element the impedance-parameter map of the
    AnalysisCircuit has an invalid parameter (i.e. a 'const' atring since it
    is constant) as the second element of the tuple. Used for testing.

    Parameters
    ----------
    element_name_list : list
        List of names (key of the dictionary) of the impedance_map to be
        tested
    parameters_list
        List of parameters of the impedance_map to be tested
    impedance_parameters_map : dict 
        Dictionary that links the elements with his own impedance function
        and related parameters

    Returns
    -------
    wrong_parameters : str
        String that contains all the wrong elements with bad parameter,
        separated by a comma and a whitespace
    """
    wrong_parameters = ''
    for i, element_name in enumerate(element_name_list):
        tuple_ = impedance_parameters_map[element_name]
        parameter_ = tuple_[1]
        if parameters_list[i]!=parameter_:
            wrong_parameters += '\'' + element_name + '\', '
    return wrong_parameters

def generate_example_impedance_map_non_const():
    """Generate examples of impedance_parameters map for the non constant
    impedance_parameters map test. Only the last one is incorrect.
    """
    function_r = lambda x, y: 1000.
    function_c = lambda x, y: 1/(x*y)
    impedance_maps = [{'R1': (function_r, 1000.), 'C2': (function_c, 1e-6)},
                      {'C1': (function_c, 2e-6)},
                      {'R1': (function_r, 2000.)},
                      {'C1': (function_c, 'const')}]
    return impedance_maps

@pytest.fixture
def example_impedance_map_non_const():
    return generate_example_impedance_map_non_const()

def generate_example_element_names_non_const():
    """Generate examples of elements for the non constant impedance_parameters
    map test. Only the last one is incorrect.
    """
    element_names = [['R1', 'C2'], ['C1'], ['R1'], ['C1']]
    return element_names

@pytest.fixture
def example_element_names_non_const():
    return generate_example_element_names_non_const()

def generate_example_parameters_non_const():
    """Generate examples of parameters for the impedance_parameters
    map test. Only the last one is incorrect.
    """
    parameters = [[1000., 1e-6], [2e-6], [2000.], [1e-6]]
    return parameters

@pytest.fixture
def example_parameters_non_const():
    return generate_example_parameters_non_const()

def test_wrong_parameter_impedance_parameters_map_non_const(
        example_element_names_non_const, example_parameters_non_const,
        example_impedance_map_non_const):
    """Check that the function to find parameters of the tuple that are just
    a 'const' string  works.

    GIVEN: a valid list of impedance_parameters_map of input parameters.
    WHEN: the setting of a impedance_parameters_map is tested
    THEN: the impedance-parameter map has the correct type for the const
    parameters
    """
    for i, impedance_map in enumerate(example_impedance_map_non_const):
        wrong_parameters = wrong_parameter_impedance_parameters_map_non_constant(
            example_element_names_non_const[i], example_parameters_non_const[i],
            impedance_map)
    assert not wrong_parameters, (
        'TypeError for element type(s)' + ' \'' + wrong_parameters
        + '\'. Its second element of the tuple must be a \'const\' string')


def generate_example_set_impedance_non_constants():
    """Generate examples ofanalyzed circuits for the set_element_non_const
    test. """
    first_example = AnalisysCircuit('(R1)')
    first_example.set_impedance_non_const_element('R1', 1000.0)
    second_example = AnalisysCircuit('(Q1)')
    second_example.set_impedance_non_const_element('Q1', ([1e-6, 0.3]))
    third_example = AnalisysCircuit('(R1C2)')
    third_example.set_impedance_non_const_element('C2', 1e-6)
    example_set_impedance_non_constants = ([first_example, second_example,
                                            third_example])
    return example_set_impedance_non_constants

@pytest.fixture
def example_set_impedance_non_constants():
    return generate_example_set_impedance_non_constants()

def generate_example_names_set_impedance_non_constants():
    """Generate the list of the element names for the example of the analyzed 
    circuits with a constat element.
    """
    example_names = [['R1'], ['Q1'], ['C2']]
    return example_names

@pytest.fixture
def example_names_set_impedance_non_constants():
    return generate_example_names_set_impedance_non_constants()

def generate_example_parameters_set_impedance_non_constants():
    """Generate the list of the element names for the example of the analyzed 
    circuits with a constat element.
    """
    example_names = [[1000.0], [([1e-6, 0.3])], [1e-6]]
    return example_names

@pytest.fixture
def example_parameters_set_impedance_non_constants():
    return generate_example_parameters_set_impedance_non_constants()

def test_set_impedance_non_const_element(
        example_names_set_impedance_non_constants,
        example_parameters_set_impedance_non_constants,
        example_set_impedance_non_constants):
    """Check that get_impedance_non_const_element() sets a valid
    impedance-parameter map (dictionary) for each type of non-constant element.

    GIVEN: a valid set of input parameters
    WHEN: the function to set the impedance of a non-constant element in the
    AnalysisCircuit
    THEN: the impedance-parameter map is set correctely for each element type
    if non-constant.
    """
    for i, analyzed_circuit in enumerate(example_set_impedance_non_constants):
        impedance_map = analyzed_circuit.impedance_parameters_map
        assert isinstance(impedance_map, dict), (
            'TypeError for example number \'' + str(i) + '\'. It must be a '
            + 'dictionary')

        elements_example = list(impedance_map.keys())
        elements_input = example_names_set_impedance_non_constants[i]
        assert set(elements_example)==set(elements_input), (
            'ValueError for example number \'' + str(i) + '\'. The element '
            + 'names in the dictionary do not match the input ones')

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
            elements_input, example_parameters_set_impedance_non_constants[i],
            impedance_map)
        assert not wrong_parameters, (
            'TypeError for element type(s)' + ' \'' + wrong_parameters
            + '\'. Its second element of the tuple must be a \'const\' string')


def wrong_parameter_impedance_parameters_map(
        input_parameters, constant_conditions, impedance_parameters_map):
    """Find for which element the impedance-parameter map of the
    AnalysisCircuit has an invalid parameter (i.e. a 'const' atring since it
    is constant) as the second element of the tuple. Used for testing.

    Parameters
    ----------
    input_parameters : dict
        Dictionary of the input parameters to be tested
    constant_conditions : list
        List of constant conditions impedance_map to be tested
    impedance_parameters_map : dict 
        Dictionary that links the elements with his own impedance function
        and related parameters

    Returns
    -------
    wrong_parameters : str
        String that contains all the wrong elements with bad parameter,
        separated by a comma and a whitespace
    """
    wrong_parameters = ''
    for i, element_name in enumerate(impedance_parameters_map.keys()):
        tuple_ = impedance_parameters_map[element_name]
        parameter_ = tuple_[1]
        if constant_conditions[i]:
            if not isinstance(parameter_, str):
                wrong_parameters += '1\'' + element_name + '\', ' + str(parameter_)
            elif not parameter_.startswith('const'):
                wrong_parameters += '2\'' + element_name + '\', '
        elif input_parameters[element_name]!=parameter_:
            wrong_parameters += '3\'' + element_name + '\', '
    return wrong_parameters

def generate_example_impedance_map_set_impedance():
    """Generate examples of impedance_parameters maps for the wrong parameters
    impedance_parameters map test. Only the last one is incorrect.
    """
    function_r = lambda x, y: y
    function_c = lambda x, y: 1/(x*y)
    impedance_maps = [{'R1': (function_r, 1000.),
                       'C2': (function_c, 'const')},
                      {'C1': (function_c, 2e-6)},
                      {'R1': (function_r, 'const')},
                      {'R1': (function_r, 2000.)}]
    return impedance_maps

@pytest.fixture
def example_impedance_map_set_impedance():
    return generate_example_impedance_map_set_impedance()

def generate_example_parameters_set_impedance():
    """Generate examples of elements for the non constant impedance_parameters
    map test. Only the last one is incorrect.
    """
    parameters = [{'R1': 1000., 'C2': 1e-6}, {'C1': 2e-6}, {'R1': 1000.},
                  {'R1': 2000.}]
    return parameters

@pytest.fixture
def example_parameters_set_impedance():
    return generate_example_parameters_set_impedance()

def generate_examples_constant_conditions_set_impedance():
    """Generate examples of constant conditions for the set_impedance test.
    Only the last one is incorrect.
    """
    constant_conditions = [[0, 1], [0], [1], [1]]
    return constant_conditions

@pytest.fixture
def examples_constant_conditions_set_impedance():
    return generate_examples_constant_conditions_set_impedance()

def test_wrong_parameter_impedance_parameters_map(
        example_parameters_set_impedance,
        examples_constant_conditions_set_impedance,
        example_impedance_map_set_impedance):
    """Check that the function to find parameters of the tuple that are just
    a 'const' string  works.

    GIVEN: a valid list of impedance_parameters_map of input parameters.
    WHEN: the setting of a impedance_parameters_map is tested
    THEN: the impedance-parameter map has the correct type for the const
    parameters
    """
    for i, impedance_map in enumerate(example_impedance_map_set_impedance):
        wrong_parameters = wrong_parameter_impedance_parameters_map(
            example_parameters_set_impedance[i],
            examples_constant_conditions_set_impedance[i], impedance_map)
        assert not wrong_parameters, (
            'TypeError for element type(s)' + ' \'' + wrong_parameters
            + '\'. The second element of the tuple must be a \'const\' string '
            + 'if the element is constant, or must be the input parameter '
            + 'if the element is not constant')


def generate_circuit_diagram_set_impedance():
    """Generate an example of a circuit diagram for the set_impedance test."""
    circuit_diagram = '(R1C2)'
    return circuit_diagram

def generate_parameters_set_impedance():
    """Generate an example of parameters for the set_impedance test."""
    parameters = {'R1': 10.0, 'C2': 3e-6}
    return parameters

@pytest.fixture
def parameters_set_impedance():
    return generate_parameters_set_impedance()

def generate_examples_circuit_set_impedance():
    """Generate an examples of circuits with both constant and non-constant
    elements for the set_impedance test.
    """
    circuit_diagram = generate_circuit_diagram_set_impedance()
    parameters = generate_parameters_set_impedance()

    constant_conditions = {'R1': 1, 'C2': 1}
    first_circuit = generate_circuit(circuit_diagram, parameters,
                                     constant_conditions)
    
    constant_conditions = {'R1': 0, 'C2': 1}
    second_circuit = generate_circuit(circuit_diagram, parameters,
                                      constant_conditions)
    
    constant_conditions = {'R1': 0, 'C2': 0}
    third_circuit = generate_circuit(circuit_diagram, parameters,
                                     constant_conditions)
    example_circuits = [first_circuit, second_circuit, third_circuit]
    return example_circuits

def generate_examples_constant_conditions():
    constant_conditions = ([[1, 1], [0, 1], [0, 0]])
    return constant_conditions

@pytest.fixture
def examples_constant_conditions():
    return generate_examples_constant_conditions()

def generate_examples_analized_circuit_set_impedance():
    """Generate an AnalysisCircuit instance consisting in a cell with two
    elements: a constant one and a non-constant one.
    """
    circuits_ = generate_examples_circuit_set_impedance()
    circuit_elements = (['R1', 'C2'])
    examples_analysis_circuit_set_impedance = []
    for circuit_ in circuits_:
        analyzed_circuit = AnalisysCircuit('(R1C2)')
        for element in circuit_elements:
            analyzed_circuit.set_impedance_element(element, circuit_)
        examples_analysis_circuit_set_impedance.append(analyzed_circuit)
    return examples_analysis_circuit_set_impedance

@pytest.fixture
def examples_analysis_circuit_set_impedance():
    return generate_examples_analized_circuit_set_impedance()

def test_set_impedance(parameters_set_impedance, examples_constant_conditions,
                       examples_analysis_circuit_set_impedance):
    """Check that set_impedance() sets the correct analysis on the
    AnalysisCircuit instance.

    GIVEN: a valid input circuit
    WHEN: the setting of an element with its impedance function and parameter
    is done
    THEN: the AnalysisCircuit instance contains all the correct elements
    """
    for i, analyzed_circuit in enumerate(
        examples_analysis_circuit_set_impedance):
        impedance_map = analyzed_circuit.impedance_parameters_map
        assert isinstance(impedance_map, dict), (
            'TypeError for example number \'' + str(i) + '\'. It must be a '
            + 'dictionary')

        wrong_tuples = wrong_tuples_impedance_parameters_map(impedance_map)
        assert not wrong_tuples, (
            'TypeError for element \'' + wrong_tuples + '\'. Its value in the '
            + ' dictionary have to be a tuple')
        wrong_functions = wrong_function_impedance_parameters_map(
            impedance_map)
        assert not wrong_functions, (
            'TypeError for element type(s) ' + ' \'' + wrong_functions
             + '\'. Its first element of the tuple must be a function')
        
        wrong_parameters = wrong_parameter_impedance_parameters_map(
            parameters_set_impedance, examples_constant_conditions[i],
            impedance_map)
        assert not wrong_parameters, (
            'TypeError for element type(s)' + ' \'' + wrong_parameters
            + '\'. The second element of the tuple must be a \'const\' string '
            + 'if the element is constant, or must be the input parameter'
            + 'if the element is not constant')


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

def generate_examples_impedance_cell_help():
    """Generate examples of impedance cells for the wrong impedance test.
    Only the last one is incorrect.
    """
    function_r = lambda x, y : y
    function_c = lambda x, y : 1/(x*y)
    first_example = [function_r]
    second_example = [function_c]
    third_example = [function_c, function_r]
    fourth_example = [1000.]
    impedance_cells = [first_example, second_example, third_example,
                        fourth_example]
    return impedance_cells

@pytest.fixture
def examples_impedance_cell_help():
    return generate_examples_impedance_cell_help()

def test_wrong_impedance_generate_cell_impedance(
        examples_impedance_cell_help):
    """Check that the function to find element of a list thta are not
    functions  works.

    GIVEN: a list.
    WHEN: the function to generate the impedance of a cell is tested
    THEN: the help function detects the 
    """
    for i, impedance_list in enumerate(examples_impedance_cell_help):
        wrong_functions_index = wrong_impedance_generate_cell_impedance(
            impedance_list)
        assert not wrong_functions_index, (
            'TypeError for element number(s) ' + ' \''
            + str(wrong_functions_index) + '\' in example ' + str(i+1)
            + '. The output must contain ony funtions')

def circuit_string_impedance_cell_same_length(cell_string, impedance_cell):
    """Return if the a string circuit's element count and the length of the
    impedance_cell is the same.

    Parameters
    ----------
    cell_string : str
        Circuit string of the cell
    impedance_cell : list
        List of impedace functions

    Returns
    -------
    equality_condition : bool
        Boolean condition for the length equality
    """
    element_list = list_elements_circuit(cell_string)
    equality_condition = len(element_list)==len(impedance_cell)
    return equality_condition

def generate_examples_circuit_diagram_help():
    """Generate examples of impedance cells for the diagram cell same length
    test. Only the last one is incorrect.
    """
    circuit_diagrams = ['(R1)', '(C1)', '[R1C2]', '(R1C2)']
    return circuit_diagrams

@pytest.fixture
def examples_circuit_diagram_help():
    return generate_examples_circuit_diagram_help()

def test_circuit_diagram_impedance_cell_same_length(
        examples_circuit_diagram_help, examples_impedance_cell_help):
    """Check that the function to find element of a list thta are not
    functions  works.

    GIVEN: a list and a circuit diagram.
    WHEN: the function to generate the impedance of a cell is tested
    THEN: the help function detects the 
    """
    for i, impedance_list in enumerate(examples_impedance_cell_help):
        assert circuit_string_impedance_cell_same_length(
            examples_circuit_diagram_help[i], impedance_list), (
            'StructuralError for a  cell '
            + examples_circuit_diagram_help[i] + '. The length of the output '
            + 'must be the same of the number of the element of the cell')


def generate_example_impedance_cells():
    """Generate an examples of circuits with both constant and non-constant
    elements for the impedance cell impedance test.
    """
    circuit_diagram_1 = '(R1)'
    parameters_1 = {'R1': 100.}
    constant_conditions_1 = {'R1': 0}
    first_circuit = generate_circuit(circuit_diagram_1, parameters_1,
                                     constant_conditions_1)
    analyzed_first_circuit = AnalisysCircuit(circuit_diagram_1, {})
    impedance_cell_1 = analyzed_first_circuit.generate_cell_impedance(
        first_circuit, i_start=0, i_end=3)
    
    circuit_diagram_2 = '(R1C2)'
    parameters_2 = {'R1': 100., 'C2': 1e-6}
    constant_conditions_2 = {'R1': 0, 'C2': 0}
    second_circuit = generate_circuit(circuit_diagram_2, parameters_2,
                                      constant_conditions_2)
    analyzed_second_circuit = AnalisysCircuit(circuit_diagram_2, {})
    impedance_cell_2 = analyzed_second_circuit.generate_cell_impedance(
        second_circuit, i_start=0, i_end=5)
    
    circuit_diagram_3 = '(R1C2[R3Q4])'
    parameters_3 = {'R1': 100., 'C2': 1e-6, 'R3': 1000., 'Q4': [1e-6, 0.6]}
    constant_conditions_3 = {'R1': 0, 'C2': 0, 'R3': 1, 'Q4': 0}
    third_circuit = generate_circuit(circuit_diagram_3, parameters_3,
                                     constant_conditions_3)
    analyzed_second_circuit = AnalisysCircuit(circuit_diagram_3, {})
    impedance_cell_3 = analyzed_second_circuit.generate_cell_impedance(
        third_circuit, i_start=5, i_end=10)
    
    example_impedance_cells = [impedance_cell_1, impedance_cell_2,
                                impedance_cell_3]
    return example_impedance_cells

@pytest.fixture
def example_impedance_cells():
    return generate_example_impedance_cells()

def generate_examples_circuit_cell_diagram():
    """Generate an index of the end of the cell for the impedance cell tests."""
    circuit_cell_diagrams = ['(R1)', '(R1C2)', '[R3Q4]']
    return circuit_cell_diagrams

@pytest.fixture
def examples_circuit_cell_diagram():
    return generate_examples_circuit_cell_diagram()

def test_impedance_list_cell_impedance(examples_circuit_cell_diagram,
                                       example_impedance_cells):
    """Check that generate_cell_impedance function returns a proper list of
    function.

    GIVEN: a correct input circuits and delimiter of the cell to be analyzed
    WHEN: in the analysis of the circuit each cell is analyzed at a time
    THEN: the output of generate_cell_impedance is a list of functions.
    """
    caller = 'generate_cell_impedance()'
    for i, impedance_cell in enumerate(example_impedance_cells):
        circuit_cell = examples_circuit_cell_diagram[i]
        assert isinstance(impedance_cell, list), (
            'TypeError in output of ' + caller + 'for \'' + circuit_cell
            + '\'. It must be a list')

        wrong_functions_index = wrong_impedance_generate_cell_impedance(
            impedance_cell)
        assert not wrong_functions_index, (
            'TypeError in output of ' + caller
            + ' for element number(s) ' + ' \'' + str(wrong_functions_index)
            + '\'. The output must contain ony funtions')

        assert circuit_string_impedance_cell_same_length(circuit_cell,
                                                         impedance_cell), (
            'StructuralError in output of ' + caller + ' with cell '
            + circuit_cell + '. The length of the output must be the same of '
            + 'the number of the element of the cell')


def consistency_brackets(circuit_diagram):
    """Given a circuit diagram, return if there is a bracket incongruence.
    Used for testing.

    Parameters
    ----------
    circuit_diagram : str
        Circuit diagram after a cycle of analysis

    Returns
    -------
    wrong_brackets : list
        List of all the bracket involbed in the bracket incongruence
    wrong_brackets_index : bool
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
                                wrong_brackets += ('\'' + str(wrong_bracket)
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

def generate_example_consistency_brackets():
    """Generate examples for the consistency brackets test. Only the last one
    is incorrect.
    """
    strings = (['()', '([])', '[()[()]]', '[(])'])
    return strings

@pytest.fixture
def example_consistency_brackets():
    return generate_example_consistency_brackets()

def test_consistency_brackets(example_consistency_brackets):
    """Check that the help function to test if a string has brackets
    consistency works.

    GIVEN: the updated circuit diagram is a string
    WHEN: the updated circuit diagram validity is tested
    THEN: the updated circuit diagram has brackets consistency
    """
    for string_ in example_consistency_brackets:
        wrong_brackets, wrong_brackets_index = consistency_brackets(
            string_)
        assert not wrong_brackets, (
            'StructuralError: inconsistent ' + str(wrong_brackets)
            + ' at ' + wrong_brackets_index + ': ' + string_ + ' from '
            + 'consistency_brackets()')

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
            wrong_characters += '\'' + char + '\', '
            wrong_characters_index.append(i)
    return wrong_characters, wrong_characters_index

def generate_example_invalid_character_update():
    """Generate examples for the invalid characters test. Only the last one
    is incorrect.
    """
    strings = (['(R1)', 'Q2(Z2CC])', '[(R1Q2)[C3(R4Q5)]]', '([Q1R2]S3)'])
    return strings

@pytest.fixture
def example_invalid_character_update():
    return generate_example_invalid_character_update()

def test_invalid_characters_updated_diagram(example_invalid_character_update):
    """Check that the help function to test if an updated string has only
    correct characters works.

    GIVEN: the updated circuit diagram is a string
    WHEN: the updated circuit diagram validity is tested
    THEN: the updated circuit diagram has only valid characters
    """
    for string_ in example_invalid_character_update:
        (wrong_characters,
        wrong_characters_index) = invalid_characters_updated_diagram(
            string_)
        assert not wrong_characters, (
            'Invalid character(s) ' + wrong_characters + ' at '
            + str(wrong_characters_index) + ' in ' + string_
            + '. Only round and square brackets, C, Q, R and '
            + 'natural numbers are valid characters')


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
                wrong_elements += ('\'' + char + str(circuit_diagram[i+1])
                                   + '\', ')
                wrong_element_index.append(i)
        elif (char.isnumeric() and circuit_diagram[0]!=char):
            if not (circuit_diagram[i-1] in {'Z','C', 'Q', 'R'}):
                wrong_elements += ('\'' + str(circuit_diagram[i-1]) + char
                                   + '\', ')
                wrong_element_index.append(i-1)
    return wrong_elements, wrong_element_index

def generate_example_inconsistent_elements_updated():
    """Generate examples for the invalid element test. Only the last one
    is incorrect.
    """
    strings = (['(R1)', 'Q1(Z2C3])', '[(R1Q2)[C3(R4Q5)]]', '([Q1R]S3)'])
    return strings

@pytest.fixture
def example_inconsistent_elements_updated():
    return generate_example_inconsistent_elements_updated()

def test_invalid_characters_updated(
    example_inconsistent_elements_updated):
    """Check that the help function to test if an updated string has only
    correct elements works.

    GIVEN: the updated circuit diagram is a string with aony valid characters
    WHEN: the updated circuit diagram validity is tested
    THEN: the updated circuit diagram has only valid elements
    """
    for string_ in example_inconsistent_elements_updated:
        (wrong_elements,
        wrong_element_index) = inconsistent_elements_updated_diagram(
            string_)
        assert not wrong_elements, (
            'element inconsistency for '+ wrong_elements + ' at '
            + str(wrong_element_index) + ' in updated string: '
            + string_ + '. An element is composed by a valid '
            + 'letter followed by a natural number')
                     
def generate_example_updated_diagram():
    """Generate examples of the updated circuit diagram given the previous
    circuit diagram and the start and end of the analyzed cell, for the update
    diagram test.
    """
    circuit_diagrams = (['(R1)', '(Q1[Z2C3])', '[(R1Q2)[C3(R4Q5)]]',
                        '([Q1R]S3)'])
    cell_count = 1
    example_i_starts = [0, 3, 1, 1]
    example_i_ends = [3, 8, 6, 5]
    example_updated_diagrams = []
    for i, diagram in enumerate(circuit_diagrams):
        circuit_ = AnalisysCircuit(diagram, {})
        _ = circuit_.update_diagram(example_i_starts[i], example_i_ends[i],
                                    cell_count)
        example_updated_diagrams.append(circuit_.circuit_diagram)
    return example_updated_diagrams

@pytest.fixture
def example_updated_diagram():
    return generate_example_updated_diagram()

def test_update_diagram_valid_diagram(example_updated_diagram):
    """Check that update_diagram() method returns a valid diagram.

    GIVEN: a valid circuit diagram, a valid position of the start and end of
    the string substitution.
    WHEN: at the end of an analysis cycle the circuit diagram is updated
    THEN: the updated diagram is valid
    """
    caller = 'update_diagram()'
    for diagram in example_updated_diagram:
        assert isinstance(diagram, str), (
            'TypeError for circuit scheme in ' + caller+ '. It must be a '
            + 'string')
        assert diagram, ('StructuralError: empty string in ' + caller)
        wrong_brackets, wrong_brackets_index = consistency_brackets(diagram)
        assert not wrong_brackets, (
                'StructuralError: inconsistent \'' + str(wrong_brackets)
                + '\' at ' + wrong_brackets_index + ': ' + diagram + ' in '
                + caller)
        (wrong_characters,
        wrong_characters_index) = invalid_characters_updated_diagram(diagram)
        assert not wrong_characters, (
            'Invalid character(s) ' + wrong_characters + ' at '
            + str(wrong_characters_index) + ' in ' + diagram + ' from '
            + caller + '. Only round and square brackets, C, Q, R and '
            + 'natural numbers are valid characters')
        (wrong_elements,
         wrong_element_index) = inconsistent_elements_updated_diagram(diagram)
        assert not wrong_elements, (
            'element inconsistency for '+ wrong_elements + ' at '
            + str(wrong_element_index) + ' from ' + caller + ': '
            + diagram + '. An element is composed by a valid '
            + 'letter followed by a natural number')


def generate_example_new_element():
    """Generate the updated circuit diagram given the previous circuit string
    and the start and end of the analyzed cell, for the update diagram test.
    """
    circuit_diagrams = (['(R1)', '(Q1[Z2C3])', '[(R1Q2)[C3(R4Q5)]]',
                        '([Q1R2]R3)'])
    cell_count = [1, 1, 1, 'e']
    example_i_starts = [0, 3, 1, 1]
    example_i_ends = [3, 8, 6, 5]
    example_new_element = []
    for i, diagram in enumerate(circuit_diagrams):
        circuit_ = AnalisysCircuit(diagram, {})
        new_element = circuit_.update_diagram(example_i_starts[i],
                                              example_i_ends[i], cell_count[i])
        example_new_element.append(new_element)
    return example_new_element

@pytest.fixture
def example_new_element():
    return generate_example_new_element()

def test_update_diagram_new_element(example_new_element):
    """Check that update_diagram returns a valid new element.

    GIVEN: a valid circuit diagram, a valid position of the start and end of
    the string substitution.
    WHEN: at the end of an analysis cycle the circuit diagram is updated
    THEN: the new element for the updated diagram is valid
    """
    caller = 'update_diagram()'
    for new_element in example_new_element:
        assert isinstance(new_element, str), (
            'TypeError for circuit scheme in ' + caller+ '. It must be a '
            + 'string')
        assert new_element, ('StructuralError: empty string in ' + caller)
        assert len(new_element)==2, (
            'Invalid length for ' + new_element + ' in ' + caller + '. It '
            + 'has to be of length 2')
        assert new_element.startswith('Z'), (
            'StrcuturalError for '+ new_element + ' in ' + caller
            + '. A  new element must begin with a \'Z\'')
        last_element = new_element[-1]
        assert last_element.isnumeric(), (
            'StrcuturalError for '+ new_element + ' in ' + caller
            + '. A  new element must end with a numeric char')


def generate_analyzed_circuit_final_results():
    """Generate examples of analyzed circuit with the final results
    attributes set, for the get_final_results test. Only the last one is
    incorrect.
    """
    function_r = lambda x, y: y
    function_c = lambda x, y: 1/(x*y)
    first_impedance_map = {'R1': (function_r, 1000.)}
    first_analyzed_circuit = AnalisysCircuit('(Z1)', first_impedance_map)
    first_analyzed_circuit.set_final_results()
    second_impedance_map = {'C1': (function_c, 1e-6)}
    second_analyzed_circuit = AnalisysCircuit('(Z1)', second_impedance_map)
    second_analyzed_circuit.set_final_results()
    third_impedance_map = {'R1': (function_r, 2000.), 'C2': (function_c, 1e-6),
                           'Z1': (add(function_r, function_r), 'equivalent')}
    third_analyzed_circuit = AnalisysCircuit('(Z1)', third_impedance_map)
    third_analyzed_circuit.set_final_results()
    fourth_impedance_map = {'R1': ('f(x)', -1)}
    fourth_analyzed_circuit = AnalisysCircuit('(Z1)', fourth_impedance_map)
    fourth_analyzed_circuit.set_final_results()
    examples_analyzed_circuit_final_results = [
        first_analyzed_circuit, second_analyzed_circuit,
        third_analyzed_circuit, fourth_analyzed_circuit]
    return examples_analyzed_circuit_final_results

def generate_examples_final_impedance():
    """Generate examples of the final impedance for the get_final_results
    test. Only the last one is incorrect.
    """
    examples_final_impedance = []
    analyzed_circuits = generate_analyzed_circuit_final_results()
    for circuit_ in analyzed_circuits:
        final_impedance = circuit_.impedance
        examples_final_impedance.append(final_impedance)
    return examples_final_impedance

@pytest.fixture
def examples_final_impedance():
    return generate_examples_final_impedance()

def test_impedance_get_final_results(examples_final_impedance):
    """Check that the final impedance of an analyzed circuit is a function.

    GIVEN: a valid analyzed circuit.
    WHEN: the results of the analysis are set into the analysis circuit object
    THEN: the final impedance is a function.
    """
    for final_impedance in examples_final_impedance:
        assert inspect.isfunction(final_impedance), (
          'TypeError for the final impedance of the AnalysisCircuit. It must '
          + 'be a function')


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
    """Generate examples of input parameters, for the get_final_results test.
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


def generate_example_final_parameters_map():
    """Generate examples of final parameters_maps, for the get_final_results
    test. Only the last one is incorrect.
    """
    examples_final_parameters_map = []
    analyzed_circuits = generate_analyzed_circuit_final_results()
    for circuit_ in analyzed_circuits:
        final_parameters_map = circuit_.parameters_map
        examples_final_parameters_map.append(final_parameters_map)
    return examples_final_parameters_map

@pytest.fixture
def example_final_parameters_map():
    return generate_example_final_parameters_map()

def generate_example_input_parameters():
    """Generate examples of final parameters_maps of analyzed circuits, for
    the get_final_results test. Only the last one is incorrect."""
    examples_input_parameters = [{'R1': (1000., 0)}, {'C1': (1e-6, 0)}, 
                                 {'R1': (2000., 0), 'C2': (1e-6, 0)},
                                 {'R1': (100., 0)}]
    return examples_input_parameters

@pytest.fixture
def example_input_parameters():
    return generate_example_input_parameters()

def test_parameters_get_final_results(example_final_parameters_map,
                                      example_input_parameters):
    """Check that the final parameters_map has all the non-constant input
    elements

    GIVEN: a valid analyzed circuit.
    WHEN: the results of the analysis are set into the analysis circuit object
    THEN: the final parameters_map matches the inout ones
    """
    for i, final_parameters_map in enumerate(example_final_parameters_map):
        wrong_elements = wrong_match_element_initial_circuit_final_parameters(
            final_parameters_map, example_input_parameters[i])
        assert not wrong_elements, (
            'Bad match between non constant elements of the initial circuit '
            + 'and the final analysis parameter. ' + wrong_elements + 'not '
            + 'found')

        wrong_parameters = wrong_match_parameter_initial_circuit_final_parameters(
            final_parameters_map, example_input_parameters[i])
        assert not wrong_parameters, (
            'Bad match between parameters of the initial circuit and the '
            + 'final analysis parameter. Parameter of element '
            + wrong_parameters + 'not found')


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

def generate_example_final_elements_list_wrong_match():
    """Generate correct examples of final element lists of analyzed circuits,
    for the final_elements_list test.
    """
    example_final_elements_list = [['R1'], ['C1'], ['R1', 'C2'], []]
    return example_final_elements_list

@pytest.fixture
def example_final_elements_list_wrong_match():
    return generate_example_final_elements_list_wrong_match()

def test_wrong_match_element_final_parameters_list_elements(
        example_final_elements_list_wrong_match,
        example_final_parameters_map_wrong_match):
    """Check that the help function that finds the element mismatch between
    final parameters dictionaries and the final element list works

    GIVEN: a valid analyzed circuit.
    WHEN: the function to list the non-constant element of the analysis is
    called
    THEN: the final non-constant element list is valid.
    """
    for i, final_parameters_map in enumerate(
        example_final_parameters_map_wrong_match):
        wrong_elements = wrong_match_element_final_parameters_list_elements(
            example_final_elements_list_wrong_match[i], final_parameters_map)
        assert not wrong_elements, (
            'Bad match between final elements of the analyzed circuit and '
            + 'its list of elements. ' + wrong_elements + 'not found')


def generate_example_final_elements_list():
    """Generate examples of final elements list out of the final
    parameters_map,  for the final_elements_list test.
    """
    final_elements_lists = []
    analyzed_circuits = generate_analyzed_circuit_final_results()
    for circuit_ in analyzed_circuits:
        final_elements_lists.append(circuit_.list_elements())
    return final_elements_lists

@pytest.fixture
def example_final_elements_list():
    return generate_example_final_elements_list()

def generate_example_final_parameters_map_element_list():
    """Generate correct examples of final parameters lists of
    analyzed circuits, for the list_elements test.
    """
    example_final_parameters = [{'R1': 1000.}, {'C1': 1e-6},
                                {'R1': 2000., 'C2': 1e-6},
                                {'C1': 2e-6}]
    return example_final_parameters

@pytest.fixture
def example_final_parameters_map_element_list():
    return generate_example_final_parameters_map_element_list()

def test_list_elements(example_final_elements_list,
                       example_final_parameters_map_element_list):
    """Check that the list_elements() method return a list containing all the
    non-constant element strings, with all the element inside the
    parameters_map and of the same length of its list of keys.

    GIVEN: a valid analyzed circuit with the final results set.
    WHEN: the function to list the non-constant element of the analysis is
    called
    THEN: the final element list is a valid list containg all and only the
    non-constant elements.
    """
    caller = 'list_elements()'
    for i, element_list in enumerate(example_final_elements_list):
        assert isinstance(element_list, list), (
            'TypeError for ' + caller + '. The output must be a list')
        assert len(element_list)==len(list(
            example_final_parameters_map_element_list[i].keys())), (
            'StructuralError for ' + caller + ' between final elements of the '
            + 'analyzed circuit and its list of elements. They have to be of '
            + 'the same length')

        wrong_elements = wrong_match_element_final_parameters_list_elements(
            element_list, example_final_parameters_map_element_list[i])
        assert not wrong_elements, (
            'Bad match for ' + caller + ' between final elements of the '
            + 'analyzed circuit and its list of elements. ' + wrong_elements
            + 'not found')



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

def generate_example_final_parameters_list_wrong_match():
    """Generate examples of final parameters lists of analyzed circuits, for
    the final_parameters_list test.
    """
    example_final_parameters_list = [[100.], [1e-6], [2000., 1e-6], [10000.]]
    return example_final_parameters_list

@pytest.fixture
def example_final_parameters_list_wrong_match():
    return generate_example_final_parameters_list_wrong_match()

def test_wrong_match_parameters_final_parameters_list_elements(
        example_final_parameters_list_wrong_match,
        example_final_parameters_map_wrong_match):
    """Check that the help function that finds the element mismatch between
    final parameters dictionaries and the final element list works

    GIVEN: a valid analyzed circuit.
    WHEN: the function to list the non-constant parameters of the analysis is
    called
    THEN: the final non-constant parameter list is valid.
    """
    for i, final_parameters_map in enumerate(
        example_final_parameters_map_wrong_match):
        wrong_parameters = wrong_match_parameter_final_parameters_list_parameters(
            example_final_parameters_list_wrong_match[i], final_parameters_map)
        assert not wrong_parameters, (
            'Bad match between final parameters of the analyzed circuit and '
            + 'its list of parameters. ' + wrong_parameters + 'not found')


def generate_example_final_parameters_map_parameters_list():
    """Generate correct examples of final parameters lists of
    analyzed circuits, for the list_parameters test.
    """
    example_final_parameters = [{'R1': 1000.}, {'C1': 1e-6},
                                {'R1': 2000., 'C2': 1e-6},
                                {'R1': 10000.}]
    return example_final_parameters

@pytest.fixture
def example_final_parameters_map_parameters_list():
    return generate_example_final_parameters_map_parameters_list()

def generate_example_final_parameters_list():
    """Generate examples of final parameters list out of the final
    parameters_map, for the list_parameters test.
    """
    final_parameters_lists = []
    analyzed_circuits = generate_analyzed_circuit_final_results()
    for circuit_ in analyzed_circuits:
        final_parameters_lists.append(circuit_.list_parameters())
    return final_parameters_lists

@pytest.fixture
def example_final_parameters_list():
    return generate_example_final_parameters_list()

def test_list_parameters(example_final_parameters_list,
                         example_final_parameters_map_parameters_list):
    """Check that the list_parameters() method return a list containing all the
    non-constant parameters, with all the parameters inside the
    parameters_map and of the same length of its list of values.

    GIVEN: a valid analyzed circuit with the final results set.
    WHEN: the function to list the non-constant parameters of the analysis is
    called
    THEN: the final parameters list is a valid list containg all and only the
    non-constant parameters.
    """
    caller = 'list_parameters()'
    for i, final_parameters_list in enumerate(example_final_parameters_list):
        assert isinstance(final_parameters_list, list), (
            'TypeError for ' + caller + '. The output must be a list')
        assert len(final_parameters_list)==len(list(
            example_final_parameters_map_parameters_list[i].values())), (
            'StructuralError for ' + caller + ' between final parameters of '
            + 'the analyzed circuit and its list of parameters. They have to '
            + 'be of the same length')
        wrong_parameters = wrong_match_parameter_final_parameters_list_parameters(
            final_parameters_list,
            example_final_parameters_map_parameters_list[i])
        assert not wrong_parameters, (
            'Bad match for ' + caller + ' between final parameters of the '
            + 'analyzed circuit and its list of parameters. ' 
            + wrong_parameters + 'not found')


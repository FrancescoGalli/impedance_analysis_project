import pytest
from hypothesis.extra import numpy as enp
from hypothesis import given, settings
import hypothesis.strategies as st
import numpy as np
import inspect

from generate_impedance import impedance_R
from generate_impedance import impedance_C
from generate_impedance import impedance_Q
from generate_impedance import get_impedance_const_RCQ_element
from generate_impedance import get_impedance_RCQ_element
from generate_impedance import get_impedance_function_element
from generate_impedance import add
from generate_impedance import serialComb
from generate_impedance import reciprocal
from generate_impedance import parallelComb
from generate_impedance import get_position_opening_bracket
from generate_impedance import generate_cell_impedance
from generate_impedance import update_string

def generate_circuit():
    """Generate a test circuit string."""
    circuit_string = '(R1C2[R3Q4])'
    return circuit_string

def generate_initial_parameters():
    """Generate a list of parameters."""
    p1 = 7000
    p2 = 8e-6
    p3 = 10000
    p4 = ([0.07e-6, 0.7])
    initial_parameters = ([p1, p2, p3, p4])
    return initial_parameters

def generate_constant_elements_array():
    """Generate an array for constant elements."""
    constant_array = ([0, 0, 1, 0])
    return constant_array

@pytest.fixture
def circuit_string():
    return generate_circuit()

@pytest.fixture
def caller():
    return 'input'

def test_is_string(circuit_string, caller):
    """Check that the circuit string is a string."""
    assert isinstance(circuit_string, str), (
        'type error for circuit scheme in ' + caller 
        + '. It must be a string')

def test_empty_string(circuit_string, caller):
    """Check that the string is not empty."""
    assert circuit_string, 'empty string in ' + caller

def test_input_string_open_brakets(circuit_string):
    """Check that there is an open round or square bracket as first character
    in the string.
    """
    assert (circuit_string.startswith('(') 
            or circuit_string.startswith('[')), (
                'no initial open bracket detected')

def test_input_string_close_brakets(circuit_string):
    """Check that there is a close round or square bracket as last character
    in the string.
    """
    assert (circuit_string.endswith(')') or circuit_string.endswith(']')), (
        'no final close bracket detected')

def test_string_different_number_brackets(circuit_string, caller):
    """Check that there is an equal number of close and open bracket, for
    both square and round types.
    """
    assert (circuit_string.count('(') == circuit_string.count(')')
            and circuit_string.count('[') == circuit_string.count(']')), (
                'inconsistent number of open and close brackets in \'' 
                + circuit_string + '\'  in ' + caller)

def test_string_consistency_brackets(circuit_string, caller):
    """Check that there is a consistency among the brackets.

    GIVEN: circuit_string is a string with an equal number of open and close 
    brackets of the same type (round or square)
    """
    position_of_brackets = [i for i, _ in enumerate(circuit_string) 
                            if (circuit_string.startswith(')', i) 
                                or circuit_string.startswith(']', i)) ]                                                              
    cut_parameter = 0
    for _ in position_of_brackets:
        for i, char_i in enumerate(circuit_string):
            if(char_i==')' or char_i==']'):
                if char_i==')': bracket, wrong_bracket = '(', '['
                if char_i==']': bracket, wrong_bracket = '[', '('
                found = False
                analyzed_string = circuit_string[:i]
                for j, _ in enumerate(analyzed_string):
                    bracket_index = len(analyzed_string) - 1 - j
                    if (circuit_string[bracket_index]==bracket 
                        and found==False):
                        found = True
                        index_wrong_bracket = circuit_string[
                            bracket_index+1:i].find(wrong_bracket)
                        assert index_wrong_bracket==-1, (
                            'inconsistent \'' + wrong_bracket + '\' at '
                            + str(index_wrong_bracket + bracket_index 
                            + 1 + cut_parameter) + ': ' + circuit_string 
                            + 'in ' + caller)
                        circuit_string = (circuit_string[:bracket_index] 
                                          + circuit_string[bracket_index+1:i]
                                          + circuit_string[i+1:])
                        cut_parameter += 2
                        break
                if found:
                    break

def test_input_string_characters(circuit_string):
    """Check that a string containes only valid characters:
    '(', ')', '[', ']', 'C', 'Q', 'R' and natural numbers.
    """
    wrong_characters = ''
    wrong_characters_index = []
    for i, char in enumerate(circuit_string):
        if (char not in {'(', ')', '[', ']', 'C', 'Q', 'R'} 
            and not char.isnumeric()):
            wrong_characters += '\'' + char + '\', '
            wrong_characters_index.append(i)
    assert not wrong_characters, (
        'Invalid character(s) ' + wrong_characters + ' at ' 
        + str(wrong_characters_index) + ' in ' + circuit_string + '. Only ' 
        + 'round and square brackets, C, Q, R and natural ' 
        + 'numbers are allowed')
        
def test_input_string_element_consistency(circuit_string):
    """Check the element consistency of a string that containes only valid 
    characters: each element is composed by a capital letter among 
    {'C', 'Q', 'R'} followed by a natural number.
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
                wrong_elements+= '\''+str(circuit_string[i-1])+char+'\', '
                wrong_element_index.append(i-1)
    assert not wrong_elements, (
        'element inconsistency for '+ wrong_elements + ' at ' 
        + str(wrong_element_index) + ': ' + circuit_string + '. An element ' 
        + 'is composed by a valid letter followed by a natural number')

def test_input_string_number_sequency(circuit_string):
    """Check that there is a correspondency between the element number and the
    order of appearance of its element.
    """
    wrong_numbers = ''
    wrong_numbers_index = []
    numeric_char_counter = 0
    for i, char in enumerate(circuit_string):
        if char.isnumeric():
            numeric_char_counter += 1
            if numeric_char_counter!=int(char):
                wrong_numbers += '\'' + str(circuit_string[i-1:i+1]) + '\', '
                wrong_numbers_index.append(i)
    assert not wrong_numbers, (
        'wrong number for element(s) '+ wrong_numbers + 'at ' 
        + str(wrong_numbers_index) + ' in ' + circuit_string 
        + '. Element numbers must increase of 1 unit per time')
    

@pytest.fixture
def parameters():
    return generate_initial_parameters()

def test_parameters_is_list(parameters, caller):
    """Check that the parameters are a list."""
    assert isinstance(parameters, list), (
        'type error for parameters in ' + caller + ' . It must be a list')

def test_parameters_type(parameters, caller):
    """Check that the only valid types as parameters are float, integer 
    and lists.

    GIVEN: parameters is list
    """
    wrong_type = ''
    wrong_type_index = []
    for i, parameter in enumerate(parameters):
        if (not isinstance(parameter, float) 
            and not isinstance(parameter, int)
            and not isinstance(parameter, list)):
            wrong_type += '\'' + str(parameter) + '\', '
            wrong_type_index.append(i)
    assert not wrong_type, (
        'type error for parameter(s) number ' + str(wrong_type_index)
        + ' ' + wrong_type + ' in ' + str(parameters) + ' in ' + caller 
        + '. Parameters can only be floats, integers or lists')

def test_parameters_values(parameters, caller):
    """Check that parameters are positive.
    
    GIVEN: parameters is a float or integer
    """
    wrong_value = ''
    wrong_value_index = []
    for i, parameter in enumerate(parameters):
        if (isinstance(parameter, float) or isinstance(parameter, int)):
            if parameter<=0:
                wrong_value += '\'' + str(parameter) + '\', '
                wrong_value_index.append(i)
    assert not wrong_value, (
        'value error for parameter(s) number ' + str(wrong_value_index) + ' '
        + wrong_value + ' in ' + str(parameters) + ' in ' + caller 
        + '. Float parameters must be positive')
        
def test_parameters_list_two_elements(parameters, caller):
    """Check that the list parameters contain exactly 2 parameters.
    
    GIVEN: parameters is a float or integer
    """
    wrong_elements = ''
    wrong_elements_index = []
    for i, parameter in enumerate(parameters):
        if isinstance(parameter, list):
            if len(parameter)!=2:
                wrong_elements_index.append(i)
                wrong_elements+= '\''+str(parameter)+'\', '
    assert not wrong_elements, (
        'type error for parameter(s) number ' + str(wrong_elements_index) 
        + ': \'' + wrong_elements + '\' in ' + str(parameters) + ' in ' 
        + caller + '. Lists parameters must contain exactly 2 parameters')

def test_parameters_list_type(parameters, caller):
    """Check that parameters contains only floats or integers.

    GIVEN: parameters is a list of length 2.
    """
    wrong_types = ''
    wrong_types_index = []
    for i, parameter in enumerate(parameters):
        if isinstance(parameter, list):
            for _, p in enumerate(parameter):
                if (not isinstance(p, float) and not isinstance(p, int)):
                    wrong_types += '\'' + str(p) + '\', '
                    wrong_types_index.append(i)
    assert not wrong_types, (
        'type error for parameter(s) '+ wrong_types  +' in parameter(s) ' 
        + 'number ' + str(wrong_types_index) + ' contained in: \'' + '\' in ' 
        + str(parameters) + ' in ' + caller + '. Lists parameters must ' 
        + 'only contain floats or integers')

def test_parameters_list_value(parameters, caller):
    """Check that the two object contained in the list parameters meet the 
    value requirements: the first one is positive, the second one is between 
    0 and 1.

    GIVEN: parameters is a list of float or integer of length 2.
    """
    wrong_value = ''
    wrong_value_index = ''
    for i, parameter in enumerate(parameters):
        if isinstance(parameter, list):
            if parameter[0]<=0:
                    wrong_value += '\'' + str(parameter[0]) + '\', '
                    wrong_value_index += 'first of [' + str(i) + ']'
            if (parameter[1]<0 or parameter[1]>1):
                    wrong_value += '\'' + str(parameter[1]) + '\', '
                    wrong_value_index += 'second of [' + str(i) + ']'
    assert not wrong_value, (
        'value error for parameter(s) '+ wrong_value + wrong_value_index 
        + ' parameter(s) ' + ' contained in: \'' + str(parameters) + ' in ' 
        + caller  + '. Lists parameters must contain as first parameter a ' 
        + 'positive float and as second parameter a float between 0 and 1')

def elements(circuit_string):
    """Return the list of elements ('C', 'Q' or 'R' ) of a string. 
    Used for testing.
    """
    elements = []
    for char in circuit_string:
        if char in {'C', 'Q', 'R'}:
            elements.append(char)
    return elements

def test_parameters_length(circuit_string, parameters):
    """Check that the list of elements and the list of parameters 
    have the same size.
    """
    elements_array = elements(circuit_string)
    assert len(elements_array)==len(parameters), (
        'element count and parameters list size must be the same. '
        + 'Element count: ' + str(len(elements_array)) 
        + ', parameters size: ' + str(len(parameters)))

def test_parameters_match(circuit_string, parameters):
    """Check that there is a consistent correspondance between the elements 
    and the parameters: C and R must have a float as parameter, Q a list.
    """
    elements_array = elements(circuit_string)
    wrong_match = ''
    wrong_match_index = []
    for i, element in enumerate(elements_array):
        if element in {'C', 'R'}:
            if (not isinstance(parameters[i], float) 
                and not isinstance(parameters[i], int)):
                wrong_match += ('\'[' + str(element) + ',' 
                                + str(parameters[i]) + ']\', ')
                wrong_match_index.append(i)
        else:
            if not isinstance(parameters[i], list):
                wrong_match += ('\'[' + str(element) + ',' 
                                + str(parameters[i]) + ']\', ')
                wrong_match_index.append(i)
    assert not wrong_match, (
        'bad match for '+ wrong_match + ' in ' + str(wrong_match_index) 
        + ': elements \'' + str(elements_array) + ' with parameters '
        + str(parameters) + '. \'R\' and \'C\' elements must have '
        + 'a float as parameter, \'Q\' must have a list')

@pytest.fixture
def constant_elements():
    return generate_constant_elements_array()

def test_constant_type(constant_elements):
    """Check that the constant arrey is a list."""
    assert isinstance(constant_elements, list), (
        'type error for circuit scheme. It must be a list')

def test_constant_list_type(constant_elements):
    """Check that the constant elements in constant_elements are integers.
    
    GIVEN: constant_elements is an array
    """
    wrong_types = ''
    wrong_types_index = []
    for i, constant_element in enumerate(constant_elements):
        if not isinstance(constant_element, int):
            wrong_types+= '\'' + str(constant_element) + '\', '
            wrong_types_index.append(i)
    assert not wrong_types, (
        'type error for constant element(s) ' + str(wrong_types) + ' number ' 
        + str(wrong_types_index) + ' in ' + str(constant_elements) 
        + '. Constant element must be an integer')

def test_constant_list_value(constant_elements):
    """Check that the constant elements in constant_elements are non 
    negative.
    
    GIVEN: constant_elements an array
    """
    wrong_value = ''
    wrong_value_index = []
    for i, constant_element in enumerate(constant_elements):
        if constant_element<0 or constant_element>1:
            wrong_value+= '\'' + str(constant_element) + '\', '
            wrong_value_index.append(i)
    assert not wrong_value, (
        'value error for constant element(s) '+ wrong_value + 'at ' 
        + str(wrong_value_index) + 'in \'' + str(constant_elements)
        + '\'. Constant array must contain only 0 or 1')

def test_constant_length(parameters, constant_elements):
    """Check that the list of elements and the list of parameters have 
    the same size.
    """
    assert len(parameters)==len(constant_elements), (
        'parameters and constant array list size must be the same. ' 
        + 'Parameters size: ' + str(len(parameters)) + ', constant array ' 
        + 'size: ' + str(len(constant_elements)))

@given(frequency=enp.arrays(dtype=float, shape=10, 
                            elements=st.floats(1, 1e4), unique=True), 
       resistance=st.floats(min_value=10, max_value=1e5))
@settings(max_examples = 10)
def test_impedance_R_array(resistance, frequency):
    """Check that the definition of the impedance of resistors returns an 
    array.
    """
    impedance = impedance_R(resistance, frequency)
    assert isinstance(impedance, np.ndarray), (
        'type error for resistive impedance. It must be a numpy array')

@given(frequency=enp.arrays(dtype=float, shape=10, 
                            elements=st.floats(1, 1e4), unique=True), 
       resistance=st.floats(min_value=10, max_value=1e5))
@settings(max_examples = 10)
def test_impedance_R_complex_array(resistance, frequency):
    """Check that the definition of the impedance of resistors returns a
    complex object.
    """
    impedance = impedance_R(resistance, frequency)
    assert np.iscomplexobj(impedance), (
        'type error for resistive impedance. It must be a complex ' 
        + 'numpy array')

@given(frequency=enp.arrays(dtype=float, shape=10, 
                            elements=st.floats(1, 1e4), unique=True), 
       capacitance=st.floats(min_value=1e-9, max_value=1e-5))
@settings(max_examples = 10)
def test_impedance_C_array(capacitance, frequency):
    """Check that the definition of the impedance of capacitors returns an 
    array.
    """
    impedance = impedance_C(capacitance, frequency)
    assert isinstance(impedance, np.ndarray), (
        'type error for capacitative impedance. It must be a numpy array')

@given(frequency=enp.arrays(dtype=float, shape=10, 
                            elements=st.floats(1, 1e4), unique=True), 
       capacitance=st.floats(min_value=1e-9,max_value=1e-5))
@settings(max_examples = 10)
def test_impedance_C_complex_array(capacitance, frequency):
    """Check that the definition of the impedance of capacitors returns a 
    complex object.
    """
    impedance = impedance_C(capacitance, frequency)
    assert np.iscomplexobj(impedance), (
        'type error for capacitative impedance. It must be a complex ' 
        + 'numpy array')

@given(frequency=enp.arrays(dtype=float, shape=10, 
                            elements=st.floats(1, 1e4), unique=True), 
       Q=st.floats(min_value=1e-9,max_value=1e-5),
       n=st.floats(min_value=0., max_value=1.))
@settings(max_examples = 10)
def test_impedance_Q_array(Q, n, frequency):
    """Check that the definition of the impedance of CPE returns an 
    array.
    """
    impedance = impedance_Q(Q, n, frequency)
    assert isinstance(impedance, np.ndarray), (
        'type error for CPE impedance. It must be a numpy array')

@given(frequency=enp.arrays(dtype=float, shape=10, 
                            elements=st.floats(1, 1e4), unique=True), 
       Q=st.floats(min_value=1e-9,max_value=1e-5),
       n=st.floats(min_value=0., max_value=1.))
@settings(max_examples = 10)
def test_impedance_Q_complex_array(Q, n, frequency):
    """Check that the definition of the impedance of resistors returns a 
    complex object.
    """
    impedance = impedance_Q(Q, n, frequency)
    assert np.iscomplexobj(impedance), (
        'type error for CPE impedance. It must be a complex numpy array')

def generate_element_types():
    """Generate the three possible element types."""
    element_types = (['R', 'C', 'Q'])
    return element_types

@pytest.fixture
def element_types():
    return generate_element_types()

def generate_parameters_type():
    """Generate three possible element parameters."""
    element_parameters = ([10, 3e-6, [2e-6, 0.5]])
    return element_parameters

@pytest.fixture
def element_parameters():
    return generate_parameters_type()

def test_get_impedance_const_RCQ_element(element_types, element_parameters):
    """Check that get_impedance_const_RCQ_element_type function returns 
    a function.

    GIVEN: element_type is a valid element type (R, C or Q) and a valid 
    parameter.
    WHEN: I am calculating the correspondant impedance function while keeping
    the parameter(s) of this element constant.
    THEN: the impedance funtion is a function
    """
    wrong_element = ''
    wrong_element_index = []
    for i, element_type in enumerate(element_types):
        const_parameter = element_parameters[i]
        impedance_element = get_impedance_const_RCQ_element(element_type, 
                                                        const_parameter)
        if not inspect.isfunction(impedance_element):
            wrong_element+= '\'' + str(element_type) + '\', '
            wrong_element_index.append(i)
    assert not wrong_element, (
        'type error in output of get_impedance_const_RCQ_element_type() ' 
        + 'for element type(s) number ' + str(wrong_element_index) 
        + ' \'' + wrong_element + '\' in ' + str(element_type)
        + '. Impedance function for an element must return a function')

def generate_circuit_parameters():
    """Generate a possible circuit parameters list."""
    circuit_parameters = ([100])
    return circuit_parameters

@pytest.fixture
def circuit_parameters():
    return generate_circuit_parameters()

def test_get_impedance_RCQ_element_function(element_types, circuit_parameters,
                                            element_parameters):
    """Check that get_impedance_RCQ_element function returns a function as 
    first argument.

    GIVEN: element_type as a valid element type (R, C or Q), a valid parameter 
    and a valid parameter list.
    WHEN: I am calculating the correspondant impedance function.
    THEN: the impedance funtion is a function.
    """
    wrong_element = ''
    wrong_element_index = []
    for i, element_type in enumerate(element_types):
        impedance_element, _ = get_impedance_RCQ_element(element_type, 
                                                     circuit_parameters, 
                                                     element_parameters[i])
        if not inspect.isfunction(impedance_element):
            wrong_element+= '\'' + str(element_type) + '\', '
            wrong_element_index.append(i)
    assert not wrong_element, (
        'type error in output of get_impedance_RCQ_element() ' 
        + 'for element type(s) number ' + str(wrong_element_index) 
        + ' \'' + wrong_element + '\' in ' + str(element_type)
        + '. Impedance function for an element must return as first argument ' 
        + 'a function')
    
def test_get_impedance_RCQ_element_parameters(element_types, 
                                              circuit_parameters,
                                              element_parameters):
    """ Check that the second argument of get_impedance_RCQ_element function
    is a valid list of parameters.

    GIVEN: a valid element type (R, C or Q), a valid description of the
    circuit and valid parameters of the analysed circuit so far.
    WHEN: I am calculating the correspondant impedance function.
    THEN: the parameters for the current element funtion are valid.
    """
    caller = 'get_impedance_RCQ_element()'
    for i, element_type in enumerate(element_types):
        _, parameters_test = get_impedance_RCQ_element(element_type,
                                                  circuit_parameters, 
                                                  element_parameters[i])
        test_parameters_is_list(parameters_test, caller)
        test_parameters_type(parameters_test, caller)
        test_parameters_list_two_elements(parameters_test, caller)
        test_parameters_list_type(parameters_test, caller)
        test_parameters_values(parameters_test, caller)
        test_parameters_list_value(parameters_test, caller)

def generate_element_strings():
    """Generate the three possible element types."""
    element_strings = (['R2', 'C2', 'Q2', 'Z2'])
    return element_strings

@pytest.fixture
def element_strings():
    return generate_element_strings()

def generate_impedance_circuit():
    element_type = 'R'
    list_parameters = []
    element_parameter = 100
    impedance_circuit = []
    impedance_element, _ = get_impedance_RCQ_element(element_type, 
                                                     list_parameters, 
                                                     element_parameter)
    impedance_circuit.append(impedance_element)
    impedance_circuit.append(impedance_element)
    return impedance_circuit

@pytest.fixture
def impedance_circuit():
    return generate_impedance_circuit()

def generate_elements_circuit():
    """Generate the three possible element types."""
    elements_circuit = (['R1'])
    return elements_circuit

@pytest.fixture
def elements_circuit():
    return generate_elements_circuit()

def generate_element_parameters():
    element_parameters = ([10, 2e-6, [1e-6, 0.5], 100])
    return element_parameters

@pytest.fixture
def element_parameters():
    return generate_element_parameters()

def generate_circuit_parameters_get_impedance():
    """Generate three possible element parameters."""
    _parameters = ([100])
    return _parameters

@pytest.fixture
def circuit_parameters_get_impedance():
    return generate_circuit_parameters_get_impedance()

def generate_constant_elements_get_impedance():
    """Generate the three possible element types."""
    constant_elements_get_impedance = ([0, 0])
    return constant_elements_get_impedance

@pytest.fixture
def constant_elements_get_impedance():
    return generate_constant_elements_get_impedance()

def test_get_impedance_function_element_function(
        element_strings, impedance_circuit, element_parameters,
        circuit_parameters_get_impedance, elements_circuit, 
        constant_elements_get_impedance):
    """Check that get_impedance_function_element function returns a 
    function as first argument.
    
    GIVEN: a valid element type (R, C, Q or Z followed by a number), 
    a valid description of the circuit and valid parameters of the 
    analysed circuit so far.
    WHEN: I am calculating the correspondant impedance function.
    THEN: the impedance funtion is a function.
    """
    wrong_element = ''
    wrong_element_index = []
    nominal_parameters = ([100, 0])
    for i, element_string in enumerate(element_strings):
        nominal_parameters[1]=element_parameters[i]
        elements_circuit_test = elements_circuit.copy()
        impedance_element, *_ = get_impedance_function_element(
            element_string, impedance_circuit, nominal_parameters, 
            circuit_parameters_get_impedance, elements_circuit_test,
            constant_elements_get_impedance)
        if not inspect.isfunction(impedance_element):
            wrong_element+= '\'' + str(element_string) + '\', '
            wrong_element_index.append(i)
    assert not wrong_element, (
        'type error in output of get_impedance_function() ' 
        + 'for element type(s) number ' + str(wrong_element_index) 
        + ' \'' + wrong_element + '\' in ' + str(element_string)
        + '. Impedance function for an element must return as first argument ' 
        + 'a function')
    
def test_get_impedance_function_element_parameters(
        element_strings, impedance_circuit, element_parameters,
        circuit_parameters_get_impedance, elements_circuit, 
        constant_elements_get_impedance):
    """Check that the second argument of get_impedance_function_element 
    function is a valid list of parameters.

    GIVEN: a valid element type (R, C or Q), a valid description of the
    circuit and valid parameters of the analysed circuit so far.
    WHEN: I am calculating the correspondant impedance function.
    THEN: the list of parameters for the current funtion are valid.
    """
    caller = 'get_impedance_function_element()'
    nominal_parameters = ([100, 0])
    for i, element_string in enumerate(element_strings):
        nominal_parameters[1] = element_parameters[i]
        elements_circuit_test = elements_circuit.copy()
        _, parameters_test, _ = get_impedance_function_element(
            element_string, impedance_circuit, nominal_parameters, 
            circuit_parameters_get_impedance, elements_circuit_test,
            constant_elements_get_impedance)
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

def elements_type(elements_circuit, caller):
    """Check that the list elements_circuit is a string list.
    
    GIVEN: elements_circuit is a list.
    """
    wrong_types = ''
    wrong_types_index = []
    for i, element in enumerate(elements_circuit):
        if not isinstance(element, str):
            wrong_types+= '\'' + str(element) + '\', '
            wrong_types_index.append(i)
    assert not wrong_types, (
        'type error for element(s) number ' + str(wrong_types_index) + ' ' 
        + wrong_types + ' in ' + str(elements_circuit) + ' in ' + caller 
        + '. Elements can only be strings')

def elements_string_length(elements_circuit, caller):
    """Check that each string in elements_circuit has a length of 2.
    
    GIVEN: elements_circuit is a list of strings.
    """
    wrong_length = ''
    wrong_length_index = []
    for i, element in enumerate(elements_circuit):
        if len(element)!=2:
            wrong_length+= '\'' + str(element) + '\', '
            wrong_length_index.append(i)
    assert not wrong_length, (
        'length error for element(s) number ' + str(wrong_length_index) 
        + ' ' + wrong_length + ' in ' + str(elements_circuit) + ' in ' 
        + caller + '. Elements must all be of length 2')

def elements_letter(elements_circuit, caller):
    """Check that each string in elements_circuit has a valid first character:
    either R, C or Q.

    GIVEN: elements_circuit is a list of strings of length 2.
    """
    wrong_char = ''
    wrong_char_index = []
    for i, element in enumerate(elements_circuit):
        if element[0] not in {'R', 'C', 'Q'}:
            wrong_char += '\'' + str(element) + '\', '
            wrong_char_index.append(i)
    assert not wrong_char, (
        'structural error for element(s) number ' + str(wrong_char_index) 
        + ' ' + wrong_char + ' in ' + str(elements_circuit) + ' in ' 
        + caller + '. All elements must begin with a letter among \'C\', ' 
        + '\'R\' and \'Q\'')
    
def elements_number(elements_circuit, caller):
    """Check that each string in elements_circuit has a valid second character
    (a number).

    GIVEN: elements_circuit is a list of strings of length 2.
    """
    wrong_char = ''
    wrong_char_index = []
    for i, element in enumerate(elements_circuit):
        if not element[1].isnumeric():
            wrong_char += '\'' + str(element) + '\', '
            wrong_char_index.append(i)
    assert not wrong_char, (
        'structural error for element(s) number ' + str(wrong_char_index) 
        + ' ' + wrong_char + ' in ' + str(elements_circuit) + ' in ' + caller 
        + '. All elements must end with a natural number')
    
def elements_number_duplicates(elements_circuit, caller):
    """Check that in elements_circuit there is no duplicate in number.
    
    GIVEN: elements_circuit is a list of strings of length 2, with as second 
    character a number.
    """
    wrong_char = ''
    wrong_char_index = []
    for i, element in enumerate(elements_circuit):
        if element[1].isnumeric():
            for j, other_element in enumerate(elements_circuit[i+1:]):
                if element[1]==other_element[1]:
                    wrong_char += '\'' + str(element[1]) + '\', '
                    wrong_char_index.append((i, j+i+1))
    assert not wrong_char, (
        'structural error for element(s). Found duplicate of number ' 
        + wrong_char + ' in positions ' + str(wrong_char_index) + ' in ' 
        + str(elements_circuit) + ' in ' + caller + '. Each element number ' 
        + 'must be unique')

def test_get_impedance_function_element_elements(
        element_strings, impedance_circuit, element_parameters,
        circuit_parameters_get_impedance, elements_circuit, 
        constant_elements_get_impedance):
    """Check that get_impedance_function_element() returns a valid elements
    array.

    GIVEN: a valid element type (R, C or Q), a valid description of the
    circuit and valid parameters of the analysed circuit so far.
    WHEN: I am calculating the correspondant impedance function.
    THEN: the list of elements for the current funtion are valid.
    """
    caller = 'get_impedance_function_element()'
    nominal_parameters = ([100, 0])
    for i, element_string in enumerate(element_strings):
        nominal_parameters[1]=element_parameters[i]
        elements_circuit_test=elements_circuit.copy()
        *_, elements_circuit_test = get_impedance_function_element(
            element_string, impedance_circuit, nominal_parameters, 
            circuit_parameters_get_impedance, elements_circuit_test,
            constant_elements_get_impedance)
        elements_is_list(elements_circuit_test, caller)
        elements_type(elements_circuit_test, caller)
        elements_string_length(elements_circuit_test, caller)
        elements_letter(elements_circuit_test, caller)
        elements_number(elements_circuit_test, caller)
        elements_number_duplicates(elements_circuit_test, caller)

def generate_f1():
    """Generate a function."""
    f1 = lambda x, y: x+y
    return f1

@pytest.fixture
def f1():
    return generate_f1()

def generate_f2():
    """Generate a function."""
    f2 = lambda x, y: x*y
    return f2

@pytest.fixture
def f2():
    return generate_f2()

def test_add(f1, f2):
    """Check that the add function returns a function.
    
    GIVEN: f1, f2 are functions.
    WHEN: I want the sum function of them.
    THEN: the sum function is a function.
    """
    assert inspect.isfunction(add(f1, f2)),(
        'type error in output of add(). It must be a function')
    
def generate_flist():
    """Generate a list of function."""
    f1 = lambda x, y: x+y
    f2 = lambda x, y: x*y
    return ([f1, f2])

@pytest.fixture
def f_list():
    return generate_flist()

def test_serialComb(f_list):
    """Check that the serialComb function returns a function.

    GIVEN: f_list is a list of fucntions.
    WHEN: I want the equivalent function of a serial comb of them.
    THEN: the equivalent function is a function.
    """
    assert inspect.isfunction(serialComb(f_list)), (
        'type error in output of serialComb(). It must be a function')

def generate_f():
    """Generate a function."""
    f = lambda x, y: x*y
    return f

@pytest.fixture
def f():
    return generate_f()  

def test_reciprocal(f):
    """Check that the add function returns a function.

    GIVEN: f is a fucntions.
    WHEN: I want the inverse function of f.
    THEN: the inverse function is a function.  
    """
    assert inspect.isfunction(reciprocal(f)),(
        'type error in output of reciprical(). It must be a function')
    
def test_parallelComb(f_list):
    """Check that the serialComb function returns a function.

    GIVEN: f_list is a list of fucntions.
    WHEN: I want the equivalent function of a parallel comb of them.
    THEN: the equivalent function is a function.
    """
    assert inspect.isfunction(parallelComb(f_list)), (
        'type error in output of parallelComb(). It must be a function')

def generate_i_end():
    """Generate a position for a close bracket."""
    i_end = 10
    return i_end

@pytest.fixture
def i_end():
    return generate_i_end()

def test_get_position_opening_bracket_type(circuit_string, i_end):
    """Check that get_position_opening_bracket() returns an integer.

    GIVEN: circuit_string is a valid string, i_end is the position of a closed
    bracket.
    """
    last_opening_bracket_position = get_position_opening_bracket(
        circuit_string, i_end)
    assert isinstance(last_opening_bracket_position, int), (
        'type error in output of get_position_opening_bracket(). Last '
        + 'opening bracket position must be an integer')

def test_get_position_opening_bracket_value(circuit_string, i_end):
    """Check that get_position_opening_bracket() returns a non-negative 
    number.

    GIVEN: circuit_string is a valid string, i_end is the position of a closed
    bracket and last_opening_bracket_position is an integer.
    """
    last_opening_bracket_position = get_position_opening_bracket(
        circuit_string, i_end)    
    assert last_opening_bracket_position >= 0, ('value error in output of ' 
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

@pytest.fixture
def initial_parameters():
    return generate_initial_parameters()

def generate_parameters_circuit_generate_cell():
    parameters_circuit = ([100])
    return parameters_circuit

@pytest.fixture
def parameters_circuit_generate_cell():
    return generate_parameters_circuit_generate_cell()

def generate_elements_circuit_generate_cell():
    elements_circuit = (['R1'])
    return elements_circuit

@pytest.fixture
def elements_circuit_generate_cell():
    return generate_elements_circuit_generate_cell()

def test_generate_cell_impedance_function_list(
        circuit_string, i_start, i_end, impedance_circuit,
        initial_parameters, parameters_circuit_generate_cell, 
        elements_circuit_generate_cell, constant_elements):
    """Check that get_impedance_function_element function returns a list
    as first argument.

    GIVEN: a proper description of the circuit
    """
    impedance_cell, *_ = generate_cell_impedance(
        circuit_string, i_start, i_end, impedance_circuit,
        initial_parameters, parameters_circuit_generate_cell,
        elements_circuit_generate_cell, constant_elements)
    assert isinstance(impedance_cell, list), (
        'type error in output of generate_cell_impedance(). Its first ' 
        + 'argument must be a list')

def test_generate_cell_impedance_function_type(
        circuit_string, i_start, i_end, impedance_circuit,
        initial_parameters, parameters_circuit_generate_cell, 
        elements_circuit_generate_cell, constant_elements):
    """Check that generate_cell_impedance_function() returns a list of 
    functions.

    GIVEN: generate_cell_impedance() returns a list as first argument
    """
    wrong_type_index = []
    impedance_cell, *_ = generate_cell_impedance(
        circuit_string, i_start, i_end, impedance_circuit,
        initial_parameters, parameters_circuit_generate_cell,
        elements_circuit_generate_cell, constant_elements)
    for i, function in enumerate(impedance_cell):
        if not inspect.isfunction(function):
            wrong_type_index.append(i)
    assert not wrong_type_index, (
        'type error for function(s) number ' + str(wrong_type_index) + ' '
        + ' in ' + str(elements_circuit_generate_cell) + ', in output of ' 
        + 'generate_cell_impedance(). Its first argument must be a list of ' 
        + 'functions')

def test_generate_cell_impedance_parameters(
        circuit_string, i_start, i_end, impedance_circuit,
        initial_parameters, parameters_circuit_generate_cell, 
        elements_circuit_generate_cell, constant_elements):
    """Check that the second argument of generate_cell_impedance function is 
    a valid list of parameters.

    GIVEN: a valid circuit string, a valid description of the
    circuit and valid parameters of the analysed circuit so far.
    WHEN: I am calculating the correspondant impedance function of a cell.
    THEN: the list of parameters for the current funtion are valid.
    """
    _, parameters_test, _ = generate_cell_impedance(
        circuit_string, i_start, i_end, impedance_circuit,
        initial_parameters, parameters_circuit_generate_cell,
        elements_circuit_generate_cell, constant_elements)
    caller = 'generate_cell_impedance()'
    test_parameters_is_list(parameters_test, caller)
    test_parameters_type(parameters_test, caller)
    test_parameters_list_two_elements(parameters_test, caller)
    test_parameters_list_type(parameters_test, caller)
    test_parameters_values(parameters_test, caller)
    test_parameters_list_value(parameters_test, caller)

def test_generate_cell_impedance_elements(
        circuit_string, i_start, i_end, impedance_circuit,
        initial_parameters, parameters_circuit_generate_cell, 
        elements_circuit_generate_cell, constant_elements):
    """Check that generate_cell_impedance() returns a valid elements
    array.

    GIVEN: a valid circuit string, a valid description of the
    circuit and valid parameters of the analysed circuit so far.
    WHEN: I am calculating the correspondant impedance function of a cell.
    THEN: the list of elements for the current funtion are valid.
    """
    *_, elements_circuit = generate_cell_impedance(
        circuit_string, i_start, i_end, impedance_circuit,
        initial_parameters, parameters_circuit_generate_cell,
        elements_circuit_generate_cell, constant_elements)
    caller = 'generate_cell_impedance()'
    elements_is_list(elements_circuit, caller)
    elements_type(elements_circuit, caller)
    elements_string_length(elements_circuit, caller)
    elements_letter(elements_circuit, caller)
    elements_number(elements_circuit, caller)
    elements_number_duplicates(elements_circuit, caller)

def generate_last_impedance_element():
    last_impedance_element = 1
    return last_impedance_element

@pytest.fixture
def last_impedance_element():
    return generate_last_impedance_element()

def test_update_string_valid_string(circuit_string, i_start, i_end,
                                    last_impedance_element):
    """Check that update_string returns a valid string.
    

    GIVEN: a valid circuit string, a valid position of the start and end of
    the string substitution.
    WHEN: I am substituting the old string with the updated string, acording
    to the analysis done so far.
    THEN: the updated string is valid, excpet for the characters and the
    element consistency.
    """
    updated_circuit_string = update_string(circuit_string, i_start, i_end,
                                           last_impedance_element)
    caller = 'update_string()'
    test_is_string(updated_circuit_string, caller)
    test_empty_string(updated_circuit_string, caller)
    test_string_different_number_brackets(updated_circuit_string, caller)
    test_string_consistency_brackets(updated_circuit_string, caller)

def test_update_string_characters(circuit_string, i_start, i_end,
                                  last_impedance_element):
    """Check that a string containes only valid characters:
    '(', ')', '[', ']', 'Z', 'C', 'Q', 'R' and natural numbers.

    GIVEN: a valid circuit string, a valid position of the start and end of
    the string substitution.
    WHEN: I am substituting the old string with the updated string, acording
    to the analysis done so far.
    THEN: the updated string has valid characters.
    """
    updated_circuit_string = update_string(circuit_string, i_start, i_end,
                                        last_impedance_element)
    wrong_characters = ''
    wrong_characters_index = []
    for i, char in enumerate(updated_circuit_string):
        if (char not in {'(', ')', '[', ']', 'Z', 'C', 'Q', 'R'} 
                and not char.isnumeric()):
            wrong_characters += '\'' + char + '\', '
            wrong_characters_index.append(i)
    assert not wrong_characters, (
        'Invalid character(s) ' + wrong_characters + ' at '
        + str(wrong_characters_index) + ' in ' + updated_circuit_string 
        + ' in update_string(). Only round and square brackets, C, Q, R ' 
        + 'and natural numbers are valid characters')

def test_update_string_element_consistency(circuit_string, i_start, i_end,
                                           last_impedance_element):
    """Check the element consistency of a string that containes only valid
    characters: each element is composed by a capital letter among 
    {'C', 'Q', 'R'} followed by a natural number.

    GIVEN: a valid circuit string, a valid position of the start and end of
    the string substitution.
    WHEN: I am substituting the old string with the updated string, acording
    to the analysis done so far.
    THEN: the updated string has element consistency.
    """
    updated_circuit_string = update_string(circuit_string, i_start, i_end,
                                           last_impedance_element)
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
    assert not wrong_elements, (
        'element inconsistency for '+ wrong_elements + ' at ' 
        + str(wrong_element_index) + ' in updated string: '
        + updated_circuit_string + '. An element is composed by a '
        + 'valid letter followed by a natural number')
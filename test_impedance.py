import pytest

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

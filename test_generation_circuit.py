"""This module containes all the test functions (and the tested functions
needed for the tests) for the input data structurization functions:
generate_circuit() of the generate_impedance.py module and
generate_constant_elements_data() from the generate_data.py module.
"""

import pytest

from generate_impedance import generate_circuit, Circuit
from generate_data import generate_constant_elements_data


#Tests for the circuit diagram

def same_number_of_brackets(circuit_diagram):
    """Given a circuit diagram, return if the count of open brackets is the
    same of close brackets. Used for testing.

    Parameters
    ----------
    circuit_diagram : str
        String of the circuit given by input

    Returns
    -------
    equality_count : bool
        Boolean of the equality count condition
    """
    equality_count = (
        circuit_diagram.count('(')==circuit_diagram.count(')')
        and circuit_diagram.count('[')==circuit_diagram.count(']'))
    return equality_count

def generate_example_number_of_brackets():
    strings = (['()', '([])', '[()[()]]', '()]'])
    return strings

@pytest.fixture
def example_number_of_brackets():
    return generate_example_number_of_brackets()

def test_same_number_of_brackets(example_number_of_brackets):
    """Check that the help function to test if a string has the same number of
    brackets for each type works.

    WHEN: the circuit diagram validity is tested
    THEN: the circuit diagram has the same number of brackets for each type
    """
    #Only the last example is incorrect
    for string_ in example_number_of_brackets:
        assert same_number_of_brackets(string_), (
            'StructuralError: inconsistent number of open and close brackets in '
            + '\'' + string_ + '\' in same_number_of_brackets()')


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
    wrong_brackets_index : bool
        Index in the string of all the aforementioned brackets
    """
    wrong_brackets = []
    wrong_brackets_index = ''
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
                                relative_index_wrong_bracket + bracket_index
                                + 1 + cut_parameter)
                            wrong_brackets.append(wrong_bracket)
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
    strings = (['()', '([])', '[()[()]]', '[(])'])
    return strings

@pytest.fixture
def example_consistency_brackets():
    return generate_example_consistency_brackets()

def test_consistency_brackets(example_consistency_brackets):
    """Check that the help function to test if a string has brackets
    consistency works.

    GIVEN: the circuit diagram has the same number of brackets for each type
    WHEN: the circuit diagram validity is tested
    THEN: the circuit diagram has brackets consistency
    """
    #Only the last example is incorrect
    for string_ in example_consistency_brackets:
        wrong_brackets, wrong_brackets_index = consistency_brackets(
            string_)
        assert not wrong_brackets, (
            'StructuralError: inconsistent \'' + str(wrong_brackets)
            + '\' at ' + wrong_brackets_index + ': ' + string_ + ' in '
            + 'consistency_brackets()')


def list_element_types(circuit_diagram):
    """Return the list of elements ('C', 'Q' or 'R' ) of a string. Used for
    testing.

    Parameters
    ----------
    circuit_diagram : str
        String of the circuit given by input

    Returns
    -------
    elements_types : list
        List of single characters representing the type of elements in the
        same order as they are written
    """
    elements_types = []
    for char in circuit_diagram:
        if char in {'C', 'Q', 'R'}:
            elements_types.append(char)
    return elements_types

def generate_example_diagrams_list():
    diagrams = (['(R1)', '([R1C2]R3)', '[C1Q2]', '(R1F3)'])
    return diagrams

@pytest.fixture
def example_diagrams_list():
    return generate_example_diagrams_list()

def test_list_element_types(example_diagrams_list):
    """Check that the help function to list the elments in a diagram works.

    GIVEN: the circuit diagram is a string
    WHEN: the circuit diagram validity is tested
    THEN: the elements of the circuit diagram are listed correctly
    """
    #Only the last example is incorrect
    correct_listing = ([['R'], ['R','C','R'], ['C', 'Q'], ['R', 'F']])
    for i, string_ in enumerate(example_diagrams_list):
        listing = list_element_types(string_)
        assert listing==correct_listing[i], (
            'Listing error: element listing of \'' + str(string_)
            + '\' differs from the correct one: ' + str(correct_listing[i]))


def invalid_characters(circuit_diagram):
    """Given a circuit diagram, return any invalid character, i.e. different
    than '(', ')', '[', ']', 'C', 'Q', 'R' or natural numbers. Used for
    testing.

    Parameters
    ----------
    circuit_diagram : str
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
    for i, char in enumerate(circuit_diagram):
        if (char not in {'(', ')', '[', ']', 'C', 'Q', 'R'}
            and not char.isnumeric()):
            wrong_characters += '\'' + char + '\', '
            wrong_characters_index.append(i)
    return wrong_characters, wrong_characters_index

def generate_example_diagrams_character():
    diagrams = (['(R1)', '[R1C2]', '([C1Q2]R3)', '(&R1G3)'])
    return diagrams

@pytest.fixture
def example_diagrams_character():
    return generate_example_diagrams_character()

def test_invalid_characters(example_diagrams_character):
    """Check that the help function to list the elments in a diagram works.

    GIVEN: the circuit diagram is a string
    WHEN: the circuit diagram validity is tested
    THEN: the circuit diagram contains only valid characters
    """
    #Only the last example is incorrect
    for string_ in example_diagrams_character:
        wrong_characters, wrong_characters_index = invalid_characters(string_)
        assert not wrong_characters, (
            'StructuralError: invalid character(s) ' + wrong_characters
            + ' at ' + str(wrong_characters_index) + ' in ' + string_
            + 'from invalid_characters()' + '. Only round and square '
            + 'brackets, C, Q, R and natural numbers are allowed')


def inconsistent_elements(circuit_diagram):
    """Given a circuit diagram, return any inconsistent element character: each
    element is composed by a capital letter among {'C', 'Q', 'R'} followed
    by a natural number. Used for testing.

    Parameters
    ----------
    circuit_diagram : str
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
    for i, char in enumerate(circuit_diagram):
        if (char in {'C', 'Q', 'R'} and circuit_diagram[-1]!=char):
            if not circuit_diagram[i+1].isnumeric():
                wrong_elements += ('\'' + char + str(circuit_diagram[i+1])
                                   + '\', ')
                wrong_element_index.append(i)
        elif (char.isnumeric() and circuit_diagram[0]!=char):
            if not (circuit_diagram[i-1] in {'C', 'Q', 'R'}):
                wrong_elements += ('\'' + str(circuit_diagram[i-1]) + char
                                   + '\', ')
                wrong_element_index.append(i-1)
    return wrong_elements, wrong_element_index

def generate_example_diagrams_consistency_element():
    diagrams = (['(C1)', '[C1C2]', '([Q1C2]R3)', '(R[2G3])'])
    return diagrams

@pytest.fixture
def example_diagrams_consistency_element():
    return generate_example_diagrams_consistency_element()

def test_invalid_characters(example_diagrams_consistency_element):
    """Check that the help function to list the elments in a diagram works.

    GIVEN: the circuit diagram is a string
    WHEN: the circuit diagram validity is tested
    THEN: the circuit diagram contains only valid characters
    """
    #Only the last example is incorrect
    for string_ in example_diagrams_consistency_element:
        wrong_elements, wrong_element_index = inconsistent_elements(string_)
        assert not wrong_elements, (
            'StructuralError: element inconsistency for '+ wrong_elements
            + ' at ' + str(wrong_element_index) + ': ' + string_ + '. An '
            + 'element is composed by a valid letter followed by a natural '
            + 'number in invalid_characters()')

def inconsistent_numbers(circuit_diagram):
    """Given a circuit diagram, return any inconsistent element number: each
    element has a number that is the same of its order of writing in the
    string. Used for testing.

    Parameters
    ----------
    circuit_diagram : str
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
    for i, char in enumerate(circuit_diagram):
        if char.isnumeric():
            numeric_char_counter += 1
            if numeric_char_counter!=int(char):
                wrong_numbers += ('\'' + str(circuit_diagram[i-1:i+1])
                                  + '\', ')
                wrong_numbers_index.append(i)
    return wrong_numbers, wrong_numbers_index

def generate_example_diagrams_consistency_numbers():
    diagrams = (['(C1)', '[C1C2]', '([Q1C2]R3)', '(R1[R3C3])'])
    return diagrams

@pytest.fixture
def example_diagrams_consistency_numbers():
    return generate_example_diagrams_consistency_numbers()

def test_inconsistent_numbers(example_diagrams_consistency_numbers):
    """Check that the help function to list the elments in a diagram works.

    GIVEN: the circuit diagram is a string
    WHEN: the circuit diagram validity is tested
    THEN: the circuit diagram contains only valid numbers
    """
    #Only the last example is incorrect
    for string_ in example_diagrams_consistency_numbers:
        wrong_numbers, wrong_numbers_index = inconsistent_numbers(string_)
        assert not wrong_numbers, (
            'StructuralError: wrong number for element(s) '+ wrong_numbers
            + 'at ' + str(wrong_numbers_index) + ' in ' + string_
            + 'from inconsistent_numbers(). Element numbers must increase of '
            + '1 unit per time')    


def generate_example_circuit_diagrams():
    example_circuit_diagrams = (['(R1)', '(R1C2)', '(R1C2[R3Q4])',
                                      '(R1Ce)'])
    return example_circuit_diagrams

@pytest.fixture
def example_circuit_diagrams():
    return generate_example_circuit_diagrams()

def generate_example_parameters():
    example_parameters = ([{'R1': 100.0},
                           {'R1': 1000.0, 'C2': 1e-6},
                           {'R1': 7100.0, 'C2': 2e-6, 'R3': 10000.0,
                            'Q4': ([0.1e-6, 0.87])},
                           {'R1': 'a', 'Ce': 1}])
    return example_parameters

@pytest.fixture
def example_parameters():
    return generate_example_parameters()

def generate_example_constant_conditions():
    example_constant_conditions = ([{'R1': 0}, {'R1': 1, 'C2': 0},
                                    {'R1': 0, 'C2': 0, 'R3': 0, 'Q4': 0},
                                    {'R1': 'a', 'Ce': -1}])
    return example_constant_conditions

@pytest.fixture
def example_constant_conditions():
    return generate_example_constant_conditions()

def generate_example_initial_circuits():
    """Generate an array of constant element conditions. Used for tests."""
    example_initial_circuits = []
    circuit_diagrams = generate_example_circuit_diagrams()
    parameters = generate_example_parameters()
    constant_conditions = generate_example_constant_conditions()
    for i, diagram in enumerate(circuit_diagrams):
        example_initial_circuits.append(generate_circuit(
            diagram, parameters[i], constant_conditions[i]))
    return example_initial_circuits

@pytest.fixture
def example_initial_circuits():
    return generate_example_initial_circuits()

def test_initial_circuit_circuit_diagram(example_initial_circuits,
                                              example_circuit_diagrams):
    """Check if the circuit diagram inside the Circuit object created by
    the generate_circuit() has a valid circuit diagram. A circuit
    diagram is made of elements (a letter among {'R', 'C', 'Q'} followed by a
    single digit number) and round and/or square brackets. This means that the
    string must not be empty, and must contain only valid characters. There
    must be a brackets consistency and the first/last character must be an
    open/closed bracket. For the elements, there must be at least a valid
    element, and the digits must represent their order of appearence.

    GIVEN: the circuit diagram is valid
    WHEN: the Circuit object's circuit diagram validity is tested
    THEN: the Circuit object has a valid circuit diagram
    """
    caller = 'generate_circuit()'
    #Only the last example is incorrect
    for i, input_circuit in enumerate(example_initial_circuits):
        assert isinstance(input_circuit, Circuit), (
            'TyperError for output of ' + caller + ' method. It must be an '
            + 'instance of the \'Circuit\' class')

        circuit_diagram = input_circuit.circuit_diagram
        assert isinstance(circuit_diagram, str), (
            'TypeError for circuit scheme in ' + caller
            + '. It must be a string')
        assert circuit_diagram, 'empty string in ' + caller
        assert (circuit_diagram.startswith('(')
                or circuit_diagram.startswith('[')), (
                    'StructuralError: no initial open bracket detected in '
                    + caller)
        assert (circuit_diagram.endswith(')') or circuit_diagram.endswith(
            ']')), (
            'StructuralError: no final close bracket detected' + caller)
        assert same_number_of_brackets(circuit_diagram), (
            'StructuralError: inconsistent number of open and close brackets '
            + 'in \'' + circuit_diagram + '\' in ' + caller)
        wrong_brackets, wrong_brackets_index = consistency_brackets(
            circuit_diagram)
        assert not wrong_brackets, (
            'StructuralError: inconsistent \'' + str(wrong_brackets) + '\' at '
            + wrong_brackets_index + ': ' + circuit_diagram + ' in ' + caller)
        elements_types = list_element_types(circuit_diagram)
        assert elements_types, (
            'StructuralError: no element found in ' + circuit_diagram + ' from '
            + caller + '. An element begins with one of the three letter C, Q '
            + 'or ' + 'R')
        wrong_characters, wrong_characters_index = invalid_characters(
            circuit_diagram)
        assert not wrong_characters, (
            'StructuralError: invalid character(s) ' + wrong_characters + ' at '
            + str(wrong_characters_index) + ' in ' + circuit_diagram + ' from '
            + caller + '. Only round and square brackets, C, Q, R and natural '
            + 'numbers are allowed')
        wrong_elements, wrong_element_index = inconsistent_elements(
            circuit_diagram)
        assert not wrong_elements, (
            'StructuralError: element inconsistency for '+ wrong_elements
            + ' at ' + str(wrong_element_index) + ': ' + circuit_diagram
            + '. An element is composed by a valid letter followed by a '
            + 'natural number in ' + caller)
        wrong_numbers, wrong_numbers_index = inconsistent_numbers(
            circuit_diagram)
        assert not wrong_numbers, (
            'StructuralError: wrong number for element(s) '+ wrong_numbers
            + 'at ' + str(wrong_numbers_index) + ' in ' + circuit_diagram
            + 'from ' + caller + '. Element numbers must increase of 1 unit '
            + 'per time')
        
        assert example_circuit_diagrams[i]==circuit_diagram, (
        'StructuralError for attribute \'circuit_diagram\' output of '
        + caller + '. It must be the same of the input circuit_diagram')


##############################################################################
#Tests for the elements names

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
    #Only the last example is incorrect
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
    #Only the last example is incorrect
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


def test_initial_circuit_elements(example_initial_circuits,
                                  example_parameters):
    """Check if the circuit diagram inside the Circuit object created by
    the generate_circuit() has valid elements. Each element is a 2-char
    string, beginning with 'R', 'C' or 'Q', and followed by a numeric char. No
    duplicates with the same number are permitted.

    GIVEN: the circuit diagram and the elements are valid
    WHEN: the Circuit object's elements validity is tested
    THEN: the Circuit object has valid elements
    """
    caller = 'generate_circuit()'
    #Only the last example is incorrect
    for i, input_circuit in enumerate(example_initial_circuits):
        parameters_map = input_circuit.parameters_map
        assert isinstance(parameters_map, dict), (
            'TypeError for attribute \'parameters_map\' in output of '
            + caller + '. It must be a dictionary')
        
        elements_list = list(parameters_map.keys())
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
        
        input_parameters = example_parameters[i]
        assert elements_list==list(input_parameters.keys()), (
        'StructuralError for elements in attribute \'parameters_map\' in '
        + 'output of ' + caller + '. The elements must be the same that '
        + 'compose the output of generate_circuit_string()')
   

##############################################################################
#Tests for the parameters

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

def generate_example_parameters_tuples():
    tuples = ([{'C1': (1e-6, 0)}, {'C1': (1e-6, 0), 'R2': (100, 0)},
               {'Q1': ([1e-6, 0.5], 1), 'R2': (100, 0)},
               {'Q1': ([1e-6, 0.5])}])
    return tuples

@pytest.fixture
def example_parameters_tuples():
    return generate_example_parameters_tuples()

def test_wrong_tuples_circuit(example_parameters_tuples):
    """Check that the help function that returns any item in a dictionary that
    is not a tuple works.

    GIVEN: the parameters are a dictionary with tuples as values
    WHEN: the parameters validity is tested
    THEN: the parameters contains only tuples as values
    """
    #Only the last example is incorrect
    for parameters in example_parameters_tuples:
        wrong_tuples = wrong_tuples_circuit(parameters)
        assert not wrong_tuples, (
            'TypeError in output of get_impedance_const_input_element_type() '
            + 'for element \'' + wrong_tuples + '\'. Its value in the '
            + 'dictionary have to be a tuple')


def invalid_parameters_type(parameters_list):
    """Given a parameters list, return any wrong type parameter: each
    parameter can be a float or a list. The objects inside the list must be
    floats. Used for testing.

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
            and not isinstance(parameter, list)):
            wrong_type += '\'' + str(parameter) + '\', '
            wrong_type_index.append(i)
        if isinstance(parameter, list):
            for _, sub_prameter in enumerate(parameter):
                if not isinstance(sub_prameter, float):
                    wrong_type += ('\'' + str(sub_prameter) + '\' in \''
                                   + str(parameter) + '\', ')
                    wrong_type_index.append(i)
    return wrong_type, wrong_type_index

def generate_example_parameters_type():
    parameters = ([[1e-6], [1000.0, 1e-5], [100.0, [1e-5, 1.1, 10.0]],
                   ['a', [1e-5, 'b']]])
    return parameters

@pytest.fixture
def example_parameters_type():
    return generate_example_parameters_type()

def test_invalid_parameters_type(example_parameters_type):
    """Check that the help function to find the invalid parameters (not float
    nor float lists) works.

    GIVEN: the parameters are in a list form
    WHEN: the parameters validity is tested
    THEN: the parameters list contains only valid types
    """
    #Only the last example is incorrect
    for parameters in example_parameters_type:
        wrong_type, wrong_type_index = invalid_parameters_type(
            parameters)
        assert not wrong_type, (
            'TypeError for parameter(s) number ' + str(wrong_type_index)
            + ' ' + wrong_type + 'in ' + str(parameters) + ' in '
            + 'invalid_parameters_type(). Parameters can only be floats '
            + 'or float lists')   


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

def generate_example_parameters_list():
    parameters = ([[1e-6], [1000.0, 1e-5], [100.0, [1e-5, 10.0]],
                   [13.0, [1e-5, 1.1, 100.0]]])
    return parameters

@pytest.fixture
def example_parameters_list():
    return generate_example_parameters_list()

def test_invalid_parameters_list(example_parameters_list):
    """Check that the help function to find the invalid list parameters length
    (length 2) works.

    GIVEN: the parameters are in a list form
    WHEN: the parameters validity is tested
    THEN: the parameters list are only of length 2
    """
    #Only the last example is incorrect
    for parameters in example_parameters_list:
        wrong_list, wrong_list_index = invalid_parameters_list(parameters)
        assert not wrong_list, (
            'TypeError for parameter(s) number ' + str(wrong_list_index)
            + ': \'' + wrong_list + '\' in ' + str(parameters)
            + ' in invalid_parameters_list(). Lists parameters must contain '
            + 'exactly 2 parameters') 


def invalid_parameters_value(parameters_list):
    """Given a parameters list, return any float parameter that has
    a non-positive value, or any float list parameter with a non-positive
    first parameter or a second parameter that is negative or greater that 1,
    thus invalid. Used for testing.

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
        if isinstance(parameter, float):
            if parameter<=0:
                wrong_value += '\'' + str(parameter) + '\', '
                wrong_value_index.append(i)
        elif isinstance(parameter, list):
            if parameter[0]<=0:
                wrong_value += '\'' + str(parameter[0]) + '\', '
                wrong_value_index += 'second of [' + str(i) + ']'
            if (parameter[1]<0 or parameter[1]>1):
                wrong_value += '\'' + str(parameter[1]) + '\', '
                wrong_value_index += 'second of [' + str(i) + ']'
    return wrong_value, wrong_value_index

def generate_example_parameters_value():
    parameters = ([[1e-6], [1000.0, 1e-5], [100.0, [1e-5, 10.0]],
                   [-300.0, [1e-5, 10.0]]])
    return parameters

@pytest.fixture
def example_parameters_value():
    return generate_example_parameters_value()

def test_invalid_parameters_value(example_parameters_value):
    """Check that the help function to find the invalid parameters value
    works.

    GIVEN: the parameters are in a list form
    WHEN: the parameters validity is tested
    THEN: the parameters have valid values
    """
    #Only the last example is incorrect
    for parameters in example_parameters_value:
        wrong_value, wrong_value_index = invalid_parameters_value(
            parameters)
    assert not wrong_value, (
        'ValueError for parameter(s) number ' + str(wrong_value_index) + ' '
        + wrong_value + ' in ' + str(parameters) + ' in '
        + 'invalid_parameters_value(). Float parameters must be positive, '
        + 'lists parameters must contain as first parameter a positive '
        + 'number and as second parameter a number between 0 and 1')


def elements_parameters_match(parameters_map):
    """Given the parameters_map, return any element and parameter that do not
    match in type: R and C have a float type, while Q has the list type. Used
    for testing.

    Parameters
    ----------
    parameters_map : dict
        Dictionary of the parameters

    Returns
    -------
    wrong_match : str
        String that contains all the invalid elements and parameters,
        separated by a comma and a whitespace
    wrong_match_index : list
        List of indexes of the invalid elements in the dictionary
    """
    elements_list = list(parameters_map.keys())
    parameters_list = list(parameters_map.values())
    wrong_match = ''
    wrong_match_index = []
    for i, element in enumerate(elements_list):
        if (element.startswith('C') or element.startswith('R')):
            if not isinstance(parameters_list[i][0], float):
                wrong_match += ('\'[' + str(element) + ','
                                + str(parameters_list[i][0]) + ']\', ')
                wrong_match_index.append(i)
        else:
            if not isinstance(parameters_list[i][0], list):
                wrong_match += ('\'[' + str(element) + ','
                                + str(parameters_list[i][0]) + ']\', ')
                wrong_match_index.append(i)
    return wrong_match, wrong_match_index

def generate_example_parameters_maps():
    parameters_maps = ([{'C1': (1e-6, 0)}, {'C1': (1e-6, 0), 'R2': (100, 0)},
                        {'Q1': ([1e-6, 0.5], 1), 'R2': (100, 0)},
                        {'R1': ([1e-6, 0.5], 0), 'Q2': (10.0, 1)}])
    return parameters_maps

@pytest.fixture
def example_parameters_maps():
    return generate_example_parameters_maps()

def test_invalid_parameters_value(example_parameters_maps):
    """Check that the help function to find the invalid match between elements
    type and parameters in the parameters dictionary works.

    GIVEN: the parameters maps are in a dictionary form, with elements as
    strings and parameters as valid tuples
    WHEN: the parameters validity is tested
    THEN: the parameters match is correct
    """
    #Only the last example is incorrect
    for parameters_map in example_parameters_maps:
        wrong_match, wrong_match_index = elements_parameters_match(
            parameters_map)
        assert not wrong_match, (
            'StructuralError: bad match for '+ wrong_match + ' in '
            + str(wrong_match_index) + 'for dictonary \''
            + str(parameters_map) + '\' from invalid_parameters_value() . \'R'
            + '\' and \'C\' elements must have a float as parameter, \'Q\''
            + 'must have a list')


def test_initial_circuit_parameters(example_initial_circuits,
                                    example_parameters):
    """Check if the parameters map inside the Circuit object created by
    the generate_circuit() has valid parameters. Each parameter may be a
    float or a list itself containing only 2 elements. Each of them have to
    be float. There are also value restriction on the float variables: if they
    are parameters they have to be positive. If they are inside a list, the
    first must be positive, the secon must be within [0,1].
    Then there must be a match in length and type between the parameters and
    the circuit string: float/int parameters are for 'R' or 'C' elements,
    while lists are for 'Q'.

    GIVEN: the circuit diagram and the parameters map are valid
    WHEN: the Circuit object's parameters validity is tested
    THEN: the Circuit object has valid parameters
    """
    caller = 'generate_circuit()'
    #Only the last example is incorrect
    for i, input_circuit in enumerate(example_initial_circuits):
        parameters_map = input_circuit.parameters_map

        wrong_tuples = wrong_tuples_circuit(parameters_map)
        assert not wrong_tuples, (
            'TypeError in output of get_impedance_const_input_element_type() '
            + 'for element \'' + wrong_tuples + '\'. Its value in the '
            + 'dictionary have to be a tuple')
        parameters_values= list(parameters_map.values())
        parameters_list = [parameter[0] for parameter in parameters_values]

        wrong_type, wrong_type_index = invalid_parameters_type(
            parameters_list)
        assert not wrong_type, (
            'TypeError for parameter(s) number ' + str(wrong_type_index)
            + ' ' + wrong_type + 'in ' + str(parameters_list) + ' in '
            + caller + '. Parameters can only be floats or float lists')

        wrong_list, wrong_list_index = invalid_parameters_list(
            parameters_list)
        assert not wrong_list, (
            'TypeError for parameter(s) number ' + str(wrong_list_index)
            + ': \'' + wrong_list + '\' in ' + str(parameters_list)
            + ' in ' + caller + '. Lists parameters must contain exactly 2 '
            + 'parameters')
        wrong_value, wrong_value_index = invalid_parameters_value(
            parameters_list)
        assert not wrong_value, (
            'ValueError for parameter(s) number ' + str(wrong_value_index) + ' '
            + wrong_value + ' in ' + str(parameters_list) + ' in ' + caller
            + '. Float parameters must be positive, lists parameters '
            + 'must contain as first parameter a positive number and as second '
            + 'parameter a number between 0 and 1')
        wrong_match, wrong_match_index = elements_parameters_match(
            parameters_map)
        assert not wrong_match, (
            'StructuralError: bad match for '+ wrong_match + ' in '
            + str(wrong_match_index) + 'for dictonary \''
            + str(parameters_map) + '\' from invalid_parameters_value() . \'R'
            + '\' and \'C\' elements must have a float as parameter, \'Q\''
            + 'must have a list')
        
        input_parameters = example_parameters[i]
        input_parameters_values = list(input_parameters.values())
        assert parameters_list==input_parameters_values, (
        'StructuralError for parameters of output of ' + caller
        + '. It must be the same of the input parameters')



##############################################################################
#Constant conditions tests

def invalid_constant_type(constant_elements_list):
    """Given a constant elements condition list, return any wrong type
    constant elements condition: they can only be integers. Used for testing.

    Parameters
    ----------
    constant_elements_list : list
        List of the constant elements condition

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

def generate_example_constant_conditions_integers():
    """Generate three examples of lists of all integers."""
    example_constant_conditions_integers = ([[2, 0, 1], [1], [3, 0],
                                             ['a', 0.3, 1]])
    return example_constant_conditions_integers

@pytest.fixture
def example_constant_conditions_integers():
    return generate_example_constant_conditions_integers()

def test_invalid_constant_type(example_constant_conditions_integers):
    """Check that the help function to test if a list contains all of integers
    works.

    GIVEN: the constant conditions are a list
    WHEN: the constant conditions are tested
    THEN: the constant conditions have a valid type
    """
    #Only the last example is incorrect
    for element in example_constant_conditions_integers:
        wrong_types, wrong_types_index = invalid_constant_type(element)
        assert not wrong_types, (
            'TypeError for constant element(s) ' + str(wrong_types)
            + ' number ' + str(wrong_types_index) + ' in ' + str(element)
            + ' from invalid_constant_type(). Constant element must be an '
            + 'integer')


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

def generate_example_constant_conditions_value():
    example_constant_conditions_value = ([[1, 0, 1], [1], [0, 0], [3, 1]])
    return example_constant_conditions_value

@pytest.fixture
def example_constant_conditions_value():
    return generate_example_constant_conditions_value()

def test_invalid_constant_value(example_constant_conditions_value):
    """Check that the help function to test if a list contains all 0s or 1s
    works.

    GIVEN: the constant conditions are a list of integers
    WHEN: the constant conditions are tested
    THEN: the constant conditions have a valid value
    """
    #Only the last example is incorrect
    for element in example_constant_conditions_value:
        wrong_value, wrong_value_index = invalid_constant_value(element)
        assert not wrong_value, (
            'ValueError for constant element(s) '+ wrong_value + 'at '
            + str(wrong_value_index) + ' in \'' + str(element) + '\' from '
            + 'invalid_constant_value(). Constant array must contain only 0 '
            + 'or 1')


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

def generate_example_parameters_length():
    parameters = ([{'R1': 100, 'C2': 1e-6, 'R3': 1000},
                   {'R1': 200},
                   {'C1': 2e-6, 'R2': 3000},
                   {'R1': 100, 'C2': 1e-6, 'R3': 1000}])
    return parameters

@pytest.fixture
def example_parameters_length():
    return generate_example_parameters_length()

def generate_example_conditionts_length():
    constant_conditions = ([[1, 0, 1], [1], [0, 0], [0, 0]])
    return constant_conditions

@pytest.fixture
def example_conditionts_length():
    return generate_example_conditionts_length()

def test_number_of_parameters_is_equal_to_number_of_const_elements(
        example_parameters_length, example_conditionts_length):
    """Check that the help function to test if a list has the same length of a
    dictionary works.

    GIVEN: the parameters are a valid dictionary of parameters andthe constant
    conditions are a list of integers
    WHEN: the constant conditions are tested
    THEN: the constant conditions have the same length of the parameters
    dictionaries
    """
    #Only the last example is incorrect
    for i, parameters in enumerate(example_parameters_length):
        assert number_of_parameters_is_equal_to_number_of_const_elements(
            parameters, example_conditionts_length[i]), (
            'StructuralError: error from '
            + 'number_of_parameters_is_equal_to_number_of_const_elements(): '
            + 'parameters and constant array list size must be the same. '
            + 'Parameters size: ' + str(len(parameters)) + ', constant array '
            + 'size: ' + str(len(example_conditionts_length[i])))

def generate_example_parameters_constant_elements():
    """Generate an array of constant element conditions. Used for tests."""
    parameters = ([{'R1': 100, 'C2': 1e-6, 'R3': 1000},
                   {'R1': 200},
                   {'C1': 2e-6, 'R2': 3000}])
    return parameters

@pytest.fixture
def example_parameters_constant_elements():
    return generate_example_parameters_constant_elements()

def generate_example_constant_elements():
    """Generate an array of constant element conditions. Used for tests."""
    parameters = generate_example_parameters_constant_elements()
    constant_conditions = []
    for parameter in parameters:
        constant_conditions.append(generate_constant_elements_data(
            parameter))
    return constant_conditions

@pytest.fixture
def example_constant_elements():
    return generate_example_constant_elements()

def test_generate_constant_elements_data(example_constant_elements,
                                         example_parameters_constant_elements):
    """Check that the constant elements list is valid. Each value has to be
    an integer, and can be 0 or 1. The constant element list has to be of the
    same length of the parameter list.

    GIVEN: the parameters list is a valid parameters list, related to the
    correspondant circuit diagram.
    WHEN: the constant list generation function is called
    THEN: the constant elements list is a valid list of constant elements
    condition
    """
    caller = 'generate_constant_elements_data()'
    for i, constant_cond in enumerate(example_constant_elements):
        assert isinstance(constant_cond, dict), (
            'TypeError for circuit scheme in ' + caller + '. It must be a '
            + 'dictionary')
        
        conditions = list(constant_cond.values())
        wrong_types, wrong_types_index = invalid_constant_type(conditions)
        assert not wrong_types, (
            'TypeError for constant element(s) ' + str(wrong_types) + ' number '
            + str(wrong_types_index) + ' in ' + str(conditions)
            + ' from ' + caller + '. Constant element must be an integer')
        wrong_value, wrong_value_index = invalid_constant_value(conditions)
        assert not wrong_value, (
            'ValueError for constant element(s) '+ wrong_value + 'at '
            + str(wrong_value_index) + ' in \'' + str(conditions)
            + '\' from ' + caller + '. Constant array must contain only 0 or '
            + '1')
        assert number_of_parameters_is_equal_to_number_of_const_elements(
            example_parameters_constant_elements[i], conditions), (
            'StructuralError: error from ' + caller + ': parameters and '
            + 'constant array list size must be the same. Parameters size: '
            + str(len(example_parameters_constant_elements[i]))
            + ', constant conditions size: ' + str(len(conditions)))



def test_initial_circuit_constant_elements(example_initial_circuits,
                                           example_constant_conditions):
    """Check that the constant elements list of the Circuit objetc is valid.

    GIVEN: the parameters list is a valid parameters list, related to the
    correspondant circuit diagram.
    WHEN: the constant list generation function is called
    THEN: the constant elements list is a valid list of constant elements
    condition
    """
    caller = 'generate_circuit()'
    #Only the last example is incorrect
    for i, input_circuit in enumerate(example_initial_circuits):
        parameters_map = input_circuit.parameters_map

        wrong_tuples = wrong_tuples_circuit(parameters_map)
        assert not wrong_tuples, (
            'TypeError in output of get_impedance_const_input_element_type() '
            + 'for element \'' + wrong_tuples + '\'. Its value in the '
            + 'dictionary have to be a tuple')
        parameters_values= list(parameters_map.values())
        constant_elements_list = [parameter[1] for parameter in
                                  parameters_values]

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
        
        input_constant_conditions = example_constant_conditions[i]
        constant_conditions = list(input_constant_conditions.values())
        assert set(constant_elements_list)==set(constant_conditions), (
            'StructuralError for constant elements in attribute '
            + '\'parameters_map\' in output of ' + caller + '. It must be the '
            + 'same of the output of return_constant_elements()')

"""This module contains all the test functions (and the tested help functions
for the tests) for the input data structurization functions:
generate_circuit() of the generate_impedance.py module and
generate_constant_conditions_data() from the generate_data.py module.
"""

import pytest

import sys
from pathlib import Path
sys.path.append(str(Path.cwd().parent))

from generate_impedance import generate_circuit, Circuit
from generate_data import generate_constant_conditions_data


###################################
#Tests for the circuit diagram

def consistency_brackets(circuit_diagram):
    """Given a circuit diagram, return if there is a bracket incongruence.
    Used for testing.

    Parameters
    ----------
    circuit_diagram : str
        Scheme of the circuit given by input

    Returns
    -------
    wrong_brackets : list
        List of all the bracket involved in the bracket incongruence
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
    THEN: no inconsistency is detected
    """
    pair_brackets = '()' #A single pair of round brackets with obvious consistency
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
    THEN: no inconsistency is detected
    """
    two_pairs = '([])' #Two pairs of bracket with obvious consistency
    wrong_brackets, wrong_brackets_index = consistency_brackets(two_pairs)

    assert not wrong_brackets, (
        'StructuralError: inconsistent ' + str(wrong_brackets)
        + ' at ' + wrong_brackets_index + ': ' + two_pairs + ' from '
        + 'consistency_brackets()')

def test_consistency_brackets_complex():
    """Check that the help function to test if a string has brackets
    consistency works on a string with many pairs of (consistent) brackets,
    with elements inside.
    If no inconsistency is detected, the returned strings given by the
    function under test are empty.

    GIVEN: the circuit diagram with many pairs of consistent brackets
    WHEN: I check if there is a brackets inconsistency
    THEN: no inconsistency is detected
    """
    complex_pairs = '[(R1C2)[(R3Q4)R5]]' #Many consistent pairs of brackets
    wrong_brackets, wrong_brackets_index = consistency_brackets(complex_pairs)

    assert not wrong_brackets, (
        'StructuralError: inconsistent ' + str(wrong_brackets)
        + ' at ' + wrong_brackets_index + ': ' + complex_pairs + ' from '
        + 'consistency_brackets()')

def test_consistency_brackets_inconsistent_pairs():
    """Check that the help function to test if a string has brackets
    consistency works on a string with inconsistent brackets.
    If an inconsistency is detected, the returned strings given by the
    function under test contain the inconsistent group and their index in
    the input string.

    GIVEN: the circuit diagram as four brackets that are inconsistent
    WHEN: I check if there is a brackets inconsistency
    THEN: the inconsistency is detected
    """
    complex_pairs = '[(])' #An evident example of inconsistent brackets
    wrong_brackets, _ = consistency_brackets(complex_pairs)

    assert wrong_brackets, (
        'StructuralError: inconsistent brackets inside ' + complex_pairs
        + 'not detected by from consistency_brackets()')


def list_element_types(circuit_diagram):
    """Return the list of elements ('C', 'Q' or 'R' ) of a diagram. Used for
    testing.

    Parameters
    ----------
    circuit_diagram : str
        Scheme of the circuit given by input

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

def test_list_element_types_no_elements():
    """Check that the help function to list the elements in a diagram works on
    an empty diagram.

    GIVEN: the circuit diagram is a pair of brackets, with no (valid) element
    WHEN: I check if the listing of the element types is correct
    THEN: the element types of the circuit diagram are listed correctly: no
    type of element detected
    """
    no_element_diagram = '()'
    listing = list_element_types(no_element_diagram)
    expected_list = []

    assert listing==expected_list, (
        'Listing error: element listing of the empty diagram \''
        + str(no_element_diagram) + '\' differs from the correct one: []')

def test_list_element_types_single_element():
    """Check that the help function to list the elements in a diagram works on
    an single element diagram.

    GIVEN: the circuit diagram is a pair of brackets, with just one (valid)
    element
    WHEN: I check if the listing of the element types is correct
    THEN: the single element type of the circuit diagram is listed correctly
    """
    single_element_diagram = '[R1]'
    listing = list_element_types(single_element_diagram)
    expected_list = ['R']

    assert listing==expected_list, (
        'Listing error: element listing of the single element diagram \''
        + str(single_element_diagram) + '\' differs from the correct one: '
        + str(expected_list))

def test_list_element_types_many_element():
    """Check that the help function to list the elements in a diagram works on
    a many element diagram.

    GIVEN: the circuit diagram is composed by three (valid) elements
    WHEN: I check if the listing of the element types is correct
    THEN: the three element types of the circuit diagram are listed correctly
    """
    many_element_diagram = '([C1Q2]R3)'
    listing = list_element_types(many_element_diagram)
    expected_list = ['C', 'Q', 'R']

    assert listing==expected_list, (
        'Listing error: element listing of the many element diagram \''
        + str(many_element_diagram) + '\' differs from the correct one: '
        + str(expected_list))

def test_list_element_types_repeated_element():
    """Check that the help function to list the elements in a diagram works on
    a diagram with repeated element.

    GIVEN: the circuit diagram is composed by two (valid) elements, with the
    same type
    WHEN: I check if the listing of the element types is correct
    THEN: the only element type present in the circuit diagram is listed
    correctly, i.e. twice
    """
    many_element_diagram = '[C1C2]'
    listing = list_element_types(many_element_diagram)
    expected_list = ['C', 'C']

    assert listing==expected_list, (
        'Listing error: element listing of the repeated element diagram \''
        + str(many_element_diagram) + '\' differs from the correct one: '
        + str(expected_list))

def test_list_element_types_invalid_element():
    """Check that the help function to list the elements in a diagram lists
    only the purposeful types ('C', 'R' or 'Q') with a diagram that also has
    other element types.

    GIVEN: the circuit diagram is composed by one valid-type element and one
    invalid-type element
    WHEN: I check if the listing of the element types considers only the
    purposeful types
    THEN: only the purposeful element type of the circuit diagram is listed
    correctly
    """
    invalid_element_diagram = '[R1F2]' #F is not a valid element type
    listing = list_element_types(invalid_element_diagram)
    expected_list = ['R']

    assert listing==expected_list, (
        'Listing error: element listing of the many element diagram \''
        + str(invalid_element_diagram) + '\' differs from the correct one: '
        + str(expected_list))


def invalid_characters(circuit_diagram):
    """Given a circuit diagram, return any invalid character, i.e. different
    than '(', ')', '[', ']', 'C', 'Q', 'R' or natural numbers. Used for
    testing.

    Parameters
    ----------
    circuit_diagram : str
        Scheme of the circuit given by input

    Returns
    -------
    wrong_characters : str
        String that contains all the invalid characters, separated by a
        whitespace
    wrong_characters_index : list
        List of indexes of the invalid characters in the string
    """
    wrong_characters = ''
    wrong_characters_index = []
    for i, char in enumerate(circuit_diagram):
        if (char not in {'(', ')', '[', ']', 'C', 'Q', 'R'}
            and not char.isnumeric()):
            wrong_characters += char + ' '
            wrong_characters_index.append(i)
    return wrong_characters, wrong_characters_index

def test_invalid_characters_empty():
    """Check that the help function to find invalid characters in a diagram
    works on a pair of round brackets diagram.
    If no invalid character is detected, the returned string and list given by
    the function under test are empty.

    GIVEN: the circuit diagram is an empty string
    WHEN: I check if there are invalid characters inside the diagram
    THEN: no invalid character is detected
    """
    empty_string_diagram = ''
    wrong_characters, wrong_characters_index = invalid_characters(
        empty_string_diagram)

    assert not wrong_characters, (
        'StructuralError: invalid character(s) ' + wrong_characters
        + ' at ' + str(wrong_characters_index) + ' in ' + empty_string_diagram
        + 'from invalid_characters(). Cannot have invalid characters because'
        + 'the string is empty')

def test_invalid_characters_single_element():
    """Check that the help function to find invalid characters in a diagram
    works on a diagram with a single element and a pair of round brackets.
    If no invalid character is detected, the returned string and list given by
    the function under test are empty.

    GIVEN: the circuit diagram as a single element inside a pair of brackets
    (all valid characters)
    WHEN: I check if there are invalid characters inside the diagram
    THEN: no invalid character is detected
    """
    single_element_diagram = '(R1)'
    wrong_characters, wrong_characters_index = invalid_characters(
        single_element_diagram)

    assert not wrong_characters, (
        'StructuralError: invalid character(s) ' + wrong_characters
        + ' at ' + str(wrong_characters_index) + ' in '
        + single_element_diagram + ' from invalid_characters(). Only round '
        + 'and square brackets, C, Q, R and natural numbers are allowed')

def test_invalid_characters_many_element():
    """Check that the help function to find invalid characters in a diagram
    works on a diagram with all element types and brackets.
    If no invalid character is detected, the returned string and list given by
    the function under test are empty.

    GIVEN: a circuit diagram with all element types possible and with both
    types of brackets (thus with all valid characters)
    WHEN: I check if there are invalid characters inside the diagram
    THEN: no invalid character is detected
    """
    many_element_diagram = '([C1Q2]R3)'
    wrong_characters, wrong_characters_index = invalid_characters(
        many_element_diagram)

    assert not wrong_characters, (
        'StructuralError: invalid character(s) ' + wrong_characters
        + ' at ' + str(wrong_characters_index) + ' in '
        + many_element_diagram + 'from invalid_characters(). Only round '
        + 'and square brackets, C, Q, R and natural numbers are allowed')

def test_invalid_characters_invalid_characters():
    """Check that the help function to find invalid characters in a diagram
    works on a diagram with multiple invalid characters.
    If invalid characters are detected, the returned string given by the
    function under test contain the invalid characters while the returned list
    their index in the input string.

    GIVEN: the circuit diagram with multiple invalid characters and some valid
    characters
    WHEN: I check if there are invalid characters inside the diagram
    THEN: all and only the invalid characters are reported as such
    """
    invalid_characters_diagram = '(Z&R1G3)'  #Z, & and G are not valid types
    expected_result = 'Z & G '
    wrong_characters, wrong_characters_index = invalid_characters(
        invalid_characters_diagram)

    assert wrong_characters==expected_result, (
        'StructuralError: invalid character(s) ' + wrong_characters
        + ' at ' + str(wrong_characters_index) + ' in '
        + invalid_characters_diagram + 'from invalid_characters() are not '
        + 'the ones expected ' + expected_result + '. Only round and square '
        + 'brackets, C, Q, R and natural numbers are allowed')


def inconsistent_elements(circuit_diagram):
    """Given a circuit diagram, return any inconsistent element character:
    each element is composed by a capital letter among {'C', 'Q', 'R'}
    followed by a natural number. Used for testing.

    Parameters
    ----------
    circuit_diagram : str
        Scheme of the circuit given by input

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
                wrong_elements += (char + str(circuit_diagram[i+1])
                                   + ' ')
                wrong_element_index.append(i)
        elif (char.isnumeric() and circuit_diagram[0]!=char):
            if not (circuit_diagram[i-1] in {'C', 'Q', 'R'}):
                wrong_elements += (str(circuit_diagram[i-1]) + char
                                   + ' ')
                wrong_element_index.append(i-1)
    return wrong_elements, wrong_element_index

def test_inconsistent_elements_no_element():
    """Check that the help function to find inconsistent elements in a diagram
    works on a diagram with a no element but only a pair of round brackets.
    If no inconsistent element is detected, the returned string and list given
    by the function under test are empty.

    GIVEN: the circuit diagram is just a pair of round brackets, with no
    (invalid) element
    WHEN: I check if there are invalid elements inside the diagram
    THEN: no invalid element is detected
    """
    no_element_diagram = '()'
    wrong_elements, wrong_element_index = inconsistent_elements(
        no_element_diagram)

    assert not wrong_elements, (
        'StructuralError: element inconsistency for '+ wrong_elements
        + ' at ' + str(wrong_element_index) + ': ' + no_element_diagram
        + 'from inconsistent_elements(). An element is composed by a valid '
        + 'letter followed by a natural number')

def test_inconsistent_elements_single_element():
    """Check that the help function to find invalid characters in a diagram
    works on a diagram with a single element and a pair of round brackets.
    If no inconsistent element is detected, the returned string and list given
    by the function under test are empty.

    GIVEN: the circuit diagram as a single (valid) element inside a pair of
    brackets
    WHEN: I check if there are invalid elements inside the diagram
    THEN: no invalid element is detected
    """
    single_element_diagram = '(R1)'
    wrong_elements, wrong_element_index = inconsistent_elements(
        single_element_diagram)

    assert not wrong_elements, (
        'StructuralError: element inconsistency for '+ wrong_elements
        + ' at ' + str(wrong_element_index) + ': ' + single_element_diagram
        + 'from inconsistent_elements(). An element is composed by a valid '
        + 'letter followed by a natural number')

def test_inconsistent_elements_many_element():
    """Check that the help function to find invalid characters in a diagram
    works on a diagram with multiple elements and a many brackets.
    If no inconsistent element is detected, the returned string and list given
    by the function under test are empty.

    GIVEN: the circuit diagram as a three (valid) element inside two sets of
    brackets
    WHEN: I check if there are invalid elements inside the diagram
    THEN: no invalid element is detected
    """
    many_element_diagram = '([C1Q2]R3)'
    wrong_elements, wrong_element_index = inconsistent_elements(
        many_element_diagram)

    assert not wrong_elements, (
        'StructuralError: element inconsistency for '+ wrong_elements
        + ' at ' + str(wrong_element_index) + ': ' + many_element_diagram
        + 'from inconsistent_elements(). An element is composed by a valid '
        + 'letter followed by a natural number')

def test_inconsistent_elements_invalid_element():
    """Check that the help function to find invalid elements in a diagram
    works on a diagram with multiple invalid elements.
    If invalid elements are detected, the returned string given by the
    function under test contain the invalid elements and the returned list
    their index in the input string.

    GIVEN: the circuit diagram with two invalid elements (the last two) and a
    valid element (the first one)
    WHEN: I check if there are invalid elements inside the diagram
    THEN: all and only the invalid characters are reported as such
    """
    invalid_element_diagram = '(C1R[2G3])' #R2 is split across a bracket,
                                           #G3 has an invalid element type
    wrong_elements, wrong_element_index = inconsistent_elements(
        invalid_element_diagram)
    expected_result = 'R[ [2 G3 '

    assert wrong_elements==expected_result, (
        'StructuralError: element inconsistency for '+ wrong_elements
        + ' at ' + str(wrong_element_index) + ' in ' + invalid_element_diagram
        + 'from inconsistent_elements(). An element is composed by a valid '
        + 'letter followed by a natural number')


def inconsistent_numbers(circuit_diagram):
    """Given a circuit diagram, return any inconsistent element number: each
    element has a number that is the same of its order of writing in the
    string. Used for testing.

    Parameters
    ----------
    circuit_diagram : str
        Scheme of the circuit given by input

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
                wrong_numbers += (str(circuit_diagram[i-1:i+1])
                                  + ' ')
                wrong_numbers_index.append(i)
    return wrong_numbers, wrong_numbers_index

def test_inconsistent_numbers_single_element():
    """Check that the help function to find invalid numbers in a diagram
    works on a diagram with a single element. I recall here that a number
    of an element must not only be a numeric char, but also it must correspond
    to the order of apparition.
    If no invalid number is detected, the returned string and list given by
    the function under test are empty.

    GIVEN: the circuit diagram with a single elements (that has a valid number)
    WHEN: I check if there are invalid numbers inside the diagram
    THEN: no invalid number is detected
    """
    single_element_diagram = '(C1)'
    wrong_numbers, wrong_numbers_index = inconsistent_numbers(
        single_element_diagram)

    assert not wrong_numbers, (
        'StructuralError: wrong number for element(s) '+ wrong_numbers
        + 'at ' + str(wrong_numbers_index) + ' in ' + single_element_diagram
        + 'from inconsistent_numbers(). Element numbers must increase of '
        + '1 unit per time')

def test_inconsistent_numbers_two_elements():
    """Check that the help function to find invalid numbers in a diagram
    works on a diagram with a two elements. I recall here that a number
    of an element must not only be a numeric char, but also it must correspond
    to the order of apparition
    If no invalid number is detected, the returned string and list given by
    the function under test are empty.

    GIVEN: the circuit diagram with two elements (that have valid numbers)
    WHEN: I check if there are invalid numbers inside the diagram
    THEN: no invalid number is detected
    """
    two_element_diagram = '[C1R2]'
    wrong_numbers, wrong_numbers_index = inconsistent_numbers(
        two_element_diagram)

    assert not wrong_numbers, (
        'StructuralError: wrong number for element(s) '+ wrong_numbers
        + 'at ' + str(wrong_numbers_index) + ' in ' + two_element_diagram
        + 'from inconsistent_numbers(). Element numbers must increase of '
        + '1 unit per time')

def test_inconsistent_numbers_two_elements_same_type():
    """Check that the help function to find invalid numbers in a diagram
    works on a diagram with a two elements that have the same type. I will
    recall here that a number of an element must not only be a numeric char,
    but also it must correspond to the order of apparition.
    If no invalid number is detected, the returned string and list given by
    the function under test are empty.

    GIVEN: the circuit diagram with two elements and the same type (that have
    valid numbers)
    WHEN: I check if there are invalid numbers inside the diagram
    THEN: no invalid number is detected
    """
    same_element_type_diagram = '(C1C2)'
    wrong_numbers, wrong_numbers_index = inconsistent_numbers(
        same_element_type_diagram)

    assert not wrong_numbers, (
        'StructuralError: wrong number for element(s) '+ wrong_numbers
        + 'at ' + str(wrong_numbers_index) + ' in ' + same_element_type_diagram
        + 'from inconsistent_numbers(). Element numbers must increase of '
        + '1 unit per time')

def test_inconsistent_numbers_gap_number():
    """Check that the help function to find invalid numbers in a diagram
    works on a diagram with a two elements that have a gap in number between
    them. I recall here that a number of an element must not only be
    a numeric char, but also it must correspond to the order of apparition,
    thus if there is a gap in number at least one of the to must be wrong.
    If invalid numbers are detected, the returned string given by the
    function under test contain the elements with the invalid number, while
    the returned string their index in the sinput string.

    GIVEN: the circuit diagram with two elements that have a gap in number
    (the second one has an invalid numbers)
    WHEN: I check if there are invalid numbers inside the diagram
    THEN: an invalid number is detected for the second element
    """
    same_element_type_diagram = '[Q1C3]'  #No number 2 but a number 3 for C
    wrong_numbers, wrong_numbers_index = inconsistent_numbers(
        same_element_type_diagram)
    expected_result = 'C3 '

    assert wrong_numbers==expected_result, (
        'StructuralError: wrong number for element(s) '+ wrong_numbers
        + 'at ' + str(wrong_numbers_index) + ' in ' + same_element_type_diagram
        + 'from inconsistent_numbers(). The elements with invalid numbers are'
        + 'different than expected ' + expected_result)

def test_inconsistent_numbers_wrong_numbers():
    """Check that the help function to find invalid numbers in a diagram
    works on a diagram with a three elements that two of them have invalid
    numbers. I recall here that a number of an element must not only be
    a numeric char, but also it must correspond to the order of apparition.
    If invalid numbers are detected, the returned string given by the
    function under test contain the elements with the invalid number, while
    the returned string their index in the sinput string.

    GIVEN: the circuit diagram with three elements, where the first and the
    last ones have invalid numbers
    WHEN: I check if there are invalid numbers inside the diagram
    THEN: an invalid number is detected for the first and third elements
    """
    same_element_type_diagram = '(R2[R3C3])' #1 is skipped and there is 3 twice
    wrong_numbers, wrong_numbers_index = inconsistent_numbers(
        same_element_type_diagram)
    expected_result = 'R2 R3 '

    assert wrong_numbers==expected_result, (
        'StructuralError: wrong number for element(s) '+ wrong_numbers
        + 'at ' + str(wrong_numbers_index) + ' in ' + same_element_type_diagram
        + 'from inconsistent_numbers(). The elements with invalid numbers are'
        + 'different than expected ' + expected_result)


def generate_circuit_single_element():
    """Generate a valid Circuit object with one (resistor) element."""
    diagram = '(R1)'
    parameters = {'R1': 100.0}
    constant_conditions = {'R1': 0}
    single_element_circuit = generate_circuit(diagram, parameters,
                                              constant_conditions)
    return single_element_circuit

@pytest.fixture
def circuit_single_element():
    """Fixture for the single element Circuit."""
    return generate_circuit_single_element()

def test_initial_circuit_circuit_diagram_single_element(
        circuit_single_element):
    """Check if the circuit diagram inside the Circuit object created by
    the generate_circuit() has a valid circuit diagram, in the case of an
    input circuit diagram with just one element.
    A circuit diagram is made of elements (a letter among {'R', 'C', 'Q'}
    followed by a single digit number) and round and/or square brackets. This
    means that the string must not be empty, and must contain only valid
    characters. There must be a brackets consistency and the first/last
    character must be an open/closed bracket. For the elements, there must be
    at least a valid element, and the digits must represent their order of
    appearence.

    GIVEN: the input circuit diagram, the parameters and the constant
    conditions are valid, they all concern one elment
    WHEN: the Circuit object is created through the generate_circuit()
    function
    THEN: the Circuit object has a valid circuit diagram, the same as the
    input one
    """
    input_circuit_diagram = '(R1)'

    caller = 'generate_circuit()'
    assert isinstance(circuit_single_element, Circuit), (
        'TyperError for output of ' + caller + ' method. It must be an '
        + 'instance of the \'Circuit\' class')

    circuit_diagram = circuit_single_element.circuit_diagram
    assert isinstance(circuit_diagram, str), (
        'TypeError for circuit diagram in ' + caller + '. It must be a string')
    assert circuit_diagram, ('empty string in ' + caller)
    assert (circuit_diagram.startswith('(')
            or circuit_diagram.startswith('[')), (
                'StructuralError: no initial open bracket detected in '
                + caller)
    assert (circuit_diagram.endswith(')') or circuit_diagram.endswith(']')), (
        'StructuralError: no final close bracket detected' + caller)
    wrong_brackets, wrong_brackets_index = consistency_brackets(
        circuit_diagram)
    assert not wrong_brackets, (
        'StructuralError: inconsistent \'' + str(wrong_brackets) + '\' at '
        + wrong_brackets_index + ': ' + circuit_diagram + ' in ' + caller)
    elements_types = list_element_types(circuit_diagram)
    assert elements_types, (
        'StructuralError: no element found in ' + circuit_diagram + ' from '
        + caller + '. An element begins with one of the three letter C, Q or '
        + 'R')
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
        'StructuralError: element inconsistency for '+ wrong_elements + ' at '
        + str(wrong_element_index) + ': ' + circuit_diagram + '. An element '
        + 'is composed by a valid letter followed by a natural number in '
        + caller)
    wrong_numbers, wrong_numbers_index = inconsistent_numbers(circuit_diagram)
    assert not wrong_numbers, (
        'StructuralError: wrong number for element(s) '+ wrong_numbers + 'at '
        + str(wrong_numbers_index) + ' in ' + circuit_diagram + 'from '
        + caller + '. Element numbers must increase of 1 unit per time')

    assert circuit_diagram==input_circuit_diagram, (
    'StructuralError for attribute \'circuit_diagram\' output of '
    + caller + '. It must be the same of the input circuit diagram')


def generate_circuit_two_elements():
    """Generate a valid Circuit object with two elements."""
    diagram = '(R1C2)'
    parameters = {'R1': 1000.0, 'C2': 1e-6}
    constant_conditions = {'R1': 1, 'C2': 0}
    two_elements_circuit = generate_circuit(diagram, parameters,
                                            constant_conditions)
    return two_elements_circuit

@pytest.fixture
def circuit_two_elements():
    """Fixture for the two elements Circuit."""
    return generate_circuit_two_elements()

def test_initial_circuit_circuit_diagram_two_elements(circuit_two_elements):
    """Check if the circuit diagram inside the Circuit object created by
    the generate_circuit() has a valid circuit diagram, in the case of an input
    circuit diagram with two elements.
    A circuit diagram is made of elements (a letter among {'R', 'C', 'Q'}
    followed by a single digit number) and round and/or square brackets. This
    means that the string must not be empty, and must contain only valid
    characters. There must be a brackets consistency and the first/last
    character must be an open/closed bracket. For the elements, there must be
    at least a valid element, and the digits must represent their order of
    appearence.

    GIVEN: the input circuit diagram, the parameters and the constant
    conditions are valid, they all concerns two elements
    WHEN: the Circuit object is created through the generate_circuit()
    function
    THEN: the Circuit object has a valid circuit diagram, the same as the ones
    in input
    """
    input_circuit_diagram = '(R1C2)'

    caller = 'generate_circuit()'
    assert isinstance(circuit_two_elements, Circuit), (
        'TyperError for output of ' + caller + ' method. It must be an '
        + 'instance of the \'Circuit\' class')

    circuit_diagram = circuit_two_elements.circuit_diagram
    assert isinstance(circuit_diagram, str), (
        'TypeError for circuit scheme in ' + caller + '. It must be a string')
    assert circuit_diagram, 'empty string in ' + caller
    assert (circuit_diagram.startswith('(')
            or circuit_diagram.startswith('[')), (
                'StructuralError: no initial open bracket detected in '
                + caller)
    assert (circuit_diagram.endswith(')') or circuit_diagram.endswith(']')), (
        'StructuralError: no final close bracket detected' + caller)
    wrong_brackets, wrong_brackets_index = consistency_brackets(
        circuit_diagram)
    assert not wrong_brackets, (
        'StructuralError: inconsistent \'' + str(wrong_brackets) + '\' at '
        + wrong_brackets_index + ': ' + circuit_diagram + ' in ' + caller)
    elements_types = list_element_types(circuit_diagram)
    assert elements_types, (
        'StructuralError: no element found in ' + circuit_diagram + ' from '
        + caller + '. An element begins with one of the three letter C, Q or'
        + 'R')
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
        'StructuralError: element inconsistency for '+ wrong_elements + ' at '
        + str(wrong_element_index) + ': ' + circuit_diagram + '. An element '
        + 'is composed by a valid letter followed by a natural number in '
        + caller)
    wrong_numbers, wrong_numbers_index = inconsistent_numbers(circuit_diagram)
    assert not wrong_numbers, (
        'StructuralError: wrong number for element(s) '+ wrong_numbers + 'at '
        + str(wrong_numbers_index) + ' in ' + circuit_diagram + 'from '
        + caller + '. Element numbers must increase of 1 unit per time')

    assert circuit_diagram==input_circuit_diagram, (
    'StructuralError for attribute \'circuit_diagram\' output of '
    + caller + '. It must be the same of the input circuit diagram')


def generate_circuit_many_elements():
    """Generate a valid Circuit object with four elements."""
    diagram = '(R1C2[R3Q4])'
    parameters = {'R1': 7100.0, 'C2': 2e-6, 'R3': 10000.0,
                  'Q4': ([0.1e-6, 0.87])}
    constant_conditions = {'R1': 0, 'C2': 0, 'R3': 1, 'Q4': 0}
    many_elements_circuit = generate_circuit(diagram, parameters,
                                             constant_conditions)
    return many_elements_circuit

@pytest.fixture
def circuit_many_elements():
    """Fixture for the four elements Circuit."""
    return generate_circuit_many_elements()

def test_initial_circuit_circuit_diagram_many_elements(circuit_many_elements):
    """Check if the circuit diagram inside the Circuit object created by
    the generate_circuit() has a valid circuit diagram, in the case of an input
    circuit diagram with many elements, a total of four.
    A circuit diagram is made of elements (a letter among {'R', 'C', 'Q'}
    followed by a single digit number) and round and/or square brackets. This
    means that the string must not be empty, and must contain only valid
    characters. There must be a brackets consistency and the first/last
    character must be an open/closed bracket. For the elements, there must be
    at least a valid element, and the digits must represent their order of
    appearence.

    GIVEN: the input circuit diagram, the parameters and the constant
    conditions are valid, they all concerns four elements
    WHEN: the Circuit object is created through the generate_circuit()
    function
    THEN: the Circuit object has a valid circuit diagram, the same as the ones
    in input
    """
    input_circuit_diagram = '(R1C2[R3Q4])'

    caller = 'generate_circuit()'
    assert isinstance(circuit_many_elements, Circuit), (
        'TyperError for output of ' + caller + ' method. It must be an '
        + 'instance of the \'Circuit\' class')

    circuit_diagram = circuit_many_elements.circuit_diagram
    assert isinstance(circuit_diagram, str), (
        'TypeError for circuit scheme in ' + caller + '. It must be a string')
    assert circuit_diagram, 'empty string in ' + caller
    assert (circuit_diagram.startswith('(')
            or circuit_diagram.startswith('[')), (
                'StructuralError: no initial open bracket detected in '
                + caller)
    assert (circuit_diagram.endswith(')') or circuit_diagram.endswith(']')), (
        'StructuralError: no final close bracket detected' + caller)
    wrong_brackets, wrong_brackets_index = consistency_brackets(
        circuit_diagram)
    assert not wrong_brackets, (
        'StructuralError: inconsistent \'' + str(wrong_brackets) + '\' at '
        + wrong_brackets_index + ': ' + circuit_diagram + ' in ' + caller)
    elements_types = list_element_types(circuit_diagram)
    assert elements_types, (
        'StructuralError: no element found in ' + circuit_diagram + ' from '
        + caller + '. An element begins with one of the three letter C, Q or'
        + 'R')
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
        'StructuralError: element inconsistency for '+ wrong_elements + ' at '
        + str(wrong_element_index) + ': ' + circuit_diagram + '. An element '
        + 'is composed by a valid letter followed by a natural number in '
        + caller)
    wrong_numbers, wrong_numbers_index = inconsistent_numbers(circuit_diagram)
    assert not wrong_numbers, (
        'StructuralError: wrong number for element(s) '+ wrong_numbers + 'at '
        + str(wrong_numbers_index) + ' in ' + circuit_diagram + 'from '
        + caller + '. Element numbers must increase of 1 unit per time')

    assert circuit_diagram==input_circuit_diagram, (
    'StructuralError for attribute \'circuit_diagram\' output of '
    + caller + '. It must be the same of the input circuit diagram')


def generate_circuit_wrong_parameters():
    """Generate a Circuit object with two elements. The second element in the
    diagram is invalid. Are also invalid the second value of the parameters
    and the first one of the constant conditions.
    """
    diagram = '(R1Ce)'
    parameters = {'R1': 2.1, 'Ce': '1'} #Ce is an invalid element name, '1' is
                                        #an invalid parameter (a string)
    constant_conditions = {'R1': -1, 'Ce': 1} #-1 is an invalid condition
    wrong_parameters_circuit = generate_circuit(diagram, parameters,
                                                constant_conditions)
    return wrong_parameters_circuit

@pytest.fixture
def circuit_wrong_parameters():
    """Fixture for the invalid Circuit."""
    return generate_circuit_wrong_parameters()

def test_initial_circuit_circuit_diagram_wrong_input(circuit_wrong_parameters):
    """Check if the circuit diagram inside the Circuit object created by
    the generate_circuit() has an invalid circuit diagram, in the case of an
    input circuit diagram that is invalid. They should however be the same.
    A circuit diagram is made of elements (a letter among {'R', 'C', 'Q'}
    followed by a single digit number) and round and/or square brackets. This
    means that the string must not be empty, and must contain only valid
    characters. There must be a brackets consistency and the first/last
    character must be an open/closed bracket. For the elements, there must be
    at least a valid element, and the digits must represent their order of
    appearence.

    GIVEN: the input circuit diagram, the parameters and the constant
    conditions are invalid, they all concerns two elements, of which the last
    one is invalid
    WHEN: the Circuit object is created through the generate_circuit()
    function
    THEN: the Circuit object has an invalid circuit diagram, the same as
    the one in input
    """
    input_circuit_diagram = '(R1Ce)'

    caller = 'generate_circuit()'
    assert isinstance(circuit_wrong_parameters, Circuit), (
        'TyperError for output of ' + caller + ' method. It must be an '
        + 'instance of the \'Circuit\' class')

    circuit_diagram = circuit_wrong_parameters.circuit_diagram
    assert isinstance(circuit_diagram, str), (
        'TypeError for circuit scheme in ' + caller + '. It must be a string')
    assert circuit_diagram, 'empty string in ' + caller
    assert (circuit_diagram.startswith('(')
            or circuit_diagram.startswith('[')), (
                'StructuralError: no initial open bracket detected in '
                + caller)
    assert (circuit_diagram.endswith(')') or circuit_diagram.endswith(']')), (
        'StructuralError: no final close bracket detected' + caller)
    wrong_brackets, wrong_brackets_index = consistency_brackets(
        circuit_diagram)
    assert not wrong_brackets, (
        'StructuralError: inconsistent \'' + str(wrong_brackets) + '\' at '
        + wrong_brackets_index + ': ' + circuit_diagram + ' in ' + caller)
    elements_types = list_element_types(circuit_diagram)
    assert elements_types, (
        'StructuralError: no element found in ' + circuit_diagram + ' from '
        + caller + '. An element begins with one of the three letter C, Q or '
        + 'R')
    expected_result_wrong_characters = 'e '
    wrong_characters, wrong_characters_index = invalid_characters(
        circuit_diagram)
    assert wrong_characters==expected_result_wrong_characters, (
        'StructuralError: invalid character(s) ' + wrong_characters
        + ' at ' + str(wrong_characters_index) + ' in '
        + circuit_diagram + ' from invalid_characters() are not '
        + 'the ones expected ' + expected_result_wrong_characters + '. Only '
        + 'round and square brackets, C, Q, R and natural numbers are allowed')
    expected_result_elements = 'Ce '
    wrong_elements, wrong_element_index = inconsistent_elements(
        circuit_diagram)
    assert wrong_elements==expected_result_elements, (
        'StructuralError: element inconsistency for '+ wrong_elements
        + ' at ' + str(wrong_element_index) + ' in ' + circuit_diagram
        + '. An element is composed by a valid letter followed by a natural '
        + 'number in inconsistent_elements()')
    wrong_numbers, wrong_numbers_index = inconsistent_numbers(circuit_diagram)
    assert not wrong_numbers, (
        'StructuralError: wrong number for element(s) '+ wrong_numbers
        + 'at ' + str(wrong_numbers_index) + ' in ' + circuit_diagram
        + 'from ' + caller + '. Element numbers must increase of 1 unit '
        + 'per time')

    assert circuit_diagram==input_circuit_diagram, (
    'StructuralError for attribute \'circuit_diagram\' output of '
    + caller + '. It must be the same of the input circuit diagram')


##############################################################################
#Tests for the elements names

def invalid_elements_type(element_list):
    """Given the elements in the circuit, return any object that is not a
    2-length string. Used for testing.

    Parameters
    ----------
    elements_circuit : list
        List of the elements in the circuit

    Returns
    -------
    wrong_type : str
        String that contains all the invalid elements, separated by a
        whitespace
    wrong_type_index : list
        List of indexes of the invalid invalid elements in the list
    """
    wrong_types = ''
    wrong_types_index = []
    for i, element in enumerate(element_list):
        if not isinstance(element, str):
            wrong_types+= str(element) + ' '
            wrong_types_index.append(i)
        elif len(element)!=2:
            wrong_types += str(element) + ' '
            wrong_types_index.append(i)
    return wrong_types, wrong_types_index

def test_invalid_elements_type_no_element():
    """Check that the help function to find the elements with the wrong type
    works on an empty list.
    If no invalid element type is detected, the returned string and list
    given by the function under test are empty.

    GIVEN: an empty list
    WHEN: I check if there are invalid elements inside the list
    THEN: no invalid element is found
    """
    no_element = []
    wrong_types, wrong_types_index = invalid_elements_type(no_element)

    assert not wrong_types, (
        'TypeError for element(s) number ' + str(wrong_types_index) + ' '
        + wrong_types + ' in the empty list from invalid_elements_type().'
        + 'Elements can only be strings')

def test_invalid_elements_type_two_elements():
    """Check that the help function to find the elements with the wrong type
    works on a list of strings.
    If no invalid element type is detected, the returned string and list
    given by the function under test are empty.

    GIVEN: a list of two strings, with right type and length
    WHEN: I check if there are invalid elements inside the list
    THEN: no invalid element type is found
    """
    two_elements = ['C1', 'CC']
    wrong_types, wrong_types_index = invalid_elements_type(two_elements)

    assert not wrong_types, (
        'TypeError for element(s) number ' + str(wrong_types_index) + ' '
        + wrong_types + ' in ' + str(two_elements) + ' from '
        + 'invalid_elements_type(). Elements can only be strings')

def test_invalid_elements_type_three_elements():
    """Check that the help function to find the elements with the wrong type
    works on a list of strings, with an element that is not a circuit element.
    If no invalid element type is detected, the returned string and list
    given by the function under test are empty.

    GIVEN: a list of three strings, with right type and length
    WHEN: I check if there are invalid elements inside the list
    THEN: no invalid element type is found
    """
    three_elements = ['Q1', 'C2', '&w'] #Last element not invalid by type
    wrong_types, wrong_types_index = invalid_elements_type(three_elements)

    assert not wrong_types, (
        'TypeError for element(s) number ' + str(wrong_types_index) + ' '
        + wrong_types + ' in ' + str(three_elements)
        + ' from invalid_elements_type(). Elements can only be strings')

def test_invalid_elements_type_wrong_element():
    """Check that the help function to find the elements with the wrong type
    works on a list of strings, with the first three elements that have a wrong
    type or length (two of them are not a string, and the third one is only
    1 char long).
    If invalid element types are detected, the returned string contains the
    invalid elements, and the returned list contains their index in the input
    string.

    GIVEN: a list of four objects, with only the last one that has a right
    type and length
    WHEN: I check if there are invalid elements inside the list
    THEN: the first three elements are detected as invalid
    """
    three_elements = [1.2, ['C2'], 'R', 'R4'] #The only valid element type is
                                              #a string of length 2
    wrong_types, wrong_types_index = invalid_elements_type(three_elements)
    expected_result = '1.2 [\'C2\'] R '

    assert wrong_types==expected_result, (
        'TypeError for element(s) number ' + str(wrong_types_index) + ' '
        + wrong_types + ' in ' + str(three_elements)
        + ' from invalid_elements_type(). The wrong element types are '
        + 'different from the expected: ' + str(expected_result))


def invalid_elements_character(elements_circuit):
    """Given an element list, return any character that as a fist character
    invalid, i.e. any outside R, C, Q, or as a second character invalid, i.e.
    not numerical. Used for testing.

    Parameters
    ----------
    elements_circuit : list
        List of the elements in the circuit that will figure in the fit

    Returns
    -------
    wrong_char : str
        String that contains all the invalid elements, separated by a
        whitespace
    wrong_char_index : list
        List of indexes of the invalid invalid elements in the list
    """
    wrong_char = ''
    wrong_char_index = []
    for i, element in enumerate(elements_circuit):
        if (element[0] not in {'R', 'C', 'Q'} or not element[1].isnumeric()):
            wrong_char += str(element) + ' '
            wrong_char_index.append(i)
        else:
            for j, other_element in enumerate(elements_circuit[i+1:]):
                if element[1]==other_element[1]:
                    wrong_char += ('(\'' + str(element) + '\', \''
                                   + str(other_element) + '\')')
                    wrong_char_index.append((i, j+i+1))
    return wrong_char, wrong_char_index

def test_invalid_elements_characters_no_element():
    """Check that the help function to find the elements with the wrong letter
    or number works on an empty list.
    If no invalid element character is detected, the returned string and list
    given by the function under test are empty.

    GIVEN: an empty list
    WHEN: I check if there are invalid characters inside the element of the
    list
    THEN: no invalid element is found
    """
    no_element = []
    wrong_char, wrong_char_index = invalid_elements_character(no_element)

    assert not wrong_char, (
        'StructuralError for element(s) number ' + str(wrong_char_index)
        + ' ' + wrong_char + ' in the empty list in '
        + 'invalid_elements_char_letter(). All elements must begin with a '
        + 'letter among \'C\', \'R\' ' + 'and \'Q\' and must end with a '
        + 'natural number and each element number must be unique')

def test_invalid_elements_characters_one_element():
    """Check that the help function to find the elements with the wrong letter
    or number works on a list with one valid element.
    If no invalid element character is detected, the returned string and list
    given by the function under test are empty.

    GIVEN: an list of an string of length 2 that is a valid elements
    WHEN: I check if there are invalid characters inside the element of the
    list
    THEN: no invalid element is found
    """
    one_element = ['R1']
    wrong_char, wrong_char_index = invalid_elements_character(one_element)

    assert not wrong_char, (
        'StructuralError for element(s) number ' + str(wrong_char_index)
        + ' ' + wrong_char + ' in ' + str(one_element) + 'in '
        + 'invalid_elements_char_letter(). All elements must begin with a '
        + 'letter among \'C\', \'R\' ' + 'and \'Q\' and must end with a '
        + 'natural number and each element number must be unique')

def test_invalid_elements_characters_three_elements():
    """Check that the help function to find the elements with the wrong letter
    or number works on a list with three valid elements.
    If no invalid element character is detected, the returned string and list
    given by the function under test are empty.

    GIVEN: an list of three strings of length 2 with only valid elements
    WHEN: I check if there are invalid characters inside the element of the
    list
    THEN: no invalid element is found
    """
    three_elements = ['Q1', 'C2', 'R3']
    wrong_char, wrong_char_index = invalid_elements_character(three_elements)

    assert not wrong_char, (
        'StructuralError for element(s) number ' + str(wrong_char_index)
        + ' ' + wrong_char + ' in ' + str(three_elements) + 'in '
        + 'invalid_elements_char_letter(). All elements must begin with a '
        + 'letter among \'C\', \'R\' ' + 'and \'Q\' and must end with a '
        + 'natural number and each element number must be unique')

def test_invalid_elements_type_invalid_characters():
    """Check that the help function to find the elements with the wrong letter
    or number works on a list with three elements, of which only the first one
    is valid.
    If invalid element characters are detected, the returned string contain
    the invalid elements, and the returned list their positions in the string.

    GIVEN: an list of three strings of length 2 with only valid element, the
    first one
    WHEN: I check if there are invalid characters inside the element of the
    list
    THEN: only the last two elements are detected as invalid
    """
    three_elements = ['R1', '1C', 'r3'] #First the (capitol) letter, then the
                                        #number
    wrong_char, wrong_char_index = invalid_elements_character(three_elements)
    expected_result = '1C r3 '

    assert wrong_char==expected_result, (
        'StructuralError for element(s) number ' + str(wrong_char_index) + ' '
        + wrong_char + ' in ' + str(three_elements)
        + 'in invalid_elements_char_letter(). The elements with wrong'
        + 'characters are different from the expected: '
        + str(expected_result))


def test_initial_circuit_elements_single_element(circuit_single_element):
    """Check if the circuit diagram inside the Circuit object created by
    the generate_circuit() has valid elements if there is only one element.
    Each element is a 2-char string, begininng with 'R', 'C' or 'Q', and
    followed by a numeric char. No duplicates with the same number are
    permitted.

    GIVEN: the input circuit diagram, the parameters and the constant
    conditions are valid, they all concerns one elment
    WHEN: the Circuit object is created through the generate_circuit()
    function
    THEN: the Circuit object has a valid element, the same as the ones in input
    """
    input_elements = ['R1']
    parameters_map = circuit_single_element.parameters_map

    caller = 'generate_circuit()'
    assert isinstance(parameters_map, dict), (
        'TypeError for attribute \'parameters_map\' in output of ' + caller
        + '. It must be a dictionary')

    elements_list = list(parameters_map.keys())
    assert isinstance(elements_list, list), (
        'TypeError for output in ' + caller + '. It must be a list')
    wrong_types, wrong_types_index = invalid_elements_type(elements_list)
    assert not wrong_types, (
        'TypeError for element(s) number ' + str(wrong_types_index) + ' '
        + wrong_types + ' in ' + str(elements_list) + ' in ' + caller
        + '. Elements (here dictionary keys) can only be strings of length 2')

    wrong_char, wrong_char_index = invalid_elements_character(elements_list)
    assert not wrong_char, (
        'StructuralError for element(s) number ' + str(wrong_char_index)
        + ' ' + wrong_char + ' in ' + str(elements_list) + ' in ' + caller
        + '. All elements must begin with a letter among \'C\', \'R\' and '
        + '\'Q\', and must end with a natural number and each element number '
        + 'must be unique')

    assert elements_list==input_elements, (
    'StructuralError for elements in attribute \'parameters_map\' in output '
    + 'of ' + caller + '. The elements must be the same of the input one')

def test_initial_circuit_elements_two_elements(circuit_two_elements):
    """Check if the circuit diagram inside the Circuit object created by
    the generate_circuit() has valid elements if there are two elements.
    Each element is a 2-char string, begininng with 'R', 'C' or 'Q', and
    followed by a numeric char. No duplicates with the same number are
    permitted.

    GIVEN: the input circuit diagram, the parameters and the constant
    conditions are valid, they all concerns two elements
    WHEN: the Circuit object is created through the generate_circuit()
    function
    THEN: the Circuit object has valid elements, the same as the oness in input
    """
    input_elements = ['R1', 'C2']
    parameters_map = circuit_two_elements.parameters_map

    caller = 'generate_circuit()'
    assert isinstance(parameters_map, dict), (
        'TypeError for attribute \'parameters_map\' in output of ' + caller
        + '. It must be a dictionary')

    elements_list = list(parameters_map.keys())
    assert isinstance(elements_list, list), (
        'TypeError for output in ' + caller + '. It must be a list')
    wrong_types, wrong_types_index = invalid_elements_type(elements_list)
    assert not wrong_types, (
        'TypeError for element(s) number ' + str(wrong_types_index) + ' '
        + wrong_types + ' in ' + str(elements_list) + ' in ' + caller
        + '. Elements (here dictionary keys) can only be strings of length 2')
    wrong_char, wrong_char_index = invalid_elements_character(elements_list)
    assert not wrong_char, (
        'StructuralError for element(s) number ' + str(wrong_char_index)
        + ' ' + wrong_char + ' in ' + str(elements_list) + ' in ' + caller
        + '. All elements must begin with a letter among \'C\', \'R\' and '
        + '\'Q\', and must end with a natural number and each element number '
        + 'must be unique')

    assert elements_list==input_elements, (
    'StructuralError for elements in attribute \'parameters_map\' in output '
    + 'of ' + caller + '. The elements must be the same of the input one')

def test_initial_circuit_elements_many_elements(circuit_many_elements):
    """Check if the circuit diagram inside the Circuit object created by
    the generate_circuit() has valid elements if there are four elements.
    Each element is a 2-char string, begininng with 'R', 'C' or 'Q', and
    followed by a numeric char. No duplicates with the same number are
    permitted.

    GIVEN: the input circuit diagram, the parameters and the constant
    conditions are valid, they all concerns four elements
    WHEN: the Circuit object is created through the generate_circuit()
    function
    THEN: the Circuit object has valid elements, the same as the oness in input
    """
    input_elements = ['R1', 'C2', 'R3', 'Q4']
    parameters_map = circuit_many_elements.parameters_map

    caller = 'generate_circuit()'
    assert isinstance(parameters_map, dict), (
        'TypeError for attribute \'parameters_map\' in output of ' + caller
        + '. It must be a dictionary')

    elements_list = list(parameters_map.keys())
    assert isinstance(elements_list, list), (
        'TypeError for output in ' + caller + '. It must be a list')
    wrong_types, wrong_types_index = invalid_elements_type(elements_list)
    assert not wrong_types, (
        'TypeError for element(s) number ' + str(wrong_types_index) + ' '
        + wrong_types + ' in ' + str(elements_list) + ' in ' + caller
        + '. Elements (here dictionary keys) can only be strings of length 2')
    wrong_char, wrong_char_index = invalid_elements_character(elements_list)
    assert not wrong_char, (
        'StructuralError for element(s) number ' + str(wrong_char_index)
        + ' ' + wrong_char + ' in ' + str(elements_list) + ' in ' + caller
        + '. All elements must begin with a letter among \'C\', \'R\' and '
        + '\'Q\', and must end with a natural number and each element number '
        + 'must be unique')

    assert elements_list==input_elements, (
    'StructuralError for elements in attribute \'parameters_map\' in '
    + 'of ' + caller + '. The elements must be the same of the input one')

def test_initial_circuit_elements_wrong_elements(circuit_wrong_parameters):
    """Check if the circuit diagram inside the Circuit object created by
    the generate_circuit() has valid elements if there are two elements of
    which one is wrong.
    Each element should be a 2-char string, begininng with 'R', 'C' or 'Q',
    and followed by a numeric char. No duplicates with the same number are
    permitted.

    GIVEN: the input circuit diagram, the parameters and the constant
    conditions are valid only for the first element, while the second element
    has all of the invalid, included the element's name
    WHEN: the Circuit object is created through the generate_circuit()
    function
    THEN: the Circuit object has a valid element, corresponding to the valid
    input element, while the second element is the same of the one in input,
    thus invalid
    """
    input_elements = ['R1', 'Ce']
    parameters_map = circuit_wrong_parameters.parameters_map

    caller = 'generate_circuit()'
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
        + '. Elements (here dictionary keys) can only be strings of '
        + 'length 2')
    expected_result = 'Ce '
    wrong_char, wrong_char_index = invalid_elements_character(elements_list)
    assert wrong_char==expected_result, (
        'StructuralError for element(s) number ' + str(wrong_char_index) + ' '
        + wrong_char + ' in ' + str(elements_list)
        + 'in invalid_elements_char_letter(). The elements with wrong'
        + 'characters are different from the expected: '
        + str(expected_result))

    assert elements_list==input_elements, (
    'StructuralError for elements in attribute \'parameters_map\' in '
    + 'of ' + caller + '. The elements must be the same of the input one')


##############################################################################
#Tests for the parameters

def wrong_tuples_circuit(parameters_map):
    """Return any element inside a dictionary that has not a tuple of length
    2 as a value. Used for testing.

    Parameters
    ----------
    parameters_map : dict
        Dictionary representing the elements with their parameters and
        constant conditions

    Returns
    -------
    wrong_tuples : str
        Elements string with a value in the dictionary that is not a tuple of
        legth 2
    """
    wrong_tuples = ''
    for element, tuple_ in parameters_map.items():
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
    wrong_tuples = wrong_tuples_circuit(no_element)

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
    wrong_tuples = wrong_tuples_circuit(single_element)

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
    wrong_tuples = wrong_tuples_circuit(two_elements)

    assert not wrong_tuples, (
        'TypeError in output of get_impedance_const_input_element_type() '
        + 'for ' + wrong_tuples + ' in ' + str(two_elements) + '. All the '
        + 'values in the dictionary have to be a tuple')

def test_wrong_tuples_circuit_wrong_elements():
    """Check that the help function that returns any item in a dictionary that
    is not a tuple of length 2 works on a dictionary with three objects inside,
    where only the last one is valid.
    If invalid values are detected, the returned string given by the function
    under test contain the element (key of the dictionary) of the invalid
    value.

    GIVEN: a dictionary with only as second value a tuple of length 2
    WHEN: I check if there are invalid values inside the dictionary (any that
    is not a tuple of length 2)
    THEN: only the first two values are detected as wrong
    """
    wrong_elements = {'Q1': ([1e-6, 0.5]), 'C1': (1e-6, 3, 0.5),
                      'R1': (1e-6, 1)} #first two have tuples of length 1 or 3
    expected_result = 'Q1 C1 '
    wrong_tuples = wrong_tuples_circuit(wrong_elements)

    assert wrong_tuples==expected_result, (
        'TypeError in output of get_impedance_const_input_element_type() '
        + 'for ' + wrong_tuples + ' in ' + str(wrong_elements) + '. the '
        + 'values detected differs from the expected ones:' + expected_result)


def invalid_parameters_type(parameters_list):
    """Given a parameters list, return any wrong type parameter: each
    parameter can be a float or a list of length 2 that contains only floats.
    Used for testing.

    Parameters
    ----------
    parameters_list : list
        List of the parameters given by input

    Returns
    -------
    wrong_type : str
        String that contains all the invalid parameters, separated by a
        whitespace
    wrong_type_index : list
        List of indexes of the invalid parameters in the list
    """
    wrong_type = ''
    wrong_type_index = []
    for i, parameter in enumerate(parameters_list):
        if (not isinstance(parameter, float)
            and not isinstance(parameter, list)):
            wrong_type += str(parameter) + ' '
            wrong_type_index.append(i)
        if isinstance(parameter, list):
            if len(parameter)!=2:
                wrong_type+= str(parameter) + ' '
                wrong_type_index.append(i)
            else:
                for _, sub_prameter in enumerate(parameter):
                    if not isinstance(sub_prameter, float):
                        wrong_type += (str(sub_prameter) +  ' in '
                                       + str(parameter) + ' ')
                        wrong_type_index.append(i)
    return wrong_type, wrong_type_index

def test_invalid_parameters_type_no_parameters():
    """Check that the help function to find the invalid parameters types (not
    float nor float lists of length 2) works on an empty list.
    If no invalid parameter is detected, the returned string and list given
    by the function under test are empty.

    GIVEN: an empty list
    WHEN: I check if there are parameters of the invalid type
    THEN: no invalid parameter found
    """
    no_parameters = []
    wrong_type, wrong_type_index = invalid_parameters_type(no_parameters)

    assert not wrong_type, (
        'TypeError for parameter(s) number ' + str(wrong_type_index)
        + ' ' + wrong_type + 'in the empty list in invalid_parameters_type(). '
        + 'Cannot have an invalid parameter because there are no elements ')

def test_invalid_parameters_type_float_parameter():
    """Check that the help function to find the invalid parameters types (not
    float nor float lists of length 2) works on a list with a float parameter.
    If no invalid parameter is detected, the returned string and list given
    by the function under test are empty.

    GIVEN: a list with just one float parameter
    WHEN: I check if there are parameters of the invalid type
    THEN: no invalid parameter found
    """
    float_parameter = [1e-5]
    wrong_type, wrong_type_index = invalid_parameters_type(float_parameter)

    assert not wrong_type, (
        'TypeError for parameter(s) number ' + str(wrong_type_index)
        + ' ' + wrong_type + 'in ' + str(float_parameter) + ' in '
        + 'invalid_parameters_type(). Parameters can only be floats or float '
        + 'lists with exactly two floats')

def test_invalid_parameters_type_list_parameter():
    """Check that the help function to find the invalid parameters types (not
    float nor float lists of length 2) works on a list with a float list of
    length 2 as parameter.
    If no invalid parameter is detected, the returned string and list given
    by the function under test are empty.

    GIVEN: a list with just one float list of length 2 as parameter
    WHEN: I check if there are parameters of the invalid type
    THEN: no invalid parameter found
    """
    list_parameter = [[1e-5, 100.]]
    wrong_type, wrong_type_index = invalid_parameters_type(list_parameter)

    assert not wrong_type, (
        'TypeError for parameter(s) number ' + str(wrong_type_index) + ' '
        + wrong_type + 'in ' + str(list_parameter) + ' in '
        + 'invalid_parameters_type().  Parameters can only be floats or float '
        + 'lists with exactly two floats')

def test_invalid_parameters_type_multiple_parameters():
    """Check that the help function to find the invalid parameters types (not
    float nor float lists of length 2) works on a list with a float list of
    length 2 and two floats as parameters.
    If no invalid parameter is detected, the returned string and list given
    by the function under test are empty.

    GIVEN: a list with one float list (of length 2) parameter and two float
    parameters (of which one is negative)
    WHEN: I check if there are parameters of the invalid type
    THEN: no invalid parameter found
    """
    list_parameter = [[1e-5, 100.], 100., -100.]
    wrong_type, wrong_type_index = invalid_parameters_type(list_parameter)

    assert not wrong_type, (
        'TypeError for parameter(s) number ' + str(wrong_type_index) + ' '
        + wrong_type + 'in ' + str(list_parameter) + ' in '
        + 'invalid_parameters_type(). Parameters can only be floats or float '
        + 'lists with exactly two floats')

def test_invalid_parameters_type_wrong_parameters():
    """Check that the help function to find the invalid parameters types (not
    float nor float lists of length 2) works on a list with a float list of
    length 3, an integer, a string and only one float as parameters.
    If invalid parameter are detected, the returned string contains the
    invalid parameters and the returned list their index in the parameters
    list.

    GIVEN: a list with a float list of length 3, an integer, a string and only
    one float as parameters. Only the last element is correct
    WHEN: I check if there are parameters of the invalid type
    THEN: all the parameters but the last one are detected as invalid
    """
    #Only floats or float lists of length 2 are valid
    list_parameter = [[1e-05, 100.0, 300.0], 1, '6', 10.]
    wrong_type, wrong_type_index = invalid_parameters_type(list_parameter)
    expected_result = '[1e-05, 100.0, 300.0] 1 6 '

    assert wrong_type==expected_result, (
        'TypeError for parameter(s) number ' + str(wrong_type_index)
        + ' ' + wrong_type + 'in ' + str(list_parameter) + ' in '
        + 'invalid_parameters_type(). The detected invalid parameters are'
        + 'different from the expected ones: ' + expected_result)

def test_invalid_parameters_type_wrong_list_parameters():
    """Check that the help function to find the invalid parameters types (not
    float nor float lists of length 2) works on a list with a list of length
    2 that has a float and an integer, and a list of length 2 with both
    floats.
    If invalid parameters are detected, the returned string contains the
    invalid parameters and the returned list their index in the parameters
    list.

    GIVEN: a list with a list of length 2 that has a float and an integer, and
    a list of length 2 with both floats. Only the last element is correct
    WHEN: I check if there are parameters of the invalid type
    THEN: only the second element of the first list is detected as invalid
    """
    #Only floats or float lists of length 2 are valid
    list_parameter = [[50., 100], [47.3e-5, 23.]]
    wrong_type, wrong_type_index = invalid_parameters_type(list_parameter)
    expected_result = '100 in [50.0, 100] '

    assert wrong_type==expected_result, (
        'TypeError for parameter(s) number ' + str(wrong_type_index)
        + ' ' + wrong_type + 'in ' + str(list_parameter) + ' in '
        + 'invalid_parameters_type(). The detected invalid parameters are'
        + 'different from the expected ones: ' + expected_result)


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
        String that contains all the invalid parameters, separated by a
        whitespace
    wrong_value_index : list
        List of indexes of the invalid parameters in the list
    """
    wrong_value = ''
    wrong_value_index = []
    for i, parameter in enumerate(parameters_list):
        if isinstance(parameter, float):
            if parameter<=0:
                wrong_value += str(parameter) + ' '
                wrong_value_index.append(i)
        elif isinstance(parameter, list):
            if parameter[0]<=0:
                wrong_value += (str(parameter[0]) +  ' in ' + str(parameter)
                                + ' ')
                wrong_value_index += str(i)
            if (parameter[1]<0 or parameter[1]>1):
                wrong_value += (str(parameter[1]) +  ' in ' + str(parameter)
                                + ' ')
                wrong_value_index += str(i)
    return wrong_value, wrong_value_index


def test_invalid_parameters_value_no_parameters():
    """Check that the help function to find the invalid parameter values works
    on an empty list.
    The parameters must be positive for float parameters and for the first
    element of the list parameters and within 0 and 1 for the second element
    of the list parameters.
    If no invalid parameter is detected, the returned string and list given
    by the function under test are empty.

    GIVEN: an empty list
    WHEN: I check if there are parameters of invalid value
    THEN: no invalid parameter value found
    """
    no_parameters = []
    wrong_value, wrong_value_index = invalid_parameters_value(no_parameters)

    assert not wrong_value, (
        'ValueError for parameter(s) number ' + str(wrong_value_index) + ' '
        + wrong_value + ' in the empty list in invalid_parameters_value(). '
        + 'Cannot find an invalid parameters because there are no parameters.')

def test_invalid_parameters_value_float_parameters():
    """Check that the help function to find the invalid parameter values
    works on a list with two float parameters.
    The parameters must be positive for float parameters and for the first
    element of the list parameters and within 0 and 1 for the second element
    of the list parameters.
    If no invalid parameter is detected, the returned string and list given
    by the function under test are empty.

    GIVEN: a list with two positve float parameters
    WHEN: I check if there are parameters of the invalid type
    THEN: no invalid parameter found
    """
    float_parameters = [1e-5, 1000.]
    wrong_value, wrong_value_index = invalid_parameters_value(float_parameters)

    assert not wrong_value, (
        'ValueError for parameter(s) number ' + str(wrong_value_index) + ' '
        + wrong_value + ' in ' + str(float_parameters)
        + ' in invalid_parameters_value(). Float parameters must be positive, '
        + 'lists parameters must contain as first parameter a positive number '
        + 'and as second parameter a number between 0 and 1')


def test_invalid_parameters_value_list_parameter():
    """Check that the help function to find the invalid parameter values
    works on a list with a float list parameter.
    The parameters must be positive for float parameters and for the first
    element of the list parameters and within 0 and 1 for the second element
    of the list parameters.
    If no invalid parameter is detected, the returned string and list given
    by the function under test are empty.

    GIVEN: a list with just one float list of a positive float and a bumber
    within 0 and 1 as parameter
    WHEN: I check if there are parameters of the invalid type
    THEN: no invalid parameter found
    """
    list_parameter = [[1e-5, 0.5]]
    wrong_value, wrong_value_index = invalid_parameters_value(list_parameter)

    assert not wrong_value, (
        'ValueError for parameter(s) number ' + str(wrong_value_index) + ' '
        + wrong_value + ' in ' + str(list_parameter)
        + ' in invalid_parameters_value(). Float parameters must be positive, '
        + 'lists parameters must contain as first parameter a positive number '
        + 'and as second parameter a number between 0 and 1')

def test_invalid_parameters_value_wrong_parameters():
    """Check that the help function to find the invalid parameter values
    works on a list with a negative float parameter, a list with as secon
    element a flot bigger than 1, and a positive float parameter.
    The parameters must be positive for float parameters and for the first
    element of the list parameters and within 0 and 1 for the second element
    of the list parameters.
    If invalid parameters are detected, the returned string contains the
    invalid parameters and the returned list their index in the parameters
    list.

    GIVEN: a list with a negative float parameter, a list with as secon
    element a flot bigger than 1, and a positive float parameter. The first
    float of the list parameter and the last float parameter are the only
    valid parameters
    WHEN: I check if there are parameters of the invalid type
    THEN: the first float parameter and the second float in the list parameter
    are detectd as invalid
    """
    list_parameter = [-200.0, [1e-05, 100.0], 23.45]
    expected_result = '-200.0 100.0 in [1e-05, 100.0] '
    wrong_value, wrong_value_index = invalid_parameters_value(list_parameter)

    assert wrong_value==expected_result, (
        'ValueError for parameter(s) number ' + str(wrong_value_index) + ' '
        + wrong_value + ' in ' + str(list_parameter)
        + ' in invalid_parameters_value(). The detected invalid parameters'
        + 'differ from the expected ones: ' + expected_result)


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
        separated by a whitespace
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
                wrong_match += (str(element) + ' and '
                                + str(parameters_list[i][0]) + ' ')
                wrong_match_index.append(i)
        else:
            if not isinstance(parameters_list[i][0], list):
                wrong_match += (str(element) + ' and '
                                + str(parameters_list[i][0]) + ' ')
                wrong_match_index.append(i)
    return wrong_match, wrong_match_index

def test_elements_parameters_match_no_parameters():
    """Check that the help function to find the invalid match between elements
    type and parameters in the parameters dictionary works on an empty
    dictionary.
    R and C elements must have a float as parameter, Q must have a list.
    If no invalid parameter is detected, the returned string and list given
    by the function under test are empty.

    GIVEN: an empty dictionary
    WHEN: I check if there are invalid parameters matches between the type of
    the element (the keys) and the type of the parameters (the first element
    of the tuple in the values)
    THEN: no invalid matches value found
    """
    no_parameters = {}
    wrong_match, wrong_match_index = elements_parameters_match(no_parameters)

    assert not wrong_match, (
        'StructuralError: bad match for '+ wrong_match + ' in '
        + str(wrong_match_index) + 'for empty dictonary from '
        + 'invalid_parameters_value(). Cannot find an invalid matches '
        + 'because there are no elements/parameters.')

def test_elements_parameters_match_single_parameter():
    """Check that the help function to find the invalid match between elements
    type and parameters in the parameters dictionary works on a dictionary with
    one (valid) item.
    R and C elements must have a float as parameter, Q must have a list.
    If no invalid match is detected, the returned string and list given by
    the function under test are empty.

    GIVEN: a dictionary with one valid item, a capacitor one
    WHEN: I check if there are invalid parameters matches between the type of
    the element (the keys) and the type of the parameters (the first element
    of the tuple in the values)
    THEN: no invalid matches value found
    """
    single_parameter = {'C1': (1e-6, 0)}
    wrong_match, wrong_match_index = elements_parameters_match(
        single_parameter)

    assert not wrong_match, (
        'StructuralError: bad match for '+ wrong_match + ' in '
        + str(wrong_match_index) + 'for ' + str(single_parameter)  + ' from '
        + 'invalid_parameters_value(). R and C elements must have a '
        + 'float as parameter, Q must have a list.')

def test_elements_parameters_match_two_parameters():
    """Check that the help function to find the invalid match between elements
    type and parameters in the parameters dictionary works on a dictionary with
    two (valid) items.
    R and C elements must have a float as parameter, Q must have a list.
    If no invalid match is detected, the returned string and list given by
    the function under test are empty.

    GIVEN: a dictionary with two valid items, a cpe and a resistor ones
    WHEN: I check if there are invalid parameters matches between the type of
    the element (the keys) and the type of the parameters (the first element
    of the tuple in the values)
    THEN: no invalid matches value found
    """
    two_parameters = {'Q1': ([1e-6, 0.5], 1), 'R2': (100., 0)}
    wrong_match, wrong_match_index = elements_parameters_match(two_parameters)

    assert not wrong_match, (
        'StructuralError: bad match for '+ wrong_match + ' in '
        + str(wrong_match_index) + 'for ' + str(two_parameters)  + ' from '
        + 'invalid_parameters_value(). R and C elements must have a '
        + 'float as parameter, Q must have a list.')

def test_elements_parameters_match_wrong_parameters():
    """Check that the help function to find the invalid match between elements
    type and parameters in the parameters dictionary works on a dictionary
    with three items, of which only the last one is valid.
    R and C elements must have a float as parameter, Q must have a list.
    If invalid matches are detected, the returned string conatin the invalid
    elements and parameters, while the returned list their indexes in the
    listing.

    GIVEN: a dictionary with three items, but the first two (a resistor and a
    cpe) have a bad match, while the last one (a resistor) has a vlid match
    WHEN: I check if there are invalid parameters matches between the type of
    the element (the keys) and the type of the parameters (the first element
    of the tuple in the values)
    THEN: the first two items of the dictionary are detected as invalid mathc,
    while the last one is considered valid
    """
    wrong_parameters = {'R1': ([1e-06, 0.5], 0), 'Q2': (10.0, 1),
                        'R2': (2000., 0)}
    wrong_match, wrong_match_index = elements_parameters_match(
        wrong_parameters)
    expected_result = 'R1 and [1e-06, 0.5] Q2 and 10.0 '

    assert wrong_match==expected_result, (
        'StructuralError: bad match for '+ wrong_match + ' in '
        + str(wrong_match_index) + 'for ' + str(wrong_parameters)  + ' from '
        + 'invalid_parameters_value(). The invalid matches found are '
        + 'different from the expected ones: ' + expected_result)


def test_initial_circuit_parameters_single_parameter(circuit_single_element):
    """Check if the parameters map inside the Circuit object created by
    the generate_circuit() has valid parameters, in the case of anjust one
    input parameter.
    Each parameter may be a float or a list itself contaiinng only 2 floats.
    There are also value restrictions on the float variables: if they
    are parameters they have to be positive. If they are inside a list, the
    first must be positive, the secon must be within [0,1].
    Then there must be a match in length and type between the parameters and
    the circuit string: float parameters are for 'R' or 'C' elements,
    while lists are for 'Q'.

    GIVEN: the input circuit diagram, the parameters and the constant
    conditions are valid, they all concerns one valid elment
    WHEN: the Circuit object is created through the generate_circuit()
    function
    THEN: the Circuit object has valid parameters, the same as the ones in
    input
    """
    input_parameters = [100.]
    parameters_map = circuit_single_element.parameters_map

    caller = 'generate_circuit()'
    wrong_tuples = wrong_tuples_circuit(parameters_map)
    assert not wrong_tuples, (
        'TypeError in output of get_impedance_const_input_element_type() '
        + 'for element \'' + wrong_tuples + '\'. Its value in the dictionary '
        + 'have to be a tuple')
    parameters_values = list(parameters_map.values())
    parameters_list = [parameter[0] for parameter in parameters_values]

    wrong_type, wrong_type_index = invalid_parameters_type(
        parameters_list)
    assert not wrong_type, (
        'TypeError for parameter(s) number ' + str(wrong_type_index) + ' '
        + wrong_type + 'in ' + str(parameters_list) + ' in ' + caller
        + '. Parameters can only be floats or float lists which contains '
        + 'exactly 2 parameters')

    wrong_value, wrong_value_index = invalid_parameters_value(parameters_list)
    assert not wrong_value, (
        'ValueError for parameter(s) number ' + str(wrong_value_index) + ' '
        + wrong_value + ' in ' + str(parameters_list) + ' in ' + caller
        + '. Float parameters must be positive, lists parameters must contain '
        + 'as first parameter a positive number and as second parameter a '
        + 'number between 0 and 1')
    wrong_match, wrong_match_index = elements_parameters_match(parameters_map)
    assert not wrong_match, (
        'StructuralError: bad match for '+ wrong_match + ' in '
        + str(wrong_match_index) + 'for dictonary \'' + str(parameters_map)
        + '\' from invalid_parameters_value() . \'R\' and \'C\' elements must '
        + 'have a float as parameter, \'Q\' must have a list')

    assert parameters_list==input_parameters, (
    'StructuralError for parameters of output of ' + caller + '. It must be '
    + 'the same of the input parameters')

def test_initial_circuit_parameters_two_parameters(circuit_two_elements):
    """Check if the parameters map inside the Circuit object created by
    the generate_circuit() has valid parameters, in the case of two parameters
    in input.
    Each parameter may be a float or a list itself contaiinng only 2 floats.
    There are also value restrictions on the float variables: if they
    are parameters they have to be positive. If they are inside a list, the
    first must be positive, the secon must be within [0,1].
    Then there must be a match in length and type between the parameters and
    the circuit string: float parameters are for 'R' or 'C' elements,
    while lists are for 'Q'.

    GIVEN: the input circuit diagram, the parameters and the constant
    conditions are valid, they all concerns two valid elements
    WHEN: the Circuit object is created through the generate_circuit()
    function
    THEN: the Circuit object has valid parameters, the same as the ones in
    input
    """
    input_parameters = [1000., 1e-6]
    parameters_map = circuit_two_elements.parameters_map

    caller = 'generate_circuit()'
    wrong_tuples = wrong_tuples_circuit(parameters_map)
    assert not wrong_tuples, (
        'TypeError in output of get_impedance_const_input_element_type() '
        + 'for element \'' + wrong_tuples + '\'. Its value in the dictionary '
        + 'have to be a tuple')
    parameters_values = list(parameters_map.values())
    parameters_list = [parameter[0] for parameter in parameters_values]

    wrong_type, wrong_type_index = invalid_parameters_type(parameters_list)
    assert not wrong_type, (
        'TypeError for parameter(s) number ' + str(wrong_type_index) + ' '
        + wrong_type + 'in ' + str(parameters_list) + ' in ' + caller
        + '. Parameters can only be floats or float lists which contains '
        + 'exactly 2 parameters')

    wrong_value, wrong_value_index = invalid_parameters_value(parameters_list)
    assert not wrong_value, (
        'ValueError for parameter(s) number ' + str(wrong_value_index) + ' '
        + wrong_value + ' in ' + str(parameters_list) + ' in ' + caller
        + '. Float parameters must be positive, lists parameters must contain '
        + 'as first parameter a positive number and as second parameter a '
        + 'number between 0 and 1')
    wrong_match, wrong_match_index = elements_parameters_match(parameters_map)
    assert not wrong_match, (
        'StructuralError: bad match for '+ wrong_match + ' in '
        + str(wrong_match_index) + 'for dictonary \'' + str(parameters_map)
        + '\' from invalid_parameters_value() . \'R\' and \'C\' elements '
        + 'must have a float as parameter, \'Q\' must have a list')

    assert parameters_list==input_parameters, (
        'StructuralError for parameters of output of ' + caller
        + '. It must be the same of the input parameters')

def test_initial_circuit_parameters_many_parameters(circuit_many_elements):
    """Check if the parameters map inside the Circuit object created by
    the generate_circuit() has valid parameters, in the case of four input
    parameters.
    Each parameter may be a float or a list itself contaiinng only 2 floats.
    There are also value restrictions on the float variables: if they
    are parameters they have to be positive. If they are inside a list, the
    first must be positive, the secon must be within [0,1].
    Then there must be a match in length and type between the parameters and
    the circuit string: float parameters are for 'R' or 'C' elements,
    while lists are for 'Q'.

    GIVEN: the input circuit diagram, the parameters and the constant
    conditions are valid, they all concerns four valid elements
    WHEN: the Circuit object is created through the generate_circuit()
    function
    THEN: the Circuit object has valid parameters, the same as the ones in
    input
    """
    input_parameters = [7100.0, 2e-6, 10000.0, [0.1e-6, 0.87]]
    parameters_map = circuit_many_elements.parameters_map

    caller = 'generate_circuit()'
    wrong_tuples = wrong_tuples_circuit(parameters_map)
    assert not wrong_tuples, (
        'TypeError in output of get_impedance_const_input_element_type() '
        + 'for element \'' + wrong_tuples + '\'. Its value in the dictionary '
        + 'have to be a tuple')
    parameters_values = list(parameters_map.values())
    parameters_list = [parameter[0] for parameter in parameters_values]

    wrong_type, wrong_type_index = invalid_parameters_type(parameters_list)
    assert not wrong_type, (
        'TypeError for parameter(s) number ' + str(wrong_type_index) + ' '
        + wrong_type + 'in ' + str(parameters_list) + ' in ' + caller
        + '. Parameters can only be floats or float lists which contains '
        + 'exactly 2 parameters')

    wrong_value, wrong_value_index = invalid_parameters_value(parameters_list)
    assert not wrong_value, (
        'ValueError for parameter(s) number ' + str(wrong_value_index) + ' '
        + wrong_value + ' in ' + str(parameters_list) + ' in ' + caller
        + '. Float parameters must be positive, lists parameters must contain '
        + 'as first parameter a positive number and as second parameter a '
        + 'number between 0 and 1')
    wrong_match, wrong_match_index = elements_parameters_match(parameters_map)
    assert not wrong_match, (
        'StructuralError: bad match for '+ wrong_match + ' in '
        + str(wrong_match_index) + 'for dictonary \'' + str(parameters_map)
        + '\' from invalid_parameters_value() . \'R\' and \'C\' elements '
        + 'must have a float as parameter, \'Q\' must have a list')

    assert parameters_list==input_parameters, (
        'StructuralError for parameters of output of ' + caller
        + '. It must be the same of the input parameters')

def test_initial_circuit_parameters_wrong_parameters(circuit_wrong_parameters):
    """Check if the parameters map inside the Circuit object created by
    the generate_circuit() has valid parameters, in the case of two input
    parameters, of which the second one is invalid.
    Each parameter may be a float or a list itself contaiinng only 2 floats.
    There are also value restrictions on the float variables: if they
    are parameters they have to be positive. If they are inside a list, the
    first must be positive, the secon must be within [0,1].
    Then there must be a match in length and type between the parameters and
    the circuit string: float parameters are for 'R' or 'C' elements,
    while lists are for 'Q'.

    GIVEN: the input circuit diagram, the parameters and the constant
    conditions are valid, they all concerns two valid elements. The second
    parameter has an invalid type
    WHEN: the Circuit object is created through the generate_circuit()
    function
    THEN: the Circuit object has one and only one invalid parameter (by type),
    the same as the one in input, thus also has a bad match
    """
    input_parameters = [2.1, '1']
    parameters_map = circuit_wrong_parameters.parameters_map

    caller = 'generate_circuit()'
    wrong_tuples = wrong_tuples_circuit(parameters_map)
    assert not wrong_tuples, (
        'TypeError in output of get_impedance_const_input_element_type() '
        + 'for element \'' + wrong_tuples + '\'. Its value in the dictionary '
        + 'have to be a tuple')
    parameters_values = list(parameters_map.values())
    parameters_list = [parameter[0] for parameter in parameters_values]

    expected_result_type = '1 '
    wrong_type, wrong_type_index = invalid_parameters_type(parameters_list)
    assert wrong_type==expected_result_type, (
        'TypeError for parameter(s) number ' + str(wrong_type_index)
        + ' ' + wrong_type + 'in ' + str(parameters_list) + ' in '
        + 'invalid_parameters_type(). The detected invalid parameters are'
        + 'different from the expected ones: ' + expected_result_type)

    wrong_value, wrong_value_index = invalid_parameters_value(parameters_list)
    assert not wrong_value, (
        'ValueError for parameter(s) number ' + str(wrong_value_index) + ' '
        + wrong_value + ' in ' + str(parameters_list) + ' in ' + caller
        + '. Float parameters must be positive, lists parameters must contain '
        + 'as first parameter a positive number and as second parameter a '
        + 'number between 0 and 1')

    expected_result_match = 'Ce and 1 '
    wrong_match, wrong_match_index = elements_parameters_match(parameters_map)
    assert wrong_match==expected_result_match, (
        'StructuralError: bad match for '+ wrong_match + ' in '
        + str(wrong_match_index) + 'for ' + str(parameters_map)  + ' from '
        + 'invalid_parameters_value(). The invalid matches found are different '
        + 'from the expected ones: ' + expected_result_match)

    assert parameters_list==input_parameters, (
        'StructuralError for parameters of output of ' + caller
        + '. It must be the same of the input parameters')


##############################################################################
#Constant conditions tests

def invalid_constant_cond(constant_conditions_list):
    """Given a constant conditions list, return any wrong constant conditions:
    they can only be 0 or 1 in integer format. Used for testing.

    Parameters
    ----------
    constant_conditions_list : list
        List of the constant conditions

    Returns
    -------
    wrong_conds : str
        String that contains all the invalid constant conditions, separated by
        a whitespace
    wrong_conds_index : list
        List of indexes of the invalid invalid constant conditions in the list
    """
    wrong_conds = ''
    wrong_conds_index = []
    for i, constant_condition in enumerate(constant_conditions_list):
        if not isinstance(constant_condition, int):
            wrong_conds+= str(constant_condition) + ' '
            wrong_conds_index.append(i)
        else:
            if constant_condition<0 or constant_condition>1:
                wrong_conds+= str(constant_condition) + ' '
                wrong_conds_index.append(i)
    return wrong_conds, wrong_conds_index

def test_invalid_constant_cond_no_const_cond():
    """Check that the help function to test if a list (which element are named
    constant conditions) contains all integers works on an empty list.
    If no invalid constant condition is detected, the returned string and list
    given by the function under test are empty.

    GIVEN: an empty list
    WHEN: I check if there are invalid constant conditions
    THEN: no invalid constant condition found
    """
    no_const_cond = []
    wrong_conds, wrong_conds_index = invalid_constant_cond(no_const_cond)

    assert not wrong_conds, (
        'TypeError for constant condition(s) ' + str(wrong_conds)
        + ' number ' + str(wrong_conds_index) + ' in the empty list from '
        + 'invalid_constant_type(). Cannot find invalid constant condition '
        + 'type because there are in constant conditions')

def test_invalid_constant_type_single_const_cond():
    """Check that the help function to test if a list (which element are named
    constant conditions) contains all integers works on a list contaiinng only
    one (valid) constant condition. Valid constant condition are only be 0
    or 1 in integer format.
    If no invalid constant condition is detected, the returned string and list
    given by the function under test are empty.

    GIVEN: a list contaiinng only one valid constant condition
    WHEN: I check if there are invalid constant conditions
    THEN: no invalid constant condition found
    """
    single_const_cond = [1]
    wrong_conds, wrong_conds_index = invalid_constant_cond(single_const_cond)

    assert not wrong_conds, (
        'TypeError for constant condition(s) ' + str(wrong_conds)
        + ' number ' + str(wrong_conds_index) + ' in ' + str(single_const_cond)
        + ' from invalid_constant_type(). Constant conditions must be all '
        + 'integers, with value either 0 or 1')

def test_invalid_constant_type_many_const_cond():
    """Check that the help function to test if a list (which element are named
    constant conditions) contains all integers works on a list contaiinng five
    valid constant conditions. Valid constant condition are only be 0
    or 1 in integer format.
    If no invalid constant condition is detected, the returned string and list
    given by the function under test are empty.

    GIVEN: a list contaiinng five valid constant conditions
    WHEN: I check if there are invalid constant conditions
    THEN: no invalid constant condition by type found
    """
    many_const_cond = [1, 0, 1, 0, 0]
    wrong_conds, wrong_conds_index = invalid_constant_cond(many_const_cond)

    assert not wrong_conds, (
        'TypeError for constant condition(s) ' + str(wrong_conds)
        + ' number ' + str(wrong_conds_index) + ' in ' + str(many_const_cond)
        + ' from invalid_constant_type(). Constant conditions must be all '
        + 'integers, with value either 0 or 1')

def test_invalid_constant_type_wrong_const_cond():
    """Check that the help function to test if a list (which element are named
    constant conditions) contains all integers works on a list contaiinng five
    constant conditions, of which the only the first one has valid type and
    value. Instead, the second has valid type but invalid value, while the
    last three have invalid type.
    If invalid constant conditions are detected, the returned string contains
    the invalid constant conditions, and the list their indexes in the list.

    GIVEN: a list contaiinng five constant conditions. The first one is the
    only one that has both valid type and value. the second one has invalid
    value, the last three have invalid type
    WHEN: I check if there are invalid constant conditions
    THEN: all and only the last four constant condition are detected as
    invalid
    """
    wrong_const_cond = [1, -1, 1.0, '0', [0]]
    wrong_conds, wrong_conds_index = invalid_constant_cond(wrong_const_cond)
    expected_result = '-1 1.0 0 [0] '

    assert wrong_conds==expected_result, (
        'TypeError for constant condition(s) ' + str(wrong_conds)
        + ' number ' + str(wrong_conds_index) + ' in ' + str(wrong_const_cond)
        + ' from invalid_constant_type(). Invalid constant conditions found'
        + 'are different from the expected ones: ' + expected_result)


def test_generate_constant_conditions_data_no_parameters():
    """Check that the constant conditions dictionary generated by the
    generate_constant_conditions_data() function is valid, when the input
    parameters is an empty dictionary.
    Each value has to be an integer, and can be either 0 or 1. The constant
    conditions list must have the same number of objects of the parameters.
    If invalid constant conditions are detected, the returned string contains
    the invalid constant conditions, and the list their indexes in the list.

    GIVEN: an empty dictionary as parameters
    WHEN: I check if the output of the constant condition generation in the
    generation file is invalid
    THEN: no invalid constant condition is found
    """
    no_parameters = {}
    no_constant_cond = generate_constant_conditions_data(no_parameters)

    caller = 'generate_constant_conditions_data()'
    assert isinstance(no_constant_cond, dict), (
        'TypeError for constant conditions in ' + caller + '. It must be a '
        + 'dictionary')

    conditions = list(no_constant_cond.values())
    wrong_types, wrong_types_index = invalid_constant_cond(conditions)
    assert not wrong_types, (
        'TypeError for constant condition(s) ' + str(wrong_types)
        + ' number ' + str(wrong_types_index) + ' in the empty list from '
        + 'invalid_constant_type(). Cannot find invalid constant condition '
        + 'type because there are in constant conditions')
    length_equality = (len(no_parameters)==len(conditions))
    assert length_equality, (
        'StructuralError: error from ' + caller + ': parameters and constant '
        + 'array list size must be the same. Parameters size: '
        + str(len(no_parameters)) + ', constant conditions size: '
        + str(len(conditions)))

def test_generate_constant_conditions_data_single_parameter():
    """Check that the constant dictionarsy generated by the
    generate_constant_conditions_data() function is valid, when the input
    parameters is a dictionary with one parameter.
    Each value has to be an integer, and can be either 0 or 1. The constant
    conditions list must have the same number of objects of the parameters.

    GIVEN: a dictionary with one valid parameter inside
    WHEN: I check if the output of the constant condition generation in the
    generation file is invalid
    THEN: no invalid constant condition is found
    """
    single_parameter = {'R1': 200.}
    single_constant_cond = generate_constant_conditions_data(single_parameter)
    caller = 'generate_constant_conditions_data()'

    assert isinstance(single_constant_cond, dict), (
        'TypeError for constant conditions in ' + caller + '. It must be a '
        + 'dictionary')

    conditions = list(single_constant_cond.values())
    wrong_types, wrong_types_index = invalid_constant_cond(conditions)
    assert not wrong_types, (
        'TypeError for constant element(s) ' + str(wrong_types) + ' number '
        + str(wrong_types_index) + ' in ' + str(conditions) + ' from '
        + caller + '. Constant conditions must be all integers, with value '
        + 'either 0 or 1')
    length_equality = (len(single_parameter)==len(conditions))
    assert length_equality, (
        'StructuralError: error from ' + caller + ': parameters and '
        + 'constant array list size must be the same. Parameters size: '
        + str(len(single_parameter)) + ', constant conditions size: '
        + str(len(conditions)))

def test_generate_constant_conditions_data_multiple_parameters():
    """Check that the constant dictionarsy generated by the
    generate_constant_conditions_data() function is valid, when the input
    parameters is a dictionary with three (valid) parameters.
    Each value has to be an integer, and can be either 0 or 1. The constant
    conditions list must have the same number of objects of the parameters.

    GIVEN: a dictionary with three valid parameters inside
    WHEN: I check if the output of the constant condition generation in the
    generation file is invalid
    THEN: no invalid constant condition is found
    """
    three_parameters = {'R1': 100., 'C2': 1e-6, 'R3': 1000.}
    three_constant_cond = generate_constant_conditions_data(three_parameters)

    caller = 'generate_constant_conditions_data()'
    assert isinstance(three_constant_cond, dict), (
        'TypeError for constant conditions in ' + caller + '. It must be a '
        + 'dictionary')

    conditions = list(three_constant_cond.values())
    wrong_types, wrong_types_index = invalid_constant_cond(conditions)
    assert not wrong_types, (
        'TypeError for constant element(s) ' + str(wrong_types) + ' number '
        + str(wrong_types_index) + ' in ' + str(conditions) + ' from '
        + caller + '. Constant conditions must be all integers, with value '
        +'either 0 or 1')
    length_equality = (len(three_parameters)==len(conditions))
    assert length_equality, (
        'StructuralError: error from ' + caller + ': parameters and '
        + 'constant array list size must be the same. Parameters size: '
        + str(len(three_parameters)) + ', constant conditions size: '
        + str(len(conditions)))

def same_input_constant_cond(input_constant_conditions, parameters_map):
    """Given an input constant conditions dictionary, return any constant
    condition inside a parameters_map dictionary, that has constant conditions
    in the second element of the values (that are tuples). Used for testing.

    Parameters
    ----------
    input_constant_conditions : dict
        Dictionary of the input constant conditions
    parameters_map : dict
        Dictionary of the parameters value and their relative constant
        conditions

    Returns
    -------
    bad_match : str
        String that contains all the invalid matches of constant conditions,
        separated by a whitespace
    bad_match_element : list
        List of elements (keys) of the invalid invalid matches constant
        conditions in the dictionary
    """
    bad_match = ''
    bad_match_element = []
    if len(input_constant_conditions)!=len(parameters_map):
        bad_match = 'different number of objects '
    else:
        for element, const_cond in input_constant_conditions.items():
            if const_cond!=parameters_map[element][1]:
                bad_match += str(const_cond) + ' '
                bad_match_element.append(element)
    return bad_match, bad_match_element

def test_same_input_constant_cond_no_const_cond():
    """Check that the help function to test if two dictionaries with the same
    number of items, have matching constant conditions works with two empty
    dictionaries.
    In the input_dictionary the constant conditions are the values, while in
    the other one the constant conditions are the first element of the tuple,
    and the tuples are the values.
    If no bad match is detected, the returned string and list given by the
    function under test are empty.

    GIVEN: two empty dictionaries
    WHEN: I check if there is a mismatch of constant conditions
    THEN: no mismatch of constant condition found
    """
    input_no_const_cond = {}
    parameter_map_no_const_cond = {}
    bad_match, bad_match_element = same_input_constant_cond(
        input_no_const_cond, parameter_map_no_const_cond)

    assert not bad_match, (
        'StrucutralError for the constant conditions: mismatch '
        + str(bad_match) + ' , ' + str(bad_match_element) + ' in '
        + str(parameter_map_no_const_cond) + ' from same_input_constant_cond(). '
        + 'Cannot have a mismatch because both of them are empty dictionaries')

def test_same_input_constant_cond_single_const_cond():
    """Check that the help function to test if two dictionaries with the same
    number of items, have matching constant conditions works with two
    dictionaries that have the same constant condition.
    In the input_dictionary the constant conditions are the values, while in
    the other one the constant conditions are the first element of the tuple,
    and the tuples are the values.
    If no bad match is detected, the returned string and list given by the
    function under test are empty.

    GIVEN: two dictionaries that have the same constant condition
    WHEN: I check if there is a mismatch of constant conditions
    THEN: no mismatch of constant condition found
    """
    input_single_const_cond = {'R1': 0}
    parameter_map_single_const_cond = {'R1': (100., 0)}
    bad_match, bad_match_element = same_input_constant_cond(
        input_single_const_cond, parameter_map_single_const_cond)

    assert not bad_match, (
        'StrucutralError for the constant conditions: mismatch '
        + str(bad_match) + ' , ' + str(bad_match_element) + ' in '
        + str(bad_match_element) + ' from same_input_constant_cond(). '
        + 'Cannot have a mismatch because both of them are empty dictionaries. '
        + 'They must be the same')

def test_same_input_constant_cond_two_const_cond():
    """Check that the help function to test if two dictionaries with the same
    number of items, have matching constant conditions works with two
    dictionaries that have the same three constant conditions.
    In the input_dictionary the constant conditions are the values, while in
    the other one the constant conditions are the first element of the tuple,
    and the tuples are the values.
    If no bad match is detected, the returned string and list given by the
    function under test are empty.

    GIVEN: two dictionaries that have the same three constant conditions
    WHEN: I check if there is a mismatch of constant conditions
    THEN: no mismatch of constant condition found
    """
    input_two_const_cond = {'R1': 1, 'C2': 0, 'R3': 0}
    parameter_map_two_const_cond = {'R1': (100., 1), 'C2': (1e-6, 0),
                                    'R3': (2e3, 0)}
    bad_match, bad_match_element = same_input_constant_cond(
        input_two_const_cond, parameter_map_two_const_cond)

    assert not bad_match, (
        'StrucutralError for the constant conditions: mismatch '
        + str(bad_match) + ' , ' + str(bad_match_element) + ' in '
        + str(bad_match_element) + ' from same_input_constant_cond(). '
        + 'They must be the same')

def test_same_input_constant_cond_mismatch_const_cond():
    """Check that the help function to test if two dictionaries with the same
    number of items, have matching constant conditions works with two
    dictionaries that have the same two constant conditions, and one constant
    condition that is different.
    In the input_dictionary the constant conditions are the values, while in
    the other one the constant conditions are the first element of the tuple,
    and the tuples are the values.
    If bad matches are detected, the returned string contains the bad
    matches and the list contains their position in the listing.

    GIVEN: one constant condition that is different (the first one)  and two
    dictionaries that have two equal constant conditions (the last two)
    WHEN: I check if there is a mismatch of constant conditions
    THEN: all and only the single mismatch of constant condition is found
    """
    input_two_const_cond = {'R1': 1, 'C2': 0, 'R3': 0}
    parameter_map_two_const_cond = {'R1': (100., 0), 'C2': (1e-6, 0),
                                    'R3': (2e3, 0)}
    bad_match, bad_match_element = same_input_constant_cond(
        input_two_const_cond, parameter_map_two_const_cond)
    expected_result = '1 '

    assert bad_match==expected_result, (
        'StrucutralError for the constant conditions: mismatch '
        + str(bad_match) + ' , ' + str(bad_match_element) + ' in '
        + str(bad_match_element) + ' from same_input_constant_cond(). '
        + 'Mismatch found are different from the ones expected:'
        + expected_result)

def test_initial_circuit_constant_conditions_single_element(
        circuit_single_element):
    """Check if the Circuit object created by the generate_circuit() has a
    valid constant condition, in the case of an circuit with just one element,
    and thus one valid constant condition.

    GIVEN: a valid constant condition dictionary with one condition inside
    WHEN: the Circuit object is created through the generate_circuit()
    function
    THEN: the Circuit object has valid constant conditions, the same of the
    input ones
    """
    input_constant_conditions = {'R1': 0}
    parameters_map = circuit_single_element.parameters_map

    caller = 'generate_circuit()'
    wrong_tuples = wrong_tuples_circuit(parameters_map)
    assert not wrong_tuples, (
        'TypeError in output of get_impedance_const_input_element_type() '
        + 'for element \'' + wrong_tuples + '\'. Its value in the dictionary '
        + 'have to be a tuple')
    parameters_values = list(parameters_map.values())
    constant_conditions_list = [parameter[1] for parameter in
                                parameters_values]

    wrong_types, wrong_types_index = invalid_constant_cond(
        constant_conditions_list)
    assert not wrong_types, (
        'TypeError for constant element(s) ' + str(wrong_types) + ' number '
        + str(wrong_types_index) + ' in ' + str(constant_conditions_list)
        + ' from ' + caller + '. Constant conditions must be all integers, '
        + 'with value either 0 or 1')

    bad_match, bad_match_element = same_input_constant_cond(
        input_constant_conditions, parameters_map)
    assert not bad_match, (
        'StrucutralError for the constant conditions: mismatch between the '
        + 'constant condition of the class onject and the input counterpart '
        + 'for' + str(bad_match) + ' , ' + str(bad_match_element) + ' in '
        + str(bad_match_element) + ' from same_input_constant_cond(). '
        + 'They must be the same')

def test_initial_circuit_constant_conditions_two_elements(
        circuit_two_elements):
    """Check if the Circuit object created by the generate_circuit() has a
    valid constant condition, in the case of an circuit with two elements,
    and thus two valid constant conditions.

    GIVEN: a valid constant condition dictionary with two conditions inside
    WHEN: the Circuit object is created through the generate_circuit()
    function
    THEN: the Circuit object has valid constant conditions, the same of the
    input ones
    """
    input_constant_conditions = {'R1': 1, 'C2': 0}
    parameters_map = circuit_two_elements.parameters_map

    caller = 'generate_circuit()'
    wrong_tuples = wrong_tuples_circuit(parameters_map)
    assert not wrong_tuples, (
        'TypeError in output of get_impedance_const_input_element_type() '
        + 'for element \'' + wrong_tuples + '\'. Its value in the dictionary '
        + 'have to be a tuple')
    parameters_values = list(parameters_map.values())
    constant_conditions_list = [parameter[1] for parameter in
                                parameters_values]

    wrong_types, wrong_types_index = invalid_constant_cond(
        constant_conditions_list)
    assert not wrong_types, (
        'TypeError for constant element(s) ' + str(wrong_types) + ' number '
        + str(wrong_types_index) + ' in ' + str(constant_conditions_list)
        + ' from ' + caller + '. Constant conditions must be all integers, '
        + 'with value either 0 or 1')

    bad_match, bad_match_element = same_input_constant_cond(
        input_constant_conditions, parameters_map)
    assert not bad_match, (
        'StrucutralError for the constant conditions: mismatch between the '
        + 'constant condition of the class onject and the input counterpart '
        + 'for' + str(bad_match) + ' , ' + str(bad_match_element) + ' in '
        + str(bad_match_element) + ' from same_input_constant_cond(). '
        + 'They must be the same')

def test_initial_circuit_constant_conditions_many_elements(
        circuit_many_elements):
    """Check if the Circuit object created by the generate_circuit() has a
    valid constant condition, in the case of an circuit with four elements,
    and thus four valid constant conditions.

    GIVEN: a valid constant condition dictionary with four conditions inside
    WHEN: the Circuit object is created through the generate_circuit()
    function
    THEN: the Circuit object has valid constant conditions, the same of the
    input ones
    """
    input_constant_conditions = {'R1': 0, 'C2': 0, 'R3': 1, 'Q4': 0}
    parameters_map = circuit_many_elements.parameters_map

    caller = 'generate_circuit()'
    wrong_tuples = wrong_tuples_circuit(parameters_map)
    assert not wrong_tuples, (
        'TypeError in output of get_impedance_const_input_element_type() '
        + 'for element \'' + wrong_tuples + '\'. Its value in the '
        + 'dictionary have to be a tuple')
    parameters_values = list(parameters_map.values())
    constant_conditions_list = [parameter[1] for parameter in
                                parameters_values]

    wrong_types, wrong_types_index = invalid_constant_cond(
        constant_conditions_list)
    assert not wrong_types, (
        'TypeError for constant element(s) ' + str(wrong_types) + ' number '
        + str(wrong_types_index) + ' in ' + str(constant_conditions_list)
        + ' from ' + caller + '. Constant conditions must be all integers, '
        + 'with value either 0 or 1')

    bad_match, bad_match_element = same_input_constant_cond(
        input_constant_conditions, parameters_map)
    assert not bad_match, (
        'StrucutralError for the constant conditions: mismatch between the '
        + 'constant condition of the class onject and the input counterpart '
        + 'for' + str(bad_match) + ' , ' + str(bad_match_element) + ' in '
        + str(bad_match_element) + ' from ' + caller + '. They must be the '
        + 'same')

def test_initial_circuit_constant_conditions_wrong_parameters(
        circuit_wrong_parameters):
    """Check if the Circuit object created by the generate_circuit() has a
    valid constant condition, in the case of an circuit with two elements,
    but only one of the two condition is valid (the second one).

    GIVEN: a constant condition dictionary with a valid condition (the second
    one) and an invalid (by value) first constant condition
    WHEN: the Circuit object is created through the generate_circuit()
    function
    THEN: the Circuit object's first constant condition is detected as invalid
    """
    input_constant_conditions = {'R1': -1, 'Ce': 1}
    parameters_map = circuit_wrong_parameters.parameters_map

    caller = 'generate_circuit()'
    wrong_tuples = wrong_tuples_circuit(parameters_map)
    assert not wrong_tuples, (
        'TypeError in output of get_impedance_const_input_element_type() '
        + 'for element \'' + wrong_tuples + '\'. Its value in the dictionary '
        + 'have to be a tuple')
    parameters_values = list(parameters_map.values())
    constant_conditions_list = [parameter[1] for parameter in
                                parameters_values]

    expected_result = '-1 '
    wrong_conds, wrong_conds_index = invalid_constant_cond(
        constant_conditions_list)
    assert wrong_conds==expected_result, (
        'TypeError for constant condition(s) ' + str(wrong_conds)
        + ' number ' + str(wrong_conds_index) + ' in '
        + str(constant_conditions_list) + ' from ' + caller + '. '
        + 'Invalid constant conditions found are different from the expected '
        + 'ones: ' + expected_result)

    bad_match, bad_match_element = same_input_constant_cond(
        input_constant_conditions, parameters_map)
    assert not bad_match, (
        'StrucutralError for the constant conditions: mismatch between the '
        + 'constant condition of the class onject and the input counterpart '
        + 'for' + str(bad_match) + ' , ' + str(bad_match_element) + ' in '
        + str(bad_match_element) + ' from same_input_constant_cond(). '
        + 'They must be the same')

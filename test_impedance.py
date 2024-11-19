import pytest

def generate_circuit():
    """Generate a test circuit string."""
    circuit_string = '(R1C2[R3Q4])'
    return circuit_string

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
"""This module is a collection of functions aimed to generate an impedance
function of a circuit, based on its elements.
Starting with a string that represent the circuit, a list of the parameters of
all the elements and an array for considering certain parameters as constants
in the function, this module aims to give the impedance function, a list with
all the non-constant parameters and a list that contains all the non-constant
elements. Both lists are ordered in the chronoclocal way of the alghoritm.
"""

import numpy as np

def impedance_resistor(resistance, frequency):
    """Definition of impedance for resistors.

    Parameters
    ----------
    resistance : float
        Value (in Ohm) of the resistance of a resistor
    frequency : array
        Values of the frequencies (in Hz) for which the impedance will be
        computed

    Returns
    -------
    impedance : complex array
        Value of the impedances (in Ohm) for the given frequencies
    """
    impedance = (resistance+0j) * np.ones(len(frequency))
    return impedance

def impedance_capacitor(capacitance, frequency):
    """Definition of impedance for capacitors.

    Parameters
    ----------
    capacitance : float
        Value (in F) of the capacitance of a capacitor
    frequency : array
        Values of the frequencies (in Hz) for which the impedance will be
        computed

    Returns
    -------
    impedance : complex array
        Value of the impedances (in Ohm) for the given frequencies
    """
    impedance = 1./(1j*frequency*2*np.pi*capacitance)
    return impedance

def impedance_cpe(q_parameter, ideality_factor, frequency):
    """Definition of impedance for (capacitative) constant phase elements.

    Parameters
    ----------
    q_parameter : float
        Value of the CPE (Q)
    ideality_factor : float
        Ideality factor of the CPE (n)
    frequency : array
        Values of the frequencies (in Hz) for which the impedance will be
        computed

    Returns
    -------
    impedance : complex array
        Value of the impedances (in Ohm) for the given frequencies
    """
    phase_factor = np.exp(np.pi/2*ideality_factor*1j)
    impedance = 1./(
        q_parameter*(frequency*2*np.pi)**ideality_factor*phase_factor)
    return impedance

def get_impedance_const_input_element(element_type, const_parameter):
    """Calculate the impedance function of an element in the input string;
    its parameters will be kept constant in the fit. Based on the
    element_type, select the proper impedance function.

    Parameters
    ----------
    element_type : string
        String corresponding to the single element type (R, C or Q)
    const_parameter : list or float
        Parameter of the element that will not figure in the fit, but
        contributes to the definition of the impedance function

    Returns
    -------
    impedance_element : function
        Impedance function of the element that will depend only on the
        frequency
    """
    if element_type=='R':
        impedance_element = lambda _, f: impedance_resistor(const_parameter,
                                                            f)
    if element_type=='C':
        impedance_element = lambda _, f: impedance_capacitor(const_parameter,
                                                             f)
    if element_type=='Q':
        impedance_element = lambda _, f: impedance_cpe(const_parameter[0],
                                                     const_parameter[1], f)
    return impedance_element

def get_impedance_input_element(element_type, parameters, parameter):
    """Calculate the impedance function of an element in the input string;
    its parameters will figure in the fit. Based on the element_type,
    select the proper impedance function.

    Parameters
    ----------
    element_type : string
        String corresponding to the single element type (R, C or Q)
    parameters : list
        List of parameters of elements (added so far), that will figure in
        the fit
    parameter : list or float
        Parameter(s) of the current element that will figure in the fit, on
        which depends the definition of the impedance function of the element

    Returns
    -------
    impedance_element : function
        Impedance function that will depend both on the parameter(s) and on
        the frequency
    parameters : list
        List of parameters (float, integer or lists) that will be object of
        the fit
    """
    impedance_element = []
    if element_type=='R':
        parameters.append(parameter)
        i_parameter = len(parameters) - 1
        impedance_element = lambda p, f: impedance_resistor(p[i_parameter], f)
    elif element_type=='C':
        parameters.append(parameter)
        i_parameter = len(parameters)-1
        impedance_element = lambda p, f: impedance_capacitor(p[i_parameter],
                                                             f)
    elif element_type=='Q':
        parameters.append(parameter[0])
        parameters.append(parameter[1])
        i_parameter = len(parameters)-1
        impedance_element = lambda p, f: impedance_cpe(p[i_parameter-1],
                                                     p[i_parameter], f)
    return impedance_element, parameters

def get_impedance_function_element(element_string, impedance_circuit,
                                   initial_parameters, parameters_circuit,
                                   elements_circuit, constant_elements):
    """Return the impedance function selecting the three cases: the element
    has already been analyzed, the element has parameters that will not figure
    in the fit or the element has parameters that WILL figure in the fit.

    Parameters
    ----------
    element_string : string
        String corresponding to the single element (letter and number)
    impedance_circuit : list
        List of impedance functions containing in chronological order each
        cell analysis (the elements inside a pair of brackets)
    initial_parameters : list
        List of parameters given by input
    parameters_circuit : list
        List of parameters containing all parameters analyzed so far, that
        will be object of the fit
    elements_circuit : list
        List of elements containing all elements analyzed so far, that
        will be object of the fit, in order of analysis
    constant_elements : list
        List of constant elements condition given by input

    Returns
    -------
    impedance_element : function
        Impedance function of the analyzed element
    parameters_circuit : list
        List of parameters containing all parameters analyzed so far, that
        will be object of the fit
    elements_circuit : list
        List of elements containing all elements analyzed so far, that will be
        object of the fit, in order of analysis
    """
    i_element = int(element_string[1]) - 1
    if element_string[0]=='Z':
        impedance_element = impedance_circuit[i_element]
    elif constant_elements[i_element]:
        const_parameter = initial_parameters[i_element]
        element_type = element_string[0]
        impedance_element = get_impedance_const_input_element(
            element_type, const_parameter)
    else:
        elements_circuit.append(element_string)
        parameter = initial_parameters[i_element]
        element_type = element_string[0]
        impedance_element, parameters_circuit = get_impedance_input_element(
            element_type, parameters_circuit, parameter)
    return impedance_element, parameters_circuit, elements_circuit

def add(first_function, second_function):
    """Add two functions given by input and return the result.

    Parameters
    ----------
    first_function : function
        First generic function to be added
    second_function : function
        Second generic function to be added

    Returns
    -------
    fsum : function
        Result function of the sum of the two
    """
    fsum = lambda x, y: first_function(x, y) + second_function(x, y)
    return fsum

def serial_comb(impedance_cell):
    """Perform a serial comb (sum) of any number of functions. If no function
    is provided, return the zero function.

    Parameters
    ----------
    impedance_cell : list
        List of all impedance functions inside a cell

    Returns
    -------
    function_cell : function
        Equivalent function of the serial comb of the cell
    """
    function_cell = lambda *_: 0
    for i, _ in enumerate(impedance_cell):
        function_cell = add(function_cell, impedance_cell[i])
    return function_cell

def reciprocal(function_):
    """Perform a (polynomial) inversion of a generic function. If no function
    is provided, return the zero function.

    Parameters
    ----------
    f : function
        Function to be inverted

    Returns
    -------
    receprocal_f : function
        Inverted function
    """
    reciprocal_function = lambda x, y: 1./function_(x, y)
    return reciprocal_function

def parallel_comb(impedance_cell):
    """Perform a parallel comb (invertion of the sum of the inverted
    functions) of any number of functions. If no function is
    provided, return the zero function.

    Parameters
    ----------
    impedance_cell : list
        List of all impedance functions inside a cell

    Returns
    -------
    function_cell : function
        Equivalent function of the prallel comb of the cell
    """
    one_over_function_cell = lambda *_: 0
    for impedance_element in impedance_cell:
        one_over_impedance_element = reciprocal(impedance_element)
        one_over_function_cell = add(one_over_function_cell,
                                     one_over_impedance_element)
    function_cell = reciprocal(one_over_function_cell)
    return function_cell

def get_position_opening_bracket(circuit_string, i_end):
    """Given the circuit string and the position of a closing bracket, find
    the corrispective opening bracket

    Parameters
    ----------
    circuit_string : string
        String of the current circuit
    i_end : int
        Index of circuit_string that corresponds to a closing bracket

    Returns
    -------
    last_opening_bracket_position : int
        Index of circuit_string that corresponds to the corresptive openening
        bracket
    """
    if circuit_string.startswith(')', i_end):
        opening_bracket = '('
    else:
        opening_bracket = '['
    opening_bracket_positions = [
        i for i, _ in enumerate(circuit_string[:i_end])
        if circuit_string.startswith(opening_bracket, i)]
    last_opening_bracket_position = opening_bracket_positions[-1]
    return last_opening_bracket_position

def generate_cell_impedance(circuit_string, i_start, i_end, impedance_circuit,
                            initial_parameters, parameters_circuit,
                            elements_circuit, constant_elements):
    """Calculate the impedance function of a cell, defined as the group of
    elements inside a pair of round or square brackets.

    Parameters
    ----------
    circuit_string : string
        String of the current circuit
    i_start : int
        Index of circuit_string that corresponds to an opening bracket.
        Delimits the beginning of the cell to be analyzed
    i_end : int
        Index of circuit_string that corresponds to a closing bracket.
        Delimits the end of the cell to be analyzed
    impedance_circuit : dict
        List of impedance functions containing in chronological order each
        cell analysis (the elements inside a pair of brackets)
    initial_parameters : list
        List of parameters given by input
    parameters_circuit : list
        List of parameters containing all parameters analyzed so far, that
        will be object of the fit
    elements_circuit : list
        List of elements containing all elements analyzed so far, that
        will be object of the fit, in order of analysis
    constant_elements : list
        List of constant elements condition given by input

    Returns
    -------
    impedance_cell : function
        Impedance function of the analyzed element
    parameters_circuit : list
        List of parameters containing all parameters analyzed so far, that
        will be object of the fit
    elements_circuit : list
        List of elements containing all elements analyzed so far, that will be
        object of the fit, in order of analysis
    """
    impedance_cell = []
    for i in range(i_start+1, i_end, 2): #Increment of 2 to jump the numbers
        #of the elements and count only the letters in the string (one letter
        #for one element)
        element_string = circuit_string[i:i+2]
        (impedance_element, parameters_circuit,
         elements_circuit) = get_impedance_function_element(
            element_string, impedance_circuit, initial_parameters,
            parameters_circuit, elements_circuit, constant_elements)
        impedance_cell.append(impedance_element)
    return impedance_cell, parameters_circuit, elements_circuit

def update_string(circuit_string, i_start, i_end, last_impedance_element):
    """Given the circuit string,  the position of the analyzed cell bordes and
    the number of cycles of analysis, update the circuit string substituting
    the analyzed cell with a generic Z followed by the corresponding number
    of cycle.

    Parameters
    ----------
    circuit_string : string
        String of the circuit before the last cycle of analysis
    i_start : int
        Index of circuit_string that corresponds to an opening bracket.
        Delimits the beginning of the cell to be analyzed
    i_end : int
        Index of circuit_string that corresponds to a closing bracket.
        Delimits the end of the cell to be analyzed
    last_impedance_element : int
        Index of the list of impedance, which corresponds to the number of
        cycles of analysis

    Returns
    -------
    updated_circuit_string : string
        String of the circuit after the last cycle of analysis
    """
    updated_circuit_string = circuit_string.replace(
        circuit_string[i_start:i_end+1], 'Z'+str(last_impedance_element))
    return updated_circuit_string

def generate_impedance_function(circuit_string, initial_parameters,
                                constant_elements):
    """Given a circuit string, the initial parameters and the constant
    element conditions, generate an impedance function for the circuit

    Parameters
    ----------
    circuit_string : string
        String of the circuit given by input
    initial_parameters : list
        List of parameters given by input
    constant_elements : list
        List of constant elements condition given by input

    Returns
    -------
    final_impedance_circuit : function
        Impedance function of the circuit
    parameters_circuit : list
        List of parameters (integers, floats or lists) of the elements that
        compose the circuit and that will figure in the fit
    elements_circuit : list
        List of elements (strings) that compose the circuit and that will
        figure in the fit, in order of analysis
    """
    working = 1
    index = 1 #first element is just a bracket, cannot be an element
    parameters_circuit = []
    elements_circuit = []
    impedance_circuit = []
    working_count = 0
    working_limit = 100
    while working:
        if (circuit_string[index]==')' or circuit_string[index]==']'):
            i_start = get_position_opening_bracket(circuit_string, index)
            (impedance_cell, parameters_circuit,
             elements_circuit) = generate_cell_impedance(
                circuit_string, i_start, index, impedance_circuit,
                initial_parameters, parameters_circuit, elements_circuit,
                constant_elements)
            if circuit_string[index]==')':
                new_impedance = serial_comb(impedance_cell)
                impedance_circuit.append(new_impedance)
            else:
                new_impedance = parallel_comb(impedance_cell)
                impedance_circuit.append(new_impedance)
            last_impedance_element = len(impedance_circuit) - 1
            circuit_string = update_string(circuit_string, i_start, index,
                                           last_impedance_element)
            index = 1
        else:
            index += 1
        if index>(len(circuit_string)-1):
            working = 0
        working_count += 1
        if working_count>working_limit:
            working = 0
    final_impedance_circuit = impedance_circuit[-1]
    return (final_impedance_circuit, parameters_circuit, elements_circuit)

"""This module is a collection of functions aimed to generate an impedance
function of a circuit, based on its elements.
It is composed by two classes with relative methods, plus other functions.
The first class is the Circuit class, describing a circuit given the circuit
string, the parameters, the constant elements for the fit and eventually the
error that will be minimized during the fit.
The second class is the AnalisysCircuit. It is an intermediary class between
the initial circuit and the circuit which impedance function will be minimized
during the fit. Its scope is to generate an impedance function based on the
circuit string and its parameters.
Given a certain initial circuit, this module divide its circuit string in
cells, based on series or parallel bracket block. For each of them
every element gets its impedance function (based on the parameter), then they
are combined using the electrical circuit rules. Thus to a single cell it is
associated an impedance function with its parameters, and the cell becomes a
single equivalent element. This analysis goes on until there is a single
element in the string, and all of the information is stored inside an
instance of the AnalysisCircuit class.
"""

import numpy as np


class Circuit:
    """
    Class describing a circuit.

    Attributes
    ----------
    circuit_diagram : str
        Circuit string, representing the circuit scheme.
    parameters_map : dict
        a dictionary that correlate each element to a tuple containing the
        element parameter and the constant condition
    error : float
        error based on the data, impedance function and parameters

    Methods
    -------
    generate_analyzed_circuit()
        Analyze the circuit and create an object that contains the analysis
    get_initial_parameters()
        Print the elements of the circuit with their relative parameter and
        the impedance error
    """
    def __init__(self, circuit_diagram, parameters_map, error=None):
        """
        Parameters
        ----------
        circuit_diagram : str
            Circuit diagram, representing the circuit scheme
        parameters_map : dict
            a dictionary that correlate each element to a tuple containing the
            element parameter and the constant condition
        error : int or float, optional
            error based on the impedance function, data and parameters
            (default is None)
        """
        self.circuit_diagram = circuit_diagram
        self.parameters_map = parameters_map
        self.error = error

    def generate_analyzed_circuit(self):
        """Generate an AnalysisCircuit instance containing all the analysis
         of the initial circuit.

        Returns
        -------
        analyzed_circuit : AnalisysCircuit
            object containing all the analysis of the initial circuit
        """
        working = 1
        index = 1 #first element is just a bracket, cannot be an element
        analyzed_circuit = AnalisysCircuit(self.circuit_diagram, {})
        working_count = 0
        working_limit = 100
        cell_count = 0
        while working:
            circuit_diagram = analyzed_circuit.circuit_diagram
            if (circuit_diagram[index]==')' or circuit_diagram[index]==']'):
                cell_count += 1
                i_start = get_position_opening_bracket(circuit_diagram, index)
                impedance_cell = analyzed_circuit.generate_cell_impedance(
                    self, i_start, index)
                if analyzed_circuit.circuit_diagram[index]==')':
                    impedance_cell_equivalent = serial_comb(impedance_cell)
                else:
                    impedance_cell_equivalent = parallel_comb(impedance_cell)
                new_element = analyzed_circuit.update_diagram(i_start, index,
                                                              cell_count)
                analyzed_circuit.impedance_parameters_map[
                    new_element] = (impedance_cell_equivalent, 'equivalent')
                index = 1
            else:
                index += 1
            if index>(len(analyzed_circuit.circuit_diagram)-1):
                working = 0
            working_count += 1
            if working_count>working_limit:
                working = 0
        analyzed_circuit.set_final_results()
        return analyzed_circuit

    def get_parameters_info(self):
        """Return a string in which each element is the circuit element
        name followed by its parameter value. The last element is the error
        estimated with the current values of the parameters.
        Used to print the parameters value and error.

        Returns
        -------
        parameters_set : str
            List of strings containing the name and inital value of the
            parameters. If the parameters is set constant, a '(constant)'
            follows the parameter value. Then the error estimated with the
            initial values of the parameters is added as last element.
        """
        parameters_info_list = []
        for element, parameter in self.parameters_map.items():
            if element.startswith('Q'):
                element_info = (element + ': ' + str(parameter[0][0]) + ', '
                                + str(parameter[0][1]))
            else:
                element_info = element + ': ' + str(parameter[0])
            if parameter[1]:
                element_info += ' (constant)'
            parameters_info_list.append(element_info)
        parameters_info_list.append('Error: ' + f'{self.error:.4f}')
        parameters_info = get_string(parameters_info_list)
        return parameters_info


class AnalisysCircuit:
    """Class describing the analysis of a circuit.

    Attributes
    ----------
    circuit_diagram : str
        Circuit diagram, representing the circuit scheme
    impedance_parameters_map : dict
        dictionary that correlate each element (or equivalent element of a
        cell) with a tuple containing its impedance function and parameter(s).
        If the element was constant a 'const' string takes the parameter's
        place. If is an equivalent element, the saying 'equivalent' is present
    impedance : function
        last impedance function calculated, i.e. the impedance of the whole
        circuit
    parameters_map : dict
        dictionary containing all the non-constant elements - parameter
        relationships, put in chronological order during the analysis

    Methods
    -------
    generate_cell_impedance(initial_circuit, i_start, i_end)
        Analyze a cell of the circuit and write the result in the instance of
        the class
    get_impedance_function_element(element_name, initial_circuit)
        Calculate the impedance function of a single element, based on the
        case of constant or non-constant parameter(s)
    """
    def __init__(self, circuit_diagram, impedance_parameters_map=None,
                 impedance=None, parameters_map=None):
        """
        Parameters
        ----------
        circuit_diagram : str
            Circuit diagram, representing the circuit scheme
        impedance_parameters_map : dict, optional
            dictionary that correlate each element with a tuple containing
            its impedance function and parameter(s) (default is None)
        impedance : function, optional
            last impedance function calculated, i.e. the impedance of the
            whole circuit (default is None)
        parameters_map : dict, optional
            dictionary containing all the non-constant elements - parameter
            relationships, put in chronological order during the analysis
            (default is None)
        """
        self.circuit_diagram = circuit_diagram
        self.impedance_parameters_map = impedance_parameters_map
        self.impedance = impedance
        self.parameters_map = parameters_map

    def set_impedance_constant_element(self, element_name, const_parameter):
        """Calculate the impedance function of a constant element in the
        input string; its parameters will be kept constant in the fit. Based
        on the element_type, select the proper impedance function.
        Then the element with its impedance function are added to the
        impedance_parameters_map attribute of the instance of the class.

        Parameters
        ----------
        element_name : str
            (Constant) element string of the analyzed element
        const_parameter : int, float or list
            Parameter of the constant element
        """
        if self.impedance_parameters_map is None:
            self.impedance_parameters_map = {}
        elif element_name.startswith('R'):
            impedance_element_f = lambda _, f: impedance_resistor(
                const_parameter, f)
        elif element_name.startswith('C'):
            impedance_element_f = lambda _, f: impedance_capacitor(
                const_parameter, f)
        elif element_name.startswith('Q'):
            impedance_element_f = lambda _, f:impedance_cpe(
                const_parameter[0], const_parameter[1], f)
        else:
            raise Exception('FatalError: Invalid constant parameter name for '
                            + 'the impedance function')
        self.impedance_parameters_map[element_name] = (impedance_element_f,
                                                         'const')

    def set_impedance_non_const_element(self, element_name, parameter):
        """Calculate the impedance function of a non-constant element in the
        input string; its parameters will figure in the fit. Based on the
        element_type, select the proper impedance function.
        Then the element with its impedance function and its parameter are
        added to the impedance_parameters_map attribute of the instance of
        the class.

        Parameters
        ----------
        element_name : str
            (Non-constant) element string of the analyzed element
        parameter : int, float or list
            Parameter of the non-constant element
        """
        n_parameter = 0
        if self.impedance_parameters_map is None:
            self.impedance_parameters_map = {}
        else:
            for element, map_ in self.impedance_parameters_map.items():
                if not isinstance(map_[1], str):
                    if element.startswith('Q'):
                        n_parameter += 2
                    else:
                        n_parameter += 1
        if element_name.startswith('R'):
            impedance_function_element = lambda p, f: impedance_resistor(
                p[n_parameter], f)
            self.impedance_parameters_map[element_name] = (
                impedance_function_element, parameter)
        elif element_name.startswith('C'):
            impedance_function_element = lambda p, f: impedance_capacitor(
                p[n_parameter], f)
            self.impedance_parameters_map[element_name] = (
                impedance_function_element, parameter)
        elif element_name.startswith('Q'):
            impedance_function_element = lambda p, f: impedance_cpe(
                p[n_parameter], p[n_parameter+1], f)
            self.impedance_parameters_map[element_name] = (
                impedance_function_element, parameter)
        else:
            raise Exception('FatalError: Invalid non-constant parameter name '
                            + 'for the impedance function')

    def set_impedance_element(self, element_name, initial_circuit):
        """Return the impedance function selecting the three cases: the
        element has already been analyzed, the element has parameters that
        will not figure in the fit (constant parameter) or the element has
        parameters that WILL figure in the fit (non-constant parameter).

        Parameters
        ----------
        element_name : str
            String corresponding to the single element (letter and number)
        impedance_circuit : list
            List of impedance functions containing in chronological order each
            cell analysis (the elements inside a pair of brackets)

        Returns
        -------
        impedance_element_f : function
            Impedance function of the analyzed element
        """
        constant_condition = initial_circuit.parameters_map[element_name][1]
        if constant_condition:
            constant_parameter = initial_circuit.parameters_map[
                element_name][0]
            self.set_impedance_constant_element(element_name,
                                                constant_parameter)
        else:
            parameter = initial_circuit.parameters_map[element_name][0]
            self.set_impedance_non_const_element(element_name, parameter)

    def generate_cell_impedance(self, initial_circuit, i_start, i_end):
        """Calculate the impedance function of all the elements inside,
        defined as the group of elements inside a pair of round or square
        brackets. During the process, save all the
        element-impedance_parameter relationshiphs inside the
        impedance_parameters_map.

        Parameters
        ----------
        initial_circuit : Circuit
            Initial circuit to be analyzed
        i_start : int
            Index of circuit_diagram that corresponds to an opening bracket.
            Delimits the beginning of the cell to be analyzed
        i_end : int
            Index of circuit_diagram that corresponds to a closing bracket.
            Delimits the end of the cell to be analyzed

        Returns
        -------
        impedance_cell : list
            List of impedance function of all the elements inside the analyzed
            cell
        """
        impedance_cell = []
        for i in range(i_start+1, i_end, 2): #Increment of 2 to jump the
            #numbers of the elements and count only the letters in the string
            # (one letter for one element)
            element_name = self.circuit_diagram[i:i+2]
            if not element_name.startswith('Z'):
                self.set_impedance_element(element_name,
                                                    initial_circuit)
            impedance_function_element = self.impedance_parameters_map[
                element_name][0]
            impedance_cell.append(impedance_function_element)
        return impedance_cell

    def update_diagram(self, i_start, i_end, cell_count):
        """Given the circuit string, the position of the analyzed cell bordes
        and the number of analyzed cells, update the circuit string
        substituting the analyzed cell with an equivalent element type 'Z'
        followed by the corresponding number of number of analyzed cells.

        Parameters
        ----------
        circuit_diagram : str
            Diagram of the circuit before the last cycle of analysis
        i_start : int
            Index of circuit_diagram that corresponds to an opening bracket.
            Delimits the beginning of the cell to be analyzed
        i_end : int
            Index of circuit_diagram that corresponds to a closing bracket.
            Delimits the end of the cell to be analyzed
        cell_count : int
            Number of analyzed cells, which corresponds to the number of
            cycles of analysis

        Returns
        -------
        new_element : str
            String of the circuit diagram after the last cycle of analysis
        """
        new_element = 'Z' + str(cell_count)
        updated_diagram = self.circuit_diagram.replace(
            self.circuit_diagram[i_start:i_end+1], new_element)
        self.circuit_diagram = updated_diagram
        return new_element

    def set_final_results(self):
        """Exctract from the impedance_parameters_map attribute the last
        (thus final) impedance and all the non-constant elements with their
        parameter. Put the first in the 'impedance' attribute, and the other
        two in the 'parameters_map' attribute.
        """
        self.impedance = list(self.impedance_parameters_map.values())[-1][0]
        parameters_map = {}
        for element, parameter in self.impedance_parameters_map.items():
            if not isinstance(parameter[1], str):
                parameters_map[element] = parameter[1]
        self.parameters_map = parameters_map

    def list_parameters(self):
        """List all the non-constant parameters in the parameters_map as
        float or integer.

        Returns
        -------
        parameters_list : list
            List of all the non-constant parameters
        """
        parameters_list = []
        for element, parameter in self.parameters_map.items():
            if element.startswith('Q'):
                parameters_list.append(parameter[0])
                parameters_list.append(parameter[1])
            else:
                parameters_list.append(parameter)
        return parameters_list

    def list_elements(self):
        """List all the non-constant elements strings in the parameters_map.
        Returns
        -------
        elements_list : list
            List of all the non-constant elements strings
        """
        elements_list = []
        for elements in self.parameters_map.keys():
            elements_list.append(elements)
        return elements_list

###########################
#Impedance definitions

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

######################################
#Functions to combine functions

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

#############################

def get_position_opening_bracket(circuit_diagram, i_end):
    """Given the circuit string and the position of a closing bracket, find
    the corrispective opening bracket

    Parameters
    ----------
    circuit_diagram : str
        String of the current circuit
    i_end : int
        Index of circuit_diagram that corresponds to a closing bracket

    Returns
    -------
    last_opening_bracket_position : int
        Index of circuit_diagram that corresponds to the corresptive openening
        bracket
    """
    if circuit_diagram.startswith(')', i_end):
        opening_bracket = '('
    else:
        opening_bracket = '['
    opening_bracket_positions = [
        i for i, _ in enumerate(circuit_diagram[:i_end])
        if circuit_diagram.startswith(opening_bracket, i)]
    last_opening_bracket_position = opening_bracket_positions[-1]
    return last_opening_bracket_position


def get_string(string_vector):
    """From a string vector creates a single string, concatenating each
    element with a \n as separator.

    Parameters
    ----------
    string_vector : list
        List of str-type variables

    Returns
    -------
    string_ : str
        Concatenated string
    """
    string_ = ''
    new_line = '\n'
    string_ = new_line.join(string_vector)
    return string_

def list_elements_circuit(circuit_diagram):
    """Return the list of input elements (type 'C', 'Q' or 'R' ) of a circuit
    diagram.

    Parameters
    ----------
    circuit_diagram : str
        Circuit diagram, representing the circuit scheme

    Returns
    -------
    elements_names : list
        Listing of all the elements in order of apparition in a circuit string
    """
    elements_names = []
    for i, char in enumerate(circuit_diagram):
        if char in {'C', 'Q', 'R'}:
            elements_names.append(circuit_diagram[i:i+2])
    return elements_names

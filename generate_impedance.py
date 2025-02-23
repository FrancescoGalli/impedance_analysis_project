"""This module is a collection of classes and functions aimed to generate an
impedanc function of a circuit, based on its element. It is composed by two
classes with relative methods, plus other functions.
The first class is the Circuit class, describing a circuit given the circuit
string, the parameters, the constant conditions for the fit and eventually the
error that will be minimized during the fit.
The second class is the AnalisysCircuit. Its purpose it to generate an object
with alle the information needed for the fit, included an impedance function,
all based on the data stored inside the initial circuit. The impedance
function will be then minimized, changing the values of the non-constant
parameters, during the fit.
Given a certain initial circuit, this module divide its circuit diagram in
cells, based on series or parallel bracket blocks. For each of them
every element gets its impedance function (based on its element type and
parameter), then they are combined using the electrical circuit rules. Thus
to a single cell it is associated an impedance function with all its
parameters, and the cell becomes a single equivalent element. This analysis
goes on until there is a single element in the diagram, and all of the
information is stored inside an instance of the AnalysisCircuit class.
"""

import numpy as np

#############################
#Generation of the initial circuit based on the input information

def generate_circuit(circuit_diagram, parameters, constant_conditions,
                     error=None):
    """Build the Circuit instance based on the input circuit diagram and
    parameters. Exceptions are raised if there is a mismatch between the
    elements in the circuit diagram and in the parameters dictionary.

    Parameters
    ----------
    circuit_diagram : str
        Diagram of the circuit
    parameters : dict
        Dictionary of element names and parameters of the circuit given by
        input
    constant_conditions : dict
        Dictionary of constant element conditions given by input
    error : int or float, optional
        Error based on the impedance function, data and parameters (default
        is None, i.e. not yet known)

    Returns
    -------
    initial_circuit : Circuit
        Circuit object of the input data
    """
    parameters_map = {}
    elements = list_elements_circuit(circuit_diagram)
    if set(elements)!=set(parameters.keys()):
        raise Exception('InputError: Mismatch between the elements in the '
                        + 'diagram and the element names of the parameters')
    if set(elements)!=set(parameters.keys()):
        raise Exception('InputError: Mismatch between the elements in the '
                        + 'diagram and the element names of the parameters')
    for element in elements:
        parameters_map[element] = (parameters[element],
                                   constant_conditions[element])
    initial_circuit = Circuit(circuit_diagram, parameters_map, error)
    return initial_circuit

############################

class Circuit:
    """Class describing an input circuit.

    Attributes
    ----------
    circuit_diagram : str
        Circuit diagram, representing the circuit scheme.
    parameters_map : dict
        Dictionary that correlates each element to a tuple containing its
        parameter and constant condition
    error : float
        Error based on the data, impedance function and parameters

    Methods
    -------
    generate_analyzed_circuit()
        Analyze the input circuit and create an AnalysisCircuit object that
        contains the analysis
    get_parameters_info()
        Put all the elements of the circuit with their relative parameter and
        the impedance error in a string
    """
    def __init__(self, circuit_diagram, parameters_map, error=None):
        """
        Parameters
        ----------
        circuit_diagram : str
            Circuit diagram, representing the circuit scheme
        parameters_map : dict
            Dictionary that correlates each element to a tuple containing its
            parameter and constant condition
        error : int or float, optional
            Error based on the data, impedance function and parameters
            (default is None)
        """
        self.circuit_diagram = circuit_diagram
        self.parameters_map = parameters_map
        self.error = error

    def generate_analyzed_circuit(self):
        """Generate an AnalysisCircuit instance containing all the analysis
        of the initial circuit. Raises an Exception if there is no closing
        brackets in the input circuit diagram (since this would make
        impossible the analysis).

        Returns
        -------
        analyzed_circuit : AnalisysCircuit
            Object containing all the analysis of the initial circuit
        """
        circuit_diagram_0 = self.circuit_diagram
        if circuit_diagram_0.find(')')==-1 and circuit_diagram_0.find(']')==-1:
            raise Exception('InputError: impossible to find any closing '
                            + 'bracket in the diagram')
        analyzed_circuit = AnalisysCircuit(self.circuit_diagram, {})
        working_count = 0
        working_limit = 100
        cell_count = 0
        index = 1 #First element in the string is just a bracket, cannot be a
                  #Circuit element
        working = 1
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
        """Return a string containing each circuit element name followed by
        its parameter value. The last element is the error estimated with the
        current values of the parameters. Used to print the parameters value
        and error.

        Returns
        -------
        parameters_set : str
            String containing the name and inital value of the parameters,
            each one is separated by a '\n'. If the parameters is set
            constant, a '(constant)' follows the parameter value. Then the
            error estimated with the initial values of the parameters is
            added as last element.
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
        Dictionary that correlates each element (or equivalent element of a
        cell) with a tuple containing its impedance function and parameter(s).
        If the element was constant a 'const' string takes the parameter's
        place. If it is an equivalent element, the saying 'equivalent' is
        present instead
    impedance : function
        Last impedance function calculated, i.e. the impedance of the whole
        circuit
    parameters_map : dict
        Dictionary containing all the non-constant element - parameter
        relationships, put in chronological order during the analysis

    Methods
    -------
    set_impedance_constant_element(element_name, constant_parameter)
        Set the impedance-parameter map of an input constant element
    set_impedance_non_const_element(element_name, parameter)
        Set the impedance-parameter map of an input non-constant element
    set_impedance_element(element_name, initial_circuit)
        Set the impedance-parameter map of any input element, based on the
        case of constant or non-constant parameter(s)
    generate_cell_impedance(initial_circuit, i_start, i_end)
        Analyze a cell of the circuit and write the result in the instance of
        the class
    update_diagram(i_start, i_end, cell_count)
        Replace the analyzed cell in the circuit string with the equivalent
        element
    set_final_results()
        Set the final impedance and the parameters map with all the
        non-constant elements parameters
    list_parameters()
        From the final parameters map, create a list with all the non-constant
        (i.e. fitting) parameters for the fit
    """
    def __init__(self, circuit_diagram, impedance_parameters_map=None,
                 impedance=None, parameters_map=None):
        """
        Parameters
        ----------
        circuit_diagram : str
            Circuit diagram, representing the circuit scheme
        impedance_parameters_map : dict, optional
            Dictionary that correlates each element with a tuple containing
            its impedance function and parameter(s) (default is None)
        impedance : function, optional
            Last impedance function calculated, i.e. the impedance of the
            whole circuit (default is None)
        parameters_map : dict, optional
            Dictionary containing all the non-constant element - parameter
            relationships, put in chronological order during the analysis
            (default is None)
        """
        self.circuit_diagram = circuit_diagram
        self.impedance_parameters_map = impedance_parameters_map
        self.impedance = impedance
        self.parameters_map = parameters_map

    def set_impedance_constant_element(self, element_name, constant_parameter):
        """Calculate the impedance function of a constant element in the
        input diagram; its parameters will be kept constant in the fit.
        Based on the element type, select the proper impedance function. The
        constant parameter won't be added as a variable in the lambda
        function, but its value will influence the impedance function of the
        element as a constant number in the function definition.
        Then the impedance function of the element is added to the
        impedance_parameters_map attribute of the instance of the class.

        Parameters
        ----------
        element_name : str
            (Constant) element string of the analyzed element
        constant_parameter : float or list
            Parameter of the constant element
        """
        if self.impedance_parameters_map is None:
            self.impedance_parameters_map = {}
        if element_name.startswith('R'):
            impedance_function_element = lambda _, freq: impedance_resistor(
                constant_parameter, freq)
        elif element_name.startswith('C'):
            impedance_function_element = lambda _, freq: impedance_capacitor(
                constant_parameter, freq)
        elif element_name.startswith('Q'):
            impedance_function_element = lambda _, freq: impedance_cpe(
                constant_parameter[0], constant_parameter[1], freq)
        else:
            raise Exception('FatalError: Invalid constant element name for '
                            + 'the setting of impedance function')
        self.impedance_parameters_map[element_name] = (
            impedance_function_element, 'const')

    def set_impedance_non_const_element(self, element_name, parameter):
        """Calculate the impedance function of a non-constant element in the
        input diagram; its parameters will figure in the fit. An Exception
        is raised if the element type is invalid.
        Based on the element type, select the proper impedance function and
        add the dependency of the parameter(s) through the first variable
        (the parameters array) of the lambda function. In particular,
        setting the position in the array of the newly added parameter based
        on how many non-constant parameters are already added in this way.
        Then the impedance function and parameter of the element are added to
        the impedance_parameters_map attribute of the instance of the class.
        Note: the final array of parameters will be provided at the impedance
        value generation, from the final parameters map of the circuit

        Parameters
        ----------
        element_name : str
            (Non-constant) element string of the analyzed element
        parameter : int, float or list
            Parameter of the non-constant element
        """
        n_parameters_set = 0
        if self.impedance_parameters_map is None:
            self.impedance_parameters_map = {}
        else:
            for element, map_ in self.impedance_parameters_map.items():
                if not isinstance(map_[1], str): #Leaves out constant
                                                 #parameters
                    if element.startswith('Q'):
                        n_parameters_set += 2
                    else:
                        n_parameters_set += 1
        if element_name.startswith('R'):
            impedance_function_element = lambda par, freq: impedance_resistor(
                par[n_parameters_set], freq) #Added parameter is R
            self.impedance_parameters_map[element_name] = (
                impedance_function_element, parameter)
        elif element_name.startswith('C'):
            impedance_function_element = lambda par, freq: impedance_capacitor(
                par[n_parameters_set], freq) #Added parameter is C
            self.impedance_parameters_map[element_name] = (
                impedance_function_element, parameter)
        elif element_name.startswith('Q'):
            impedance_function_element = lambda par, freq: impedance_cpe(
                par[n_parameters_set], par[n_parameters_set+1], freq)
                #Added parameter are Q and n, respectively
            self.impedance_parameters_map[element_name] = (
                impedance_function_element, parameter)
        else:
            raise Exception('FatalError: Invalid non-constant element name '
                            + 'for the setting of impedance function')

    def set_impedance_element(self, element_name, initial_circuit):
        """Return the impedance function selecting the three cases: the
        element has already been analyzed, the element has parameters that
        will not figure in the fit (constant parameter) or the element has
        parameters that WILL figure in the fit (non-constant parameter).

        Parameters
        ----------
        element_name : str
            String corresponding to the single element (letter and number)
        initial_circuit : Circuit
            Input circuit object to be analyzed
        """
        parameters_map = initial_circuit.parameters_map
        if element_name in parameters_map.keys():
            constant_condition = parameters_map[element_name][1]
        else:
            raise Exception('FatalError: Invalid element name for the '
                            + 'constant conditions')
        if constant_condition:
            constant_parameter = initial_circuit.parameters_map[
                element_name][0]
            self.set_impedance_constant_element(element_name,
                                                constant_parameter)
        else:
            parameter = initial_circuit.parameters_map[element_name][0]
            self.set_impedance_non_const_element(element_name, parameter)

    def generate_cell_impedance(self, initial_circuit, i_start, i_end):
        """Calculate the impedance function of all the elements inside a cell,
        defined as the group of elements between a pair of round or square
        brackets.
        During the process, save all the element-impedance_parameters
        relationshiphs inside the impedance_parameters_map.

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
            List of impedance functions of all the elements inside the
            analyzed cell
        """
        impedance_cell = []
        for i in range(i_start+1, i_end, 2):
            #Increment of 2 to jump the numbers of the elements and count
            #only the letters in the string (one letter for one element)
            element_name = self.circuit_diagram[i:i+2]
            if not element_name.startswith('Z'): #Z elements are the result
                                                 #of a past analysis
                self.set_impedance_element(element_name, initial_circuit)
            impedance_function_element = self.impedance_parameters_map[
                element_name][0]
            impedance_cell.append(impedance_function_element)
        return impedance_cell

    def update_diagram(self, i_start, i_end, cell_count):
        """Given the circuit diagram, the position of the analyzed cell bordes
        and the number of analyzed cells, update the circuit diagram
        substituting the analyzed cell with an equivalent element type 'Z'
        followed by the corresponding number of analyzed cells.
        Returns the equivalent element name.

        Parameters
        ----------
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
            String of the equivalent element newly created
        """
        new_element = 'Z' + str(cell_count)
        updated_diagram = self.circuit_diagram.replace(
            self.circuit_diagram[i_start:i_end+1], new_element)
        self.circuit_diagram = updated_diagram
        return new_element

    def set_final_results(self):
        """From the impedance_parameters_map attribute, exctract the last
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
        floats.

        Returns
        -------
        parameters_list : list
            List of all the non-constant parameters, in chronological order of
            analysis
        """
        parameters_list = []
        for element, parameter in self.parameters_map.items():
            if element.startswith('Q'):
                parameters_list.append(parameter[0])
                parameters_list.append(parameter[1])
            else:
                parameters_list.append(parameter)
        return parameters_list


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
    """Definition of impedance for capacitors. Raises a ZeroDivisionError if
    the value of the capacitance is 0. or if 0. is a value in the frequency
    array

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
    impedance = 0.
    if (capacitance==0. or 0. in frequency):
        raise ZeroDivisionError('Zero Division in capacitance impedance '
                                + 'definition')
    impedance = 1./(1j*frequency*2*np.pi*capacitance)
    return impedance


def impedance_cpe(q_parameter, ideality_factor, frequency):
    """Definition of impedance for (capacitative) constant phase elements.
    Raises a ZeroDivisionError if the value of the cpe is 0. or if 0. is a
    value in the frequency array

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
    impedance = 0.
    if (q_parameter==0. or 0. in frequency):
        raise ZeroDivisionError('Zero Division in cpe impedance definition')
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
    sum_function : function
        Result function of the sum of the two
    """
    sum_function = lambda x, y: first_function(x, y) + second_function(x, y)
    return sum_function


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
    for function_ in impedance_cell:
        function_cell = add(function_cell, function_)
    return function_cell


def reciprocal(function_):
    """Return the reciprocal function of a generic function. If no function
    is provided, return the zero function.

    Parameters
    ----------
    function_ : function
        Input function

    Returns
    -------
    reciprocal_function : function
        Reciprocal function of the input function
    """
    reciprocal_function = lambda x, y: 1./function_(x, y)
    return reciprocal_function


def parallel_comb(impedance_cell):
    """Perform a parallel comb (reciprocal of the sum of the reciprocal
    functions) of any number of functions. If no function is provided, return
    the zero function.

    Parameters
    ----------
    impedance_cell : list
        List of all impedance functions inside a cell

    Returns
    -------
    function_cell : function
        Equivalent function of the prallel comb of the cell
    """
    sum_of_reciprocal_functions = lambda *_: 0
    for impedance_element in impedance_cell:
        reciprocal_impedance_element = reciprocal(impedance_element)
        sum_of_reciprocal_functions = add(sum_of_reciprocal_functions,
                                          reciprocal_impedance_element)
    function_cell = reciprocal(sum_of_reciprocal_functions)
    return function_cell


#############################

def get_position_opening_bracket(circuit_diagram, i_end):
    """Given the circuit diagran and the position of a closing bracket, find
    the corrispective opening bracket.

    Parameters
    ----------
    circuit_diagram : str
        Diagram of the current circuit
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
    if opening_bracket_positions:
        last_opening_bracket_position = opening_bracket_positions[-1]
    else:
        raise Exception('StructuralError: Impossible to find the opening '
                        + 'bracket. Possible brackets inconsistency')
    return last_opening_bracket_position


def get_string(string_vector):
    """From a string vector creates a single string, concatenating each
    element with a \n as separator.

    Parameters
    ----------
    string_vector : list
        List of string type variables

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
        Listing of all the elements in order of apparition in a circuit
        diagram
    """
    elements_names = []
    for i, char in enumerate(circuit_diagram):
        if char in {'C', 'Q', 'R'}:
            elements_names.append(circuit_diagram[i:i+2])
    return elements_names

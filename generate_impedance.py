import numpy as np

def impedance_R(resistance, frequency):
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

def impedance_C(capacitance, frequency):
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

def impedance_Q(Q, n, frequency):
    """Definition of impedance for (capacitative) constant phase elements.
    
    Parameters
    ----------
    Q : float
        Value of the CPE
    n : float
        Ideality factor of the CPE
    frequency : array
        Values of the frequencies (in Hz) for which the impedance will be 
        computed

    Returns
    -------
    impedance : complex array
        Value of the impedances (in Ohm) for the given frequencies
    """
    impedance = 1./(Q*(frequency*2*np.pi)**n*np.exp(np.pi/2*n*1j))
    return impedance

def get_impedance_const_RCQ_element(element_type, const_parameter):
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
        impedance_element = lambda _, f: impedance_R(const_parameter,f)
    if element_type=='C':
        impedance_element = lambda _, f: impedance_C(const_parameter,f)
    if element_type=='Q':
        impedance_element = lambda _, f: impedance_Q(const_parameter[0],
                                                     const_parameter[1], f)
    return impedance_element

def get_impedance_RCQ_element(element_type, parameters, parameter):
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
        impedance_element = lambda p, f: impedance_R(p[i_parameter], f)
    elif element_type=='C':
        parameters.append(parameter)
        i_parameter = len(parameters)-1
        impedance_element = lambda p, f: impedance_C(p[i_parameter], f)
    elif element_type=='Q':
        parameters.append(parameter[0])
        parameters.append(parameter[1])
        i_parameter = len(parameters)-1
        impedance_element = lambda p, f: impedance_Q(p[i_parameter-1], 
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
        will be object of the fit
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
        object of the fit
    """
    i_element = int(element_string[1]) - 1
    if element_string[0]=='Z':
        impedance_element = impedance_circuit[i_element]
    elif constant_elements[i_element]:
        const_parameter = initial_parameters[i_element]
        element_type = element_string[0]
        impedance_element = get_impedance_const_RCQ_element(
            element_type, const_parameter)
    else:
        elements_circuit.append(element_string)
        parameter = initial_parameters[i_element]
        element_type = element_string[0]
        impedance_element, parameters_circuit = get_impedance_RCQ_element(
            element_type, parameters_circuit, parameter)
    return impedance_element, parameters_circuit, elements_circuit

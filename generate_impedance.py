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

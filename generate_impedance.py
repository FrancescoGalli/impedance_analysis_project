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

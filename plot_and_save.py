"""This module contains the functions to plot data (extracting the modulus and
the phase of the impedance) or data and fit togheter, and saves the plots in a
.pdf file. In addition, it contains a function to save data in a .txt filey.
"""

import numpy as np
import matplotlib.pyplot as plt

OHM_CHARACTER_UNICODE = u'\u03A9'

def get_modulus(impedance_vector):
    """Given a complex vector, return its modulus."""
    modulus_vector = abs(impedance_vector)
    return modulus_vector

def get_phase(impedance_vector):
    """Given a complex vector, return its phase in deg."""
    phase_vector = np.angle(impedance_vector) * 180/np.pi
    return phase_vector

def plot_data(frequency_vector, impedance_vector):
    """Plot in two subfigures the impedance modulus and the phase as a
    function of the frequency. Saves the graphs in a .pdf file.

    Parameters
    ----------
    frequency_vector : array
        Array containing the data frequencies
    impedance_vector : array
        Array containing the data impedances
    """
    _, (modulus, phase) = plt.subplots(ncols=2, figsize=(12, 5.5))
    modulus_data_vector = get_modulus(impedance_vector)
    modulus.set_title('Modulus', fontsize=12)
    modulus.set_xlabel('Frequency(Hz)')
    modulus.set_ylabel('|Z|('+OHM_CHARACTER_UNICODE+')')
    modulus.loglog(frequency_vector, modulus_data_vector, color='blue',
                   linestyle='-', marker='o')
    phase_data_vector = get_phase(impedance_vector)
    phase.set_title('Phase', fontsize=12)
    phase.set_xlabel('Frequency(Hz)')
    phase.set_ylabel('Phase(deg)')
    ticks_array = np.linspace(-90, 0, 10)
    phase.set_yticks(ticks_array)
    phase.semilogx(frequency_vector, phase_data_vector, color='orange',
                   linestyle='-', marker='o')
    plt.suptitle('Impedance data', fontsize=17)
    plt.tight_layout()
    plt.savefig('Data.pdf')
    plt.show()

def save_data(file_name, frequency_vector, impedance_vector):
    """Save the data in a .txt file with as header the name of the
    quantities.

    Parameters
    ----------
    file_name : string
        Name of the file where the data will be saved
    frequency_vector : array
        Array containing the data frequencies
    impedance_vector : array
        Array containing the data impedances
    """
    header_text = 'Frequency(Hz)    Impedance(Ohm)'
    np.savetxt(file_name, np.c_[frequency_vector, impedance_vector],
               delimiter=';', header=header_text, comments='%')

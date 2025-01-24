"""This module contains the functions to plot data (extracting the modulus and
the phase of the impedance) or data and fit togheter, and saves the plots in a
.pdf file. In addition, it contains a function to save data in a .txt filey.
"""

import numpy as np
import matplotlib.pyplot as plt

OHM_CHARACTER_UNICODE = u'\u03A9'

def get_modulus(impedance):
    """Given a complex vector, return its modulus.
    
    Parameters
    ----------
    impedance : array
        Array containing complex impedances

    Returns
    -------
    modulus : array
        Array containing the correspondant impedance modulus
    """
    modulus = abs(impedance)
    return modulus

def get_phase(impedance):
    """Given a complex vector, return its phase in deg.
    
    Parameters
    ----------
    impedance : array
        Array containing complex impedances

    Returns
    -------
    modulus : array
        Array containing the correspondant impedance phase
    """
    phase_vector = np.angle(impedance) * 180/np.pi
    return phase_vector

def plot_data(frequency, impedance):
    """Plot in two subfigures the impedance modulus and the phase as a
    function of the frequency. Saves the graphs in a .pdf file.

    Parameters
    ----------
    frequency : array
        Array containing the data frequencies
    impedance : array
        Array containing the data impedances
    """
    _, (modulus, phase) = plt.subplots(ncols=2, figsize=(12, 5.5))
    modulus_data = get_modulus(impedance)
    modulus.set_title('Modulus', fontsize=12)
    modulus.set_xlabel('Frequency(Hz)')
    modulus.set_ylabel('|Z|('+OHM_CHARACTER_UNICODE+')')
    min_y_mod = min(modulus_data)/2
    max_y_mod = max(modulus_data)*2
    modulus.set_ylim(min_y_mod, max_y_mod)
    modulus.loglog(frequency, modulus_data, color='blue', linestyle='-',
                   marker='o')
    phase_data = get_phase(impedance)
    phase.set_title('Phase', fontsize=12)
    phase.set_xlabel('Frequency(Hz)')
    phase.set_ylabel('Phase(deg)')
    min_y_phase_plot = (min(phase_data)//10 - 1)*10
    max_y_phase_plot = (max(phase_data)//10 + 2)*10
    ticks_array = np.arange(min_y_phase_plot, (max_y_phase_plot)*11/10, 10)
    phase.set_yticks(ticks_array)
    phase.set_ylim(min_y_phase_plot, max_y_phase_plot)
    phase.semilogx(frequency, phase_data, color='orange', linestyle='-',
                   marker='o')
    plt.suptitle('Impedance data', fontsize=17)
    plt.tight_layout()
    plt.savefig('Data.pdf')
    plt.show()

def save_data(file_name, number_of_columns, frequency, impedance):
    """Save the data in a .txt file with as header the name of the
    quantities. The two formats avaible are two-column (complex frequence
    and impedance) or three-column (frequence, modulus and phase).

    Parameters
    ----------
    file_name : string
        Name of the file where the data will be saved
    number_of_columns : int
        Number of columns (and thus the format) to write the data
    frequency : array
        Array containing the data frequencies
    impedance : array
        Array containing the data impedances
    """
    if number_of_columns==2:
        header_text = 'Frequency(Hz)    Impedance(Ohm)'
        np.savetxt(file_name, np.c_[frequency, impedance], delimiter=';',
                   header=header_text, comments='%')
    elif number_of_columns==3:
        modulus = get_modulus(impedance)
        phase_vector = get_phase(impedance)
        header_text = 'Frequency(Hz)    Modulus(Ohm)    Phase(deg)'
        np.savetxt(file_name, np.c_[frequency, modulus,phase_vector],
                   delimiter=';', header=header_text, comments='%')
    else:
        raise Exception('InputError: Invalid format for saving data. It must '
                        + 'be 2 for complex impedance or 3 for modulus and '
                        + 'phase')

def get_box_coordinates(x_vector, y_vector):
    """Return the box position in log-log scale graph.

    Parameters
    ----------
    x_vector : array
        Array containing the indipendent variables
    y_vector : array
        Array containing the dipendent variables

    Returns
    -------
    box_x : float
        X coordinate of the bottom-left corner of the box
    box_y : float
        Y coordinate of the bottom-left corner of the box
    """
    max_x = np.log10(np.max(x_vector))
    min_x = np.log10(np.min(x_vector))
    max_y = np.log10(np.max(y_vector))
    min_y = np.log10(np.min(y_vector))
    box_x = 10**(max_x - (max_x - min_x)/2.5)
    box_y = 10**((max_y + min_y)/1.9)
    return box_x, box_y

def plot_fit(frequency, impedance_data_vector, impedance_fit,
             result_info):
    """Plot in two subfigures the impedance modulus and the phase as a
    function of the frequency. Superimposed to the data the fit curve is
    plotted as well (in red). In the modulus graph, draw a box containing the
    value of the fitted parameters. Saves the graphs in a .pdf file.

    Parameters
    ----------
    frequency : array
        Array containing the data frequencies
    impedance : array
        Array containing the data impedances
    impedance_fit : array
        Array containing the impedances given by the parameter of the best fit
    result_info : string
        String containing the names and value of the fitted parameters.
        Constant parameters are present as well, with a '(constant)' just
        after their values
    """
    _, (modulus, phase) = plt.subplots(ncols=2, figsize=(12, 5.5))
    modulus_data = get_modulus(impedance_data_vector)
    modulus_fit_vector = get_modulus(impedance_fit)
    modulus.set_title('Modulus', fontsize=18)
    modulus.set_xlabel('Frequency(Hz)')
    modulus.set_ylabel('|Z|('+OHM_CHARACTER_UNICODE+')')
    min_y_mod = min(modulus_data)/2
    max_y_mod = max(modulus_data)*2
    modulus.set_ylim(min_y_mod, max_y_mod)
    modulus.loglog(frequency, modulus_data, label='Data', color='blue',
                   marker='o')
    modulus.loglog(frequency, modulus_fit_vector, label='Fit', color='red',
                   linestyle='-')
    modulus.legend()
    box_x, box_y = get_box_coordinates(frequency, modulus_data)
    result_info = 'Fit parameters:\n' + result_info
    modulus.text(box_x, box_y, result_info, fontsize=11, bbox=dict(
        fill=False, edgecolor='black', linewidth=2))
    phase_data = get_phase(impedance_data_vector)
    phase_fit_vector = get_phase(impedance_fit)
    phase.set_title('Phase', fontsize=18)
    phase.set_xlabel('Frequency(Hz)')
    phase.set_ylabel('Phase(deg)')
    min_y_phase_plot = (min(phase_data)//10 - 1)*10
    max_y_phase_plot = (max(phase_data)//10 + 2)*10
    ticks_array = np.arange(min_y_phase_plot, (max_y_phase_plot)*11/10, 10)
    phase.set_yticks(ticks_array)
    phase.set_ylim(min_y_phase_plot, max_y_phase_plot)
    phase.semilogx(frequency, phase_data, label='Data', color='orange',
                   marker='o')
    phase.semilogx(frequency, phase_fit_vector, label='Fit', color='red',
                   linestyle='-')
    phase.legend()
    plt.suptitle('Fitted impedance', fontsize=17)
    plt.tight_layout()
    plt.savefig('Fit.pdf')
    plt.show()

"""This module containes all the test functions (and the tested help functions
for the tests) of the plot_and_save.py module, aside from the plot funtions.
"""


import numpy as np

import sys
from pathlib import Path
sys.path.append(str(Path.cwd().parent))

from plot_and_save import get_amplitude, get_phase, get_box_coordinates


def test_get_amplitude_zero():
    """Check that the output of get_amplitude() is a proper impedance
    amplitude array in the case of a zero impedance.

    GIVEN: a valid zero impedance array of one value
    WHEN: I call the function to extract the amplitude of an impedance
    THEN: the amplitude is a valid amplitudes array, with the expected value
    (zero)
    """
    impedance = np.array([complex(0,0)])
    amplitude = get_amplitude(impedance)
    expected_result = np.array([0])

    assert isinstance(amplitude, np.ndarray), (
        'TypeError in get_amplitude(): the output must be a numpy.ndarray')
    assert amplitude.size>0, ('StructuralError in get_amplitude(): the output '
                              + 'cannot be empty')
    assert amplitude.ndim==1, (
        'TypeError in get_amplitude(): the output must be a one-dimention '
        + 'array, while it is ' + str(amplitude.ndim))
    assert amplitude.dtype==float, (
        'TypeError in get_amplitude(): the output must be a float array, '
        + 'while it is ' + str(amplitude.dtype))
    assert np.all(amplitude>=0), (
        'ValueError for get_amplitude(): the output must have all its '
        + 'elements non-negative.')
    assert amplitude==expected_result, ('ValueError for get_amplitude(): the '
                                        + 'output is incorrect')

def test_get_amplitude_resistor():
    """Check that the output of get_amplitude() is a proper impedance
    amplitude array in the case of a valid resistor-like impedance.

    GIVEN: a valid resistor-like impedance array of one value (thus with
    only a real part)
    WHEN: I call the function to extract the amplitude of an impedance
    THEN: the amplitude is a valid amplitudes array, with the expected value
    """
    impedance = np.array([complex(100,0)])
    amplitude = get_amplitude(impedance)
    expected_result = np.array([100])

    assert isinstance(amplitude, np.ndarray), (
        'TypeError in get_amplitude(): the output must be a numpy.ndarray')
    assert amplitude.size>0, ('StructuralError in get_amplitude(): the output '
                              + 'cannot be empty')
    assert amplitude.ndim==1, (
        'TypeError in get_amplitude(): the output must be a one-dimention '
        + 'array, while it is ' + str(amplitude.ndim))
    assert amplitude.dtype==float, (
        'TypeError in get_amplitude(): the output must be a float array, '
        + 'while it is ' + str(amplitude.dtype))
    assert np.all(amplitude>=0), (
        'ValueError for get_amplitude(): the output must have all its '
        + 'elements non-negative.')
    assert amplitude==expected_result, ('ValueError for get_amplitude(): the '
                                        + 'output is incorrect')

def test_get_amplitude_capacitor():
    """Check that the output of get_amplitude() is a proper impedance
    amplitude array in the case of five capacitor-like impedances.

    GIVEN: a valid capacitor-like impedance array of five values (thus with
    only imaginary parts)
    WHEN: I call the function to extract the amplitude of an impedance
    THEN: the amplitude is a valid amplitudes array, with the expected value
    """
    impedance = np.array([complex(0,-1000), complex(0,-100), complex(0,-10),
                          complex(0,-1)])
    amplitude = get_amplitude(impedance)
    expected_result = np.array([1000, 100, 10, 1])

    assert isinstance(amplitude, np.ndarray), (
        'TypeError in get_amplitude(): the output must be a numpy.ndarray')
    assert amplitude.size>0, ('StructuralError in get_amplitude(): the output '
                              + 'cannot be empty')
    assert amplitude.ndim==1, (
        'TypeError in get_amplitude(): the output must be a one-dimention '
        + 'array, while it is ' + str(amplitude.ndim))
    assert amplitude.dtype==float, (
        'TypeError in get_amplitude(): the output must be a float array, '
        + 'while it is ' + str(amplitude.dtype))
    assert np.all(amplitude>=0), (
        'ValueError for get_amplitude(): the output must have all its values '
        + 'non-negative.')
    assert np.all(amplitude==expected_result), (
        'ValueError for get_amplitude(): the output is incorrect')

def test_get_amplitude_empty():
    """Check that the output of get_amplitude() is a proper impedance
    amplitude array in the case of an empty array for the impedances.

    GIVEN: an invalid empty impedance array
    WHEN: I call the function to extract the amplitude of an impedance
    THEN: the amplitude is an invalid empty array
    """
    impedance = np.array([])
    amplitude = get_amplitude(impedance)

    assert isinstance(amplitude, np.ndarray), (
        'TypeError in get_amplitude(): the output must be a numpy.ndarray')
    assert amplitude.size==0, ('StructuralError in get_amplitude(): the '
                               + 'output is not empty')


def test_get_phase_zero():
    """Check that the output of get_phase() is a proper impedance phase array
    in the case of a zero impedance.

    GIVEN: a valid zero impedance array of one value
    WHEN: I call the function to extract the phase of an impedance
    THEN: the phase is a valid phases array, with the expected value (zero)
    """
    impedance = np.array([complex(0,0)])
    phase = get_phase(impedance)
    expected_result = np.array([0])

    assert isinstance(phase, np.ndarray), (
        'TypeError in get_phase(): the output must be a numpy.ndarray')
    assert phase.size>0, ('StructuralError in get_phase(): the output cannot '
                          + 'be empty')
    assert phase.ndim==1, (
        'TypeError in get_phase(): the output must be a one-dimention array, '
        + 'while it is ' + str(phase.ndim))
    assert phase.dtype==float, (
        'TypeError in get_phase(): the output must be a float array, while '
        + 'it is ' + str(phase.dtype))
    assert -90.< phase <90., (
        'ValueError for get_phase(): the output must have all its elements '
        + 'between -90 and +90 deg')
    assert phase==expected_result, ('ValueError for get_phase(): the output '
                                    + 'is incorrect')

def test_get_phase_resistor():
    """Check that the output of get_phase() is a proper impedance phase array
    in the case of a finite resistor-like impedance.

    GIVEN: a valid resistor-like impedance array of one value (thus with
    only a real part)
    WHEN: I call the function to extract the phase of an impedance
    THEN: the phase is a valid phase array, with the expected value
    (again, zero)
    """
    impedance = np.array([complex(100,0)])
    phase = get_phase(impedance)
    expected_result = np.array([0])

    assert isinstance(phase, np.ndarray), (
        'TypeError in get_phase(): the output must be a numpy.ndarray')
    assert phase.size>0, ('StructuralError in get_phase(): the output cannot '
                          + 'be empty')
    assert phase.ndim==1, (
        'TypeError in get_phase(): the output must be a one-dimention array, '
        + 'while it is ' + str(phase.ndim))
    assert phase.dtype==float, (
        'TypeError in get_phase(): the output must be a float array, while '
        + 'it is ' + str(phase.dtype))
    assert -90.< phase <90., (
        'ValueError for get_phase(): the output must have all its elements '
        + 'between -90 and +90 deg')
    assert phase==expected_result, ('ValueError for get_phase(): the output '
                                    + 'is incorrect')

def test_get_phase_capacitor():
    """Check that the output of get_phase() is a proper impedance phase array
    in the case of four capacitor-like impedances.

    GIVEN: a valid capacitor-like impedance array of four values (thus with
    only imaginary parts)
    WHEN: I call the function to extract the phase of an impedance
    THEN: the phase is a valid phase array, with the expected value
    """
    impedance = np.array([complex(0,-1000), complex(0,-100), complex(0,-10),
                          complex(0,-1)])
    phase = get_phase(impedance)
    expected_result = np.array([-90., -90., -90., -90.])

    assert isinstance(phase, np.ndarray), (
        'TypeError in get_phase(): the output must be a numpy.ndarray')
    assert phase.size>0, ('StructuralError in get_phase(): the output cannot '
                          + 'be empty')
    assert phase.ndim==1, (
        'TypeError in get_phase(): the output must be a one-dimention array, '
        + 'while it is ' + str(phase.ndim))
    assert phase.dtype==float, (
        'TypeError in get_phase(): the output must be a float array, while it '
        + 'is ' + str(phase.dtype))
    assert np.all(-90.<=phase) and np.all(phase<=90.), (
        'ValueError for get_phase(): the output must have all its elements '
        + 'between -90 and +90 deg')
    assert np.all(phase==expected_result), ('ValueError for get_phase(): the '
                                            + 'output is incorrect')


def test_get_box_coordinates_two_points():
    """Check that the box coordinates are within the data for two points with
    different amplitudes.

    GIVEN: a valid set of data points (with the same y) to be plotted (2
    arrays) in logarithmic scale
    WHEN: I call the function to get the info box for the plot
    THEN: the coordinates are a proper x, y set, within the ranges defined by
    the data
    """
    frequency = np.array([10, 50])
    amplitude = np.array([100., 10.0])
    box_x, box_y =  get_box_coordinates(frequency, amplitude)

    caller = 'get_box_coordinates()'
    assert isinstance(box_x, float), (
        'TypeError for box x coordinate in ' + caller +'. It must be a float '
        + 'number')
    assert (np.min(frequency)<box_x<np.max(frequency)), (
        'ValueError for box x coordinate in ' + caller +'. It must  be within '
        + 'the range defined by the frequency vector (x vector)')
    assert isinstance(box_y, float), (
        'TypeError for box y coordinate in ' + caller +'. It must be a float '
        + 'number.')
    assert (np.min(amplitude)<box_y<np.max(amplitude)), (
        'ValueError for box y coordinate in ' + caller +'. It must be within '
        + 'the range defined by the amplitude vector (y vector).')

def test_get_box_coordinates_many_points():
    """Check that the box coordinates are within the data for many points
    with different amplitudes.

    GIVEN: a valid set of data points to be plotted (5 arrays) in logarithmic
    scale
    WHEN: I call the function to get the info box for the plot
    THEN: the coordinates are a proper x, y set, within the ranges defined
    by the data
    """
    frequency = np.array([1, 10, 100, 1000, 10000])
    amplitude = np.array([101., 101., 100., 50, 1])
    box_x, box_y =  get_box_coordinates(frequency, amplitude)

    caller = 'get_box_coordinates()'
    assert isinstance(box_x, float), (
        'TypeError for box x coordinate in ' + caller +'. It must be a float '
        + 'number.')
    assert (np.min(frequency)<box_x<np.max(frequency)), (
        'ValueError for box x coordinate in ' + caller +'. It must  be within '
        + 'the range defined by the frequency vector (x vector).')
    assert isinstance(box_y, float), (
        'TypeError for box y coordinate in ' + caller +'. It must be a float '
        + 'number.')
    assert (np.min(amplitude)<box_y<np.max(amplitude)), (
        'ValueError for box y coordinate in ' + caller +'. It must be within '
        + 'the range defined by the amplitude vector (y vector).')

def test_get_box_coordinates_same_y_points():
    """Check that the box coordinate y is outside the  y data range, leading
    to a possible poor visualization, if all the points have all the same
    amplitude.

    GIVEN: a valid set of data points (with the same y) to be plotted (5) in
    logarithmic scale
    WHEN: I call the function to get the info box for the plot
    THEN: the coordinates are a proper x, y set, but they are outside the
    ranges defined by the data
    """
    frequency = np.array([1, 10, 100, 1000, 10000])
    amplitude = np.array([100., 100., 100., 100., 100.])
    box_x, box_y =  get_box_coordinates(frequency, amplitude)

    caller = 'get_box_coordinates()'
    assert isinstance(box_x, float), (
        'TypeError for box x coordinate in ' + caller +'. It must be a float '
        + 'number.')
    assert (np.min(frequency)<box_x<np.max(frequency)), (
        'ValueError for box x coordinate in ' + caller +'. It must be within '
        + 'the range defined by the frequency vector (x vector).')
    assert isinstance(box_y, float), (
        'TypeError for box y coordinate in ' + caller +'. It must be a float '
        + 'number.')
    assert box_y>np.max(amplitude), (
        'ValueError for box y coordinate in ' + caller +'. It should be '
        + 'within the range defined by the amplitude vector (y vector).')

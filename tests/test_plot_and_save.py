import pytest
import numpy as np

import sys
from pathlib import Path
sys.path.append(str(Path.cwd().parent)) 

from plot_and_save import get_amplitude, get_phase, get_box_coordinates



def non_positive_values_get_amplitude(amplitude):
    """Given an impedance array, return amplitude that is not positive. Used
    for testing.

    Parameters
    ----------
    amplitude : array
        Array of impedances

    Returns
    -------
    wrong_value : list
        List that contains all the invalid amplitude
    wrong_value_index : list
        List of indexes of the invalid amplitude in the array
    """
    wrong_value = []
    wrong_value_index = []
    for i, element in enumerate(amplitude):
        if element<=0:
            wrong_value.append(element)
            wrong_value_index.append(i)
    return wrong_value, wrong_value_index

def generate_example_amplitudes_non_positive():
    """Generate the amplitude of an impedance vector with simulated noise, for
    the non_positive_values_get_amplitude test. Only the last one is incorrect.
    """
    example_amplitudes = [[100., 100., 100.], [1000., 100., 10., 1.],
                          [1100., 200., 110., 101.], [-1000., 100., -10., 1.]]
    return example_amplitudes

@pytest.fixture
def example_amplitudes_non_positive():
    return generate_example_amplitudes_non_positive()

def test_non_positive_values_get_amplitude(example_amplitudes_non_positive):
    """Check that the help function that finds the negative amplitudes works.

    GIVEN: a valid ampltitude array
    WHEN: the function to test the amplitude of an impedance is called
    THEN: the amplitude is valid
    """
    for amplitude in example_amplitudes_non_positive:
        wrong_value, wrong_value_index = non_positive_values_get_amplitude(
            amplitude)
        assert not wrong_value, (
            'ValueError for amplitude ' + str(wrong_value) + ' number '
            + str(wrong_value_index) + ' in get_amplitude() output. Ampltudes '
            + 'must be positive')

def generate_example_amplitude():
    """Generate examples of amplitudes arrays of an impedance array, for
    the get_amplitude test.
    """
    signals = [np.array([complex(100,0), complex(100,0), complex(100,0),
                         complex(100,0)]),
               np.array([complex(0,-1000), complex(0,-100), complex(0,-10),
                         complex(0,-1)]),
               np.array([complex(100,1000), complex(100,100), complex(100,10),
                         complex(100,1)])]
    examples_amplitudes = []
    for impedance in signals:
        amplitude = get_amplitude(impedance)
        examples_amplitudes.append(amplitude)
    return examples_amplitudes

@pytest.fixture
def example_amplitude():
    return generate_example_amplitude()

def test_get_amplitude(example_amplitude):
    """Check that the output of get_amplitude() is a proper impedance
    amplitude array.

    GIVEN: a valid ampliude array
    WHEN: the function to exctract the amplitude of the impedance array is
    called
    THEN: the amplitude is a valid amplitudes array
    """
    for amplitude in example_amplitude:
        assert isinstance(amplitude, np.ndarray), (
            'TypeError in get_amplitude(): the output must be a '
            + 'numpy.ndarray')
        assert amplitude.size>0, (
            'StructuralError in get_amplitude(): the output cannot be empty')
        assert amplitude.ndim==1, (
            'TypeError in get_amplitude(): the output must be a '
            + 'one-dimention array, while it is ' + str(amplitude.ndim))
        assert amplitude.dtype==float, (
            'TypeError in get_amplitude(): the output must be a float array, '
            + 'while it is ' + str(amplitude.dtype))
        wrong_value, wrong_value_index = non_positive_values_get_amplitude(
            amplitude)
        assert not wrong_value, (
            'ValueError for amplitude ' + str(wrong_value) + ' number '
            + str(wrong_value_index) + ' in get_amplitude() output. '
            + 'Ampltudes must be positive')



def generate_example_phase():
    """Generate examples of phase arrays of an impedance array, for
    the get_amplitude test.
    """
    signals = [np.array([complex(100,0), complex(100,0), complex(100,0),
                         complex(100,0)]),
               np.array([complex(0,-1000), complex(0,-100), complex(0,-10),
                         complex(0,-1)]),
               np.array([complex(100,1000), complex(100,100), complex(100,10),
                         complex(100,1)])]
    examples_phase = []
    for impedance in signals:
        phase = get_phase(impedance)
        examples_phase.append(phase)
    return examples_phase

@pytest.fixture
def example_phase():
    return generate_example_phase()

def test_get_phase(example_phase):
    """Check that the output of get_phase() is a valid phase array.

    GIVEN: a valid impedance array
    WHEN: the function to exctract the phase of the impedance array is called
    THEN: the phase is a valid phase array
    """
    for phase in example_phase:
        assert isinstance(phase, np.ndarray), (
            'TypeError in get_phase(): the output must be a numpy.ndarray')
        assert phase.size>0, (
            'StructuralError in get_phase(): the output cannot be empty')
        assert phase.ndim==1, (
            'TypeError in get_phase(): the output must be a one-dimention '
            + 'array, while it is ' + str(phase.ndim))
        assert phase.dtype==float, (
            'TypeError in get_phase(): the output must be a float array, '
            + 'while it is ' + str(phase.dtype))


def generate_example_frequencies_box():
    """Generate the example frequencies for the box coordinates, for the
    get_box test. Only the last one is incorrect.
    """
    example_frequencies = [np.array([10, 50]), np.array([1, 10, 100, 1000]),
                           np.array([1, 2, 3, 4]), np.array([1])]
    return example_frequencies

@pytest.fixture
def example_frequencies_box():
    return generate_example_frequencies_box()

def generate_example_amplitudes_box():
    """Generate the example amplitudes for the box coordinates, for the
    get_box test. Only the last one is incorrect.
    """
    example_amplitudes = [np.array([100., 10.0]), np.array([1000, 100, 10, 1]),
                          np.array([1100, 200, 110, 101]), np.array([1])]
    return example_amplitudes

@pytest.fixture
def example_amplitudes_box():
    return generate_example_amplitudes_box()

def generate_example_box_coordinates():
    """Generate the box coordinates of the result string, for the get_box
    test. Only the last one is incorrect.
    """
    frequencies = generate_example_frequencies_box()
    amplitudes = generate_example_amplitudes_box()
    example_box_coordinates = []
    for i, frequency in enumerate(frequencies):
        coordinates = get_box_coordinates(frequency, amplitudes[i])
        example_box_coordinates.append(coordinates)
    return example_box_coordinates

@pytest.fixture
def example_box_coordinates():
    return generate_example_box_coordinates()

def test_get_box_coordinates(example_box_coordinates, example_frequencies_box,
                             example_amplitudes_box):
    """Check that the box coordinates are a float and within the data.

    GIVEN: a valid set of data to be plotted in logarithmic scale
    WHEN: the function to plot the fit result is called
    THEN: the coordinates are a proper x, y set
    """
    for i, coords in enumerate(example_box_coordinates):
        box_x, box_y = coords
        caller = 'get_box_coordinates()'
        assert isinstance(box_x, float), (
            'TypeError for box x coordinate in ' + caller +'. It must be a '
            + 'float number.')
        assert (np.min(example_frequencies_box[i])<box_x<np.max(
            example_frequencies_box[i])), (
                'ValueError for box x coordinate in ' + caller +'. It must  '
                + 'be within the range defined by the frequency vector '
                + '(x vector).')
        assert isinstance(box_y, float), (
            'TypeError for box y coordinate in ' + caller +'. It must be a '
            + 'float number.')
        assert (np.min(example_amplitudes_box[i])<box_y<np.max(
            example_amplitudes_box[i])), (
                'ValueError for box y coordinate in ' + caller +'. It must '
                + 'be within the range defined by the amplitude vector '
                + '(y vector).')

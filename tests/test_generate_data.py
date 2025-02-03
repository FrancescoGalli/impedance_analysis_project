import numpy as np
import pytest
from hypothesis import given, settings
import hypothesis.strategies as st

import sys
from pathlib import Path
sys.path.append(str(Path.cwd().parent))

from generate_data import generate_random_error_component, simulate_noise


def wrong_elements_generate_random_error(random_error_component):
    """Given the signal length find the elements in the output of
    generate_random_error_component() that are not within 0 and 1. Used for
    testing.

    Parameters
    ----------
    random_error_component : array
        Array of pseudo-random numbers within -1 and 1

    Returns
    -------
    wrong_elements : list
        List that contains all the wrong elements
    wrong_element_index : list
        List of indexes of the wrong elements in the array
    """
    wrong_element = []
    wrong_element_index = []
    for i, element in enumerate(random_error_component):
        if abs(element)>1.:
            wrong_element.append(element)
            wrong_element_index.append(i)
    return wrong_element, wrong_element_index

def generate_example_random_errors():
    """Generate  random values within -1 and 1 for the
    test of the wrong elements in generate_random_error test. Only the last
    one is incorrect.
    """
    examples_random_errors = [[0.2, 0.034, -0.45], [0.], [-0.98, 0.0003, 0.5],
                             [-0.3, 1.4, 10.]]
    return examples_random_errors

@pytest.fixture
def example_random_errors():
    return generate_example_random_errors()

def test_wrong_elements_generate_random_error(example_random_errors):
    for i, example in enumerate(example_random_errors):
        (wrong_element,
         wrong_element_index) = wrong_elements_generate_random_error(example)
        assert not wrong_element, (
            'ValueError for the '+str(i+1)+'th example: '
            + 'element(s) ' + str(wrong_element) + ' in position(s) '
            + str(wrong_element_index) + ' are not within 0 and 1')


@given(signal_length=st.integers(min_value=1, max_value=100),
       seed=st.integers(min_value=0, max_value=1000000))
@settings(max_examples=10)
def test_generate_random_error_component_array(seed, signal_length):
    """Check that the output of generate_random_error_component() is an array.

    GIVEN: a valid length of the generated signal
    WHEN: the function to generate random numbers to simulate noise is called
    THEN: the random noise is an array
    """
    random_error_component = generate_random_error_component(seed,
                                                             signal_length)
    assert isinstance(random_error_component, np.ndarray), (
        'TypeError in generate_random_error_component(): the output must be '
        + 'a numpy.ndarray')
    assert random_error_component.size>0, (
        'StructuralError in generate_random_error_component(): the output'
        + 'cannot be empty')
    (wrong_element,
     wrong_element_index) = wrong_elements_generate_random_error(
         random_error_component)
    assert not wrong_element, (
        'ValueError in output of generate_random_error_component(): '
        + 'element(s) ' + str(wrong_element) + ' in position(s) '
        + str(wrong_element_index) + ' are not within 0 and 1')


def generate_examples_simulated_signal():
    """Generate examples of simulated signals, with simulated noise, for the
    simulate_noise test.
    """
    seeds = [0, 12, 300]
    signals = [np.array([complex(100,0), complex(100,0), complex(100,0),
                         complex(100,0)]),
               np.array([complex(0,-1000), complex(0,-100), complex(0,-10),
                         complex(0,-1)]),
               np.array([complex(100,1000), complex(100,100), complex(100,10),
                         complex(100,1)])]
    examples_simulated_signals = []
    for i, signal in enumerate(signals):
        examples_simulated_signals.append(simulate_noise(seeds[i], signal))
    return examples_simulated_signals

@pytest.fixture
def examples_simulated_signal():
    return generate_examples_simulated_signal()

def test_simulate_noise(examples_simulated_signal):
    """Check that the output of simulate_noise() is a valid 1D array.

    GIVEN: a valid generated signal
    WHEN: the function to generate random numbers to simulate noise is called
    THEN: the random noise array is an numpy array
    """
    for simulated_signal in examples_simulated_signal:
        assert isinstance(simulated_signal, np.ndarray), (
            'TypeError in simulate_noise(): the output must be a '
            + 'numpy.ndarray')
        assert simulated_signal.size>0, (
            'TypeError in simulate_noise(): the output cannot be an empty '
            + 'array')
        assert simulated_signal.ndim==1, (
            'TypeError in simulate_noise(): the output must be a '
            + 'one-dimention array, while it is '
            + str(simulated_signal.ndim))
        assert simulated_signal.dtype==complex, (
            'TypeError in simulate_noise(): the output must be a float '
            + 'array, while it is ' + str(simulated_signal.dtype))

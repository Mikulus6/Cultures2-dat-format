from copy import deepcopy
from collections.abc import Callable
import numpy as np
import os
from shutil import rmtree
from sections.arrays.transitions import get_transitions_accuracy
from sections.parameters import sections_primary
from map_data import MapData

from .prepare_tests import tests_sources_directory

def test_map_data(filepath: str, *, print_successes: bool = True):

    _print_prefix_correct = "✅"
    _print_prefix_warning = "⚠️"
    _print_prefix_mistake = "❌"

    _temporary_file         = "temp.dat"
    _temporary_subdirectory = "temp"

    _temporary_file_path      = os.path.join(os.path.dirname(filepath), _temporary_file)
    _temporary_directory_path = os.path.join(os.path.dirname(filepath), _temporary_subdirectory)

    data_object = MapData()
    data_object.load(filepath)

    # transitions test

    transitions_accuracy = get_transitions_accuracy(data_object)
    if transitions_accuracy == 1:
        if print_successes: print(f"{_print_prefix_correct} Transitions accuracy: {(transitions_accuracy * 100):05f}%")
    else:                   print(f"{_print_prefix_warning} Transitions accuracy: {(transitions_accuracy * 100):05f}%")

    # extract & pack tests

    data_object_2 = MapData()
    data_object.extract(_temporary_directory_path)
    data_object_2.pack(_temporary_directory_path)
    rmtree(_temporary_directory_path)

    if data_object == data_object_2:
        if print_successes: print(f"{_print_prefix_correct} Extract and pack procedures are working correctly.")
    else:                   print(f"{_print_prefix_mistake} Extract and pack procedures are not working correctly.")

    del data_object_2

    # save & load tests

    data_object_2 = MapData()
    data_object.save(_temporary_file_path)
    data_object_2.load(_temporary_file_path)
    os.remove(_temporary_file_path)

    if data_object == data_object_2:
        if print_successes: print(f"{_print_prefix_correct} Save and load procedures are working correctly.")
    else:                   print(f"{_print_prefix_mistake} Save and load procedures are not working correctly.")

    del data_object_2

    # update test

    data_object_2 = deepcopy(data_object)
    data_object_2.update(refresh_primary=True)

    for section_name, val1 in vars(data_object).items():
        if section_name in sections_primary or section_name[0] == "_":
            continue
        derivation_correct = True
        val2 = getattr(data_object_2, section_name)
        if isinstance(val1, np.ndarray) or isinstance(val2, np.ndarray):
            if not np.array_equal(val1, val2): derivation_correct = False
        elif val1 != val2:                     derivation_correct = False

        if derivation_correct:
            if print_successes: print(f"{_print_prefix_correct} Section \"{section_name}\" was correctly updated.")
        else:                   print(f"{_print_prefix_mistake} Section \"{section_name}\" was not correctly updated.")

def run_tests(test_function: Callable = test_map_data):
    """Run all prepared tests"""

    any_file_tested = False
    for filename in os.listdir(tests_sources_directory):
        filepath = os.path.join(tests_sources_directory, filename)
        print(f"Running tests for \"{filepath}\" file.")
        try:
            test_function(filepath)
        except Exception as e:
            print(f"{type(e).__name__} was encountered, skipping tests for \"{filepath}\" file.")
        any_file_tested = True
    if not any_file_tested:
        raise FileNotFoundError("Files must be prepared before running tests. No files are currently prepared.")

from copy import deepcopy
import numpy as np
import os
from shutil import rmtree
from sections.arrays.transitions import get_transitions_accuracy
from sections.parameters import sections_primary
from supplements import prepare_readable
from .grabber import grab_files_from_games, test_sources_directory
from .sources import games_base_directories

prepare_readable(games_base_directories[max(games_base_directories.keys())])

from map_data import MapData

def test_map_data(filepath: str, *, print_successes: bool = False):

    print(f"Analyzing \"{filepath}\" file.")

    _print_indent_correct   = " ✅ "
    _print_indent_neutral   = " ⚠️ "
    _print_indent_incorrect = " ❌ "

    _temporary_file         = "temp.dat"
    _temporary_subdirectory = "temp"

    _temporary_file_path      = os.path.join(os.path.dirname(filepath), _temporary_file)
    _temporary_directory_path = os.path.join(os.path.dirname(filepath), _temporary_subdirectory)

    data_object = MapData()
    data_object.load(filepath)

    # transitions test

    transitions_accuracy = get_transitions_accuracy(data_object)
    if transitions_accuracy == 1:
        if print_successes: print(f"{_print_indent_correct}Transitions accuracy: {(transitions_accuracy * 100):05f}%")
    else:                   print(f"{_print_indent_neutral}Transitions accuracy: {(transitions_accuracy * 100):05f}%")

    # extract+pack test

    data_object_2 = MapData()
    data_object.extract(_temporary_directory_path)
    data_object_2.pack(_temporary_directory_path)
    rmtree(_temporary_directory_path)

    if data_object == data_object_2:
        if print_successes: print(f"{_print_indent_correct  }Extract and pack procedures are working correctly.")
    else:                   print(f"{_print_indent_incorrect}Extract and pack procedures are not working correctly.")

    del data_object_2

    # save+load test

    data_object_2 = MapData()
    data_object.save(_temporary_file_path)
    data_object_2.load(_temporary_file_path)
    os.remove(_temporary_file_path)

    if data_object == data_object_2:
        if print_successes: print(f"{_print_indent_correct  }Save and load procedures are working correctly.")
    else:                   print(f"{_print_indent_incorrect}Save and load procedures are not working correctly.")

    del data_object_2

    # update test

    data_object_2 = deepcopy(data_object)
    data_object_2.update()

    for section_name, val1 in vars(data_object).items():
        if section_name in sections_primary:
            continue
        derivation_correct = True
        val2 = getattr(data_object_2, section_name)
        if isinstance(val1, np.ndarray) or isinstance(val2, np.ndarray):
            if not np.array_equal(val1, val2): derivation_correct = False
        elif val1 != val2:                     derivation_correct = False

        if derivation_correct:
            if print_successes: print(f"{_print_indent_correct  }Section \"{section_name}\" was correctly derived.")
        else:                   print(f"{_print_indent_incorrect}Section \"{section_name}\" was not correctly derived.")

    print()  # newline

def run_tests_for_all_files(grab_files: bool = False, print_successes: bool = False):
    """Test all maps grabbed into the directory test_sources.
    Before running this function, make sure the right local paths are given in "tests/sources.py" file.
    Note that it is not expected for all tests to be successful due to the existence of corrupted tata"""
    if grab_files:
        grab_files_from_games(text_output=True)

    any_file_tested = False
    for filename in os.listdir(test_sources_directory):
        filepath = os.path.join(test_sources_directory, filename)
        test_map_data(filepath, print_successes=print_successes)
        any_file_tested = True

    if not any_file_tested:
        raise FileNotFoundError("Files must be grabbed before running tests. Set grab_files argument to True.")

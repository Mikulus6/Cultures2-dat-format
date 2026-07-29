from collections.abc import Iterable
import os
from supplements.library import Library
from supplements.read import library_global_path

tests_sources_directory = "tests_sources"

def _generate_all_dat_content(dir_path: str, *, text_output: bool = False):
    library = Library()

    library_path = os.path.join(dir_path, library_global_path)
    if os.path.isfile(library_path):
        if text_output:
            print(f"Reading library file from \"{dir_path}\" game directory.")
        library.load(os.path.join(dir_path, library_global_path), cultures_1=False)

    for name, data in library.items():
        if name.lower().endswith(".dat"):
            if data != b"x":
                yield data

    for root, dirs, files in os.walk(dir_path):
        for filename in files:
            match filename.lower().split(".")[-1]:
                case "dat":
                    dat_path = os.path.join(root, filename)
                    with open(dat_path, "rb") as file: yield file.read()
                case "c2m":
                    c2m_library = Library()
                    c2m_library.load(os.path.join(root, filename), cultures_1=False)
                    yield c2m_library["currentusermap\\map.dat"]

def prepare_tests(gameroot_directories: Iterable, skip_if_any_test_exists: bool = False, text_output: bool = True):
    """Prepare data necessary to run all tests. As gameroot_directories use a list of strings with local paths to main
    directories of various games from the Cultures series whose engine is based on "Cultures 2: The Gates of Asgard"."""

    if skip_if_any_test_exists and \
       os.path.exists(tests_sources_directory) and \
       len(os.listdir(tests_sources_directory)) != 0:
        return

    hashes = set()
    for game_num, path in enumerate(gameroot_directories):
        for num, data in enumerate(_generate_all_dat_content(path, text_output=text_output)):

            hash_value = hash(data)
            if hash_value in hashes:
                print(f"Skipping in game no. {game_num} data file no. {num:03d}. (duplicate)")
                continue
            hashes.add(hash_value)

            if text_output:
                print(f"Grabbing from game no. {game_num} data file no. {num:03d}.")
            os.makedirs(tests_sources_directory, exist_ok=True)

            new_path = os.path.join(tests_sources_directory, os.path.join(f"{game_num}_{num:03d}.dat"))
            with open(new_path, "wb") as file:
                file.write(data)

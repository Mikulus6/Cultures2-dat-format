import os
from supplements.library import Library
from .sources import games_base_directories, test_sources_directory

def generate_all_dat_content(dir_path: str, *, text_output: bool = False):

    library = Library()
    try:
        if text_output:
            print(f"Extracting \"{dir_path}\" library file...")
        library.load(os.path.join(dir_path, "DataX\\Libs\\data0001.lib"), cultures_1=False)
    except FileNotFoundError:
        pass

    for name, data in library.items():
        if name.lower().endswith(".dat"):
            yield data

    try:
        for root, dirs, files in os.walk(dir_path):

            # "*.dat" maps
            if "map.dat" in files:
                dat_path = os.path.join(root, "map.dat")
                with open(dat_path, "rb") as file:
                    yield file.read()

            # "*.c2m" maps
            for file in files:
                if file.lower().endswith(".c2m"):
                    c2m_library = Library()
                    c2m_library.load(os.path.join(root, file), cultures_1=False)
                    yield c2m_library["currentusermap\\map.dat"]

    except FileNotFoundError:
        pass

def grab_files_from_games(text_output: bool = False):
    hashes = set()
    for version, path in games_base_directories.items():
        for num, data in enumerate(generate_all_dat_content(path, text_output=text_output)):
            hash_value = hash(data)
            if hash_value in hashes:
                print(f"Duplicate found in game no. {version} data file no. {num:03d}.")
                continue
            hashes.add(hash_value)
            if text_output:
                print(f"Grabbing from game no. {version} data file no. {num:03d}.")
            os.makedirs(test_sources_directory, exist_ok=True)
            new_path = os.path.join(test_sources_directory, os.path.join(f"{version}_{num:03d}.dat"))
            with open(new_path, "wb") as file:
                file.write(data)

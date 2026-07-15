import json
import os
import shutil
from grabber.preparation import prepare_lib_data
from supplements.library import Library

# You can get all relevant Cultures games here:
#  https://www.gog.com/en/game/cultures_12
#  https://www.gog.com/en/game/cultures_34
#  https://archive.org/details/cultures-saga

games_location_source = "grabber\\info.json"
dirname = "tests\\grabbed"


with open(games_location_source, "r") as source_file:
    games_base_directories_ = json.loads(source_file.read())


def generate_all_dat_content(dir_path: str, *, text_output: bool = False):

    library = Library()
    try:
        if text_output:
            print(f"Extracting {dir_path} library file...")
        library.load(os.path.join(dir_path, "DataX\\Libs\\data0001.lib"), cultures_1=False)
    except FileNotFoundError:
        pass

    for name, data in library.items():
        if name.lower().endswith(".dat"):
            yield data

    try:
        for root, dirs, files in os.walk(dir_path):

            # ".dat" maps
            if "map.dat" in files:
                dat_path = os.path.join(root, "map.dat")
                with open(dat_path, "rb") as file:
                    yield file.read()

            # ".c2m" maps
            for file in files:
                if file.lower().endswith(".c2m"):
                    c2m_library = Library()
                    c2m_library.load(os.path.join(root, file), cultures_1=False)
                    yield c2m_library["currentusermap\\map.dat"]

    except FileNotFoundError:
        pass

def iterate_grabbed_paths():
    for item in os.listdir(dirname):
        if item.endswith(".dat") or item.endswith(".c2m"):
            yield os.path.join(dirname, item)

def grab_files_from_games(games_base_directories, *, omit_datax: bool = False, text_output: bool = False):
    hashes = set()
    path_datax = None
    for version, path in games_base_directories.items():
        for num, data in enumerate(generate_all_dat_content(path, text_output=text_output)):
            hash_value = hash(data)
            if hash_value in hashes:
                print(f"Duplicate found in game no. {version} data file no. {num:03d}")
                continue
            hashes.add(hash_value)
            if text_output:
                print(f"Grabbing from game no. {version} data file no. {num:03d}")
            os.makedirs(dirname, exist_ok=True)
            new_path = os.path.join(dirname, os.path.join(f"{version}_{num}.dat"))
            with open(new_path, "wb") as file:
                file.write(data)
        path_datax = path

    if not omit_datax:
        assert path_datax is not None
        if text_output:
            print("Preparing readable library data from the newest game...")
        shutil.copytree(os.path.join(path_datax, "DataX"), "datax", dirs_exist_ok=True)
        prepare_lib_data()
        if text_output:
            print("Grabbing process has been finished.")

def grab_source_files():
    grab_files_from_games(games_base_directories_, text_output=True)

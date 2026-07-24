import os
import pathlib
import time
from supplements import prepare_readable

# Edit these paths according to your local files.
gameroot_path = "C:\\GOG Games\\Northland and 8th Wonder of the World\\8th Wonder of the World"
dat_path      = "C:\\Users\\USERNAME\\Desktop\\Map.c2m"
dir_path      = "C:\\Users\\USERNAME\\Desktop\\Map"

prepare_readable(gameroot_path)  # Copy game files to the project and prepare them for quicker usage.

from map_data import MapData  # This module can be imported only if the necessary game files are copied to the project.

def get_directory_mtime(directory_path):
    try: return max([f.stat().st_mtime for f in pathlib.Path(directory_path).rglob('*') if f.is_file()])
    except ValueError: raise FileNotFoundError

def get_file_mtime(file_path):
    return os.path.getmtime(file_path)

# The following code operates on the file specified in dat_path variable and directory specified in dir_path variable.
# If *.dat / *.c2m file was modified, it will be loaded and extracted to the specified directory.
# If the directory was modified, it will be packed and saved to the specified file.
# This way one can easily experiment how raw extracted file content and map appearance correlate with each other.

is_file_found          = True
is_dir_found           = True
last_file_mod_time     = 0
last_file_mod_time_old = 0
last_dir_mod_time      = 0
last_dir_mod_time_old  = 0

refresh_delay = 1

try: last_file_mod_time = get_file_mtime(dat_path)
except FileNotFoundError: pass

try: last_dir_mod_time  = get_directory_mtime(dir_path)
except FileNotFoundError: pass

while True:
    current_time_string = f"[{time.strftime("%H:%M:%S")}]"

    try:
        last_file_mod_time = get_file_mtime(dat_path)  # noqa
        if last_file_mod_time != last_file_mod_time_old and last_file_mod_time > last_dir_mod_time:

            data = MapData()
            data.load(dat_path)
            data.extract(dir_path)

            is_file_found = True
            is_dir_found  = True

            last_dir_mod_time     = get_directory_mtime(dir_path)
            last_dir_mod_time_old = last_dir_mod_time

            print(f"{current_time_string} Loaded and extracted *.dat file.")

    except FileNotFoundError:
        if is_file_found:
            print(f"{current_time_string} File not found (\"{dat_path}\").")
            is_file_found = False

    try:
        last_dir_mod_time = get_directory_mtime(dir_path)
        if last_dir_mod_time != last_dir_mod_time_old and last_dir_mod_time > last_file_mod_time:

            data = MapData()
            data.pack(dir_path)
            data.save(dat_path)

            is_file_found = True
            is_dir_found  = True

            last_file_mod_time     = get_file_mtime(dat_path)
            last_file_mod_time_old = last_file_mod_time

            print(f"{current_time_string} Packed and saved *.dat file.")

    except FileNotFoundError:
        if is_dir_found:
            print(f"{current_time_string} Directory not found (\"{dir_path}\").")
            is_dir_found = False
        pass

    last_file_mod_time_old = last_file_mod_time
    last_dir_mod_time_old  = last_dir_mod_time
    time.sleep(refresh_delay)

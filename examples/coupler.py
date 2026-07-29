from collections.abc import Callable
import os
import pathlib
import time
from map_data import MapData

def get_directory_mtime(directory_path):
    try: return max([f.stat().st_mtime for f in pathlib.Path(directory_path).rglob('*') if f.is_file()])
    except ValueError: raise FileNotFoundError

def get_file_mtime(file_path):
    return os.path.getmtime(file_path)

def coupler(dat_path: str, dir_path: str, *, print_output: bool = True, loop_condition: Callable = lambda: True):
    """Couples the \\*.dat/\\*.c2m file specified in dat_path with the extracted raw data specified in dir_path.
    The function checks which of the two was modified earlier and updates it to synchronize with the other in real time
    """

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

    while loop_condition():
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

                if print_output:
                    print(f"{current_time_string} Loaded and extracted *.dat file.")

        except FileNotFoundError:
            if is_file_found:
                if print_output:
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

                last_file_mod_time = get_file_mtime(dat_path)

                if print_output:
                    print(f"{current_time_string} Packed and saved *.dat file.")

        except FileNotFoundError:
            if is_dir_found:
                if print_output:
                    print(f"{current_time_string} Directory not found (\"{dir_path}\").")
                is_dir_found = False
            pass

        last_file_mod_time_old = last_file_mod_time
        last_dir_mod_time_old  = last_dir_mod_time
        time.sleep(refresh_delay)


if __name__ == "__main__":
    dat_path_glob = input("Specify *.dat/*.c2m file path:")
    dir_path_glob = input("Specify extracted data directory path:")
    coupler(dat_path_glob, dir_path_glob)

import os
from typing import Literal
from scripts.buffer import data_encoding
from supplements.initialization import decode
from supplements.library import Library

# cultures 1
libraries_directory = "data_l"
loaded_libraries    = dict()

# cultures 2
library_global_path   = "DataX\\Libs\\data0001.lib"
library_global_loaded = False
library_global        = Library()


def read(filepath: str, mode: Literal["r", "rb"] = "r", *,
         skip_file = False, skip_library = False, skip_cif_check = False,
         cultures_1 = False) -> bytes | str:
    """
    This function is supposed to work as combination of built-in open() and file.read() functions, but with the addition
    of backup libraries and cif <-> ini files equivalence similarly to how games from Cultures series load files.

    Warnings:
     - Parameter 'mode' will be ignored if file extension is *.ini, *.cif, *.tab or *.sal.
     - File *.cif will check for backup *.ini file, but it does not work the other way around.
     - Skips-related parameter should be left as False and modified only in recursive cases.
    """
    global loaded_libraries, library_global_loaded, library_global

    filepath = filepath.lower()

    assert not skip_cif_check or filepath.endswith(".cif")

    if not (skip_file or skip_library or skip_cif_check):
        if filepath.endswith(".cif"):

            filepaths = filepath[:-4]+".ini", filepath[:-4]+".cif"

            for skip_lib in (True, False):
                for is_decoded, sub_filepath in zip((True, False), filepaths):
                    try:
                        content = read(sub_filepath, mode= "r" if is_decoded else "rb",
                                       skip_file=not skip_lib, skip_library=skip_lib)
                        return content if isinstance(content, str) else decode(content, sal_tab_file_format=False)
                    except FileNotFoundError:
                        pass

        if (filepath.endswith(".tab") or filepath.endswith(".sal")) and mode == "r":
            return decode(read(filepath, "rb", skip_file=False, skip_library=False), sal_tab_file_format=True)

    if not skip_file:
        try:
            match mode:
                case "r":
                    with open(filepath, mode, encoding=data_encoding) as file:
                        return file.read()
                case "rb":
                    with open(filepath, mode) as file:
                        return file.read()
                case _:
                    raise ValueError

        except FileNotFoundError:
            pass

    if not skip_cif_check and filepath.endswith(".ini"):
        try:                      return decode(read(filepath[:-4] + ".cif", mode="rb", skip_cif_check=True),
                                                sal_tab_file_format=False)
        except FileNotFoundError: pass

    if not skip_library:
        if cultures_1:
            if not skip_library:
                parent_directory = os.path.normpath(filepath).split(os.sep)[0]
                library_path = libraries_directory + os.sep + parent_directory.lower() + ".lib"
                if library_path not in loaded_libraries.keys():

                    try:
                        library = Library()
                        library.load(library_path, cultures_1=True)
                        loaded_libraries[library_path] = library
                    except FileNotFoundError:
                        raise FileNotFoundError

                try:
                    return loaded_libraries[library_path][filepath]
                except KeyError:
                    pass
        else:
            if not library_global_loaded:
                try:
                    library_global.load(library_global_path, cultures_1=False)
                    library_global_loaded = True
                except FileNotFoundError:
                    raise FileNotFoundError

            try:
                return library_global[filepath]
            except KeyError:
                pass

    raise FileNotFoundError


# cultures 2 only
def load_global_library():
    global library_global, library_global_loaded
    if not library_global_loaded:
        library_global.load(library_global_path, cultures_1=False)
        library_global_loaded = True

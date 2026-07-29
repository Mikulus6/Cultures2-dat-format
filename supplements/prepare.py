import os
from .buffer import data_encoding
from .initialization import decode
from .read import library_global, load_global_library

def prepare_data(gameroot_directory: str, project_directory: str = "."):
    """Copy and modify game files to make them more human-readable and quicker to load."""

    data_full_path = os.path.join(project_directory, "data")

    load_global_library(gameroot_directory=gameroot_directory)
    library_global.extract(project_directory)

    for dirpath, _, filenames in os.walk(data_full_path):
        for filename in filenames:
            if filename.lower().endswith(".cif"):
                cif_path = os.path.join(dirpath, filename)
                ini_path = os.path.join(dirpath, os.path.splitext(filename)[0] + ".ini")

                with open(cif_path, "rb") as f:
                    content = f.read()

                with open(ini_path, "w", encoding=data_encoding) as f:
                    f.write(decode(content, sal_tab_file_format=False))

                os.remove(cif_path)

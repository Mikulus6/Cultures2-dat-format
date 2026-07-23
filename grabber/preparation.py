import os
from supplements.buffer import data_encoding
from supplements.initialization import decode
from supplements.read import library_global, load_global_library

def prepare_lib_data():
    # This function is important only for project memebers working on reverse engineering to make things easier to use
    # and debug. It should not be used in the final application, because computers can read binary files directly
    # without converting it to human-readable text.

    load_global_library()
    library_global.extract(".")

    for dirpath, _, filenames in os.walk("data"):
        for filename in filenames:
            if filename.lower().endswith(".cif"):
                cif_path = os.path.join(dirpath, filename)

                with open(cif_path, "rb") as f:
                    content = f.read()

                ini_path = os.path.join(dirpath, os.path.splitext(filename)[0] + ".ini")
                with open(ini_path, "w", encoding=data_encoding) as f:
                    f.write(decode(content, sal_tab_file_format=False))

                os.remove(cif_path)

from data import Data
from grabber.grabber import iterate_grabbed_paths
from sections.primary import extract_primary
from scripts.colormap import ColorMap, apply_colormap
import os
import numpy as np
from PIL import Image
from sections.overlays import emmi_to_emm1
from scripts.expansions import expand_image_object_to_hexagons

# grab_source_files() # Run it only once, after specifying paths in "grabber\info.json" file.


solutions = "tests\\output"
for item in iterate_grabbed_paths():
    print(item)

    solution_dir = os.path.join(solutions, os.path.basename(item).split(".")[0])

    data_object = Data()
    data_object.load(item)
    data_object.extract(solution_dir)
    extract_primary(data_object, solution_dir)

    del data_object
    # data_object = Data()
    # data_object.pack(solution_dir)
    # data_object.save("example.dat")
    # input("...")

import os
import numpy as np
from map_data import MapData
from grabber.grabber import iterate_grabbed_paths, grab_source_files

# grab_source_files() # Run it only once, after specifying paths in "grabber\info.json" file.

solutions = "tests\\output"
for item in iterate_grabbed_paths():
    print(item)

    solution_dir = os.path.join(solutions, os.path.basename(item).split(".")[0])

    data_object = MapData()
    data_object.load(item)
    data_object.extract(solution_dir)
    extract_primary(data_object, solution_dir)

    del data_object
    # data_object = Data()
    # data_object.pack(solution_dir)
    # data_object.save("example.dat")
    # input("...")

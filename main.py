import os
from data import Data
from grabber.grabber import grab_source_files, iterate_grabbed_paths

from supplements.patterns import *
from supplements.textures import *

from sections.mesh_points import combine_emp
from scripts.colormap import apply_colormap
from PIL import Image


# grab_source_files() # Run it only once, after specifying paths in "grabber\info.json" file.

solutions = "tests\\output"
for item in iterate_grabbed_paths():
    print(item)

    solution_dir = os.path.join(solutions, os.path.basename(item).split(".")[0])

    data_object = Data()
    data_object.load(item)
    data_object.extract(solution_dir)

    # TODO: cool map export (clean it up to some other func, but do not remove it). Also implement inverse function later.
    Image.fromarray(apply_colormap(combine_emp(data_object.empa, data_object.empb), mep_colormap),
                    mode="RGB").save(os.path.join(solution_dir, "emp.png"))

    del data_object
    # data_object = Data()
    # data_object.pack(solution_dir)
    # data_object.save("example.dat")
    # input("...")

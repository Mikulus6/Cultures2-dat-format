from data import Data
from grabber.grabber import iterate_grabbed_paths
from sections.primary import extract_primary
import os

from sections.block          import update_lmsb
from sections.brightness     import update_embr
from sections.infrastructure import update_emm1
from sections.logic_type     import update_lmp
from sections.roads          import update_lmro

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

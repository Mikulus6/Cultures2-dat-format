import os
import numpy as np
from PIL import Image

from data import Data
from grabber.grabber import iterate_grabbed_paths, grab_source_files
from sections.primary import extract_primary

from sections.block           import update_lm_b, update_lmsb
from sections.brightness      import update_embr
from sections.continents      import update_lmco_laco
from sections.external_assets import update_ea_d
from sections.infrastructure  import update_emm1
from sections.logic_type      import update_lmp_, update_lmlt
from sections.moveable_size   import update_lmms
from sections.roads           import update_lmro
from sections.roughness       import update_lmpr
from sections.travel_way      import update_lmtw

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

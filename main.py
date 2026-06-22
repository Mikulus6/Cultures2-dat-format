import copy
import os
from data import Data
from grabber.grabber import grab_source_files, iterate_grabbed_paths

from supplements.patterns import *
from supplements.textures import *

from sections.patterns_def import derive_pattern_defs, simplify_pattern_defs
from sections.mesh_points import combine_emp
from scripts.colormap import apply_colormap
from PIL import Image

data_object = Data()
data_object.load("map.dat")
data_object = simplify_pattern_defs(data_object)
data_object.save("map_new.dat")
exit()


# grab_source_files() # Run it only once, after specifying paths in "grabber\info.json" file.

solutions = "tests\\output"
for item in iterate_grabbed_paths():
    print(item)

    # if item.split("\\")[-1][0] not in ("4", "5"):
    #     continue

    solution_dir = os.path.join(solutions, os.path.basename(item).split(".")[0])

    data_object = Data()
    data_object.load(item)
    data_object.extract(solution_dir)

    # TODO: cool map export (clean it up to some other func, but do not remove it). Also implement inverse function later.
    emp_combined = combine_emp(data_object.empa, data_object.empb)
    emp_texts = np.asarray(data_object.eapd)[emp_combined]

    # function tests
    data_object_new = copy.deepcopy(data_object)
    data_object_new = derive_pattern_defs(data_object_new)

    assert data_object_new.eapd == data_object.eapd
    assert np.array_equal(data_object_new.empa, data_object.empa)
    assert np.array_equal(data_object_new.empb, data_object.empb)

    Image.fromarray(apply_colormap(emp_texts, epm_colors_dict),
                    mode="RGB").save(os.path.join(solution_dir, "emp.png"))

    del data_object
    # data_object = Data()
    # data_object.pack(solution_dir)
    # data_object.save("example.dat")
    # input("...")

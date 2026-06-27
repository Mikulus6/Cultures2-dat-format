from data import Data
from grabber.grabber import iterate_grabbed_paths

from supplements.textures import *
from supplements.vertexcolors import *

from sections.patterns import update_patterns
from sections.ab_sections import combine_ab_sections
from scripts.colormap import apply_colormap
from PIL import Image

data_obj = Data()
data_obj.load("map.dat")
data_obj = update_patterns(data_obj)
data_obj.save("map_new.dat")
exit()


# grab_source_files() # Run it only once, after specifying paths in "grabber\info.json" file.

solutions = "tests\\output"
for item in iterate_grabbed_paths():
    print(item)

    solution_dir = os.path.join(solutions, os.path.basename(item).split(".")[0])

    data_object = Data()
    data_object.load(item)
    data_object.extract(solution_dir)

    # TODO: clean it up later
    os.makedirs(os.path.join(solution_dir, "primary"), exist_ok=True)

    # TODO: cool map export (clean it up to some other func, but do not remove it). Also implement inverse function later.
    emp_combined = combine_ab_sections(data_object.empa, data_object.empb)
    emp_texts = np.asarray(data_object.eapd)[emp_combined]
    Image.fromarray(apply_colormap(emp_texts, epm_colors_dict), mode="RGB").save(os.path.join(solution_dir, "primary\\terrain.png"))

    # TODO: vertexcolors export (clean it up later)
    if data_object.emvc is not None:
        Image.fromarray(apply_colormap(data_object.emvc, vertexcolors), mode="RGB").save(os.path.join(solution_dir, "primary\\vertexcolors.png"))

    del data_object
    # data_object = Data()
    # data_object.pack(solution_dir)
    # data_object.save("example.dat")
    # input("...")

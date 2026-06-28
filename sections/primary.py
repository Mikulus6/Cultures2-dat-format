import os
import numpy as np
from PIL import Image
from scripts.colormap import ColorMap, apply_colormap
from scripts.image import bytes_to_image
from sections.ab_sections import combine_ab_sections
from supplements.textures import emp_colors_dict, emt_colors_dict
from supplements.palettes import vertexcolors

transition_types_num = 6
no_transition_color = (0, 0, 0)
emt_corners_presence = {0: (False, True,  True ),
                        1: (True,  False, True ),
                        2: (True,  True,  False),
                        3: (True,  False, False),
                        4: (False, True,  False),
                        5: (False, False, True )}

emm_transition_types = {3: "overlay road 1",
                        4: "overlay road 2",
                        5: "overlay house 1",
                        6: "overlay house 2"}

assert no_transition_color not in emt_colors_dict.values()

# transitions colormap
emt_colors_dict_with_empty = ColorMap(dict_={"": no_transition_color})
emt_colors_dict_with_empty.update(emt_colors_dict)
emt_cover_colormap = ColorMap(dict_={k: tuple(0 if not x else 255 for x in v)
                                     for k, v in emt_corners_presence.items()})
emt_cover_colormap[transition_types_num] = no_transition_color

def extract_primary(data_object, directory):
    _directory_name = "primary"
    directory_full_name = os.path.join(directory, _directory_name)
    os.makedirs(directory_full_name, exist_ok=True)

    # terrain
    emp_combined = combine_ab_sections(data_object.empa, data_object.empb)
    emp_texts = np.asarray(data_object.eapd)[emp_combined]
    Image.fromarray(apply_colormap(emp_texts, emp_colors_dict), mode="RGB").save(
        os.path.join(directory_full_name, "terrain.png"))

    # transitions (4 sections)
    for emt_a, emt_b, layer in ((data_object.emt1, data_object.emt2, "foreground"),
                                (data_object.emt3, data_object.emt4, "background")):
        emt_combined = combine_ab_sections(emt_a, emt_b)

        match np.issubdtype(data_object.emt1.dtype, np.unsignedinteger):
            case True:  minus_one = np.iinfo(data_object.emt1.dtype).max
            case False: minus_one = -1

        mask = (emt_combined == minus_one)  # noqa
        emt_terrain_type, emt_cover_type = np.divmod(emt_combined, transition_types_num)
        emt_terrain_type[mask] = minus_one
        emt_cover_type[mask] = transition_types_num

        emt_texts = np.asarray(data_object.eatd)[np.where(mask, 0, emt_terrain_type)]
        emt_texts[mask] = ""

        Image.fromarray(apply_colormap(emt_texts, emt_colors_dict_with_empty), mode="RGB").save(
            os.path.join(directory_full_name, f"transitions_terrain_{layer}.png"))

        Image.fromarray(apply_colormap(emt_cover_type, emt_cover_colormap), mode="RGB").save(
            os.path.join(directory_full_name, f"transitions_cover_{layer}.png"))

        del minus_one

    # vertexcolors
    if data_object.emvc is not None:
        Image.fromarray(apply_colormap(data_object.emvc, vertexcolors), mode="RGB").save(
            os.path.join(directory_full_name, "vertexcolors.png"))

    # landscapes + landscapes players
    landscapes_dict = {}
    for (y, x), landscape_id in np.ndenumerate(data_object.emla):
        if int(landscape_id) == (2**16) - 1:
            assert int(np.uint8(data_object.lmlp[y, x]).view(np.int8)) == -1
            continue
        landscapes_dict[x, y] = data_object.eald[landscape_id]
    with open(os.path.join(directory_full_name, "landscapes.csv"), "w") as file:
        for coordinates, landscape in landscapes_dict.items():
            landscape_owner_player_id = int(np.uint8(data_object.lmlp[coordinates[::-1]]).view(np.int8))
            file.write(f"{coordinates[0]},{coordinates[1]},\"{landscape}\",{landscape_owner_player_id}\n")

    # heightmap
    bytes_to_image(data_object.lmhe.tobytes(),
                   os.path.join(directory_full_name, "heightmap.png"), width=data_object.lsiz.width)

    # fishes
    data_object.lafm.to_file(os.path.join(directory_full_name, "fishes.csv"))

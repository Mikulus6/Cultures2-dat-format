import numpy as np
from sections.common.minus_one import get_minus_one
from supplements.external import landscapes
from typing import Literal

# TODO: non obstructable landscapes are the current bes hypothesis for lmms derivation.
non_obstructable_landscapes = ("gate_01_open", "gate_02_open", "gate_03_open", "tree_dead 03")

# lm_b = {lmwb, lmbb}
def data_to_lm_b(data_object, *, block_type: Literal["Walk", "Build"] = "Walk", exclude_non_obstructable: bool = False):
    lm_b = np.zeros_like(data_object.lmwb)
    block_typ_name = f"Logic{block_type}BlockArea"

    micro_width  = 2 * data_object.lsiz.width
    micro_height = 2 * data_object.lsiz.height

    no_landscape = get_minus_one(data_object.emla.dtype)

    for y in range(micro_height):
        for x in range(micro_width):
            landscape_id = data_object.emla[y, x]
            if landscape_id == no_landscape:  # noqa
                continue
            landscape = landscapes[data_object.eald[landscape_id]]
            landscape_valency = data_object.lmlv[y, x]

            for valency, x_offset, y_offset, indent in landscape.get(block_typ_name, []):
                if landscape_valency < valency:
                    continue

                for x_iter in range(indent):
                    y_real = y + y_offset
                    x_real = x + x_offset + x_iter + int((y % 2 != 0) and (y_real % 2 == 0))

                    if 0 <= x_real < micro_width and 0 <= y_real < micro_height:
                        lm_b[y_real, x_real] = 1
    return lm_b

def update_lm_b(data_object):
    data_object.lmwb = data_to_lm_b(data_object, block_type="Walk")
    data_object.lmbb = data_to_lm_b(data_object, block_type="Build")

def data_to_lmsb(data_object):
    lmsb = np.zeros_like(data_object.lmsb)
    for walkable_terrain_type in data_object.lasw.__class__._walkable_terrain_types: # noqa
        for walk_sector in getattr(data_object.lasw, walkable_terrain_type):
            for point in walk_sector.points:
                lmsb[*point[::-1]] = 1
    return lmsb

def update_lmsb(data_object):
    data_object.lmsb = data_to_lmsb(data_object)
    return data_object

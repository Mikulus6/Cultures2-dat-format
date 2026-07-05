import numpy as np
from math import floor, ceil
from sections.common.geometry import get_adjacent_triangles, get_neighbouring_vertices
from sections.continents import continents_logic_types
from sections.logic_type import get_adjacent_logic_types

logic_types_roughness = {0: 0, 1: 1, 2: 2, 3: 4, 4: 3, 5: 0, 6: 0, 7: 5, 8: 3, 9: 3, 10: 1}

def data_to_lmpr(data_object):
    # There exist three original maps on which this algoritm does not produce the exactly same output as the section
    # included in the game files. Those are "The swords of the kings" and "Trophy hunt" in the game "Northland" and
    # "Servant of the oracle" in the game "8th Wonder of the World". These discrepancies are considered negligible.
    lmpr = np.zeros_like(data_object.lmpr)
    for y in range(2 * data_object.lsiz.height):
        for x in range(2 * data_object.lsiz.width):
            continent_type = data_object.laco[data_object.lmco[y, x]].type
            if continent_type == 0:
                continue
            elif continent_type == 2 or data_object.lmro[y, x] == 1:
                lmpr[y, x] = 1
            else:
                roughness_values = [logic_types_roughness[logic_type] for logic_type
                                    in get_adjacent_logic_types(data_object, (x, y))
                                    if logic_type in continents_logic_types[1]]
                lmpr[y, x] = sum(roughness_values) // len(roughness_values)
    return lmpr

def update_lmpr(data_object):
    data_object.lmpr = data_to_lmpr(data_object)
    return data_object

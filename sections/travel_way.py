import numpy as np
from sections.common.ab_sections import get_neighbouring_vertices, get_tangent_triangles
from sections.continents import continents_types_priority, continents_logic_types


def get_connection_type(data_object, coordinates_1, coordinates_2):
    width = data_object.lsiz.width
    height = data_object.lsiz.height
    adjacent_logic_types = set()
    for coordinates_iter, lmp_section in zip(get_tangent_triangles(coordinates_1, coordinates_2),
                                             (data_object.lmpa, data_object.lmpb)):
        for x_1, y_1 in coordinates_iter:
            if not (0 <= x_1 < width) or \
               not (0 <= y_1 < height):
                continue
            adjacent_logic_types.add(lmp_section[y_1, x_1])

    for continent_type in continents_types_priority:
        if not continents_logic_types[continent_type].isdisjoint(adjacent_logic_types):
            return continent_type
    else:
        raise ValueError  # undefined connection type

def data_to_lmtw(data_object):
    # TODO: doesn't work on map edges. I also checked and there's no difference between swamp and void in the middle of the map.
    #       This function is not finished yet!!!
    micro_width  = 2 * data_object.lsiz.width
    micro_height = 2 * data_object.lsiz.height

    lmtw = np.zeros_like(data_object.lmco, dtype=np.uint8)

    for y in range(0, micro_height):
        for x in range(0, micro_width):
            continent_index = data_object.lmco[y, x]
            continent_type = int(data_object.laco[continent_index].type)
            if continent_type == 0:
                continue

            for index_, coordinates in enumerate(get_neighbouring_vertices((x, y))):
                if not (0 <= coordinates[0] < micro_width) or \
                   not (0 <= coordinates[1] < micro_height):
                    continue

                if continent_index == data_object.lmco[coordinates[::-1]] and \
                   continent_type == get_connection_type(data_object, (x, y), coordinates):
                    lmtw[y, x] += 2 ** index_
    return lmtw

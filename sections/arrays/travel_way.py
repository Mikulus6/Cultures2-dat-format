import numpy as np
from ..arrays.continents import get_continent_type
from ..generic.geometry import get_neighbouring_vertices

def check_boundary(data_object, coordinates):
    x, y = coordinates

    if y < 4 or y >= 2 * data_object.lsiz.height - 4:
        return True

    match y % 4:
        case 0: return x < 4 or x >= 2 * data_object.lsiz.width - 4
        case 1: return x < 3 or x >= 2 * data_object.lsiz.width - 5
        case 2: return x < 5 or x >= 2 * data_object.lsiz.width - 3
        case 3: return x < 4 or x >= 2 * data_object.lsiz.width - 4
        case _: raise ArithmeticError

def data_to_lmtw(data_object):
    # There are two types of exceptions in exisitng maps where lmtw is not correctly derived. On of them, possible to
    # easily recreate in the original editor, is that edges might not update when drawing with void on top of land or
    # water. The other one is present only on the map "Trophy hunt" in the game "Northland". This map does not seem to
    # be properly finished (as there are *.bak files present), which would explain presence of uexpected values in lmtw.

    lmtw = np.zeros(data_object.lsiz.shape_micro, dtype=np.uint8)
    continent_types = -1 * np.ones(data_object.lsiz.shape_micro, dtype=np.int8)

    for y in range(0, 2 * data_object.lsiz.height):
        for x in range(0, 2 * data_object.lsiz.width):
            if continent_types[y, x] == -1:
                continent_types[y, x] = get_continent_type(data_object, (x, y))

            if check_boundary(data_object, (x, y)) or continent_types[y, x] == 0:
                continue

            for index_, coordinates in enumerate(get_neighbouring_vertices((x, y))[:3]):
                # Connections can be represented as an undirected graph, therefore it is necessary to check only three
                # out of six connections, because remaining three can be checked from the side of other vertices.
                if check_boundary(data_object, coordinates):
                    continue

                if continent_types[coordinates[::-1]] == -1:
                    continent_types[coordinates[::-1]] = get_continent_type(data_object, coordinates)

                if continent_types[y, x] == \
                   continent_types[coordinates[::-1]] == \
                   get_continent_type(data_object, (x, y), coordinates):

                    lmtw[y, x]              |= (1 << index_)
                    lmtw[coordinates[::-1]] |= (1 << (index_ + 3))
    return lmtw

def update_lmtw(data_object):
    data_object.lmtw = data_to_lmtw(data_object)
    return data_object

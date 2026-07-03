import numpy as np
from functools import lru_cache

def combine_ab_sections(a_sec: np.ndarray, b_sec: np.ndarray):
    sec = np.empty((a_sec.shape[0], a_sec.shape[1] * 2), dtype=a_sec.dtype)
    sec[:, 0::2] = a_sec
    sec[:, 1::2] = b_sec
    return sec

def split_ab_sections(sec):
    sec = np.asarray(sec)
    return sec[:, 0::2], \
           sec[:, 1::2]

def get_neighbouring_vertices(coordinates):
    x, y = coordinates
    # Order of elements in lists is important here due to directions being ordered in some rare cases.
    if y % 2 == 0: return [(x + 1, y), (x, y + 1), (x - 1, y + 1), (x - 1, y), (x - 1, y - 1), (x, y - 1)]
    else:          return [(x + 1, y), (x + 1, y + 1), (x, y + 1), (x - 1, y), (x, y - 1), (x + 1, y - 1)]

def get_adjacent_triangles(coordinates):
    a_offsets, b_offsets = get_adjacent_triangles_offets(coordinates)
    a_coordinates = [(coordinates[0] // 2 + x, coordinates[1] // 2 + y) for x, y in a_offsets]
    b_coordinates = [(coordinates[0] // 2 + x, coordinates[1] // 2 + y) for x, y in b_offsets]
    return a_coordinates, b_coordinates

def get_adjacent_triangles_offets(coordinates) -> (tuple, tuple):
    x, y =  coordinates
    match x % 2, y % 4:
        case 0, 0: return ((0, 0), (-1, -1), (0, -1)), ((0, 0), (-1, -1), (-1, 0))
        case 0, 1: return ((0, 0),), ((0, 0),)
        case 0, 2: return ((0, -1),), ((-1, 0),)
        case 0, 3: return ((0, 0),), ((-1, 0),)
        case 1, 0: return ((0, -1),), ((0, 0),)
        case 1, 1: return ((1, 0),), ((0, 0),)
        case 1, 2: return ((0, 0), (0, -1), (1, -1)), ((0, 0), (0, -1), (-1, 0))
        case 1, 3: return ((0, 0),), ((0, 0),)
        case _: raise ValueError

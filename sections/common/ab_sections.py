import numpy as np

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

def get_adjacent_triangles(coordinates, *, ignore_minor_vertices=False):
    # 'ignore_minor_vertices' should always be set to False, except for recursive case in function definitnion.
    x, y = coordinates

    if x % 2 == 0 and y % 4 == 0:    # major vertex, even row
        a_coordinates = [(x//2, y//2), (x//2 - 1, y//2 - 1), (x//2, y//2 - 1)]
        b_coordinates = [(x//2, y//2), (x//2 - 1, y//2 - 1), (x//2 - 1, y//2)]
    elif x % 2 == 1 and y % 4 == 2:  # major vertex, odd row
        a_coordinates = [(x//2, y//2), (x//2, y//2 - 1), (x//2 + 1, y//2 - 1)]
        b_coordinates = [(x//2, y//2), (x//2, y//2 - 1), (x//2 - 1, y//2)]
    elif not ignore_minor_vertices:  # minor vertex

        a_coordinates_collection = []
        b_coordinates_collection = []

        for neighbour in get_neighbouring_vertices(coordinates):
            a_coordinates_temp, b_coordinates_temp = get_adjacent_triangles(neighbour, ignore_minor_vertices=True)
            if len(a_coordinates_temp) + len(b_coordinates_temp) != 0:  # major vertex
                a_coordinates_collection.append(a_coordinates_temp)
                b_coordinates_collection.append(b_coordinates_temp)

        a_coordinates = [coordinates for coordinates in a_coordinates_collection[0] if
                            coordinates in a_coordinates_collection[1]]
        b_coordinates = [coordinates for coordinates in b_coordinates_collection[0] if
                            coordinates in b_coordinates_collection[1]]

        return a_coordinates, b_coordinates
    else:
        a_coordinates, b_coordinates = [], []

    return a_coordinates, b_coordinates

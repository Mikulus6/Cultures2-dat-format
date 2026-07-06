import numpy as np
from collections import deque
from collections.abc import Callable
from sections.arrays.common.geometry import get_neighbouring_vertices
from sections.special.continents import Continents, Continent
from sections.arrays.logic_type import get_adjacent_logic_types


continents_logic_types = {0: {0, 5, 6},              # void
                          1: {2, 3, 4, 7, 8, 9, 10}, # land
                          2: {1, }}                  # water
void_continent_id = 0
minimum_continent_size = 20
continents_types_priority = (1, 0, 2)  # from the most important to the least important

continents_logic_types_inverse = {v: k for k, vs in continents_logic_types.items() for v in vs}

def get_continent_type(data_object, coordinates_1, coordinates_2 = None):
    adjacent_logic_types = get_adjacent_logic_types(data_object, coordinates_1, coordinates_2)
    for continent_type in continents_types_priority:
        if not continents_logic_types[continent_type].isdisjoint(adjacent_logic_types):
            return continent_type
    else:
        raise ValueError  # undefined continent type

def flood_fill_hexagonal_generator(input_data: np.ndarray | Callable, coordinates_start, *, shape=None):
    """ Generates triplets of form (x, y, z), where (x, y) are coordinates and z is a binary indicator of vertex
    belonging to filled area or to its boundary (1 = filled area, 0 = bounadry) """

    if isinstance(input_data, Callable):
        func = input_data
        assert isinstance(shape, tuple)
    else:
        assert isinstance(input_data, np.array)
        func = lambda coords: input_data[coords[::-1]]
        if shape is None: shape = input_data.shape
        assert shape == input_data.shape

    value = func(coordinates_start)
    searched = np.zeros(shape=shape, dtype=np.bool)
    searched[coordinates_start[::-1]] = True
    queue = deque([coordinates_start])

    while len(queue) > 0:
        x, y = queue.popleft()

        if func((x, y)) == value:
            yield x, y, 1 # filled area
            for x_1, y_1 in get_neighbouring_vertices((x, y)):
                if not(0 <= x_1 < shape[1]) or \
                   not(0 <= y_1 < shape[0]):
                    continue
                if not searched[y_1, x_1]:
                    queue.append((x_1, y_1))
                    searched[y_1, x_1] = True
        else:
            yield x, y, 0 # boundary

def data_to_lmco_laco(data_object):

    def get_current_continent_type(coordinates):
        return get_continent_type(data_object, coordinates)

    def cost_function(coordinates):
        return coordinates[1] * (2 * data_object.lsiz.width) + coordinates[0]

    is_assigned = np.zeros(shape=data_object.lsiz.shape_micro, dtype=np.bool)
    lmco        = np.zeros(shape=data_object.lsiz.shape_micro, dtype=np.uint8)
    laco = Continents()

    laco.append(Continent(type=void_continent_id, anchor_vertex=(0, 0), size=0))
    current_continent_id = 1
    boundary_vertices = set()
    anchor_vertex = (0, 0)

    while anchor_vertex is not None:

        continent_type = get_current_continent_type(anchor_vertex)
        elements_to_clear = []
        continent_size = 0

        for x, y, inner_fill in flood_fill_hexagonal_generator(input_data=get_current_continent_type,
                                                               coordinates_start=anchor_vertex,
                                                               shape=data_object.lsiz.shape_micro):
            if inner_fill:
                is_assigned[y, x] = True
                lmco[y, x]        = current_continent_id if continent_type != 0 else void_continent_id

                continent_size += 1
                if   continent_size <  minimum_continent_size: elements_to_clear.append((x, y))
                elif continent_size == minimum_continent_size: elements_to_clear.clear()
            else:
                boundary_vertices.add((x, y))

        for vertex in elements_to_clear: lmco[vertex[::-1]] = void_continent_id

        if continent_type != void_continent_id and len(elements_to_clear) == 0:
            laco.append(Continent(type=continent_type, anchor_vertex=anchor_vertex, size=continent_size))
            current_continent_id += 1

            if current_continent_id > Continents._continents_limit: # noqa
                raise OverflowError

        # updating anchor_vertex below

        anchor_vertex_min_cost = float("inf")
        anchor_vertex = None

        boundary_vertices_to_remove = set()
        for boundary_vertex in boundary_vertices:
            if is_assigned[boundary_vertex[::-1]]:
                boundary_vertices_to_remove.add(boundary_vertex)
                continue
            cost_value = cost_function(boundary_vertex)
            if anchor_vertex_min_cost > cost_value:
                anchor_vertex = boundary_vertex
                anchor_vertex_min_cost = cost_value
        boundary_vertices -= boundary_vertices_to_remove

    return lmco, laco

def update_lmco_laco(data_object):
    data_object.lmco, data_object.laco = data_to_lmco_laco(data_object)
    return data_object

def check_continents_isomorphicity(data_object_1, data_object_2, *, ignore_void_mismatch: bool = False):

    if data_object_1.lsiz != data_object_2.lsiz:
        return False

    vertex_bijection_1 = dict()
    vertex_bijection_2 = dict()

    for y in range(0, 2 * data_object_1.lsiz.height):
        for x in range(0, 2 * data_object_1.lsiz.width):
            value_1 = int(data_object_1.lmco[y, x])
            value_2 = int(data_object_2.lmco[y, x])

            if ignore_void_mismatch and (data_object_1.laco[value_1].type == 0 or
                                         data_object_2.laco[value_2].type == 0):
                # On rare cases this mismatch happens on original maps. Consider land where in two different orders you
                # draw a water basin with size slightly bigger than the minimum size required for a continent, and a
                # void area adjacent to it, which now makes the water basin to small to be considered a continent.
                # If water basin was drawn first, it is still considered a continent, even if due to the void presence
                # it no longer satisfies criteria to be considered one of them. If void was drawn first, and then water
                # was drawn next to it, never satisfying the condition of a continent minimum size, it will never be
                # considerd a continent in the first place. These exceptions are present in several maps from games
                # "Northland" and "8th Wonder of the World".
                continue

            if value_2 != vertex_bijection_1.setdefault(value_1, value_2): return False
            if value_1 != vertex_bijection_2.setdefault(value_2, value_1): return False

        for continent_1_id, continent_2_id in vertex_bijection_1.items():
            try:
                continent_1 = data_object_1.laco[continent_1_id]
                continent_2 = data_object_2.laco[continent_2_id]
            except IndexError:                       return False
            if continent_1.type != continent_2.type: return False
            if not ignore_void_mismatch and (data_object_1.lmco[continent_1.anchor_vertex[::-1]] != continent_1_id and
                                             data_object_2.lmco[continent_2.anchor_vertex[::-1]] != continent_2_id):
                return False
            # It is unnecessary to check sizes of continents here, because bijection already requires sizes to match.
    return True

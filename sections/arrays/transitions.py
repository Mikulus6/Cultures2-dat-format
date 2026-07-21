from functools import cache
from itertools import product, repeat
import numpy as np
from random import randint
from typing import Literal
from ..generic.geometry import get_adjacent_triangles, get_triangle_corner_vertices
from ..generic.imports import transitions, points, patterns
from ..generic.minus_one import get_minus_one

# Capitalization of various names is not consistent across game files related to transitions.
# To prevent any confusion, it was decided to turn all ambigious strings into lowercase.

points_lowercase = {key.lower(): value for key, value in points.items()}
points_editnames_ordered_lowercase = list(map(str.lower, points.editnames_ordered))
points_inversed = {point["patterngroup"].lower() : point["name"].lower() for point in points.values()}

transitions_inversed = {transition["pointtype"].lower(): list() for transition in transitions.values()}
for transition in transitions.values():
    transitions_inversed[transition["pointtype"].lower()].append(transition["name"].lower())

transitions_per_pointtype_upper_limit = 2
logic_type_void = 0

priority_lowercase = ('ice', 'snow', 'meadow megadark', 'meadow', 'meadow dark', 'mountain', 'swamp', 'concrete',
                      'desertbrown d', 'desertbrown', 'desertbrown c', 'desertbrown b', 'desertbrown a', 'mud', 'sand',
                      'water bright', 'water')  # Calculated using StatisticalPriority.

permutations_per_transition = 6
cover_presence = {0: (False, True,  True ),
                  1: (True,  False, True ),
                  2: (True,  True,  False),
                  3: (True,  False, False),
                  4: (False, True,  False),
                  5: (False, False, True )}

class StatisticalPriority(dict):
    # This class is supposed to be used to determine the priority of transitions based on frequencies of occurrence of
    # different transitions in existing maps.

    def __init__(self):
        super().__init__(dict())

    def analyze(self, data_object):
        for y, x, triangle_type in product(range(data_object.lsiz.height),
                                           range(data_object.lsiz.width),
                                           ("a", "b")):

            current_transitions = get_current_transitions(data_object, (x, y), triangle_type, as_pointtype=True)

            for i, corner in enumerate(get_triangle_corner_vertices((x, y), triangle_type)):
                current_upper_transition = current_transitions[0][i]
                current_lower_transition = current_transitions[1][i]

                if current_upper_transition is None and current_lower_transition is not None:
                    current_upper_transition, current_lower_transition = \
                    current_lower_transition, current_upper_transition

                if current_upper_transition is not None and current_lower_transition is None:
                    corner_characteristic = get_corner_characteristic(data_object, corner)
                    less_important = set(corner_characteristic) - {current_upper_transition, None}
                    more_important = current_upper_transition

                    for item in less_important:
                        self.setdefault((more_important, item), 0)
                        self[more_important, item] += 1

    def is_priority_correct(self, more_important, less_important, *, cutoff: int = 0) -> bool:
        count_normal   = self.get((more_important, less_important), 0)
        count_reversed = self.get((less_important, more_important), 0)
        return count_normal > max(count_reversed, cutoff)

    def is_priority_ambiguous(self, pointtype_1, pointtype_2, *, cutoff: int = 0) -> bool:
        return not(self.is_priority_correct(pointtype_1, pointtype_2, cutoff=cutoff) or\
                   self.is_priority_correct(pointtype_2, pointtype_1, cutoff=cutoff))

    def get_linear_order(self):
        # Earlier elements have higher priority.
        for cutoff in (0, *sorted(self.values())):
            values = set()
            dependencies = {}
            for key in self.keys():
                values.update({*key})
                if self.is_priority_correct(*key, cutoff=cutoff):
                    dependencies.setdefault(key[0], set())
                    dependencies.setdefault(key[1], set()).add(key[0])
            if not values.issubset(dependencies.keys()):
                raise ValueError  # Cycles in priority graph cannot be removed without making the graph disjoint.

            priority_list = list()
            try:  # Kahn's algorithm
                while dependencies:
                    free = next(key for key, value in dependencies.items() if not value)
                    dependencies.pop(free)
                    for deps in dependencies.values():
                        deps.discard(free)
                    priority_list.append(free)
            except StopIteration:
                continue  # Cycle is present in priority graph. Increase edges cutoff until no cycle is found.
            break

        for iteration_depth in range(len(priority_list)-1, 0, -1):
            for index_ in range(iteration_depth):
                item_1 = priority_list[index_]
                item_2 = priority_list[index_ + 1]

                if self.is_priority_ambiguous(item_1, item_2, cutoff=cutoff) and\
                   self.is_priority_correct(item_2, item_1, cutoff=0):

                    priority_list[index_]     = item_2
                    priority_list[index_ + 1] = item_1

                elif self.is_priority_ambiguous(item_1, item_2, cutoff=0):
                    raise ValueError  # Linear order is not well-defined.

        return priority_list


def get_current_transitions(data_object, coordinates, triangle_type: Literal["a", "b"], *, as_pointtype: bool = False):
    no_transition = get_minus_one(data_object.emt1.dtype)

    match triangle_type:
        case "a": upper_emt, lower_emt = data_object.emt1, data_object.emt3
        case "b": upper_emt, lower_emt = data_object.emt2, data_object.emt4
        case _: raise ValueError

    upper_raw_info = int(upper_emt[coordinates[::-1]])
    lower_raw_info = int(lower_emt[coordinates[::-1]])

    transitions_data = list()

    for raw_info in (upper_raw_info, lower_raw_info):
        if raw_info == no_transition:
            transitions_data.append([None, None, None])
            continue

        terrain_type_num, cover_type_num = divmod(raw_info, permutations_per_transition)
        terrain_type = data_object.eatd[terrain_type_num]
        cover_type = cover_presence[cover_type_num]

        if as_pointtype:
            terrain_type = transitions[terrain_type]["pointtype"]

        transitions_data.append(list(terrain_type.lower() if cover_type[i] else None for i in range(3)))

    return transitions_data

def set_transitions(data_object, coordinates, triangle_type: Literal["a", "b"], transitions_data):
    no_transition = get_minus_one(data_object.emt1.dtype)
    raw_infos = list()
    eatd_lowercase_list = [transition_name.lower() for transition_name in data_object.eatd]

    for layer in transitions_data:
        if layer == [None, None, None]:
            raw_infos.append(no_transition)
            continue

        assert len(set(layer) - {None}) == 1  # requirement for transitions_data
        terrain_name = [item for item in layer if item is not None][0]

        try:
            terrain_type_num = eatd_lowercase_list.index(terrain_name.lower())
        except ValueError:
            terrain_type_num = len(eatd_lowercase_list)
            eatd_lowercase_list.append(terrain_name)
            data_object.eatd.append(terrain_name)

        target_cover = tuple(item is not None for item in layer)
        cover_type_num = [k for k, v in cover_presence.items() if v == target_cover][0]

        raw_infos.append(terrain_type_num * permutations_per_transition + cover_type_num)

    match triangle_type:
        case "a": data_object.emt1[coordinates[::-1]], data_object.emt3[coordinates[::-1]] = raw_infos
        case "b": data_object.emt2[coordinates[::-1]], data_object.emt4[coordinates[::-1]] = raw_infos
        case _: raise ValueError

    return data_object

def triangle_in_bounds(data_object, coordinates, *, margin: int = 0):
    return margin <= coordinates[0] < data_object.lsiz.width  - margin and \
           margin <= coordinates[1] < data_object.lsiz.height - margin

@cache
def get_triangle_pointtype(data_object, coordinates, triangle_type: Literal["a", "b"]):
    match triangle_type:
        case "a": triangle_name = data_object.eapd[data_object.empa[coordinates[::-1]]]
        case "b": triangle_name = data_object.eapd[data_object.empb[coordinates[::-1]]]
        case _:
            raise ValueError

    for editgroup in patterns[triangle_name]["EditGroups"]:
        point_name = points_inversed.get(editgroup.lower())
        if point_name is not None:
            return point_name
    return None

@cache
def get_corner_characteristic(data_object, coordinates):
    triangles_a, triangles_b = get_adjacent_triangles(coordinates)
    characteristic = set()
    for triangle_coordinates, triangle_type in tuple(zip(triangles_a, repeat("a"))) + \
                                               tuple(zip(triangles_b, repeat("b"))):
        if not triangle_in_bounds(data_object, triangle_coordinates):
            continue

        characteristic.add(get_triangle_pointtype(data_object, triangle_coordinates, triangle_type))
    return characteristic

def get_triangle_corners_characteristics(data_object, coordinates, triangle_type: Literal["a", "b"]):
    for corner in get_triangle_corner_vertices(coordinates, triangle_type):
        yield get_corner_characteristic(data_object, corner)

def get_vertex_type_by_characteristic(characteristic, priority_order):
    for pointtype in priority_order:
        if pointtype in characteristic:
            return pointtype
    return None

def get_new_transitions(data_object, coordinates, triangle_type: Literal["a", "b"], priority_order,
                        as_pointtype: bool = False):
    # This method is not the same as what is present in the original games or editors. Those contain many visual
    # mistakes, including corruption of data on lower layers, lack of transitions near map borders, unnecessary presence
    # of transitions on top of void triangles or nearby map borders. Moreover, it is likely that the original algorithm
    # was modified between "Cultures 2: The Gates of Asgard" and newer games from the Cultures series, as the maps from
    # the aforementioned game contain invalid transitions nearby map borders such that original external editors cannot
    # recreate those invalid transitions in any way, suggesting by this that the one correct transition layout does not
    # exist either way. This function updates transitions in such a way that is meant to make them visually coherent.

    _transition_layers = 2
    transitions_data = [[None, None, None] for _ in range(_transition_layers)]

    match triangle_type:
        case "a": logic_type = int(data_object.lmpa[coordinates[::-1]])
        case "b": logic_type = int(data_object.lmpb[coordinates[::-1]])
        case _: raise ValueError

    if logic_type == logic_type_void:
        return transitions_data

    corners_characteristics = list(get_triangle_corners_characteristics(data_object, coordinates, triangle_type))

    for transitions_layer in range(_transition_layers):
        corner_types = tuple(map(lambda characteristic:
                                 get_vertex_type_by_characteristic(characteristic, priority_order),
                                 corners_characteristics))

        if len(set(corner_types)) == 1:
            break

        try: pointtype = priority_order[min(map(lambda corner_type:
                                        priority_order.index(corner_type) if corner_type is not None else float('inf'),
                                        corner_types))]
        except IndexError: break

        for _index, corner_characteristic in enumerate(corners_characteristics):

            if pointtype in corner_characteristic:
                transitions_data[transitions_layer][_index] = \
                    None if (transitions_inversed.get(pointtype.lower()) is None) else pointtype

            corners_characteristics[_index] = set(corners_characteristics[_index]) - {pointtype}

    if not as_pointtype:
        forced_choices = dict()
        for index_1, layer in enumerate(transitions_data):
            for index_2, pointtype_name in enumerate(layer):
                if transitions_inversed.get(pointtype_name) is None:
                    continue

                transitions_available = transitions_inversed[pointtype_name]

                if forced_choices.get(index_1) is None:
                    forced_choices[index_1] = randint(0, min(len(transitions_available),
                                                             transitions_per_pointtype_upper_limit) - 1)

                transitions_data[index_1][index_2] = transitions_available[forced_choices[index_1]]
    return transitions_data

def update_emt_(data_object):
    # This is not a derivation algorithm, because transitions are a primary data.
    # It also is not meant to be historically-accurate, but visually correct.

    data_object.emt1 = np.zeros(shape=data_object.lsiz.shape, dtype=np.uint8)
    data_object.emt2 = np.zeros(shape=data_object.lsiz.shape, dtype=np.uint8)
    data_object.emt3 = np.zeros(shape=data_object.lsiz.shape, dtype=np.uint8)
    data_object.emt4 = np.zeros(shape=data_object.lsiz.shape, dtype=np.uint8)

    for y, x, triangle_type in product(range(data_object.lsiz.height),
                                       range(data_object.lsiz.width),
                                       ("a", "b")):

        trans_new_data = get_new_transitions(data_object, (x, y), triangle_type, priority_lowercase, as_pointtype=False)
        data_object = set_transitions(data_object, (x, y), triangle_type, trans_new_data)

        get_triangle_pointtype.cache_clear()
        get_corner_characteristic.cache_clear()

    return data_object

def get_transitions_accuracy(data_object) -> float:

    all_transitions = 0
    correct_transitions = 0
    correct_transitions_empty = 0

    for y, x, triangle_type in product(range(data_object.lsiz.height),
                                       range(data_object.lsiz.width),
                                       ("a", "b")):

        data_old = get_current_transitions(data_object, (x, y), triangle_type, as_pointtype=True)
        data_new = get_new_transitions(data_object, (x, y), triangle_type, priority_lowercase, as_pointtype=True)
        data_empty = [[None, None, None], [None, None, None]]

        all_transitions += 1
        correct_transitions += int(data_old == data_new)
        correct_transitions_empty += int(data_old == data_new == data_empty)

    get_triangle_pointtype.cache_clear()
    get_corner_characteristic.cache_clear()

    coeff_full  = correct_transitions / all_transitions
    coeff_naive = correct_transitions_empty / all_transitions

    try:
        return ((1/(1-coeff_naive)) * coeff_full) - (coeff_naive / (1 - coeff_naive))
    except ZeroDivisionError:
        assert coeff_full == 1.0
        return 1.0

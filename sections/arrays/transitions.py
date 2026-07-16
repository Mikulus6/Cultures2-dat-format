from itertools import product, repeat
from typing import Literal
from ..generic.imports import transitions, points, patterns
from ..generic.minus_one import get_minus_one
from ..generic.geometry import get_adjacent_triangles, get_triangle_corner_vertices

# Capitalization of various names is not consistent across game files related to transitions.
# To prevent any confusion, it was decided to turn all ambigious strings into lowercase.

points_editnames_ordered_lowercase = list(map(str.lower, points.editnames_ordered))
points_inversed = {point["patterngroup"].lower() : point["name"].lower() for point in points.values()}

priority_lowercase = ('ice', 'snow', 'meadow megadark', 'meadow', 'meadow dark', 'mountain', 'swamp',
                      'concrete', 'desertbrown d', 'desertbrown c', 'desertbrown b', 'desertbrown a',
                      'desertbrown', 'mud', 'sand', 'water bright', 'water')  # Calculated using StatisticalPriority.

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

            current_transitions = get_transitions(data_object, (x, y), triangle_type, as_pointtype=True)

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


def get_transitions(data_object, coordinates, triangle_type: Literal["a", "b"], *, as_pointtype: bool = False):
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
            transitions_data.append((None, None, None))
            continue

        terrain_type_num, cover_type_num = divmod(raw_info, permutations_per_transition)
        terrain_type = data_object.eatd[terrain_type_num]
        cover_type = cover_presence[cover_type_num]

        if as_pointtype:
            terrain_type = transitions[terrain_type]["pointtype"]

        transitions_data.append(tuple(terrain_type.lower() if cover_type[i] else None for i in range(3)))

    return transitions_data

def vertex_in_bounds(data_object, coordinates):
    return 0 <= coordinates[0] < data_object.lsiz.width and \
           0 <= coordinates[1] < data_object.lsiz.height

def get_corner_characteristic(data_object, coordinates):
    a_triangles, b_triangles = get_adjacent_triangles(coordinates)

    for triangle_coordinates, triangle_type in tuple(zip(a_triangles, repeat("a"))) + \
                                               tuple(zip(b_triangles, repeat("b"))):
        if not vertex_in_bounds(data_object, triangle_coordinates):
            continue

        match triangle_type:
            case "a": triangle_name = data_object.eapd[data_object.empa[triangle_coordinates[::-1]]]
            case "b": triangle_name = data_object.eapd[data_object.empb[triangle_coordinates[::-1]]]
            case _: raise ValueError

        for editgroup in patterns[triangle_name]["EditGroups"]:
            point_name = points_inversed.get(editgroup.lower())
            if point_name is not None:
                yield point_name

def get_corner_type(data_object, coordinates, priority_order):
    corner_characteristic = set(get_corner_characteristic(data_object, coordinates))
    for point_type in priority_order:
        if point_type in corner_characteristic:
            return point_type
    return None

def get_triangle_corners_types(data_object, coordinates, triangle_type: Literal["a", "b"], priority_order):
    for corner in get_triangle_corner_vertices(coordinates, triangle_type):
        yield get_corner_type(data_object, corner, priority_order)

def get_triangle_corners_characteristics(data_object, coordinates, triangle_type: Literal["a", "b"]):
    for corner in get_triangle_corner_vertices(coordinates, triangle_type):
        yield get_corner_characteristic(data_object, corner)

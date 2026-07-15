from itertools import repeat
from typing import Literal
from ..generic.imports import transitions, points, patterns
from ..generic.minus_one import get_minus_one
from ..generic.geometry import get_adjacent_triangles, get_triangle_corner_vertices

# Capitalization of various names is not consistent across game files related to transitions.
# To prevent any confusion, it was decided to turn all ambigious strings into lowercase.

# TODO: Check what should be turned into lowercase and what can remain as original string (maybe change it to lowercase
#       only when required?) It would be cool if original capitalization was preserved after doing some operations on
#       lowercase string without the need of manually interating all of them and reverting to original capitalization.
#       Right now I just pasted some str.lower methods to make the stuff work, but I'm not sure if all of them are
#       necessary.

points_editnames_ordered_lowercase = list(map(str.lower, points.editnames_ordered))
points_inversed = {point["patterngroup"].lower() : point["name"].lower() for point in points.values()}

permutations_per_transition = 6
cover_presence = {0: (False, True,  True ),
                  1: (True,  False, True ),
                  2: (True,  True,  False),
                  3: (True,  False, False),
                  4: (False, True,  False),
                  5: (False, False, True )}

def vertex_in_bounds(data_object, coordinates):
    return 0 <= coordinates[0] < data_object.lsiz.width and \
           0 <= coordinates[1] < data_object.lsiz.height

def get_corner_characteristic(data_object, coordinates):
    a_triangles, b_triangles = get_adjacent_triangles(coordinates)

    point_names = list()
    for triangle_coordinates, triangle_type in tuple(zip(a_triangles, repeat("a"))) + \
                                               tuple(zip(b_triangles, repeat("b"))):
        if not vertex_in_bounds(data_object, triangle_coordinates):
            point_names.append(None)
            continue

        match triangle_type:
            case "a": triangle_name = data_object.eapd[data_object.empa[triangle_coordinates[::-1]]]
            case "b": triangle_name = data_object.eapd[data_object.empb[triangle_coordinates[::-1]]]
            case _: raise ValueError

        for editgroup in patterns[triangle_name]["EditGroups"]:
            point_name = points_inversed.get(editgroup.lower())
            if point_name is not None:
                point_names.append(point_name)
                break  # TODO: I'm not sure is this correct. Can a single point have multiple types?
                       #       If so, this is incorrect. If not, I should make sure that order of sections is preserved
                       #       in the initial dictionary in the first place. For now this seems to be fine, but maybe
                       #       there will be some rare exceptions encountered in the future.
        else:
            point_names.append(None)

    return point_names

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

class StatisticalPriority(dict):
    # This class is supposed to be used to determine the priority of transitions based on frequencies of occurrence of
    # different transitions in existing maps.

    def __init__(self):
        super().__init__(dict())

    def analyze(self, data_object):
        for y in range(data_object.lsiz.height):
            for x in range(data_object.lsiz.width):
                for triangle_type in ("a", "b"):
                    current_transitions = get_transitions(data_object, (x, y), triangle_type, as_pointtype=True)

                    for i, corner in enumerate(get_triangle_corner_vertices((x, y), triangle_type)):
                        corner_characteristic = get_corner_characteristic(data_object, corner)
                        current_upper_transition = current_transitions[0][i]
                        current_lower_transition = current_transitions[1][i]

                        if current_upper_transition is None and current_lower_transition is not None:
                            current_upper_transition, current_lower_transition = \
                            current_lower_transition, current_upper_transition

                        if current_upper_transition is not None and current_lower_transition is None:
                            less_important = set(corner_characteristic) - {current_upper_transition, None}
                            more_important = current_upper_transition

                            for item in less_important:
                                self.setdefault((more_important, item), 0)
                                self[more_important, item] += 1

    def is_priority_correct(self, more_important, less_important, cutoff: int = 0) -> bool:
        count_normal   = self.get((more_important, less_important), 0)
        count_reversed = self.get((less_important, more_important), 0)
        return count_normal > max(count_reversed, cutoff)

    @property
    def linear_order(self):
        # Earlier elements have higher priority.
        for cutoff in (0, *sorted(self.values())):
            dependencies = {}
            for key in self.keys():
                if not self.is_priority_correct(*key, cutoff=cutoff):
                    continue

                dependencies.setdefault(key[0], set())
                dependencies.setdefault(key[1], set()).add(key[0])

            priority_list = list()
            try:
                while dependencies:
                    print(dependencies.keys())
                    print(points_editnames_ordered_lowercase)

                    free = next(key for key in sorted(dependencies.keys(),
                                key=lambda name: points_editnames_ordered_lowercase.index(name), reverse=True)
                                if not dependencies[key])

                    # The only reason why reversed sorting is applied here above is the ambiguous priority between
                    # transitions "DesertBrown" and "DesertBrown d". Examples existing in various original maps show
                    # that "DesertBrown" should have a higher priority. However, those examples are so rare that when
                    # using cutoff to prevent cycles in the graph of priority in other existing transitions, those rare
                    # examples are being entirely removed as well in many cases. The original editor often crashes when
                    # the user is trying to apply the "DesertBrown" transition, leaving it as an experimentally
                    # unverifiable presupposition extrapolated from scarce data present in various Cultures games.

                    dependencies.pop(free)
                    for deps in dependencies.values():
                        deps.discard(free)

                    priority_list.append(free)
            except StopIteration:
                continue  # Cycle is present in priority graph. Increase edges cutoff until no cycle is found.
            break

        return priority_list

# TODO: This is the result I found after checking all unique maps from c2+c3+c4+c4 and using StatisticalPriority class:
#       ['ice', 'snow', 'meadow megadark', 'meadow', 'meadow dark', 'mountain', 'swamp', 'concrete', 'desertbrown d',
#       'desertbrown', 'desertbrown c', 'desertbrown b', 'desertbrown a', 'mud', 'sand', 'water bright', 'water']
#       I should do something with it.

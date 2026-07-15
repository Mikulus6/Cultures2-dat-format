from itertools import repeat
from typing import Literal
from ..generic.imports import transitions, points, patterns
from ..generic.minus_one import get_minus_one
from ..generic.geometry import get_adjacent_triangles, get_triangle_corner_vertices

points_inversed = {point["patterngroup"] : point["name"] for point in points.values()}

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
            case "a": triangle_info = data_object.eapd[data_object.empa[triangle_coordinates[::-1]]]
            case "b": triangle_info = data_object.eapd[data_object.empb[triangle_coordinates[::-1]]]
            case _: raise ValueError

        for editgroup in patterns[triangle_info]["EditGroups"]:
            point_name = points_inversed.get(editgroup)
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

        transitions_data.append(tuple(terrain_type if cover_type[i] else None for i in range(3)))

    return transitions_data

def trans_test_data(data_object):
    # TODO: for testing only
    for y in range(data_object.lsiz.height):
        for x in range(data_object.lsiz.width):
            for triangle_type in ("a", "b"):
                current_transitions = get_transitions(data_object, (x, y), triangle_type, as_pointtype=True)

                for i, corner in enumerate(get_triangle_corner_vertices((x, y), triangle_type)):
                    corner_characteristic = get_corner_characteristic(data_object, corner)
                    current_upper_transition = current_transitions[0][i]
                    current_lower_transition = current_transitions[1][i]

                    print(corner,
                          f"'{current_upper_transition}'" if isinstance(current_upper_transition, str) else current_upper_transition,
                          f"'{current_lower_transition}'" if isinstance(current_lower_transition, str) else current_lower_transition,
                          corner_characteristic)

                print()

                # Corner characteristic is what I can derive by now, current transition is what is present in game and
                # what I need to figure out how to derive.

                # In general current transition (upper+lower) should be derivable from 3 corner characteristics
                # If single-vertex bjection is not satisfied and one of the potential values is None, it means that all
                # three transitions would be the same, so the game ignores it and changes pattern triangle instead.

import numpy as np
from collections import deque
from sections.generic.geometry import get_neighbouring_vertices
from sections.arrays.continents import get_adjacent_logic_types, continents_logic_types_inverse

max_vehicle_size = 7

def get_adjacent_continent_types(data_object, coordinates):
    for logic_type in set(get_adjacent_logic_types(data_object, coordinates)):
        yield continents_logic_types_inverse[logic_type]

def distance_transform(input_data: np.array, value_to_fill, max_output_value, output_dtype):

    output_data = max_output_value * np.ones_like(input_data, dtype=output_dtype)
    searched = np.zeros_like(input_data, dtype=np.bool)
    starting_area = np.where(input_data != value_to_fill)
    searched[starting_area] = True
    output_data[starting_area] = 0
    queue = deque(zip(*starting_area[::-1]))

    while len(queue) > 0:
        x, y = queue.popleft()

        for x_1, y_1 in get_neighbouring_vertices((x, y)):
            if not(0 <= x_1 < input_data.shape[1]) or \
               not(0 <= y_1 < input_data.shape[0]):
                continue

            if output_data[y_1, x_1] > output_data[y, x] + 1:
                output_data[y_1, x_1] = output_data[y, x] + 1
                queue.append((x_1, y_1))

    return output_data

def moveable_block(data_object) -> np.ndarray:

    # There exists one map in the game "Cultures: Die Saga" where this derivation is incorrect. This is map "Daheim".
    # Such discrepency is caused by stockade disappearing after removing player in the external editor. This mismatch
    # is easily recreatable by placing stockade and removing player to whom it belongs in the aforementioned editor.

    moveable_array = np.zeros(data_object.lsiz.shape_micro, dtype=np.bool)

    for y in range(0, 2 * data_object.lsiz.height):
        for x in range(0, 2 * data_object.lsiz.width):
            continent_id = data_object.lmco[y, x]
            continent_type = data_object.laco[continent_id].type

            if continent_type == 0 or data_object.lmwb[y, x] or data_object.lmtw[y, x] != 0b111111:
                moveable_array[y, x] = True
                continue

            adjacent_continent_types = set(get_adjacent_continent_types(data_object, (x, y)))
            if len(adjacent_continent_types) != 1 or (adjacent_continent_types == {0}):
                moveable_array[y, x] = True
                continue

            for index_, coordinates in enumerate(get_neighbouring_vertices((x, y))):
                x_1, y_1 = coordinates
                if not (0 <= x_1 < 2 * data_object.lsiz.width) or \
                   not (0 <= y_1 < 2 * data_object.lsiz.height):
                    continue
                if continent_id != data_object.lmco[y_1, x_1] or data_object.lmwb[y_1, x_1]:
                    moveable_array[y, x] = True
                    break
    return moveable_array

def data_to_lmms(data_object):
    return distance_transform(moveable_block(data_object), False, max_vehicle_size, np.uint8)

def update_lmms(data_object):
    data_object.lmms = data_to_lmms(data_object)
    return data_object

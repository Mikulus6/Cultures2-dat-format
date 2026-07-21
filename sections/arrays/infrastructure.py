import numpy as np
from ..generic.ab_sections import combine_ab_sections, split_ab_sections
from ..generic.geometry import get_adjacent_triangles

emm_pattern_types = {3: "overlay road 1",
                     4: "overlay road 2",
                     5: "overlay house 1",
                     6: "overlay house 2"}

def emm1_to_binary(emm1: np.ndarray) -> np.ndarray:
    return combine_ab_sections(*(np.divmod(emm1, 2)[::-1]))

def binary_to_emm1(binary_sec: np.ndarray) -> np.ndarray:
    emm1_a, emm1_b = split_ab_sections(binary_sec)
    return (emm1_b * 2) + emm1_a

def emmi_to_types(emmi: np.ndarray) -> np.ndarray:
    with np.errstate(divide='ignore'):
        return np.where(emmi == 0, 0, np.log2(emmi & -emmi) + 1).astype(emmi.dtype)

def types_to_emmi(types: np.ndarray) -> np.ndarray:
    safe_powers = np.maximum(types - 1, 0)
    return np.where(types == 0, 0, types.dtype.type(2) ** safe_powers)

def types_to_binary(types: np.ndarray):

    size_y, size_x = types.shape[0] // 2, types.shape[1] // 2

    output_array_a = np.zeros((size_y, size_x), dtype=np.int32)
    output_array_b = np.zeros((size_y, size_x), dtype=np.int32)

    nonzero_indices = np.argwhere(types)

    for y, x in nonzero_indices:
        a_coords, b_coords = get_adjacent_triangles((x, y))

        for nx, ny in a_coords:
            nx_wrapped = nx % size_x
            ny_wrapped = ny % size_y
            output_array_a[ny_wrapped, nx_wrapped] = 1

        for nx, ny in b_coords:
            nx_wrapped = nx % size_x
            ny_wrapped = ny % size_y
            output_array_b[ny_wrapped, nx_wrapped] = 1

    return combine_ab_sections(output_array_a, output_array_b)

def emmi_to_emm1(emmi: np.ndarray) -> np.ndarray:
    return binary_to_emm1(types_to_binary(emmi_to_types(emmi)))

def data_to_emm1(data_object):
    return emmi_to_emm1(data_object.emmi)

def update_emm1(data_object):
    data_object.emm1 = emmi_to_emm1(data_object.emmi)
    return data_object

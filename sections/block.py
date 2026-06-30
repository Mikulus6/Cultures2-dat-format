import numpy as np
from supplements.external import landscapes
from typing import Literal

# lm_b = {lmwb, lmbb}
def data_to_lm_b(data_object, *, block_type: Literal["Walk", "Build"] = "Walk"):
    lm_b = np.zeros_like(data_object.lmwb)
    block_typ_name = f"Logic{block_type}BlockArea"

    micro_width  = 2 * data_object.lsiz.width
    micro_height = 2 * data_object.lsiz.height

    match np.issubdtype(data_object.emla.dtype, np.unsignedinteger):  # TODO: duplicated code
        case True:  minus_one = np.iinfo(data_object.emla.dtype).max
        case False: minus_one = -1

    for y in range(micro_height):
        for x in range(micro_width):
            landscape_id = data_object.emla[y, x]
            if landscape_id == minus_one:  # noqa
                continue
            landscape = landscapes[data_object.eald[landscape_id]]
            landscape_valency = data_object.lmlv[y, x]

            for valency, x_offset, y_offset, indent in landscape.get(block_typ_name, []):
                if landscape_valency < valency:
                    continue

                for x_iter in range(indent):
                    y_real = y + y_offset
                    x_real = x + x_offset + x_iter + int((y % 2 != 0) and (y_real % 2 == 0))

                    lm_b[y_real % micro_height, x_real % micro_width] = 1
    return lm_b

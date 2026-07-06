import numpy as np
from sections.arrays.common.minus_one import get_minus_one
from supplements.external import landscapes

def data_to_lmao(data_object):
    lmao = np.zeros(shape=data_object.lsiz.shape_micro, dtype=np.uint16)

    micro_width  = 2 * data_object.lsiz.width
    micro_height = 2 * data_object.lsiz.height

    no_landscape = get_minus_one(data_object.emla.dtype)

    for y in range(micro_height):
        for x in range(micro_width):
            landscape_id = data_object.emla[y, x]
            if landscape_id == no_landscape:
                continue

            landscape = landscapes[data_object.eald[landscape_id]]

            for x_offset, y_offset, indent in landscape.get("LogicAdditionalAttachPointArea", []):
                for x_iter in range(indent):
                    y_real = y + y_offset
                    x_real = x + x_offset + x_iter + int((y % 2 != 0) and (y_real % 2 == 0))

                    if 0 <= x_real < micro_width and 0 <= y_real < micro_height:
                        x_attach = x_real - x
                        y_attach = y_real - y - int(x_attach > 0)

                        lmao[y_real, x_real] = (-x_attach - (y_attach << 8)) % 0x10000
    return lmao

def update_lmao(data_object):
    data_object.lmao = data_to_lmao(data_object)
    return data_object

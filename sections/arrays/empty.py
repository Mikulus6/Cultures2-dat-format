import numpy as np

def data_to_lmhf(data_object):
    return np.zeros(shape=data_object.lsiz.shape_micro, dtype=np.uint8)

def update_lmhf(data_object):
    data_object.lmhf = data_to_lmhf(data_object)
    return data_object

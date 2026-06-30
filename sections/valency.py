import numpy as np
from supplements.external import landscapes

def data_to_maximum_lmlv(data_object):
    match np.issubdtype(data_object.emla.dtype, np.unsignedinteger):  # TODO: duplicated code
        case True:  minus_one = np.iinfo(data_object.emla.dtype).max
        case False: minus_one = -1

    def func(landscape_id):
        if landscape_id == minus_one: return 0
        else: return landscapes[data_object.eald[landscape_id]]["LogicMaximumValency"]

    return np.vectorize(func)(data_object.emla).astype(data_object.lmlv.dtype)

def update_lmlv_to_maximum(data_object):
    data_object.lmlv = data_to_maximum_lmlv(data_object)
    return data_object

def check_lmlv_limits(data_object):
    return np.all(data_to_maximum_lmlv(data_object) >= data_object.lmlv)

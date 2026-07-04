import numpy as np
from sections.common.minus_one import get_minus_one
from supplements.external import patterns, landscapes

def data_to_lmp_(data_object):
    func = lambda pattern_id: patterns[data_object.eapd[pattern_id]]["LogicType"]
    lmpa = np.vectorize(func)(data_object.empa).astype(data_object.lmpa.dtype)
    lmpb = np.vectorize(func)(data_object.empb).astype(data_object.lmpb.dtype)
    return lmpa, lmpb

def update_lmp_(data_object):
    data_object.lmpa, data_object.lmpb = data_to_lmp_(data_object)
    return data_object

def data_to_lmlt(data_object):
    minus_one = get_minus_one(data_object.emla.dtype)
    def func(landscape_id):
        if landscape_id != minus_one: return landscapes[data_object.eald[landscape_id]]["LogicType"]
        else:                         return 0
    lmlt = np.vectorize(func)(data_object.emla).astype(data_object.emla.dtype)
    return lmlt

def update_lmlt(data_object):
    data_object.lmlt = data_to_lmlt(data_object)
    return data_object

import numpy as np
from supplements.external import patterns

def data_to_lmp(data_object):
    func = lambda pattern_id: patterns[data_object.eapd[pattern_id]]["LogicType"]
    lmpa = np.vectorize(func)(data_object.empa).astype(data_object.lmpa.dtype)
    lmpb = np.vectorize(func)(data_object.empb).astype(data_object.lmpb.dtype)
    return lmpa, lmpb

def update_lmp(data_object):
    data_object.lmpa, data_object.lmpb = data_to_lmp(data_object)
    return data_object

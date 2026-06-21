import numpy as np

def combine_emp(empa, empb):
    empa = np.asarray(empa)
    empb = np.asarray(empb)

    emp = np.empty((empa.shape[0], empa.shape[1] * 2), dtype=empa.dtype)

    emp[:, 0::2] = empa
    emp[:, 1::2] = empb

    return emp

def split_emp(emp):
    emp = np.asarray(emp)

    empa = emp[:, 0::2]
    empb = emp[:, 1::2]

    return empa, empb

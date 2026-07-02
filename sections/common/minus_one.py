import numpy as np

def get_minus_one(dtype):
    if np.issubdtype(dtype, np.unsignedinteger): return np.iinfo(dtype).max
    else:                                        return -1

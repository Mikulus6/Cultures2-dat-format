import numpy as np

def combine_ab_sections(a_sec: np.ndarray, b_sec: np.ndarray):
    sec = np.empty((a_sec.shape[0], a_sec.shape[1] * 2), dtype=a_sec.dtype)
    sec[:, 0::2] = a_sec
    sec[:, 1::2] = b_sec
    return sec

def split_ab_sections(sec):
    sec = np.asarray(sec)
    return sec[:, 0::2], \
           sec[:, 1::2]

import numpy as np

def emmi_to_lmro(emmi: np.ndarray) -> np.ndarray:
    return np.where(emmi != 0, 1, 0).astype(emmi.dtype)

def data_to_lmro(data_object):
    return emmi_to_lmro(data_object.emmi)

def update_lmro(data_object):
    data_object.lmro = emmi_to_lmro(data_object.emmi)
    return data_object

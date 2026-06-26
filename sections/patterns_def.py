import copy
import numpy as np
from sections.mesh_points import combine_emp, split_emp
from special.texts import TextSection
from supplements.patterns import pattern

eapd_global = TextSection(list_=pattern.editnames_ordered)

def derive_pattern_defs(data_object):
    emp_combined = combine_emp(data_object.empa, data_object.empb)
    emp_texts = np.asarray(data_object.eapd)[emp_combined]

    data_object.eapd = copy.copy(eapd_global)
    emp_combined_new = np.vectorize({v: i for i, v in enumerate(data_object.eapd)}.__getitem__)(emp_texts)
    empa_new, empb_new = split_emp(emp_combined_new)
    data_object.empa = empa_new
    data_object.empb = empb_new

    return data_object

def simplify_pattern_defs(data_object):

    emp_combined = combine_emp(data_object.empa, data_object.empb)
    emp_texts = np.asarray(data_object.eapd)[emp_combined]
    eapd_texts, emp_combined_new = np.unique(emp_texts, return_inverse=True)
    empa_new, empb_new = split_emp(emp_combined_new.reshape(emp_texts.shape))

    data_object.eapd = TextSection(list_=eapd_texts)
    data_object.empa = empa_new.astype(data_object.empa.dtype)
    data_object.empb = empb_new.astype(data_object.empb.dtype)

    return data_object

def substitute_pattern_defs(data_object, eapd_new: TextSection):

    emp_combined = combine_emp(data_object.empa, data_object.empb)
    emp_texts = np.asarray(data_object.eapd)[emp_combined]
    emp_combined_new = np.array([eapd_new.index(text) for text in emp_texts.flatten()]).reshape(emp_texts.shape)
    empa_new, empb_new = split_emp(emp_combined_new)

    data_object.eapd = eapd_new
    data_object.empa = empa_new.astype(data_object.empa.dtype)
    data_object.empb = empb_new.astype(data_object.empb.dtype)

    return data_object

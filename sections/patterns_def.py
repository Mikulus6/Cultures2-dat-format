import numpy as np
from sections.mesh_points import combine_emp, split_emp
from special.texts import TextSection
from supplements.patterns import pattern

def derive_pattern_defs(data_object):
    emp_combined = combine_emp(data_object.empa, data_object.empb)
    emp_texts = np.asarray(data_object.eapd)[emp_combined]

    data_object.eapd = TextSection(list_=pattern.editnames_ordered)

    emp_combined_new = np.vectorize({v: i for i, v in enumerate(data_object.eapd)}.__getitem__)(emp_texts)
    empa_new, empb_new = split_emp(emp_combined_new)
    data_object.empa = empa_new
    data_object.empb = empb_new

    return data_object

def simplify_pattern_defs(data_object):

    # TODO: This function is not yet completed. There are some more sections than empa and empb that are dependent on
    #       eapd, so more corrections are required when wanting to simplify eapd (and we want to make at some point
    #       this function work, because that reduces memory used by *.dat file). After this fix, NotImplementedError
    #       can be removed from this function. Section eapd remains in progres until this function is finished)

    raise NotImplementedError

    # emp_combined = combine_emp(data_object.empa, data_object.empb)
    # emp_texts = np.asarray(data_object.eapd)[emp_combined]
    # eapd_texts, emp_combined_new = np.unique(emp_texts, return_inverse=True)
    # empa_new, empb_new = split_emp(emp_combined_new.reshape(emp_texts.shape))
    #
    # data_object.eapd = TextSection(list_=eapd_texts)
    # data_object.empa = empa_new
    # data_object.empb = empb_new
    #
    # return data_object

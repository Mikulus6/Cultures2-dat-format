import copy
import numpy as np
from sections.ab_sections import combine_ab_sections, split_ab_sections
from special.texts import TextSection
from supplements.external import patterns

eapd_global = TextSection(list_=patterns.editnames_ordered)

def update_patterns(data_object, eapd_new: TextSection | list | None = None):
    emp = combine_ab_sections(data_object.empa, data_object.empb)
    emp_texts = np.asarray(data_object.eapd)[emp]

    if eapd_new is None:  # If eapd_new is not specified, then generate new optimum eapd content.
        eapd_new, emp_new = np.unique(emp_texts, return_inverse=True)
        emp_new = emp_new.reshape(emp_texts.shape)
    else:                 # If eapd_new is specified, substitute numerical values to fit that new eapd.
        emp_new = np.vectorize({v: i for i, v in enumerate(eapd_new)}.__getitem__)(emp_texts)

    empa_new, empb_new = split_ab_sections(emp_new)
    data_object.eapd = TextSection(list_=eapd_new)
    data_object.empa = empa_new.astype(data_object.empa.dtype)
    data_object.empb = empb_new.astype(data_object.empb.dtype)

    return data_object

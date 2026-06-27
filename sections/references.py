import copy
import numpy as np
from sections.ab_sections import combine_ab_sections, split_ab_sections
from special.texts import TextSection
from supplements.external import patterns, landscapes

eapd_global = TextSection(list_=patterns.editnames_ordered)
eald_global = TextSection(list_=landscapes.editnames_ordered)

def update_external_assets_references(array_section: np.ndarray,
                                      text_section_old: list, text_section_new: list | None = None):

    minus_one = np.iinfo(array_section.dtype).max if np.issubdtype(array_section.dtype, np.unsignedinteger) else -1
    mask = (array_section == minus_one)

    array_texts = np.asarray(text_section_old)[np.where(mask, 0, array_section)]
    array_texts[mask] = ""

    if text_section_new is None:  # If text_section_new is not specified, then generate new optimum content of it.
        text_section_new, array_section_new = np.unique(array_texts, return_inverse=True)
        array_section_new = array_section_new.reshape(array_texts.shape)

    else:                         # If text_section_new is specified, substitute numerical values deterministically.
        bijection = {v: k for k, v in enumerate(text_section_new)}
        array_section_new = np.vectorize(lambda x: bijection.get(x, minus_one))(array_texts)

    return array_section_new.astype(array_section.dtype), TextSection(list_=text_section_new)

def update_patterns(data_object, eapd_new: list | None = None):
    emp = combine_ab_sections(data_object.empa, data_object.empb)
    emp_new, data_object.eapd = update_external_assets_references(emp, data_object.eapd, eapd_new)
    empa_new, empb_new = split_ab_sections(emp_new)
    data_object.empa = empa_new.astype(data_object.empa.dtype)
    data_object.empb = empb_new.astype(data_object.empb.dtype)
    return data_object

def update_landscapes(data_object, eald_new: list | None = None):
    data_object.emla, data_object.eald = update_external_assets_references(data_object.emla, data_object.eald, eald_new)
    return data_object

def update_transitions(data_object, eatd_new: list | None = None):

    # This is just a technical combination. Such combination does not represent human-readable array.
    emt = combine_ab_sections(combine_ab_sections(data_object.emt1, data_object.emt2),
                              combine_ab_sections(data_object.emt3, data_object.emt4))

    # emt1 - foreground transitions A
    # emt2 - foreground transitions B
    # emt3 - background transitions A
    # emt4 - background transitions B

    minus_one = 255
    transition_types_num = 6  # In how many ways is it possible to choose vertices of a triangle, excluding choosing all
                              # of them or none of them. This is how many different types of transitions there are.

    mask = (emt == minus_one)
    emt, transition_types_array = np.divmod(emt, transition_types_num)
    emt[mask] = minus_one
    transition_types_array[mask] = 0

    emt_new, data_object.eatd = update_external_assets_references(emt, data_object.eatd, eatd_new)

    emt[mask] = minus_one // transition_types_num
    emt_new = (emt_new * transition_types_num) + transition_types_array

    emt12_new, emt34_new = split_ab_sections(emt_new)
    emt1_new, emt2_new = split_ab_sections(emt12_new)
    emt3_new, emt4_new = split_ab_sections(emt34_new)

    data_object.emt1, data_object.emt2, data_object.emt3, data_object.emt4 = \
        emt1_new.astype(data_object.emt1.dtype), emt2_new.astype(data_object.emt2.dtype), \
        emt3_new.astype(data_object.emt3.dtype), emt4_new.astype(data_object.emt3.dtype)

    return data_object

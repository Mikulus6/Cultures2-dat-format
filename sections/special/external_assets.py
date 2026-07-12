import numpy as np
from sections.generic.ab_sections import combine_ab_sections, split_ab_sections
from sections.generic.external_inis import patterns, landscapes
from sections.generic.minus_one import get_minus_one
from sections.special.texts import TextSection

eapd_global = TextSection(list_=patterns.editnames_ordered)
eald_global = TextSection(list_=landscapes.editnames_ordered)

def update_external_assets_references(array_section: np.ndarray,
                                      text_section_old: list, text_section_new: list | None = None):

    minus_one = get_minus_one(array_section.dtype)

    mask = (array_section == minus_one)

    array_texts = np.asarray(text_section_old)[np.where(mask, 0, array_section)]
    array_texts[mask] = ""

    if text_section_new is None:  # If text_section_new is not specified, then generate new optimum content of it.
        text_section_new, array_section_new = np.unique(array_texts, return_inverse=True)
        if "" in text_section_new:
            text_section_new = text_section_new[1:]
            array_section_new = np.where(array_section_new == 0, minus_one, array_section_new - 1)
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
    emt = combine_ab_sections(combine_ab_sections(data_object.emt1, data_object.emt3),  # transitions A
                              combine_ab_sections(data_object.emt2, data_object.emt4))  # transitions B
    # 1, 2 -> foreground
    # 3, 4 -> background

    no_transition = get_minus_one(data_object.emt1.dtype)

    transition_types_num = 6  # In how many ways is it possible to choose vertices of a triangle, excluding choosing all
                              # of them or none of them. This is how many different types of transitions there are.

    mask = (emt == no_transition)  # noqa
    emt, transition_types_array = np.divmod(emt, transition_types_num)
    emt[mask] = no_transition
    transition_types_array[mask] = 0

    emt_new, data_object.eatd = update_external_assets_references(emt, data_object.eatd, eatd_new)

    emt_new = (emt_new * transition_types_num) + transition_types_array
    emt_new[mask] = no_transition

    emt_a_new, emt_b_new = split_ab_sections(emt_new)
    emt1_new, emt3_new = split_ab_sections(emt_a_new)
    emt2_new, emt4_new = split_ab_sections(emt_b_new)

    data_object.emt1, data_object.emt2, data_object.emt3, data_object.emt4 = \
        emt1_new.astype(data_object.emt1.dtype), emt2_new.astype(data_object.emt2.dtype), \
        emt3_new.astype(data_object.emt3.dtype), emt4_new.astype(data_object.emt3.dtype)

    return data_object

def update_ea_d(data_object,
                eapd_new: list | None = None,
                eatd_new: list | None = None,
                eald_new: list | None = None):

    data_object = update_patterns   (data_object, eapd_new)
    data_object = update_transitions(data_object, eatd_new)
    data_object = update_landscapes (data_object, eald_new)

    return data_object

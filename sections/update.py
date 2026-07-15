from .arrays.valency import check_lmlv_limits
from .parameters import sections_optional, sections_primary, derivations_dependencies, update_functions
from .special.external_assets import update_ea_d

def get_sections_with_common_update_function(update_funcs):
    return tuple(tuple(k for k, v in update_funcs.items() if v == val) for val in set(update_funcs.values()))

def get_linear_order(sources, dependencies_dict, update_funcs) -> list:
    common_update_functions = list(get_sections_with_common_update_function(update_funcs))
    updated_dict = {key: False for key in dependencies_dict.keys()}
    updated_dict.update({source: True for source in sources})

    while False in updated_dict.values():
        looped = True
        for successor, predecessors in dependencies_dict.items():
            if not updated_dict[successor] and False not in (updated_dict[predecessor] for predecessor in predecessors):
                updated_dict[successor] = True
                looped = False

                for index_, subiterable in enumerate(common_update_functions):
                    if successor in subiterable:
                        index_to_remove = index_
                        break
                else:
                    continue
                yield successor
                common_update_functions.pop(index_to_remove)

        if looped:
            raise ValueError # Cycle is present in dependency graph.

update_order = list(get_linear_order(sections_primary, derivations_dependencies, update_functions))

def update(data_object):
    assert check_lmlv_limits(data_object)
    data_object = update_ea_d(data_object)  # This one update is only to reduce memory usage.
    for section_name in update_order:
        if section_name in sections_optional and getattr(data_object, section_name) is None: continue
        data_object = update_functions[section_name](data_object)
    return data_object

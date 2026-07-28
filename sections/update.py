from functools import cache
from .parameters import sections_optional, sections_primary, derivations_dependencies, update_functions

@cache
def get_all_predecessors(section_name: str) -> set:
    predecessors_set = set()
    for predecessor in derivations_dependencies.get(section_name, ()):
        predecessors_set.update({predecessor})
        predecessors_set.update(get_all_predecessors(predecessor))
    return predecessors_set

def get_sections_with_common_update(update_funcs: dict) -> list:
    result = []

    for unique_func in set(update_funcs.values()):
        sections = [[]]
        matching = [section for section, func in update_funcs.items() if func == unique_func]

        for section in matching:
            for group in sections:
                conflict = any((item in get_all_predecessors(section) or
                                section in get_all_predecessors(item)) and
                               (item not in derivations_dependencies.get(section, ()) and
                                section not in derivations_dependencies.get(item, ()))
                                for item in group)
                # Two sections cannot be updated together if one of them is an indirect predecessor of the other one.
                # On the other hand, if they are in a direct line of precedence, and they share a common update
                # function, such a function most likely takes that precedence into consideration, and so they can be
                # updated together.
                if not conflict:
                    group.append(section)
                    break
            else:
                sections.append([section])

        result.extend(sections)

    return result

def get_update_order(sources, dependencies_dict, update_funcs) -> list:
    common_update_functions = list(get_sections_with_common_update(update_funcs))
    updated_dict = {key: False for key in dependencies_dict.keys()}
    updated_dict.update({source: True for source in sources if source not in dependencies_dict.keys()})

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
            raise ValueError # Cycle is present in the dependency graph.

update_order = list(get_update_order(sections_primary, derivations_dependencies, update_functions))

def update(data_object, *, refresh_primary: bool = False):

    for section_name in update_order:
        if not (section_name in sections_primary and not refresh_primary) and \
           not (section_name in sections_optional and getattr(data_object, section_name) is None):

            data_object = update_functions[section_name](data_object)

    return data_object

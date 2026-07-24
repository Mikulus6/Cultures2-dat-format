from itertools import count
from supplements import BufferGiver, BufferTaker  # noqa,  used by other files
from supplements.parser import parse_ini_file


class ExternalAssets(dict):
    def __init__(self, cif_path: str, section_name: str, key_name: str, entries_duplicated: tuple = tuple(),
                 merge_duplicates: bool = False):

        super().__init__(
            parse_ini_file(cif_path,
                           allowed_section_names=section_name,
                           entries_duplicated=entries_duplicated,
                           global_key=lambda x: x[key_name],
                           merge_duplicates=merge_duplicates))

        assets_count = count()
        assets_dict = \
            parse_ini_file(cif_path,
                           allowed_section_names=section_name,
                           entries_duplicated=entries_duplicated,
                           global_key=lambda x: next(assets_count),
                           merge_duplicates=merge_duplicates)

        self.editnames_ordered = [assets_dict[i][key_name] for i in range(len(assets_dict))]
        del assets_count, assets_dict


patterns_path    = "data\\engine2d\\inis\\patterns\\pattern.cif"
transitions_path = "data\\engine2d\\inis\\patterntransitions\\transitions.cif"
landscapes_path  = "data\\engine2d\\inis\\landscapes\\landscapes.cif"

patterns_entries_keys_duplicated    = ("EditGroups",)
points_entries_keys_duplicated      = ()
transitions_entries_keys_duplicated = ("GfxCoordsA", "GfxCoordsB")
landscapes_entries_keys_duplicated  = ("LogicWalkBlockArea", "LogicBuildBlockArea", "LogicWorkArea",
                                       "LogicAdditionalAttachPointArea", "GfxFrames", "GfxTransition")

try:
    patterns    = ExternalAssets(patterns_path,
                                 section_name="GfxPattern",
                                 key_name="EditName",
                                 entries_duplicated=patterns_entries_keys_duplicated,
                                 merge_duplicates=True)

    points      = ExternalAssets(transitions_path,
                                 section_name="pointtype",
                                 key_name="name",
                                 entries_duplicated=points_entries_keys_duplicated,
                                 merge_duplicates=False)

    transitions = ExternalAssets(transitions_path,
                                 section_name="transition",
                                 key_name="name",
                                 entries_duplicated=transitions_entries_keys_duplicated,
                                 merge_duplicates=False)

    landscapes  = ExternalAssets(landscapes_path,
                                 section_name="GfxLandscape",
                                 key_name="EditName",
                                 entries_duplicated=landscapes_entries_keys_duplicated,
                                 merge_duplicates=False)
except FileNotFoundError:
    raise FileNotFoundError("Unable to find game files in the current working directory.")

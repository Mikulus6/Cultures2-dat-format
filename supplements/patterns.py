from scripts.data_loader import load_ini_as_dict
from itertools import count

patterns_path = "data\\engine2d\\inis\\patterns\\pattern.ini"  # TODO: should work for .cif without reading the damn library


class Pattern(dict):
    def __init__(self, cif_path: str = patterns_path):

        super().__init__(
            load_ini_as_dict(patterns_path,
                             allowed_section_names="GfxPattern",
                             entries_duplicated=tuple(),
                             global_key = lambda x: x["EditName"],
                             merge_duplicates=False))

        patterns_count = count()
        patterns_dict = \
            load_ini_as_dict(patterns_path,
                             allowed_section_names="GfxPattern",
                             entries_duplicated=tuple(),
                             global_key=lambda x: next(patterns_count),
                             merge_duplicates=False)

        self.editnames_ordered = [patterns_dict[i]["EditName"] for i in range(len(patterns_dict))]
        del patterns_count, patterns_dict

pattern = Pattern(patterns_path)

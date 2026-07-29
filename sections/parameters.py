from .arrays.attach           import update_lmao
from .arrays.block            import update_lm_b, update_lmsb
from .arrays.brightness       import update_embr
from .arrays.continents       import update_lmco_laco
from .arrays.empty            import update_lmhf
from .arrays.infrastructure   import update_emm1
from .arrays.logic_type       import update_lmlt, update_lmp_
from .arrays.moveable_size    import update_lmms
from .arrays.roads            import update_lmro
from .arrays.roughness        import update_lmpr
from .arrays.transitions      import update_emt_
from .arrays.travel_way       import update_lmtw
from .special.continents      import Continents
from .special.external_assets import update_eald, update_eapd, update_eatd
from .special.fishes          import Fishes
from .special.size            import Size, update_lsiz
from .special.walk_sectors    import WalkSectors, update_lasw



section_names = \
    ("logi", "lgmm", "lsiz", "lmhe", "lmpa", "lmpb", "lmlt", "lmlv", "lmlp", "lmco", "lmtw", "lmms", "lmpr",
     "lmwb", "lmbb", "lmro", "lmsb", "lmao", "laco", "lasw", "lafm", "lmhf", "emmm", "embr", "emm1", "emmi",
     "eapd", "empa", "empb", "eatd", "emt1", "emt2", "emt3", "emt4", "eald", "emla", "emvc", "xend", "tend")

section_matrices = \
    {"lmhe": (1, 1), "lmpa": (1, 1), "lmpb": (1, 1), "lmlt": (1, 2), "lmlv": (1, 2), "lmlp": (1, 2),
     "lmco": (1, 2), "lmtw": (1, 2), "lmms": (1, 2), "lmpr": (1, 2), "lmwb": (1, 2), "lmbb": (1, 2),
     "lmro": (1, 2), "lmsb": (1, 2), "lmao": (2, 2), "lmhf": (1, 2), "embr": (1, 1), "emm1": (1, 1),
     "emmi": (1, 2), "empa": (2, 1), "empb": (2, 1), "emt1": (1, 1), "emt2": (1, 1), "emt3": (1, 1),
     "emt4": (1, 1), "emla": (2, 2), "emvc": (1, 1)}  # name: (bytes_per_vertex, width_multiplier)

section_type_empty     = 0
section_type_default   = 1
sections_optional      = {"lmhf", "emvc"}
sections_texts         = {"eapd", "eatd", "eald"}
sections_empty         = {"logi", "lgmm", "emmm", "xend", "tend"}
sections_types_special = {"lafm": 2, "lasw": 4}

section_special = \
    {"lsiz": Size,
     "laco": Continents,
     "lasw": WalkSectors,
     "lafm": Fishes}

sections_primary = \
    {"lsiz", "lmhe", "lmlv", "lmlp", "lafm", "emmi", "eapd", "empa", "empb",
     "eatd", "emt1", "emt2", "emt3", "emt4", "eald", "emla", "emvc"}

# some primary but can be refreshed based on other sections.
derivations_dependencies = \
    {"lsiz": {"empa"},
     "lmpa": {"lsiz", "eapd", "empa"},
     "lmpb": {"lsiz", "eapd", "empb"},
     "lmlt": {"lsiz", "eald", "emla"},
     "lmco": {"lsiz", "lmpa", "lmpb"},
     "lmtw": {"lsiz", "lmpa", "lmpb"},
     "lmms": {"lsiz", "lmpa", "lmpb", "lmco", "lmtw", "lmwb", "laco"},
     "lmpr": {"lsiz", "lmpa", "lmpb", "lmco", "lmro", "laco"},
     "lmwb": {"lsiz", "eald", "emla"},
     "lmbb": {"lsiz", "eald", "emla"},
     "lmro": {"lsiz", "emmi"},
     "lmsb": {"lsiz", "lasw"},
     "lmao": {"lsiz", "eald", "emla"},
     "laco": {"lsiz", "lmco"},
     "lasw": {"lsiz", "lmco", "lmtw", "lmms", "lmwb", "laco"},
     "lmhf": {"lsiz"},
     "embr": {"lsiz", "lmhe", "eapd", "empa", "empb"},
     "emm1": {"lsiz", "emmi"},
     "eapd": {"empa", "empb"},
     "eatd": {"emt1", "emt2", "emt3", "emt4"},
     "emt1": {"lsiz", "lmpa", "lmpb", "eapd", "empa", "empb"},
     "emt2": {"lsiz", "lmpa", "lmpb", "eapd", "empa", "empb"},
     "emt3": {"lsiz", "lmpa", "lmpb", "eapd", "empa", "empb"},
     "emt4": {"lsiz", "lmpa", "lmpb", "eapd", "empa", "empb"},
     "eald": {"emla"}}

update_functions = \
    {"lsiz": update_lsiz,
     "lmpa": update_lmp_,
     "lmpb": update_lmp_,
     "lmlt": update_lmlt,
     "lmco": update_lmco_laco,
     "lmtw": update_lmtw,
     "lmms": update_lmms,
     "lmpr": update_lmpr,
     "lmwb": update_lm_b,
     "lmbb": update_lm_b,
     "lmro": update_lmro,
     "lmsb": update_lmsb,
     "lmao": update_lmao,
     "laco": update_lmco_laco,
     "lasw": update_lasw,
     "lmhf": update_lmhf,
     "embr": update_embr,
     "emm1": update_emm1,
     "eapd": update_eapd,
     "eatd": update_eatd,
     "emt1": update_emt_,
     "emt2": update_emt_,
     "emt3": update_emt_,
     "emt4": update_emt_,
     "eald": update_eald,}

assert update_functions.keys() == derivations_dependencies.keys()
assert set.union(sections_empty, sections_primary, derivations_dependencies) == set(section_names)

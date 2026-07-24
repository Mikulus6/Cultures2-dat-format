from .generic.checksum   import calculate_checksum
from .generic.run_length import run_length_decryption, run_length_encryption
from .parameters         import sections_empty, section_names, section_matrices, sections_texts, sections_optional, \
                                section_special, section_type_default, sections_types_special
from .primary            import Vertex, get_vertex, set_vertex
from .special.size       import Size
from .special.special    import SpecialSection
from .special.texts      import TextSection
from .update             import update

assert all(isinstance(section_special_class, SpecialSection) for section_special_class in section_special.values())
assert isinstance(TextSection, SpecialSection)

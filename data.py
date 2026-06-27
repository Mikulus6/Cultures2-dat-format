import os
import numpy as np
from scripts.buffer import BufferGiver, BufferTaker
from special.common.checksum import calculate_checksum
from special.common.run_length import run_length_decryption, run_length_encryption
from special.continents import Continents
from special.fishes import Fishes
from special.size import Size
from special.special import SpecialSection
from special.texts import TextSection
from special.walk_sectors import WalkSectors
from scripts.image import bytes_to_image, shorts_to_image, image_to_bytes, image_to_shorts
from supplements.library import Library


class Data:

    _sections_empty = {"logi", "lgmm", "emmm", "xend", "tend"}

    _section_names = ("logi", "lgmm", "lsiz", "lmhe", "lmpa", "lmpb", "lmlt", "lmlv", "lmlp", "lmco", "lmtw", "lmms",
                      "lmpr", "lmwb", "lmbb", "lmro", "lmsb", "lmao", "laco", "lasw", "lafm", "lmhf", "emmm", "embr",
                      "emm1", "emmi", "eapd", "empa", "empb", "eatd", "emt1", "emt2", "emt3", "emt4", "eald", "emla",
                      "emvc", "xend", "tend")

    # name: [bytes_per_vertex, width_multiplicator]
    _section_matrices = {"lmhe": [1, 1], "lmpa": [1, 1], "lmpb": [1, 1], "lmlt": [1, 2], "lmlv": [1, 2], "lmlp": [1, 2],
                         "lmco": [1, 2], "lmtw": [1, 2], "lmms": [1, 2], "lmpr": [1, 2], "lmwb": [1, 2], "lmbb": [1, 2],
                         "lmro": [1, 2], "lmsb": [1, 2], "lmao": [2, 2], "lmhf": [1, 2], "embr": [1, 1], "emm1": [1, 1],
                         "emmi": [1, 2], "empa": [2, 1], "empb": [2, 1], "emt1": [1, 1], "emt2": [1, 1], "emt3": [1, 1],
                         "emt4": [1, 1], "emla": [2, 2], "emvc": [1, 1]}

    _section_texts =    {"eapd", "eatd", "eald"}
    _section_optional = {"lmhf", "emvc"}

    _section_special = {"lsiz": Size,
                        "laco": Continents,
                        "lasw": WalkSectors,
                        "lafm": Fishes}

    _section_type_default = 1
    _section_types_special = {"logi": 0, "lgmm": 0, "emmm": 0, "xend": 0, "tend": 0, "lafm": 2, "lasw": 4}

    assert all(isinstance(section_special_class, SpecialSection) for section_special_class in _section_special.values())
    assert isinstance(TextSection, SpecialSection)

    def __init__(self):

        for name in set(self.__class__._section_names) - set(self.__class__._sections_empty):
            setattr(self, name, None)

    def load(self, filename: str):

        match filename.lower().split(".")[-1]:
            case "dat":
                with open(filename, "rb") as file:
                    buffer = BufferGiver(file.read())
            case "c2m":
                library = Library()
                library.load(filename, cultures_1=False)
                buffer = BufferGiver(library["currentusermap\\map.dat"])
                del library

        while len(buffer) != 0:
            assert buffer.string(length=4, encoding="ascii")[::-1] == "xioh"  # "x input-output handler"
            name = buffer.string(length=4, encoding="ascii")[::-1]
            assert name in self.__class__._section_names

            section_type = buffer.unsigned(length=4)
            length = buffer.unsigned(length=4)

            assert self.__class__._get_section_type(name) == section_type

            assert buffer.unsigned(length=4) == 0
            checksum = buffer.unsigned(length=4)
            assert buffer.unsigned(length=8) == 0

            section_buffer = BufferGiver(buffer.bytes(length=length))

            assert checksum == calculate_checksum(bytes(section_buffer))

            if section_type == 0:  # empty sections
                assert name in self.__class__._sections_empty
                assert length == 0

            elif name in self.__class__._section_matrices.keys():
                assert self.lsiz.width  is not None and\
                       self.lsiz.height is not None

                match self.__class__._section_matrices[name][0]:
                    case 1: ndarray_dtype = np.uint8
                    case 2: ndarray_dtype = np.uint16
                    case _: raise ValueError

                size_multiplicator = self.__class__._section_matrices[name][1]
                section_ndarray = np.frombuffer(run_length_decryption(bytes(section_buffer)),
                                                dtype=ndarray_dtype).reshape(self.lsiz.height * size_multiplicator,
                                                                             self.lsiz.width  * size_multiplicator)
                setattr(self, name, section_ndarray)

            elif name in self.__class__._section_texts:
                text_section = TextSection()
                text_section.load(section_buffer)
                setattr(self, name, text_section)

            else:
                assert name in self._section_special.keys()
                setattr(self, name, self._section_special[name]())
                getattr(self, name).load(section_buffer)

        # optional sections, not present in some versions of Cultures 2
        assert set(key for key in self.__dict__
                   if getattr(self, key) is None).issubset(self.__class__._section_optional)

    def save(self, filename: str):
        buffer_taker = BufferTaker()

        names_ordered = [name for name in self.__class__._section_names if name[0] == "l"] + ["xend"] + \
                        [name for name in self.__class__._section_names if name[0] == "e"] + ["xend", "tend"]

        for name in names_ordered:

            section_existence = getattr(self, name, None) is not None

            if not section_existence and name in self.__class__._section_optional:
                continue

            buffer_taker.string("xioh"[::-1])
            buffer_taker.string(name[::-1])

            if not section_existence or (self.__class__._get_section_type(name) == 0):
                buffer_taker.unsigned(0, length=24)

            else:

                section_bytes = self.get_section_bytes(name)
                checksum = calculate_checksum(section_bytes)

                buffer_taker.unsigned(self.__class__._get_section_type(name), length=4)
                buffer_taker.unsigned(len(section_bytes), length=4)
                buffer_taker.unsigned(0, length=4)
                buffer_taker.unsigned(checksum, length=4)
                buffer_taker.unsigned(0, length=8)
                buffer_taker.bytes(section_bytes)

        if os.path.dirname(filename) != "":
            os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "wb") as file:
            file.write(bytes(buffer_taker))

    def extract(self, directory: str):

        os.makedirs(directory, exist_ok=True)

        for name, params in self.__class__._section_matrices.items():
            section_ndarray = getattr(self, name)

            if section_ndarray is None:
                continue

            match section_ndarray.dtype:
                case np.uint8:  assert params[0] == 1; to_image_func = bytes_to_image
                case np.uint16: assert params[0] == 2; to_image_func = shorts_to_image
                case _: raise TypeError

            to_image_func(section_ndarray.tobytes(), os.path.join(directory, f"{name}.png"),
                          width=self.lsiz.width * params[1])

        for name in self.__class__._section_texts:
            text_section = getattr(self, name)
            text_section.to_file(os.path.join(directory, f"{name}.txt"))

        for name in self._section_special.keys():
            getattr(self, name).to_file(os.path.join(directory, f"{name}.csv"))

        # TODO: this is temporary for further interpetation - not direct data
        # self.lasw.draw_data(self, os.path.join(directory, "lasw_edges_land.png"))
        # self.lasw.draw_data(self, os.path.join(directory, "lasw_edges_water.png"), water=True)

    def pack(self, directory: str):

        self.lsiz = Size()  # noqa, precaculate map size
        assert min(self._section_matrices.values(), key=lambda x: x[1])[1] == 1
        minimal_width_section_name = min(self._section_matrices, key=lambda x: x[1])
        image_bytes, self.lsiz.width = image_to_bytes(os.path.join(directory, f"{minimal_width_section_name}.png"),
                                                     get_width=True)
        self.lsiz.height = len(image_bytes) // self.lsiz.width

        for name, params in self.__class__._section_matrices.items():

            match self._section_matrices[name][0]:
                case 1: section_ndarray_dtype = np.uint8;  from_image_func_temp = image_to_bytes
                case 2: section_ndarray_dtype = np.uint16; from_image_func_temp = image_to_shorts
                case _: raise TypeError

            from_image_func = lambda path: np.frombuffer(from_image_func_temp(path),
                                                         dtype=section_ndarray_dtype).reshape(
                self.lsiz.height * self._section_matrices[name][1],
                self.lsiz.width  * self._section_matrices[name][1])

            try:
                setattr(self, name, from_image_func(os.path.join(directory, f"{name}.png")))
            except FileNotFoundError:
                if name in self._section_optional: pass
                else: raise FileNotFoundError

        for name in self.__class__._section_texts:
            text_section = TextSection()
            text_section.from_file(os.path.join(directory, f"{name}.txt"))
            setattr(self, name, text_section)

        for name in self._section_special.keys():

            setattr(self, name, self._section_special[name]())
            getattr(self, name).from_file(os.path.join(directory, f"{name}.csv"))

    def get_section_bytes(self, name):

        section = getattr(self, name)
        section_buffer_taker = BufferTaker()

        if section is None:
            raise AttributeError

        if name in self.__class__._section_matrices.keys():
            section_buffer_taker.bytes(run_length_encryption(section.tobytes(),
                                                             bytes_per_entry=self._section_matrices[name][0]))

        elif name in self.__class__._section_texts:
            section_buffer_taker.bytes(bytes(section))

        else:
            assert name in self.__class__._section_special.keys()

            if   section.to_bytes.__code__.co_argcount == 1: section_buffer_taker.bytes(section.to_bytes())
            elif section.to_bytes.__code__.co_argcount == 2: section_buffer_taker.bytes(section.to_bytes(self))
            else: raise NotImplementedError

        return bytes(section_buffer_taker)

    @classmethod
    def _get_section_type(cls, name):
        return cls._section_types_special.get(name, cls._section_type_default)

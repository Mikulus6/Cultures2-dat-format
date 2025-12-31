import os
import numpy as np
from scripts.buffer import BufferGiver, BufferTaker
from sections.run_length import run_length_decryption
from scripts.image import bytes_to_image, shorts_to_image


class Data:

    _sections_empty = {"logi", "lgmm", "emmm", "xend", "tend"}

    _section_names = {"logi", "lgmm", "lsiz", "lmhe", "lmpa", "lmpb", "lmlt", "lmlv", "lmlp", "lmco", "lmtw", "lmms",
                      "lmpr", "lmwb", "lmbb", "lmro", "lmsb", "lmao", "laco", "lasw", "lafm", "lmhf", "emmm", "embr",
                      "emm1", "emmi", "eapd", "empa", "empb", "eatd", "emt1", "emt2", "emt3", "emt4", "eald", "emla",
                      "emvc", "xend", "tend"}

    # name: [bytes_per_vertex, width_multiplicator]
    _section_matrices = {"lmhe": [1, 1], "lmpa": [1, 1], "lmpb": [1, 1], "lmlt": [1, 2], "lmlv": [1, 2], "lmlp": [1, 2],
                         "lmco": [1, 2], "lmtw": [1, 2], "lmms": [1, 2], "lmpr": [1, 2], "lmwb": [1, 2], "lmbb": [1, 2],
                         "lmro": [1, 2], "lmsb": [1, 2], "lmao": [2, 2], "lmhf": [1, 2], "embr": [1, 1], "emm1": [1, 1],
                         "emmi": [1, 2], "empa": [2, 1], "empb": [2, 1], "emt1": [1, 1], "emt2": [1, 1], "emt3": [1, 1],
                         "emt4": [1, 1], "emla": [2, 2], "emvc": [1, 1]}

    _section_type_default = 1
    _section_types_special = {"logi": 0, "lgmm": 0, "emmm": 0, "xend": 0, "tend": 0, "lafm": 2, "lasw": 4}

    def __init__(self):

        self.map_width  = 0  # noqa: E221
        self.map_height = 0  # noqa: E221

        self.headers = {name: None for name in self.__class__._section_names}

        for name in (self.__class__._section_names - self.__class__._sections_empty - {"lsiz"}):
            setattr(self, name, None)

    def load(self, filename: str):
        with open(filename, "rb") as file:
            buffer = BufferGiver(file.read())

        while len(buffer) != 0:
            assert buffer.string(length=4, encoding="ascii")[::-1] == "xioh"  # "x input-output handler"
            name = buffer.string(length=4, encoding="ascii")[::-1]
            assert name in self.__class__._section_names

            section_type = buffer.unsigned(length=4)
            length = buffer.unsigned(length=4)

            if section_type != self.__class__._section_type_default:
                assert self.__class__._section_types_special[name] == section_type

            assert buffer.unsigned(length=4) == 0
            self.headers[name] = buffer.unsigned(length=4)  # TODO: unknown, this has to be figured out eventually.
            assert buffer.unsigned(length=8) == 0

            section_buffer = BufferGiver(buffer.bytes(length=length))

            if section_type == 0:  # empty sections
                assert name in self.__class__._sections_empty
                assert self.headers[name] == 0
                assert length == 0
                del self.headers[name]

            elif name == "lsiz":  # map size
                self.map_width  = section_buffer.unsigned(length=4)
                self.map_height = section_buffer.unsigned(length=4)
                assert len(section_buffer) == 0

            elif name in self.__class__._section_matrices.keys():
                assert self.map_width  is not None and\
                       self.map_height is not None

                match self.__class__._section_matrices[name][0]:
                    case 1: ndarray_dtype = np.uint8
                    case 2: ndarray_dtype = np.uint16
                    case _: raise ValueError

                size_multiplicator = self.__class__._section_matrices[name][1]
                section_ndarray = np.frombuffer(run_length_decryption(bytes(section_buffer)),
                                                dtype=ndarray_dtype).reshape(self.map_height * size_multiplicator,
                                                                             self.map_width  * size_multiplicator)

                setattr(self, name, section_ndarray)

            else:

                # TODO: further interpretation may be required later. Maybe those sections must be interpreted as
                #       some kind of iterable objects, not just as raw bytes. They should be easy to manipulate and
                #       also easily convertible back to raw bytes.
                setattr(self, name, bytes(section_buffer))

                # TODO: These are all known section which fall into this category. Each of them requires separeted
                #       interpretation.
                assert name in ("laco", "lasw", "lafm", "eapd", "eatd", "eald")

        # Optional sections
        assert set(key for key in self.__dict__ if getattr(self, key) is None).issubset({"lmhf", "emvc"})

    def save(self, filename: str):
        raise NotImplementedError

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
                          width=self.map_width * params[1])

    def pack(self, directory: str):
        raise NotImplementedError
import numpy as np
import os
import random
from scripts.buffer import BufferGiver, BufferTaker
from sections import *
from supplements.initialization import encode
from supplements.library import Library
from PIL import Image


class Data:
    assert all(isinstance(section_special_class, SpecialSection) for section_special_class in section_special.values())
    assert isinstance(TextSection, SpecialSection)

    def __init__(self):

        for name in set(section_names) - set(sections_empty):
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
            assert name in section_names

            section_type = buffer.unsigned(length=4)
            length = buffer.unsigned(length=4)

            assert self.__class__._get_section_type(name) == section_type

            assert buffer.unsigned(length=4) == 0
            checksum = buffer.unsigned(length=4)  # noqa
            assert buffer.unsigned(length=8) == 0

            section_buffer = BufferGiver(buffer.bytes(length=length))

            assert checksum == calculate_checksum(bytes(section_buffer))

            if section_type == 0:  # empty sections
                assert name in sections_empty
                assert length == 0

            elif name in section_matrices.keys():
                assert self.lsiz.width  is not None and\
                       self.lsiz.height is not None

                match section_matrices[name][0]:
                    case 1: ndarray_dtype = np.uint8
                    case 2: ndarray_dtype = np.uint16
                    case _: raise ValueError

                size_multiplicator = section_matrices[name][1]
                section_ndarray = np.frombuffer(run_length_decryption(bytes(section_buffer)),
                                                dtype=ndarray_dtype).reshape(
                                                                     self.lsiz.height * size_multiplicator,
                                                                     self.lsiz.width  * size_multiplicator).copy()
                setattr(self, name, section_ndarray)

            elif name in sections_texts:
                text_section = TextSection()
                text_section.load(section_buffer)
                setattr(self, name, text_section)

            else:
                assert name in section_special.keys()
                setattr(self, name, section_special[name]())
                getattr(self, name).load(section_buffer)

        # optional sections, not present in some versions of Cultures 2
        assert set(key for key in self.__dict__
                   if getattr(self, key) is None).issubset(sections_optional)

    def save(self, filename: str):
        buffer_taker = BufferTaker()

        names_ordered = [name for name in section_names if name[0] == "l"] + ["xend"] + \
                        [name for name in section_names if name[0] == "e"] + ["xend", "tend"]

        for name in names_ordered:

            section_existence = getattr(self, name, None) is not None

            if not section_existence and name in sections_optional:
                continue

            buffer_taker.string("xioh"[::-1])
            buffer_taker.string(name[::-1])

            if not section_existence or (self.__class__._get_section_type(name) == 0):
                buffer_taker.unsigned(0, length=24)

            else:

                section_bytes = self._get_section_bytes(name)
                checksum = calculate_checksum(section_bytes)  # noqa

                buffer_taker.unsigned(self.__class__._get_section_type(name), length=4)
                buffer_taker.unsigned(len(section_bytes), length=4)
                buffer_taker.unsigned(0, length=4)
                buffer_taker.unsigned(checksum, length=4)
                buffer_taker.unsigned(0, length=8)
                buffer_taker.bytes(section_bytes)

        if os.path.dirname(filename) != "":
            os.makedirs(os.path.dirname(filename), exist_ok=True)

        match filename.lower().split(".")[-1]:
            case "dat":
                with open(filename, "wb") as file:
                    file.write(bytes(buffer_taker))
            case "c2m":
                template_text = f"[logiccontrol]\nversion 1\nmapsize {self.lsiz.width} {self.lsiz.height}\n" + \
                                f"mapguid" + " ".join([str(random.randint(0, 0xff)) for _ in range(16)]) + \
                                "\n[logiccontrolend]"

                library = Library()
                library["currentusermap\\map.cif"] = encode(template_text, cultures_1=False, sal_tab_file_format=False)
                library["currentusermap\\map.dat"] = bytes(buffer_taker)
                library.save(filename, cultures_1=False)
                del library

    def extract(self, directory: str):

        os.makedirs(directory, exist_ok=True)

        for name, params in section_matrices.items():
            section_ndarray = getattr(self, name)

            if section_ndarray is None:
                continue

            match section_ndarray.dtype:
                case np.uint8:
                    assert params[0] == 1
                    to_image_func = lambda arr:(
                        Image.fromarray(arr, mode="L"))
                case np.uint16:
                    assert params[0] == 2
                    to_image_func = lambda arr:(
                        Image.fromarray(np.dstack((arr % 0x100, arr // 0x100, np.zeros_like(arr))).astype(np.uint8),
                                        mode="RGB"))
                case _: raise TypeError

            to_image_func(section_ndarray).save(os.path.join(directory, f"{name}.png"))

        for name in sections_texts:
            text_section = getattr(self, name)
            text_section.to_file(os.path.join(directory, f"{name}.txt"))

        for name in section_special.keys():
            getattr(self, name).to_file(os.path.join(directory, f"{name}.csv"))

    def pack(self, directory: str):

        self.lsiz = Size()  # noqa, precaculate map size
        assert min(section_matrices.values(), key=lambda x: x[1])[1] == 1
        minimal_width_section_name = min(section_matrices, key=lambda x: x[1])
        minimal_width_section = Image.open(os.path.join(directory, f"{minimal_width_section_name}.png"))
        self.lsiz.width, self.lsiz.height  = minimal_width_section.size

        del minimal_width_section_name, minimal_width_section

        for name, params in section_matrices.items():

            match section_matrices[name][0]:
                case 1: from_image_func_temp = lambda image: image
                case 2: from_image_func_temp = lambda image: ((arr := np.array(image, dtype=np.uint16))[..., 0] | (arr[..., 1] << 8))
                case _: raise TypeError

            from_image_func = lambda path: np.array(from_image_func_temp(Image.open(path)))

            try:
                setattr(self, name, from_image_func(os.path.join(directory, f"{name}.png")))
            except FileNotFoundError:
                if name in sections_optional: pass
                else: raise FileNotFoundError

        for name in sections_texts:
            text_section = TextSection()
            text_section.from_file(os.path.join(directory, f"{name}.txt"))
            setattr(self, name, text_section)

        for name in section_special.keys():

            setattr(self, name, section_special[name]())
            getattr(self, name).from_file(os.path.join(directory, f"{name}.csv"))

    def update(self, *, refresh_primary: bool = False):
        self.__dict__.update(vars(update(self, refresh_primary=refresh_primary)))

    def _get_section_bytes(self, name):

        section = getattr(self, name)
        section_buffer_taker = BufferTaker()

        if section is None:
            raise AttributeError

        if name in section_matrices.keys():
            section_buffer_taker.bytes(run_length_encryption(section.tobytes(),
                                                             bytes_per_entry=section_matrices[name][0]))

        elif name in sections_texts:
            section_buffer_taker.bytes(bytes(section))

        else:
            assert name in section_special.keys()
            if   section.to_bytes.__code__.co_argcount == 1: section_buffer_taker.bytes(section.to_bytes())
            elif section.to_bytes.__code__.co_argcount == 2: section_buffer_taker.bytes(section.to_bytes(self))
            else: raise NotImplementedError

        return bytes(section_buffer_taker)

    @staticmethod
    def _get_section_type(name):
        return sections_types_special.get(name, section_type_default)

import os
from scripts.buffer import BufferGiver, BufferTaker
from sections.special.special import SpecialSection

class Size(metaclass=SpecialSection):
    def __init__(self):
        self.width:  int = 0
        self.height: int = 0

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.width == other.width and self.height == other.height

    @property
    def shape(self):
        # Property used for numpy arrays, therefore order of coordinates is reversed.
        return self.height, self.width

    @property
    def shape_micro(self):
        # Property used for numpy arrays, therefore order of coordinates is reversed.
        return 2 * self.height, 2 * self.width

    def load(self, bytes_obj: bytes):
        buffer = BufferGiver(bytes_obj)
        self.width = buffer.unsigned(length=4)
        self.height = buffer.unsigned(length=4)

    def to_bytes(self):
        buffer_taker = BufferTaker()
        buffer_taker.unsigned(self.width,  length=4)
        buffer_taker.unsigned(self.height, length=4)
        return bytes(buffer_taker)

    def to_file(self, filename):
        # preferred file extension: *.csv
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as file:
            file.write(f"{self.width}\n{self.height}")

    def from_file(self, filename):
        # preferred file extension: *.csv
        with open(filename, "r") as file:
            self.width, self.height = tuple(map(int, file.read().strip("\n").split("\n")))


def update_lsiz(data_object):
    data_object.lsiz.height, data_object.lsiz_width = data_object.empa.shape
    return data_object

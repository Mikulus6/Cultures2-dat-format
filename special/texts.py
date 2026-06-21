import os
from scripts.buffer import BufferGiver, BufferTaker
from special.special import SpecialSection

class TextSection(list, metaclass=SpecialSection):

    def __init__(self, *, list_: list = None):
        super().__init__(list_ if list_ is not None else list())

    def load(self, bytes_obj: bytes):
        assert len(self) == 0
        buffer = BufferGiver(bytes_obj)

        for _index in range(buffer.unsigned(length=4)):
            self.append(buffer.string(buffer.unsigned(length=1)))
            assert buffer.unsigned(length=1) == 0
        assert len(buffer) == 0

    def __bytes__(self):

        buffer_taker = BufferTaker()
        buffer_taker.unsigned(len(self), length=4)

        for item in self:
            buffer_taker.unsigned(len(item), length=1)
            buffer_taker.string(item)
            buffer_taker.unsigned(0, length=1)

        return bytes(buffer_taker)

    def to_file(self, filename: str):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as file:
            file.write("\n".join(self))

    def from_file(self, filename: str):
        with open(filename, "r") as file:
            super().__init__(file.read().rstrip("\n").split("\n"))

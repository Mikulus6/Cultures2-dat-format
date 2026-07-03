import os
from dataclasses import dataclass
from scripts.buffer import BufferGiver, BufferTaker
from special.special import SpecialSection

@dataclass
class Continent:
    type: int
    anchor_vertex: tuple[int, int]
    size: int

class Continents(list, metaclass=SpecialSection):
    _continents_limit = 250

    def __init__(self):
        super().__init__()

    def load(self, bytes_obj: bytes):
        assert len(self) == 0
        buffer = BufferGiver(bytes_obj)

        number_of_continents = buffer.unsigned(length=4)

        for index_, _ in enumerate(range(number_of_continents)):
            continent_type = buffer.unsigned(length=4)  # 0 = void, 1 = land, 2 = water
            anchor_vertex_x = buffer.signed(length=2)
            anchor_vertex_y = buffer.signed(length=2)
            continent_size = buffer.signed(length=4)

            # Cordinates of anchor vertex being -1 x -1 and negative continent size are most likely a result of a
            # removal of previously existing continent during development process. The second type of this issue is
            # absent in "Cultures 2: The Gates of Asgard" and is present only in newer Cultures games.

            assert (int(bool(index_)) == buffer.unsigned(length=4)) or continent_size == 0

            continent = Continent(type=continent_type,
                                  anchor_vertex=(anchor_vertex_x, anchor_vertex_y),
                                  size=continent_size)

            self.append(continent)

        self.check_internal_consistency()

    def to_bytes(self):
        buffer_taker = BufferTaker()

        buffer_taker.unsigned(len(self), length=4)

        self.check_internal_consistency()

        for index_, continent in enumerate(self):

            buffer_taker.unsigned(continent.type,          length=4)
            buffer_taker.signed(continent.anchor_vertex[0], length=2)
            buffer_taker.signed(continent.anchor_vertex[1], length=2)
            buffer_taker.signed(continent.size[2],         length=4)

            match bool(index_):
                case True : buffer_taker.unsigned(1, length=4)
                case False: buffer_taker.unsigned(0, length=4)
                case _: raise ValueError

        buffer_taker.unsigned(0, length=16 * (self.__class__._continents_limit - len(self)))

        return bytes(buffer_taker)

    def check_internal_consistency(self):

        assert len(self) <= self.__class__._continents_limit

        for index_, continent in enumerate(self):

            assert continent.anchor_vertex[0] >= -1
            assert continent.anchor_vertex[1] >= -1
            assert (continent.anchor_vertex[0] == -1) == (continent.anchor_vertex[1] == -1)

            if index_ == 0 or continent.type == 0:
                assert continent.type == 0 and continent.anchor_vertex == (0, 0)
                assert continent.size <= 0
            else:
                assert continent.type in (1, 2)
                assert continent.size >= 0

    def to_file(self, filename: str):
        # preferred file extension: *.csv
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as file:
            file.write("\n".join((f"{continent.type},{continent.anchor_vertex[0]},{continent.anchor_vertex[1]},{continent.size}" for continent in self)))

    def from_file(self, filename: str):
        # preferred file extension: *.csv
        self.clear()
        with open(filename, "r") as file:
            for line in file.read().rstrip("\n").split("\n"):
                if len(line) == 0:
                    continue
                entries = tuple(map(lambda entry: int(entry.rstrip(" ")), line.split(",")))
                self.append(Continent(type=entries[0], anchor_vertex=(entries[1], entries[2]), size=entries[3]))

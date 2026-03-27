import os
from scripts.buffer import BufferGiver, BufferTaker


class Continents(list):
    _continents_limit = 250

    def __init__(self):
        super().__init__()

    def load(self, bytes_obj: bytes):
        assert len(self) == 0
        buffer = BufferGiver(bytes_obj)

        number_of_continents = buffer.unsigned(length=4)

        for index_, _ in enumerate(range(number_of_continents)):
            continent_type = buffer.unsigned(length=4)  # 0 = void, 1 = land, 2 = water  # TODO: verify
            first_vertex_x = buffer.signed(length=2)
            first_vertex_y = buffer.signed(length=2)
            continent_size = buffer.signed(length=4)

            # Cordinates of first vertex being -1 x -1 and negative continent size are most likely a result of a removal
            # of previously existing continent during development process. The second type of this issue is absent in
            # "Cultures 2: The Gates of Asgard" and is present only in newer Cultures games.

            assert bool(index_) == bool(buffer.unsigned(length=4))

            self.append([continent_type, (first_vertex_x, first_vertex_y), continent_size])

        self.check_internal_consistency()

    def to_bytes(self):
        buffer_taker = BufferTaker()

        buffer_taker.unsigned(len(self), length=4)

        self.check_internal_consistency()

        for index_, item in enumerate(self):

            buffer_taker.unsigned(item[0], length=4)
            buffer_taker.signed(item[1][0], length=2)
            buffer_taker.signed(item[1][1], length=2)
            buffer_taker.signed(item[2], length=4)

            match bool(index_):
                case True : buffer_taker.unsigned(1, length=4)
                case False: buffer_taker.unsigned(0, length=4)
                case _: raise ValueError

        buffer_taker.unsigned(0, length=16 * (self.__class__._continents_limit - len(self)))

        return bytes(buffer_taker)

    def check_internal_consistency(self):

        assert len(self) <= self.__class__._continents_limit

        for index_, item in enumerate(self):
            continent_type = item[0]
            first_vertex_x, first_vertex_y = item[1]
            continent_size = item[2]

            assert first_vertex_x >= -1
            assert first_vertex_y >= -1
            assert (first_vertex_x == -1) == (first_vertex_y == -1)

            if index_ == 0:
                assert (continent_type, first_vertex_x, first_vertex_y) == (0, 0, 0)
                assert continent_size <= 0
            else:
                assert continent_type in (1, 2)
                assert continent_size >= 0

    def to_file(self, filename: str):
        # preferred file extension: *.csv
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as file:
            file.write("\n".join((f"{item[0]},{item[1][0]},{item[1][1]},{item[2]}" for item in self)))

    def from_file(self, filename: str):
        # preferred file extension: *.csv
        self.clear()
        with open(filename, "r") as file:
            for line in file.read().rstrip("\n").split("\n"):
                if len(line) == 0:
                    continue
                entries = tuple(map(lambda entry: int(entry.rstrip(" ")), line.split(",")))
                self.append([entries[0], (entries[1], entries[2]), entries[3]])

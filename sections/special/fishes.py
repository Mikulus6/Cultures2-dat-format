import os
from ..generic.external import BufferGiver, BufferTaker
from ..special.special import SpecialSection


class Fishes(dict, metaclass=SpecialSection):
    _fishes_swarms_limit = 500

    def __init__(self):
        super().__init__()

    def load(self, bytes_obj: bytes):
        assert len(self) == 0
        buffer = BufferGiver(bytes_obj)
        buffer.skip(self.__class__._fishes_swarms_limit * 12)
        sum_of_swarms = buffer.unsigned(length=4)
        buffer.skip_to(0)

        assert len(buffer) == self.__class__._fishes_swarms_limit * 12 + 4
        assert sum_of_swarms <= self.__class__._fishes_swarms_limit

        for _ in range(self.__class__._fishes_swarms_limit):
            position_x = buffer.unsigned(length=2)
            position_y = buffer.unsigned(length=2)
            fish_count = buffer.unsigned(length=4)
            continent  = buffer.unsigned(length=4)
            # Continent value is correctly assigned only in "Cultures 2: The Gates of Asgard". In newer Culture games,
            # this value is not always correctly updated when "lmco" section is considered. That is because water basins
            # can be modified after fishes are placed on the map, and the data of fish swarms will not be corrected.

            position = (position_x, position_y)

            if fish_count == 0:
                assert position == (0, 0)
                assert continent == 0
                continue

            assert position not in self.keys()

            self[position] = fish_count

            if len(self) >= sum_of_swarms:
                # Further content of this section can be filled with corrupted data. Those are most likely fish swarms
                # which were deleted in original editors by covering them with land without deleting them directly.
                break

    def to_bytes(self, data_obj):
        buffer_taker = BufferTaker()
        sum_of_swarms = 0
        for position in sorted(self.keys(), key=lambda pos: pos[1] * (2 * data_obj.lsiz.width) + pos[0]):
            buffer_taker.unsigned(position[0], length=2)
            buffer_taker.unsigned(position[1], length=2)
            buffer_taker.unsigned(self[position], length=4)
            buffer_taker.unsigned(int(data_obj.lmco[position[::-1]]), length=4)
            sum_of_swarms += 1

        buffer_taker.unsigned(0, length=12 * (self.__class__._fishes_swarms_limit - sum_of_swarms))
        buffer_taker.unsigned(sum_of_swarms, length=4)

        return bytes(buffer_taker)

    def to_file(self, filename: str):
        # preferred file extension: *.csv
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as file:
            file.write("\n".join((f"{position[0]},{position[1]},{fish_count}"
                                  for position, fish_count in self.items())))

    def from_file(self, filename: str):
        # preferred file extension: *.csv
        self.clear()
        with open(filename, "r") as file:
            for line in file.read().rstrip("\n").split("\n"):
                if len(line) == 0:
                    continue
                entries = tuple(map(lambda entry: int(entry.rstrip(" ")), line.split(",")))
                self[entries[0], entries[1]] = entries[2]

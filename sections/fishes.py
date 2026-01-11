import os
from scripts.buffer import BufferGiver, BufferTaker


class Fishes(dict):
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
            # Continent value is correctly assigned only in "Cultures 2: The Gates of Asgard". In newer Cultures games
            # this value is not always correctly updated when "lmco" section is considered. Incorrectly updated data
            # is not considered a primary non-derivable section, because it serves no known purpose in game for now.

            # TODO: Continent value might be related to swarm initial orientation. I need to check it later.

            position = (position_x, position_y)

            if fish_count == 0:
                assert position == (0, 0)
                continue

            if position in self.keys():
                continue
                # Some positions are duplicated in exisiting maps. One such position in "8th Wonder of the World" on map
                # "singleplayer_03_04/map.dat" ("Bleak Awakening") contains different values for different duplicates.
                # In such scenarion the game reads the first entry mentioning given position and ignores further
                # duplicates, as we do here.

            self[position] = fish_count

            if len(self) >= sum_of_swarms:
                # There is a map in "Northland" on which more fishes are declared than there are present in the game.
                break

    def to_bytes(self, data_obj):
        buffer_taker = BufferTaker()
        sum_of_swarms = 0
        for position in sorted(self.keys(), key=lambda pos: pos[1] - 1/(pos[0] + 1)):
            buffer_taker.unsigned(position[0], length=2)
            buffer_taker.unsigned(position[1], length=2)
            buffer_taker.unsigned(self[position], length=4)
            buffer_taker.unsigned(int(data_obj.lmco[position[::-1]]), length=4)
            sum_of_swarms += 1

        buffer_taker.unsigned(0, length=12 * (self.__class__._fishes_swarms_limit - sum_of_swarms))
        buffer_taker.unsigned(sum_of_swarms, length=4)

        return bytes(buffer_taker)

    def to_file(self, filename: str):
        # preferred file extension" *.csv
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as file:
            for position, fish_count in self.items():
                file.write(f"{position[0]},{position[1]},{fish_count}\n")

    def from_file(self, filename: str):
        # preferred file extension" *.csv
        self.clear()
        with open(filename, "r") as file:
            for line in file.read().rstrip("\n").split("\n"):
                if len(line) == 0:
                    continue
                entries = tuple(map(lambda entry: int(entry.rstrip(" ")), line.split(",")))
                self[entries[0], entries[1]] = entries[2]

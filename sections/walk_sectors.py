import os
from scripts.buffer import BufferGiver, BufferTaker


class WalkSector:

    def __init__(self):
        self.connections = {"up":    False,
                            "left":  False,
                            "down":  False,
                            "right": False}

        self.edge_numbers = list()
        self.points = list()

    def load(self, bytes_obj):

        sector_buffer = BufferGiver(bytes_obj)
        assert sector_buffer.unsigned(1) == 1

        connections_raw_bits = sector_buffer.binary(1)
        assert connections_raw_bits[::2] == "0000"  # Even bytes (counting from zero) must be zero
        self.connections = {"up":    connections_raw_bits[1] == "1",
                            "left":  connections_raw_bits[3] == "1",
                            "down":  connections_raw_bits[5] == "1",
                            "right": connections_raw_bits[7] == "1"}

        sector_buffer.skip(1) # continent number
        assert sector_buffer.unsigned(1) == 0

        self.edge_numbers = list()
        for _ in range(8):
            self.edge_numbers.append(sector_buffer.unsigned(4))

        assert max(self.edge_numbers) <= 7

        coordinates_1 = (sector_buffer.unsigned(2), sector_buffer.unsigned(2))
        coordinates_2 = (sector_buffer.unsigned(2), sector_buffer.unsigned(2))
        coordinates_3 = (sector_buffer.unsigned(2), sector_buffer.unsigned(2))

        assert sector_buffer.unsigned(4) == sum(coordinates != (0, 0) for coordinates in (coordinates_1,
                                                                                          coordinates_2,
                                                                                          coordinates_3))

        for coordinates in (coordinates_1, coordinates_2, coordinates_3):
            if coordinates == (0, 0):
                break
            self.points.append(coordinates)

    def to_bytes(self, data_obj):
        buffer_taker = BufferTaker()
        buffer_taker.unsigned(1, length=1)
        connections_raw_bits = ("01" if self.connections["up"]    else "00") + \
                               ("01" if self.connections["left"]  else "00") + \
                               ("01" if self.connections["down"]  else "00") + \
                               ("01" if self.connections["right"] else "00")
        buffer_taker.binary(connections_raw_bits)

        if len(self.points) == 0: walk_point_1 = (0, 0)
        else:                     walk_point_1 = self.points[0]

        buffer_taker.unsigned(int(data_obj.lmco[walk_point_1[::-1]]), length=1)
        buffer_taker.unsigned(0, length=1)

        assert len(self.edge_numbers) == 8
        assert max(self.edge_numbers) <= 7

        for edge_number in self.edge_numbers:
            buffer_taker.unsigned(edge_number, length=4)

        walk_points_used_count = 0
        for points_counter in range(3):
            if len(self.points) <= points_counter: walk_point = (0, 0)
            else:                                  walk_point = self.points[points_counter]

            if walk_point != (0, 0):
                walk_points_used_count += 1

            buffer_taker.unsigned(walk_point[0], length=2)
            buffer_taker.unsigned(walk_point[1], length=2)

        buffer_taker.unsigned(walk_points_used_count, length=4)

        return bytes(buffer_taker)

    _text_subseparator_1 = "|"
    _text_subseparator_2 = ";"

    def to_text(self) -> str:
        return self.__class__._text_subseparator_1.join(key for key, value in self.connections.items() if value)+ "," +\
               self.__class__._text_subseparator_1.join(map(str, self.edge_numbers))+ "," +\
               self.__class__._text_subseparator_1.join(str(point[0]) +
                                                        self.__class__._text_subseparator_2 +
                                                        str(point[1]) for point in self.points)

    def from_text(self, text_: str):
        connections_raw, edge_numbers_raw, points_raw = text_.rstrip("\n").split(",")
        self.connections = {direction: (direction in connections_raw.split("|")) for direction in ("up", "left",
                                                                                                   "down", "right")}
        self.edge_numbers = list(map(int, edge_numbers_raw.split("|")))
        points_raw_list =  points_raw.split("|")
        if len(points_raw_list[0]) == 0:
            points_raw_list = list()
        self.points = list(map(lambda point_text:tuple(map(int, point_text.split(self.__class__._text_subseparator_2))),
                               points_raw_list))


class WalkSectors:
    _walkable_terrain_types = ("land", "water")
    _bytes_per_sector = 52

    def __init__(self):

        for terrain_type in self.__class__._walkable_terrain_types:
            setattr(self, terrain_type, list())

    def load(self, bytes_obj: bytes):

        assert len(bytes_obj) % (self.__class__._bytes_per_sector * len(self._walkable_terrain_types)) == 0
        buffer = BufferGiver(bytes_obj)

        for terrain_type in self.__class__._walkable_terrain_types:
            setattr(self, terrain_type, list())
            for _ in range(len(bytes_obj) // (self.__class__._bytes_per_sector * len(self._walkable_terrain_types))):
                walk_sector = WalkSector()
                walk_sector.load(buffer.bytes(self.__class__._bytes_per_sector))
                getattr(self, terrain_type).append(walk_sector)

    def to_bytes(self, data_obj):
        buffer_taker = BufferTaker()
        for terrain_type in self.__class__._walkable_terrain_types:
            for walk_sector in getattr(self, terrain_type):
                buffer_taker.bytes(walk_sector.to_bytes(data_obj))
        return bytes(buffer_taker)

    def to_text(self) -> dict:
        text = str()
        for terrain_type in self.__class__._walkable_terrain_types:
            text += terrain_type + "\n"
            for sector_point in getattr(self, terrain_type, list()):
                text += sector_point.to_text() + "\n"
        return text.rstrip("\n")

    def from_text(self, text):

        current_terrain_type = None
        current_terrain_type_sectors = list()

        for line in (*text.rstrip("\n").split("\n"), None):  # None means eof.
            for terrain_type in self.__class__._walkable_terrain_types:
                if line == terrain_type or line is None:
                    if current_terrain_type is not None:
                        setattr(self, current_terrain_type, current_terrain_type_sectors)
                    current_terrain_type = line
                    current_terrain_type_sectors = list()
                    break
            else:
                walk_sector = WalkSector()
                walk_sector.from_text(line)
                current_terrain_type_sectors.append(walk_sector)

    def to_file(self, filename: str):
        # preferred file extension: *.csv
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "w") as file:
            file.write(self.to_text())

    def from_file(self, filename: str):
        # preferred file extension: *.csv
        with open(filename, "r") as file:
            self.from_text(file.read())

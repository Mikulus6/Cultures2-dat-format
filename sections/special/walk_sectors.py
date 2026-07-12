from collections import deque
from collections.abc import Callable, Iterable
import numpy as np
import os
import time
from typing import Literal
from scripts.buffer import BufferGiver, BufferTaker
from sections.generic.geometry import get_neighbouring_vertices
from sections.generic.minus_one import get_minus_one
from sections.special.external_assets import update_ea_d
from sections.special.special import SpecialSection

walk_sector_size = (10, 10)
walk_sector_size_micro = type(walk_sector_size)(map(lambda s: 2 * s, walk_sector_size))

class WalkSector:

    def __init__(self):
        self.connections = {"up":    False,
                            "left":  False,
                            "down":  False,
                            "right": False}

        self.max_vehicle_sizes = list()
        # Starting from the direction to the right and going clockwise, these eight numbers are used to determine how
        # big a vehicle can be for navigation from a walk sector in a given direction. However, the original
        # implementation in the game is flawed, and this number does not satisfy the conditions to be redundant to an
        # undirected graph.

        self.points = list()

    def load(self, bytes_obj):

        sector_buffer = BufferGiver(bytes_obj)
        assert sector_buffer.unsigned(1) in (0, 1)

        connections_raw_bits = sector_buffer.binary(1)
        assert connections_raw_bits[::2] == "0000"  # Even bits (counting from zero) must be zero
        self.connections = {"up":    connections_raw_bits[1] == "1",
                            "left":  connections_raw_bits[3] == "1",
                            "down":  connections_raw_bits[5] == "1",
                            "right": connections_raw_bits[7] == "1"}

        sector_buffer.skip(1) # continent number
        assert sector_buffer.unsigned(1) == 0

        self.max_vehicle_sizes = list()
        for _ in range(8):
            self.max_vehicle_sizes.append(sector_buffer.unsigned(4))

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

        assert self.max_vehicle_sizes[1] == self.max_vehicle_sizes[3] == self.max_vehicle_sizes[5] == self.max_vehicle_sizes[7]
        assert max(self.max_vehicle_sizes) <= 7
        if coordinates_1 == (0, 0):
            assert max(self.max_vehicle_sizes) == 0

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

        assert len(self.max_vehicle_sizes) == 8
        assert max(self.max_vehicle_sizes) <= 7

        for edge_number in self.max_vehicle_sizes:
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
               self.__class__._text_subseparator_1.join(map(str, self.max_vehicle_sizes))+ "," +\
               self.__class__._text_subseparator_1.join(str(point[0]) +
                                                        self.__class__._text_subseparator_2 +
                                                        str(point[1]) for point in self.points)

    def from_text(self, text_: str):
        connections_raw, max_vehicle_sizes_raw, points_raw = text_.rstrip("\n").split(",")
        self.connections = {direction: (direction in connections_raw.split("|")) for direction in ("up", "left",
                                                                                                   "down", "right")}
        self.max_vehicle_sizes = list(map(int, max_vehicle_sizes_raw.split("|")))
        points_raw_list =  points_raw.split("|")
        if len(points_raw_list[0]) == 0:
            points_raw_list = list()
        self.points = list(map(lambda point_text:tuple(map(int, point_text.split(self.__class__._text_subseparator_2))),
                               points_raw_list))


class WalkSectors(metaclass=SpecialSection):
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


class _WalkSectorsVehiclesDecorrupter:
    # This class is used as an empirical verifier for walk sectors data corruption. It finds potentially corrupted
    # information in the given data object and then asks the user to refresh this information by placing and removing a
    # landscape with a tangible hitbox near the given coordinates in the original external editor of any game from the
    # Cultures series. If the corruption is removed due to the user refreshing walk sectors data by placing and removing
    # a landscape, and no other data is changed, it is proven to be corrupted data and not deterministically derivable
    # information.

    directions_dict = {0: "right",
                       2: "down",
                       4: "left",
                       8: "up"}

    def __init__(self, editable_c2m_path: str, refresh_time: float):
        self.editable_c2m_path = editable_c2m_path
        self.refresh_time = refresh_time  # seconds

        assert self.editable_c2m_path.lower().endswith(".c2m")

    @staticmethod
    def _simplify_and_compare(data_object_1, data_object_2):
        data_object_1 = update_ea_d(data_object_1)
        data_object_2 = update_ea_d(data_object_2)

        return np.all(data_object_1.emla == data_object_2.emla) and \
               np.all(data_object_1.empa == data_object_2.empa) and \
               np.all(data_object_1.empb == data_object_2.empb) and \
               np.all(data_object_1.emmi == data_object_2.emmi) and \
               np.all(data_object_1.lmhe == data_object_2.lmhe)

    def _get_corruption_info(self, data_object):
        sectors_width, sectors_height = sectors_grid_size(data_object)

        for terrain_type in ("land", "water"):
            for sector_y in range(sectors_height):
                for sector_x in range(sectors_width):
                    sector_index = sector_y * sectors_width + sector_x
                    sector_center = (sector_x * walk_sector_size_micro[0] + (walk_sector_size_micro[0] // 2),
                                     sector_y * walk_sector_size_micro[1] + (walk_sector_size_micro[1] // 2))
                    sector = getattr(data_object.lasw, terrain_type)[sector_index]

                    sector_max_vehicle_sizes_old = sector.max_vehicle_sizes
                    sector_max_vehicle_sizes_new = get_sector_max_vehicle_sizes(data_object, sector_index, terrain_type)

                    if sector_max_vehicle_sizes_old != sector_max_vehicle_sizes_new:
                        for size_index in range(len(sector_max_vehicle_sizes_old)):
                            size_old = sector_max_vehicle_sizes_old[size_index]
                            size_new = sector_max_vehicle_sizes_new[size_index]
                            connection_iden = sector.connections.get(self.__class__.directions_dict.get(size_index,
                                                                                                        None), None)
                            if size_old != size_new:
                                error_iden = (size_old, size_new, terrain_type, connection_iden)
                                yield sector_center, error_iden

    def _await_c2m_edit(self, data_object):
        data_object.save(self.editable_c2m_path)
        time_edit_old = os.path.getmtime(self.editable_c2m_path)
        time_edit_new = time_edit_old
        while time_edit_new == time_edit_old:
            time_edit_new = os.path.getmtime(self.editable_c2m_path)
            time.sleep(self.refresh_time)
        data_object_new = data_object.__class__()
        data_object_new.load(self.editable_c2m_path)
        return data_object_new

    @staticmethod
    def _find_empty_vertex_in_sector(data_object, sector_center, terrain_type: Literal["land", "water"] = "land"):

        no_landscape = get_minus_one(data_object.emla.dtype)

        match terrain_type:
            case "land":  terrain_type = 1
            case "water": terrain_type = 2
            case _: raise ValueError

        for x, y in generate_hex_spiral():
            x_real = sector_center[0] + x - walk_sector_size[0]
            y_real = sector_center[1] + y - walk_sector_size[1]
            continent_type = data_object.laco[data_object.lmco[y_real, x_real]].type
            if continent_type == terrain_type and data_object.emla[y_real, x_real] == no_landscape:
                return x_real, y_real
        else:
            raise NotImplementedError # no free vertex (further manual investigation is required)

    def check(self, data_object):
        print(f"Started checking data file with macro map dimensions" + \
              f"{data_object.lsiz.width}x{data_object.lsiz.height}")
        data_object = update_ea_d(data_object)
        corruption_info = tuple(self._get_corruption_info(data_object))
        if len(corruption_info) > 0:
            print(f"Please open {self.editable_c2m_path} in the external editor.")
        while len(corruption_info) > 0:
            sector_info = corruption_info[0]
            empty_vertex = self._find_empty_vertex_in_sector(data_object, sector_info[0], sector_info[1][2])
            print(f"(Corruptions remaining: {len(corruption_info)}) " + \
                  f"Refresh sectors at {empty_vertex} on terrain type {sector_info[1][2]}.")
            data_object_new = self._await_c2m_edit(data_object)
            data_object_new = update_ea_d(data_object_new)
            if not self._simplify_and_compare(data_object, data_object_new):
                print(f"Primary data was not preserved. Please open the map again.")
            corruption_info = tuple(self._get_corruption_info(data_object_new))
        print("No corruptions were found.")


def sectors_grid_size(data_object):
    sectors_width =  ( data_object.lsiz.width  // walk_sector_size[0]) + \
                     ((data_object.lsiz.width  %  walk_sector_size[0]) != 0)
    sectors_height = ( data_object.lsiz.height // walk_sector_size[1]) + \
                     ((data_object.lsiz.height %  walk_sector_size[1]) != 0)
    return sectors_width, sectors_height

def pathfind_bounds(coordinates_1, coordinates_2):
    x_min = min((coordinates_1[0] // walk_sector_size_micro[0]) * walk_sector_size_micro[0],
                (coordinates_2[0] // walk_sector_size_micro[0]) * walk_sector_size_micro[0])
    y_min = min((coordinates_1[1] // walk_sector_size_micro[1]) * walk_sector_size_micro[1],
                (coordinates_2[1] // walk_sector_size_micro[1]) * walk_sector_size_micro[1])
    x_max = max(((coordinates_1[0] // walk_sector_size_micro[0]) + 1) * walk_sector_size_micro[0],
                ((coordinates_2[0] // walk_sector_size_micro[0]) + 1) * walk_sector_size_micro[0]) - 1
    y_max = max(((coordinates_1[1] // walk_sector_size_micro[1]) + 1) * walk_sector_size_micro[1],
                ((coordinates_2[1] // walk_sector_size_micro[1]) + 1) * walk_sector_size_micro[1]) - 1
    return (x_min, y_min), (x_max, y_max)

def pathfind(data_object, coordinates_start, coordinates_end,
             vextex_availability_func: Callable = lambda *args, **kwargs: True):

    coords_min, coords_max = pathfind_bounds(coordinates_start, coordinates_end)
    x_min, y_min = coords_min
    x_max, y_max = coords_max

    if coordinates_start == coordinates_end:
        return True

    if not vextex_availability_func(coordinates_end) or \
       data_object.lmco[coordinates_start[::-1]] != data_object.lmco[coordinates_end[::-1]]:
        return False

    queue = deque([coordinates_start])
    searched = np.zeros(shape=(y_max - y_min + 1, x_max - x_min + 1), dtype=bool)
    searched[coordinates_start[1] - y_min, coordinates_start[0] - x_min] = True

    while len(queue) > 0:
        x, y = queue.popleft()
        if vextex_availability_func((x, y)):
            if (x, y) == coordinates_end:
                return True

            for direction, coordinates in enumerate(get_neighbouring_vertices((x, y))):
                x_1, y_1 = coordinates
                if not(x_min <= x_1 <= x_max) or \
                   not(y_min <= y_1 <= y_max) or \
                   searched[y_1 - y_min, x_1 - x_min] or \
                   (data_object.lmtw[y, x] & (1 << direction)) == 0:  # edge availability
                    continue

                queue.append((x_1, y_1))
                searched[y_1 - y_min, x_1 - x_min] = True
    return False

def get_neighbouring_sector_indices(data_object, sector_index):
    sectors_width, sectors_height = sectors_grid_size(data_object)
    return (sector_index + 1             if sector_index % sectors_width != sectors_width - 1   else None, # right
            sector_index + sectors_width if sector_index < sectors_width * (sectors_height - 1) else None, # down
            sector_index - 1             if sector_index % sectors_width != 0                   else None, # left
            sector_index - sectors_width if sector_index >= sectors_width                       else None) # up

def get_sector_connections(data_object, sector_index, terrain_type: Literal["land", "water"] = "land"):
    sectors_type = getattr(data_object.lasw, terrain_type)
    sector = sectors_type[sector_index]
    if len(sector.points) != 0:
        availability_func = lambda coordinates: (data_object.lmwb[coordinates[::-1]] == 0)

        connections = list()
        for sector_neighbour_index in get_neighbouring_sector_indices(data_object, sector_index):
            if sector_neighbour_index is None:
                connections.append(False)
                continue

            sector_neighbour = sectors_type[sector_neighbour_index]
            if len(sector_neighbour.points) == 0:
                connections.append(False)
                continue

            connections.append(pathfind(data_object, sector.points[0], sector_neighbour.points[0], availability_func))
    else:
        connections = [False, False, False, False]

    return {"right": connections[0],
            "down":  connections[1],
            "left":  connections[2],
            "up":    connections[3]}

def get_cardinal_edge_value(data_object, coordinates_start, coordinates_end,
                            terrain_type: Literal["land", "water"] = "land"):
    # This function does not always return output identical to the original external editor present in multiple games
    # from the Cultures series. These exceptions are caused by the editor not updating walk sectors data correctly. For
    # any given exception, one can verify this fact by opening the relevant map in the original external editor and
    # updating the walk sector point by putting a landscape with a hitbox capable of blocking walking near it and then
    # removing it. This action will result in an identical map, but with walk sector points now updated. For all tests
    # performed so far, this method provided confirmation that walk sector points could be not updated correctly. Until
    # a counter example is found, this method remains the most accurate known derivation algorithm coherent with
    # knowledge provided by decompilation research done by push42. For more details use _WalkSectorsVehiclesDecorrupter
    # class defined in this file.

    match terrain_type:
        case "land":  size_limit = 1
        case "water": size_limit = 4
        case _: raise ValueError

    max_vehicle_size = int(data_object.lmms[coordinates_start[::-1]])
    size_cap = min(max_vehicle_size, size_limit)

    for vehicle_size in range(size_cap, -1, -1):

        def availability_func(coordinates):
            return (data_object.lmwb[coordinates[::-1]] == 0) and vehicle_size <= data_object.lmms[coordinates[::-1]]

        if pathfind(data_object, coordinates_start, coordinates_end, availability_func):
            return vehicle_size

    return max_vehicle_size

def get_sector_max_vehicle_sizes(data_object, sector_index, terrain_type: Literal["land", "water"] = "land"):
    _number_of_neighbours = 8
    sectors_type = getattr(data_object.lasw, terrain_type)
    sector = sectors_type[sector_index]

    if len(sector.points) == 0:
        return [0] * _number_of_neighbours

    max_vehicle_sizes = [int(data_object.lmms[sector.points[0][::-1]])] * _number_of_neighbours
    for direction_index, sector_neighbour_index in enumerate(get_neighbouring_sector_indices(data_object,
                                                                                             sector_index)):
        if sector_neighbour_index is None:
            continue

        sector_neighbour = sectors_type[sector_neighbour_index]
        if len(sector_neighbour.points) == 0:
            continue

        max_vehicle_sizes[2 * direction_index] = \
            get_cardinal_edge_value(data_object, sector.points[0], sector_neighbour.points[0], terrain_type)

    if len(sector.points) == 0: diagonal_edge_number = 0
    else: diagonal_edge_number = max(max_vehicle_sizes)
    max_vehicle_sizes[1::2] = [diagonal_edge_number] * len(max_vehicle_sizes[1::2])

    return max_vehicle_sizes

def generate_hex_spiral():
    x, y = walk_sector_size
    seen = {(x, y)}
    yield x, y

    side_length = 1
    active_loop = True
    direction_start = 4

    while active_loop:
        active_loop = False
        x, y = get_neighbouring_vertices((x, y))[direction_start]

        for direction in range(6):
            direction = (direction - 4 + direction_start) % 6
            for _ in range(side_length):
                if 0 <= x < walk_sector_size_micro[0] and 0 <= y < walk_sector_size_micro[1] and (x, y) not in seen:
                    seen.add((x, y))
                    yield x, y
                    active_loop = True
                x, y = get_neighbouring_vertices((x, y))[direction]
        side_length += 1

import numpy as np
import os
import time
from data import Data
from sections.arrays.external_assets import update_ea_d
from sections.special.walk_sectors import sectors_grid_size, get_sector_edge_numbers, walk_sector_size_micro


class WalkSectorsEdgesDecorrupter:
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

    def __init__(self, editable_c2m_path: str, *, refresh_time: float = 1.0):
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

                    sector_edges_old = sector.edge_numbers
                    sector_edges_new = get_sector_edge_numbers(data_object, sector_index, terrain_type)

                    if sector_edges_old != sector_edges_new:
                        for edge_index in range(len(sector_edges_old)):
                            edge_old = sector_edges_old[edge_index]
                            edge_new = sector_edges_new[edge_index]
                            connection_iden = sector.connections.get(self.__class__.directions_dict.get(edge_index,
                                                                                                        None), None)
                            if edge_old != edge_new:
                                error_iden = (edge_old, edge_new, terrain_type, connection_iden)
                                yield sector_center, error_iden

    def _await_c2m_edit(self, data_object) -> Data:
        data_object.save(self.editable_c2m_path)
        time_edit_old = os.path.getmtime(self.editable_c2m_path)
        time_edit_new = time_edit_old
        while time_edit_new == time_edit_old:
            time_edit_new = os.path.getmtime(self.editable_c2m_path)
            time.sleep(self.refresh_time)
        data_object_new = Data()
        data_object_new.load(self.editable_c2m_path)
        return data_object_new

    def check(self, data_object):
        data_object = update_ea_d(data_object)
        corruption_info = tuple(self._get_corruption_info(data_object))
        if len(corruption_info) > 0:
            print(f"Please open {self.editable_c2m_path} in the external editor.")
        while len(corruption_info) > 0:

            sector_info = corruption_info[0]
            print(f"(Corruptions remaining: {len(corruption_info)}) " +\
                  f"Refresh sectors near {sector_info[0]} at terrain type {sector_info[1][2]}.")
            data_object_new = self._await_c2m_edit(data_object)
            data_object_new = update_ea_d(data_object_new)
            if not self._simplify_and_compare(data_object, data_object_new):
                print(f"Primary data was not preserved. Please open the map again.")
            corruption_info = tuple(self._get_corruption_info(data_object_new))
        print("No corruptions were found.")

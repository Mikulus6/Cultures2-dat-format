from scripts.colormap import ColorMap, load_colormap_from_pcx_data
from supplements.read import read
from supplements.external import palettes

vertexcolors_path = "data\\engine2d\\bin\\palettes\\misc\\vertexcolors.pcx"
try:                      vertexcolors = load_colormap_from_pcx_data(read(vertexcolors_path, "rb"))
except FileNotFoundError: vertexcolors = ColorMap()

# num_of_players, palette_index = 10, 24
# players_colormap = ColorMap()
# for player_id in range(1, num_of_players+1):
#     pcx_path = palettes[f"human_Player{player_id:02d}"]["gfxfile"]
#     players_colormap[player_id] = load_colormap_from_pcx_data(read(pcx_path, "rb"))[palette_index]

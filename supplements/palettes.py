from scripts.colormap import ColorMap, load_colormap_from_pcx_data
from supplements.read import read

vertexcolors_path = "data\\engine2d\\bin\\palettes\\misc\\vertexcolors.pcx"

try:                      vertexcolors = load_colormap_from_pcx_data(read(vertexcolors_path, "rb"))
except FileNotFoundError: vertexcolors = ColorMap()

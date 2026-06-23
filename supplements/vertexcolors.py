from scripts.colormap import load_colormap_from_pcx_data
from supplements.read import read

vertexcolors_path = "data\\engine2d\\bin\\palettes\\misc\\vertexcolors.pcx"
vertexcolors = load_colormap_from_pcx_data(read(vertexcolors_path, "rb"))

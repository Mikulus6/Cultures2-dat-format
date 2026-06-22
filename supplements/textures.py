from io import BytesIO
import os
from math import sqrt
import numpy as np
from PIL import Image, ImageDraw
from scripts.colormap import ColorMap, find_closest_color
from supplements.patterns import pattern
from supplements.read import read

textures_path_free = "data_v\\ve_graphics\\textures1\\free"
textures_path_sys  = "data_v\\ve_graphics\\textures1\\sys"

def get_average_color(image: Image.Image) -> tuple:
    img_array = np.array(image)
    non_transparent_pixels = img_array[:, :, :3][img_array[:, :, 3] > 0]

    # Arithmetic mean is not the correct way to average a set of colors in an RGB color space.
    # However, most of the textures are homogenous enough to make this fact negligible.
    # For further context watch this video: https://www.youtube.com/watch?v=LKnqECcg6Gw

    if len(non_transparent_pixels) > 0: return tuple(map(int, np.mean(non_transparent_pixels, axis=0).astype(int)))
    else:                               return None


def rect_bound(coordinates):
    min_x = float('inf')
    max_x = float('-inf')
    min_y = float('inf')
    max_y = float('-inf')

    for x, y in coordinates:
        if x < min_x: min_x = x
        if x > max_x: max_x = x
        if y < min_y: min_y = y
        if y > max_y: max_y = y

    return (min_x, max_x), (min_y, max_y)


def add_margin_to_trianges_corners(corners: tuple | list, *, margin: int = 0) -> list:

    center_of_area = ((corners[0][0] + corners[1][0] + corners[2][0]) // 3,
                      (corners[0][1] + corners[1][1] + corners[2][1]) // 3,)

    new_corners = []
    for corner in corners:
        vector = (corner[0] - center_of_area[0],
                  corner[1] - center_of_area[1])
        distance = sqrt(vector[0]**2 + vector[1]**2)
        try:
            versor = (vector[0] / distance,
                      vector[1] / distance)
        except ZeroDivisionError:
            new_corners.append(corner)
            continue

        new_corner = (round(corner[0] + versor[0] * margin),
                      round(corner[1] + versor[1] * margin))
        new_corners.append(new_corner)
    return new_corners


all_used_colors_in_textures = set()


class Texture:

    def __init__(self, pixel_coords, source_path):

        bounds_x, bounds_y = rect_bound(pixel_coords)
        self.size = (bounds_x[1] - bounds_x[0], bounds_y[1] - bounds_y[0])
        self.pixel_coords = tuple(map(lambda coords: (coords[0] - bounds_x[0],
                                                      coords[1] - bounds_y[0]), pixel_coords))

        image_path = os.path.join(source_path)
        bounds = (bounds_x[0], bounds_y[0], bounds_x[1], bounds_y[1])
        image_texture = Image.open(BytesIO(read(image_path, mode="rb"))).crop(bounds)

        transparent_color = tuple(image_texture.getpalette()[:3])

        image_texture = image_texture.convert('RGB')
        mask = Image.new("L", image_texture.size, 0)
        ImageDraw.Draw(mask).polygon(add_margin_to_trianges_corners(self.pixel_coords, margin=2), fill=255)

        all_used_colors_in_textures.update(set(image_texture.get_flattened_data()))

        self.image = Image.new("RGBA", image_texture.size, (0, 0, 0, 0))
        self.image.paste(image_texture, mask=mask)

        image_array = np.array(self.image)
        mask = (image_array[:, :, :3] == transparent_color).all(axis=-1)  # noqa
        image_array[mask] = [0, 0, 0, 0]
        self.image = Image.fromarray(image_array)
        self.average_color = get_average_color(self.image)


class Textures(dict):

    def __init__(self):
        super().__init__(dict())
        self.pygame_converted = False

    def load(self, source_dict: dict):
        super().clear()
        for pattern_id, source in source_dict.items():

                a_pixel_coords = self.flat_pixel_coords_to_pairs(source["GfxCoordsA"])
                b_pixel_coords = self.flat_pixel_coords_to_pairs(source["GfxCoordsB"])

                texture_a = Texture(a_pixel_coords, source["GfxTexture"])
                texture_b = Texture(b_pixel_coords, source["GfxTexture"])

                self[pattern_id] = {"a": texture_a, "b": texture_b}

    @staticmethod
    def flat_pixel_coords_to_pairs(pixel_coords):
        return (pixel_coords[0], pixel_coords[1]), \
               (pixel_coords[2], pixel_coords[3]), \
               (pixel_coords[4], pixel_coords[5])

    def load_colormap(self) -> ColorMap:
        _default_color = (0, 0, 0)
        colormap = ColorMap()
        for key, value in self.items():
            average_color_a = value["a"].average_color if value["a"].average_color is not None else _default_color
            average_color_b = value["b"].average_color if value["b"].average_color is not None else _default_color

            colormap[key] = ((average_color_a[0] + average_color_b[0]) // 2,
                             (average_color_a[1] + average_color_b[1]) // 2,
                             (average_color_a[2] + average_color_b[2]) // 2)

        colormap.deduplicate_colors()
        return colormap


patterndefs_textures = Textures()
patterndefs_textures.load(source_dict=pattern)
epm_colors_dict = patterndefs_textures.load_colormap()

safe_alpha_color = find_closest_color((255, 0, 255), excluded_colors=all_used_colors_in_textures)
del all_used_colors_in_textures

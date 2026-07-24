from math import floor
import numpy as np
from ..generic.external import patterns

# shadow kernel
shadow_kernel_center = (2, 0)
shadow_kernel = np.array([[0,     0, 4.5],
                          [-1.5,  0,   0],
                          [ 0, -4.5, 1.5]])

# linear interpolation
max_value_dark = 60
min_value_bright = 200
inversed_slope = 4
intercept_dark = 46
intercept_bright = 150
upper_bound = 255
lower_bound = 4

# miscellaneous factors
default_light_value = 127
round_fix = 0.001

# terrain without brightness
force_dark_patterns = [pattern["EditName"] for pattern in patterns.values() if pattern["LogicType"] == 0]

def convolve_hexagonal_2d(input_array, kernel_array, kernel_center=(0, 0), dtype=np.int32):
    input_height, input_width = input_array.shape
    kernel_height, kernel_width = kernel_array.shape

    output_array = np.zeros(shape=input_array.shape, dtype=dtype)

    for y in range(input_height):
        for x in range(input_width):
            x_real, y_real = x - kernel_center[0], y - kernel_center[1]
            conv_item = 0
            for y_shift in range(0, kernel_height):
                for x_shift in range(0, kernel_width):
                    x_real_shifted = x_real + x_shift
                    y_real_shifted = y_real + y_shift

                    if y % 2 == 0 or y_shift % 2 == 0:  kernel_item = kernel_array[y_shift, x_shift]
                    elif x_shift != 0:                  kernel_item = kernel_array[y_shift, x_shift - 1]
                    else:                               kernel_item = 0

                    conv_item += kernel_item * input_array[y_real_shifted % input_array.shape[0],
                                                           x_real_shifted % input_array.shape[1]]
            output_array[y, x] = conv_item

    return output_array

def data_to_embr(data_object, *, local_kernel = shadow_kernel, local_kernel_center = shadow_kernel_center):

    embr = convolve_hexagonal_2d(data_object.lmhe, local_kernel, kernel_center=local_kernel_center, dtype=np.int32)
    embr += default_light_value

    for y in range(0, data_object.lsiz.height):
        for x in range(0, data_object.lsiz.width):
            if embr[y, x] >= min_value_bright: embr[y, x] = floor(embr[y, x] / inversed_slope + intercept_bright + round_fix)
            if embr[y, x] <= max_value_dark:   embr[y, x] = floor(embr[y, x] / inversed_slope + intercept_dark   - round_fix)

            embr[y, x] = max(min(embr[y, x], upper_bound), lower_bound)

            if y % 2 == 0:
                a_coordinates = ((x, y), (x, y-1), (x-1, y-1))
                b_coordinates = ((x, y), (x-1, y), (x-1, y-1))
            else:
                a_coordinates = ((x, y), (x, y-1), (x+1, y-1))
                b_coordinates = ((x, y), (x, y-1), (x-1, y))

            try:
                for coordinates in b_coordinates:
                    coordinates = (coordinates[0] % data_object.lsiz.width, coordinates[1] % data_object.lsiz.height)
                    if data_object.eapd[data_object.empb[*coordinates[::-1]]] in force_dark_patterns:
                        raise ValueError

                for coordinates in a_coordinates:
                    coordinates = (coordinates[0] % data_object.lsiz.width, coordinates[1] % data_object.lsiz.height)
                    if data_object.eapd[data_object.empa[*coordinates[::-1]]] in force_dark_patterns:
                        raise ValueError

            except ValueError:
                embr[y, x] = 0

    return embr.astype(dtype=data_object.lmhe.dtype)

def update_embr(data_object):
    data_object.embr = data_to_embr(data_object)
    return data_object


class StochasticGradientDescentShadowKernel:
    # supplementary class used for reversee-engineering shadow kernel in existing data files with SGD method

    def __init__(self, kernel_size, kernel_center=(0, 0)):
        self.kernel_ndarray = np.zeros(kernel_size, dtype=np.uint32)
        self.kernel_center = kernel_center
        self.last_error_value = float('inf')
        self.tests = list()

    @staticmethod
    def error_func(ndarray_1: np.ndarray, ndarray_2: np.ndarray, *, norm=1):
        return np.sum(np.pow(np.abs(np.pow(ndarray_1, norm) - np.pow(ndarray_2, norm)), 1/norm))

    def generate_descendants(self, num_of_descendants, noise_level: float):
        for _ in range(num_of_descendants):

            yield self.kernel_ndarray + np.random.uniform(-noise_level, noise_level,
                                        size=self.kernel_ndarray.size).reshape(self.kernel_ndarray.shape)

    def update_generation(self, num_of_descendants, *, noise_level = 1/256):

        for descendant in self.generate_descendants(num_of_descendants, noise_level):
            total_error = 0
            for data_object in self.tests:

                embr_old = np.copy(data_object.embr)
                embr_new = data_to_embr(data_object, local_kernel=descendant)

                total_error += self.error_func(embr_old, embr_new, norm=1)

            else:

                if total_error <= self.last_error_value:
                    self.kernel_ndarray = descendant
                    self.last_error_value = total_error

    def update_error(self):
        total_error = 0
        for data_object in self.tests:

            embr_old = np.copy(data_object.embr)
            embr_new = data_to_embr(data_object, local_kernel=self.kernel_ndarray,
                                                 local_kernel_center = self.kernel_center)

            total_error += self.error_func(embr_old, embr_new, norm=1)
        self.last_error_value = total_error

    def run(self, iterations: int | float = float('inf'),
            descendants_per_generation: int = 1, noise_level: float = 1/256):

        self.update_error()

        iteration_num = 0
        while iteration_num < iterations:
            iteration_num += 1

            print("current shadow kernel:")
            print(np.array2string(self.kernel_ndarray))
            print(f"total error: {self.last_error_value}")

            self.update_generation(num_of_descendants=descendants_per_generation,
                                   noise_level=noise_level)

import os
from data import Data
import grabber


solutions = "solutions"

for item in grabber.iterate_copies_paths():

    solution_dir = os.path.join(solutions, os.path.basename(item).split(".")[0])

    data_object = Data()
    data_object.load(item)
    data_object.extract(solution_dir)


import os
from data import Data
import grabber


solutions = "solutions"

for item in grabber.iterate_copies_paths():
    print(item)

    solution_dir = os.path.join(solutions, os.path.basename(item).split(".")[0])

    data_object = Data()
    data_object.load(item)
    data_object.extract(solution_dir)
    del data_object
    data_object = Data()
    data_object.pack(solution_dir)
    data_object.save("example.dat")  # TODO: check (simple) for laco and lafm does it work correctly (load->save = original w/o corrupted data)
    del data_object
    data_object = Data()
    data_object.load("example.dat")
    data_object.extract("example")

    input("...")


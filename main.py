import os
from data import Data
import grabber

# for x in (100, 120, 140, 160, 180, 200):
#     for y in (100, 120, 140, 160, 180, 200):
#        print(x, y, end=": ")
#         data_object = Data()
#         data_object.load(f"empty\\{x}x{y}.c2m")
#         data_object.save("example.dat")

# data_obj = Data()
# data_obj.load("C:\\Users\\Mikolaj\\Desktop\\Mapa.c2m")
# data_obj.save("example.dat")
# input()

solutions = "solutions"

for item in grabber.iterate_copies_paths():
    print(item)

    solution_dir = os.path.join(solutions, os.path.basename(item).split(".")[0])

    data_object = Data()
    data_object.load(item)

    # data_object.extract(solution_dir)
    # del data_object
    # data_object = Data()
    # data_object.pack(solution_dir)
    data_object.save("example.dat")  # TODO: check (simple) for laco and lafm does it work correctly (load->save = original w/o corrupted data)
    del data_object
    data_object = Data()
    data_object.load("example.dat")
    # data_object.extract("example")

    # input("...")


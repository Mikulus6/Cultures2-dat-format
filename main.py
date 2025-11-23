import os.path

import grabber
from scripts.buffer import BufferGiver, BufferTaker
from sections.run_length import run_length_decryption
from PIL import Image
from scripts.image import bytes_to_image, shorts_to_image
# grabber.save_copied_dats(dirs_dict_)

solutions = "solutions"

for item in grabber.iterate_copies_paths():
    with open(item, "rb") as file:
        buffer = BufferGiver(file.read())

    solution_dir = os.path.join(solutions, os.path.basename(item).split(".")[0])
    os.makedirs(solution_dir, exist_ok=True)

    map_width = 0
    map_height = 0

    while len(buffer) != 0:
        assert buffer.bytes(length=4)[::-1] == b"xioh" # According to Siguza this stands for "x input-output handler"
        name = buffer.string(length=4, encoding="ascii")[::-1]

        section_type = buffer.unsigned(length=4)
        length = buffer.unsigned(length=4)

        match section_type:
            case 0:
                assert name in ("logi", "lgmm", "emmm", "xend", "tend")
                assert buffer.unsigned(length=16) == length == 0
            case 1 | 2 | 4:
                assert (section_type != 2 or name == "lafm")\
                   and (section_type != 4 or name == "lasw")

                assert buffer.unsigned(length=4) == 0
                buffer.unsigned(length=4) # TODO: unknown
                assert buffer.unsigned(length=8) == 0
                section_buffer = BufferGiver(buffer.bytes(length=length))

                match name:
                    case "lsiz": # size
                        map_width  = section_buffer.unsigned(length=4)
                        map_height = section_buffer.unsigned(length=4)
                    case "lmhe" | "lmpa" | "lmpb" | "lmlt" | "lmlv" | "lmlp" | "lmco" | "lmtw" | "lmms" | "lmpr" |\
                         "lmwb" | "lmbb" | "lmro" | "lmsb" | "lmao":
                        bytes_2d_map = run_length_decryption(bytes(section_buffer))
                        if name != "lmao":
                            bytes_to_image(bytes_2d_map, os.path.join(solution_dir, f"{name}.png"),
                                           width=map_width if name in ("lmhe", "lmpa", "lmpb") else map_width*2)
                        else:
                            shorts_to_image(bytes_2d_map, os.path.join(solution_dir, f"{name}.png"), width=map_width*2)
                    case "laco" | "lasw" | "lafm":
                        pass
            case _:
                raise ValueError

        # print(name)
    # print("\n")
import os.path

import grabber
from scripts.buffer import BufferGiver, BufferTaker
from sections.run_length import run_length_decryption
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
                assert name in ("logi", "lgmm", "xend", "emmm", "tend")
                assert buffer.unsigned(length=16) == length == 0
            case 1 | 2 | 4:
                assert (section_type != 2 or name == "lafm")\
                   and (section_type != 4 or name == "lasw")

                assert buffer.unsigned(length=4) == 0
                buffer.unsigned(length=4) # TODO: unknown
                assert buffer.unsigned(length=8) == 0
                section_buffer = BufferGiver(buffer.bytes(length=length))

                if name == "lsiz":
                    map_width = section_buffer.unsigned(length=4)
                    map_height = section_buffer.unsigned(length=4)
                    continue

                if name in ("laco", "lasw", "lafm", "eapd", "eatd", "eald"):
                    continue

                bytes_2d_map = run_length_decryption(bytes(section_buffer))

                match name:
                    case "lmhe" | "lmpa" | "lmpb" | "embr" | "emm1" |\
                         "emt1" | "emt2" | "emt3" | "emt4" | "emvc":
                        bytes_per_vertex, width_multiplicator = 1, 1

                    case "lmlt" | "lmlv" | "lmlp" | "lmco" | "lmtw" |\
                         "lmms" | "lmpr" | "lmwb" | "lmbb" | "lmro" |\
                         "lmsb" | "lmhf" | "emmi":
                        bytes_per_vertex, width_multiplicator = 1, 2

                    case "empa" | "empb":
                        bytes_per_vertex, width_multiplicator = 2, 1

                    case "lmao" | "emla":
                        bytes_per_vertex, width_multiplicator = 2, 2

                    case _:
                        raise ValueError(f"Unknown section \"{name}\".")

                to_image_func = bytes_to_image if bytes_per_vertex == 1 else shorts_to_image
                to_image_func(bytes_2d_map, os.path.join(solution_dir, f"{name}.png"),
                              width=map_width*width_multiplicator)
            case _:
                raise ValueError

        # print(name)
    # print("\n")
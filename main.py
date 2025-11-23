import grabber
from scripts.buffer import BufferGiver, BufferTaker

# grabber.save_copied_dats(dirs_dict_)

for item in grabber.iterate_copies_paths():
    with open(item, "rb") as file:
        buffer = BufferGiver(file.read())

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
                        print(f"{map_width}x{map_height}")
                    case _:
                        pass
            case _:
                raise ValueError

        # print(name)
    # print("\n")
import grabber
from scripts.buffer import BufferGiver, BufferTaker

# grabber.save_copied_dats(dirs_dict_)

for item in grabber.iterate_copies_paths():
    with open(item, "rb") as file:
        buffer = BufferGiver(file.read())

    while len(buffer) != 0:
        assert buffer.bytes(length=4)[::-1] == b"xioh" # According to Siguza this stands for "x input-output handler"
        name = buffer.string(length=4, encoding="ascii")[::-1]

        buffer.unsigned(length=4)
        length = buffer.unsigned(length=4)

        match name:
            case "logi" | "lgmm" | "xend" | "tend":
                assert buffer.unsigned(length=16) == 0
                assert length == 0
            case _:
                buffer.unsigned(length=16)
                buffer.bytes(length=length)

        print(name)
    print("\n")
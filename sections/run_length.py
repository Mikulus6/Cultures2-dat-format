from scripts.buffer import BufferGiver, BufferTaker


def run_length_decryption(sequence: bytes, *, from_save_file: bool = False) -> bytes:
    buffer_input = BufferGiver(sequence)
    buffer_output = BufferTaker()

    assert buffer_input.unsigned(1) == 1
    number_of_entries = buffer_input.unsigned(4)
    assert buffer_input.string(4)[::-1] == "Xpck"
    assert (bytes_per_entry_indicator := int(buffer_input.string(1))) in (8, 6)
    assert buffer_input.string(3)[::-1] == "rle"
    number_of_tiles   = buffer_input.unsigned(4)
    assert number_of_entries == buffer_input.unsigned(4)
    assert number_of_entries + 5 == len(sequence)

    match bytes_per_entry_indicator:
        case 8: bytes_per_entry = 1
        case 6: bytes_per_entry = 2
        case _: raise ValueError

    while number_of_tiles > len(buffer_output):
        bits = buffer_input.binary(1)
        flag = int(bits[0]) == 1
        head = int(bits[1:], 2)

        if flag:
            buffer_output.bytes(buffer_input.bytes(bytes_per_entry) * head)
        else:
            buffer_output.bytes(buffer_input.bytes(bytes_per_entry * head))

    assert number_of_tiles == len(buffer_output)

    return bytes(buffer_output)

# TODO: inverse function can be copied and slightly modified from Cultures 1 Map Edtior project

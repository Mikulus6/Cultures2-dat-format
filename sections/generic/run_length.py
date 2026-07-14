from ..generic.imports import BufferGiver, BufferTaker


def run_length_decryption(sequence: bytes) -> bytes:
    buffer_input = BufferGiver(sequence)
    buffer_output = BufferTaker()

    assert buffer_input.unsigned(1) == 1
    number_of_entries = buffer_input.unsigned(4)
    assert buffer_input.string(4)[::-1] == "Xpck"
    assert (bytes_per_entry_indicator := int(buffer_input.string(1))) in (8, 6)
    assert buffer_input.string(3)[::-1] == "rle"
    number_of_tiles = buffer_input.unsigned(4)
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

        if flag: buffer_output.bytes(buffer_input.bytes(bytes_per_entry) * head)
        else:    buffer_output.bytes(buffer_input.bytes(bytes_per_entry * head))

    assert number_of_tiles == len(buffer_output)
    assert len(buffer_input) == 0

    return bytes(buffer_output)

def run_length_encryption(sequence: bytes, bytes_per_entry: int) -> bytes:
    buffer_input = BufferGiver(sequence)
    buffer_output = BufferTaker()
    buffer_output_data = BufferTaker()

    pre_compressed_data = []
    current_count = 1
    current_entry = buffer_input.bytes(bytes_per_entry)

    while len(buffer_input) > 0:
        new_entry = buffer_input.bytes(bytes_per_entry)
        if new_entry == current_entry and current_count < 127:
            current_count += 1
        else:
            if current_count == 1:
                if len(pre_compressed_data) != 0 and isinstance(pre_compressed_data[-1], bytes) and\
                   len(pre_compressed_data[-1]) < 127:
                    pre_compressed_data[-1] += current_entry
                else:
                    pre_compressed_data.append(current_entry)
            else:
                pre_compressed_data.append([current_count, current_entry])
            current_entry = new_entry
            current_count = 1

    pre_compressed_data.append([current_count, current_entry])

    for item in pre_compressed_data:
        if isinstance(item, bytes):
            buffer_output_data.unsigned(len(item)//bytes_per_entry, length=1)
            buffer_output_data.bytes(item)
        else:
            item_temp = bin(item[0])[2:]
            item_temp = "1" + "0" * (7 - len(item_temp)) + item_temp
            buffer_output_data.binary(item_temp)
            buffer_output_data.bytes(item[1])

    number_of_entries = len(buffer_output_data) + 16

    buffer_output.unsigned(1, length=1)
    buffer_output.unsigned(number_of_entries, length=4)
    buffer_output.string("Xpck"[::-1])
    buffer_output.string("8" if bytes_per_entry == 1 else "6")
    buffer_output.string("rle"[::-1])
    buffer_output.unsigned(len(sequence), length=4)
    buffer_output.unsigned(number_of_entries, length=4)
    buffer_output.bytes(bytes(buffer_output_data))
    return bytes(buffer_output)

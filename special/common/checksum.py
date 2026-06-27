def calculate_checksum(section_bytes: bytes) -> int:

    if len(section_bytes) == 0:
        return 0

    checksum = 0

    # Constant values a, b, c are coprime with exception that gcd(b, c) = 13.
    a = 1695929585
    b = 1876105387
    c = 1677611962

    for index, byte in enumerate(section_bytes):
        checksum = ((checksum * 256) | byte) % (2 ** 32)

        if index % 4 == 3:
            a = (a ^ b ^ checksum)   % (2 ** 32)
            b = ((b ^ checksum) + c) % (2 ** 32)

    return (checksum ^ a) % (2 ** 32)

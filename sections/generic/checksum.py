def calculate_checksum(section_bytes: bytes) -> int:

    if len(section_bytes) == 0:
        return 0

    checksum = 0

    # Initial values of a, b, c are coprime with exception that gcd(b, c) = 13.
    a = 1695929585
    b = 1876105387
    c = 1677611962

    for index, byte in enumerate(section_bytes):
        checksum = ((checksum * 0x100) | byte)  % 0x100000000

        if index % 4 == 3:
            a = (a ^ b ^ checksum)              % 0x100000000
            b = ((b ^ checksum) + c)            % 0x100000000

    return (checksum ^ a)                       % 0x100000000

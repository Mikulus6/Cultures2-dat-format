# All sections-specific external imports should be done via this file.

try:
    from supplements import BufferGiver, BufferTaker, patterns, points, transitions, landscapes
except FileNotFoundError:
    raise FileNotFoundError("Unable to find game files in the current working directory.")

class SpecialSection(type):
    def load(cls):
        raise NotImplementedError

    def to_bytes(cls):
        raise NotImplementedError

    def to_file(cls, filename):
        raise NotImplementedError

    def from_file(cls, filename):
        raise NotImplementedError

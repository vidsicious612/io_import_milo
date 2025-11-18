from . metadata import Metadata

class MoggClip:
    def __init__(self):
        self.version: int = 1
        self.metadata = Metadata()
        self.file: str = ""
        self.volume: float = 0.0
        self.loop: bool = True
        self.mogg: bytes = ()

    def read(self, reader):
        self.version = reader.int32()

        self.metadata.read(reader)

        self.file = reader.numstring()

        self.volume = reader.float32()

        self.loop = reader.milo_bool()

        if self.version > 0:
            mogg_size = reader.int32()
            
            self.mogg = reader.read_bytes(mogg_size)

        padding = reader.read_bytes(4)

        if padding != b"\xAD\xDE\xAD\xDE":
            raise Exception("Padding was not AD DE AD DE, read most likely failed.")

    def write(self, writer):
        writer.int32(self.version)

        self.metadata.write(writer)

        writer.numstring(self.file)

        writer.float32(self.volume)

        writer.milo_bool(self.loop)

        if self.version > 0:
            writer.int32(len(self.mogg))

            writer.write_bytes(self.mogg)
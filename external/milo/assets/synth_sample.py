from dataclasses import dataclass, field
from . metadata import Metadata
from . sample_data import SampleData

@dataclass
class SynthSample:
    version: int = 0
    metadata: Metadata = field(default_factory=Metadata)
    file: str = ""
    looped: bool = False
    loop_start_sample: int = 0
    loop_start_end: int = -1
    sample_data: SampleData = field(default_factory=SampleData)

    def read(self, reader):
        self.version = reader.int32()

        self.metadata.read(reader)

        self.file = reader.numstring()

        if self.version < 6:
            self.looped = reader.milo_bool()

            self.loop_start_sample = reader.int32()

            if self.version > 2:
                self.loop_start_end = reader.int32()

        if self.version == 0x10005:
            reader.seek(21)

            reader.little_endian = True

        self.sample_data.read(reader)

        if self.version == 0x10005:
            reader.little_endian = False

        padding = reader.read_bytes(4)

        if padding != b"\xAD\xDE\xAD\xDE":
            raise Exception("Padding was not AD DE AD DE, read most likely failed.")
    
    def write(self, writer):
        writer.int32(self.version)

        self.metadata.write(writer)

        writer.numstring(self.file)

        if self.version < 6:
            writer.milo_bool(self.looped)

            writer.int32(self.loop_start_sample)

            if self.version > 2:
                writer.int32(self.loop_start_end)

        self.sample_data.write(writer)
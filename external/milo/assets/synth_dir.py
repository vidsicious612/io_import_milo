from dataclasses import dataclass, field
from . object_dir import ObjectDir

@dataclass
class SynthDir:
    version: int = 1
    object_dir: ObjectDir = field(default_factory=ObjectDir)

    def read(self, reader, directory_meta, entry, super: bool) -> None:
        self.version = reader.int32()

        self.object_dir.read(reader, directory_meta, entry, True)
        
        if super == False:
            padding = reader.read_bytes(4)

            if padding != b"\xAD\xDE\xAD\xDE":
                raise Exception("Padding was not AD DE AD DE, read most likely failed.")
    
    def write(self, writer):
        writer.int32(self.version)

        self.object_dir.write(writer)
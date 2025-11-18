from dataclasses import dataclass, field
from . character import Character

@dataclass
class BandCharacter:
    version: int = 1
    character: Character = field(default_factory=Character)
    play_flags: int = 0
    tempo: str = ""

    def read(self, reader, directory_meta, entry, super: bool):
        self.version = reader.int32()

        self.character.read(reader, directory_meta, entry, True)

        if self.version == 1:
            if super == False:
                padding = reader.read_bytes(4)

                if padding != b"\xAD\xDE\xAD\xDE":
                    raise Exception("Padding was not AD DE AD DE, read most likely failed.")
                
                return
                
        self.play_flags = reader.uint32()

        self.tempo = reader.numstring()

        if self.version < 6:
            if self.version < 4:
                unk_int_1 = reader.int32()

                if self.version < 3:
                    unk_string_1 = reader.numstring()

            unk_string_2 = reader.numstring()

        if super == False:
            padding = reader.read_bytes(4)

            if padding != b"\xAD\xDE\xAD\xDE":
                raise Exception("Padding was not AD DE AD DE, read most likely failed.")

    def write(self, writer):
        writer.int32(self.version)

        self.character.write(writer)
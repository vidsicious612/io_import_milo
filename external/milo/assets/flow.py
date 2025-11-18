from dataclasses import dataclass, field
from . object_dir import ObjectDir

@dataclass
class Flow:
    version: int = 0
    obj_dir: ObjectDir = field(default_factory=ObjectDir)
    strings: list[str] = field(default_factory=list)
    
    def read(self, reader, directory_meta, is_proxy: bool):
        self.version = reader.int32()

        self.obj_dir.read(reader, directory_meta, "Flow", is_proxy)

        if is_proxy == False:
            end = reader.read_bytes(4)
        else:
            always_0 = reader.int32()
            always_0_2 = reader.int32()

            unk_int = reader.int32()

            string_count_1 = reader.int32()

            for _ in range(string_count_1):
                self.strings.append(reader.numstring())

            unk_int_2 = reader.int32()

            unk_bool = reader.milo_bool()

            string_count_2 = reader.int32()

            for _ in range(string_count_2):
                self.strings.append(reader.numstring())
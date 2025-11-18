from dataclasses import dataclass, field
from . object_dir import ObjectDir

@dataclass
class CharClipPtr:
    clip: str = ""
    
    def read(self, reader):
        self.clip = reader.numstring()

        unk_1 = reader.uint32()
        unk_2 = reader.uint32()

@dataclass
class CharClipSet:
    version: int = 0
    object_dir: ObjectDir = field(default_factory=ObjectDir)
    char_file_path: str = ""
    preview_clip: str = ""
    filter_flags: int = 0
    bpm: int = 0
    preview_walk: bool = False
    still_clip: str = ""
    graph_path: str = ""
    char_clip_ptrs: list[CharClipPtr] = field(default_factory=list)

    def read(self, reader, directory_meta, entry, super: bool):
        char_clip_sample_count = 0

        for entry in directory_meta.entries:
            if entry.type == "CharClipSamples":
                char_clip_sample_count += 1
        
        self.version = reader.int32()

        self.object_dir.read(reader, directory_meta, entry, True)

        if entry.is_proxy == True:
            padding = reader.read_bytes(4)

            if padding != b"\xAD\xDE\xAD\xDE":
                raise Exception("Padding was not AD DE AD DE, read most likely failed.")
            
            return

        if self.version < 17:
            unk_int_1 = reader.int32()
            unk_int_2 = reader.int32()
        
        if (self.version == 15) or (self.version == 16):
            unk_int_3 = reader.int32()

        if self.version < 9:
            self.graph_path = reader.numstring()

        if self.version < 6:
            unk_string = reader.numstring()

        if self.version < 7:
            unk_int_4 = reader.int32()

        if self.version < 24:
            for _ in range(char_clip_sample_count):
                char_clip_ptr = CharClipPtr()
                char_clip_ptr.read(reader)

                self.char_clip_ptrs.append(char_clip_ptr)

        if self.version > 12:
            if self.version < 24:
                unk_bool_1 = reader.milo_bool()

                if self.version > 18:
                    unk_bool_2 = reader.milo_bool()
        else:
            unk_string_list_count = reader.int32()

            for _ in range(unk_string_list_count):
                unk_string = reader.numstring()

        if (self.version >= 5) and (self.version <= 23):
            unk_strings_count_1 = reader.int32()

            for _ in range(unk_strings_count_1):
                unk_string = reader.numstring()

            unk_string_count_2 = reader.int32()

            for _ in range(unk_string_count_2):
                unk_string = reader.numstring()

            unk_bool_3 = reader.milo_bool()
        
        if (self.version >= 10) and (self.version <= 23):
            unk_string_2 = reader.numstring()

            unk_int_5 = reader.int32()

        if self.version == 11:
            unk_bool_4 = reader.milo_bool()

        if self.version > 17:
            self.char_file_path = reader.numstring()

            self.preview_clip = reader.numstring()
        if self.version > 19:
            self.filter_flags = reader.uint32()
        if self.version > 20:
            self.bpm = reader.int32()
        if self.version > 21:
            self.preview_walk = reader.milo_bool()
        if self.version > 22:
            self.still_clip = reader.numstring()

        if super == False:
            padding = reader.read_bytes(4)

            if padding != b"\xAD\xDE\xAD\xDE":
                raise Exception("Padding was not AD DE AD DE, read most likely failed.")
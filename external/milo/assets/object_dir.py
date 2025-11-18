from dataclasses import dataclass, field
from enum import Enum
from . dtb import DTB
from . metadata import Metadata

class ReferenceType(Enum):
    kInlineNever = 0
    kInlineCached = 1
    kInlineAlways = 2
    kInlineCachedShared = 3

@dataclass
class ObjectDir:
    version: int = 0
    metadata: Metadata = field(default_factory=Metadata)
    viewports: list[tuple] = field(default_factory=list)
    curr_viewport_index: int = 0
    inline_proxy: bool = True
    proxy_file: str = ""
    current_camera: str = ""
    subdirs: list[str] = field(default_factory=list)
    inline_subdir: ReferenceType = ReferenceType.kInlineNever
    inline_subdir_names: list[str] = field(default_factory=list)
    reference_types: list[ReferenceType] = field(default_factory=list)
    reference_types_alt: list[ReferenceType] = field(default_factory=list)
    inline_subdirs: list = field(default_factory=list)
    unknown_cam_reference: str = ""

    def get_dir_path(self, dir_path: str, filepath: str):
        import os
        from pathlib import Path

        if dir_path.startswith("../../../"):
            current_path = Path(filepath).parent

            up_count = 4

            dir_path = dir_path.replace("../../../", "")
        elif dir_path.startswith("../../"):
            current_path = Path(filepath).parent

            up_count = 3

            dir_path = dir_path.replace("../../", "")
        elif dir_path.startswith("../"):
            current_path = Path(filepath).parent

            up_count = 2

            dir_path = dir_path.replace("../", "")
        else:
            current_path = Path(filepath).parent

            up_count = 0

            dir_path = dir_path.replace("/", "\\")

            dirname = Path(dir_path).parent
            basename = Path(dir_path).name

            if len(dirname) > 0:
                up_count = 1

        dir_path = dir_path.replace("/", "\\")

        if up_count > 0:
            dirname = Path(dir_path).parent
            basename = Path(dir_path).name
            
            for _ in range(up_count):
                current_path = Path(current_path).parent
            
            current_path = Path.joinpath(current_path, dirname)
            os.chdir(current_path)

        for root, dirs, files in os.walk(current_path):
            for file in files:
                if basename in file: 
                    final_path = os.path.join(root, file)

        return final_path

    def read(self, reader, directory_meta, entry, super: bool):
        from .. directory_meta import DirectoryMeta

        self.version = reader.int32()

        if self.version < 22:
            if (self.version >= 2) and (self.version < 17):
                self.metadata.read(reader)
        else:
            if self.version != 26:
                self.metadata.revision = reader.int32()
                self.metadata.metadata_type = reader.numstring()
            else:
                self.metadata.read(reader)
        
        if self.version > 1:
            if self.version >= 27:
                unk_1 = reader.int32()
                unk_2 = reader.int32()

            viewport_count = reader.int32()

            for _ in range(viewport_count):
                self.viewports.append(reader.matrix())

                if self.version <= 17:
                    padding = reader.read_bytes(4)

            self.curr_viewport_index = reader.int32()

        if self.version > 12:
            if self.version > 19:
                if self.version < 28:
                    self.inline_proxy = reader.milo_bool()
                else:
                    self.inline_proxy = reader.ubyte()

            self.proxy_file = reader.numstring()

        if (self.version >= 2) and (self.version < 11):
            some_object_1 = reader.numstring()

        if (self.version >= 4) and (self.version < 11):
            self.current_camera = reader.numstring()

        if self.version == 5:
            ignore_string = reader.numstring()

        if self.version > 2:
            subdir_count = reader.int32()

            self.subdirs = [reader.numstring() for _ in range(subdir_count)]

            if self.version >= 21:
                self.inline_subdir = ReferenceType(reader.ubyte())

                inline_subdir_count = reader.int32()

                for _ in range(inline_subdir_count):
                    self.inline_subdir_names.append(reader.numstring())

                if self.version >= 26:
                    for _ in range(inline_subdir_count):
                        self.reference_types.append(ReferenceType(reader.ubyte()))

                    for _ in range(inline_subdir_count):
                        self.reference_types_alt.append(ReferenceType(reader.ubyte()))
                        
                for _ in range(inline_subdir_count):
                    dir_meta = DirectoryMeta()
                    dir_meta.platform = directory_meta.platform

                    if (len(self.reference_types) > 0) and (len(self.reference_types_alt) > 0):
                        if (self.reference_types[0] == ReferenceType.kInlineCached) and (self.reference_types_alt[0] == ReferenceType.kInlineCached):
                            unknown = reader.milo_bool()
                        else:
                            dir_meta.read(reader)
                            
                            self.inline_subdirs.append(dir_meta)

                            for e in dir_meta.entries:
                                directory_meta.inline_entries.append(e)
                    else:
                        dir_meta.read(reader)
                        
                        self.inline_subdirs.append(dir_meta)

                        for e in dir_meta.entries:
                            directory_meta.inline_entries.append(e)

        if self.version < 19:
            if self.version == 15:
                ignore_string_2 = reader.numstring()
            else:
                ignore_string_3 = reader.numstring()

        if (entry.type == "WorldInstance") and (self.version > 20):
            entry.has_persistent_objects = reader.milo_bool()

            if entry.is_proxy == True:
                return
            
        some_string = reader.numstring()
        self.unknown_cam_reference = reader.numstring()

        if self.version < 22:
            if self.version > 16:
                self.metadata.read(reader)
        else:
            dtb = DTB()
            dtb.read(reader)

            self.metadata.props = dtb

            if directory_meta.version >= 25:
                self.metadata.note = reader.numstring()

        if super == False:
            padding = reader.read_bytes(4)

            if padding != b"\xAD\xDE\xAD\xDE":
                raise Exception("Padding was not AD DE AD DE, read most likely failed.")

    def write(self, writer):
        writer.int32(self.version)

        writer.int32(len(self.viewports))

        for viewport in self.viewports:
            writer.matrix(*viewport)

        writer.int32(self.curr_viewport_index)

        writer.milo_bool(self.inline_proxy)

        writer.numstring(self.proxy_file)

        writer.int32(len(self.subdirs))

        for subdir in self.subdirs:
            writer.numstring(subdir)

        writer.numstring("")
        writer.numstring("")

        self.metadata.write(writer)
    
    def from_blender(self, bpy_self):
        from .. default_transform import DEFAULT_TRANSFORM

        self.version = 20 if bpy_self.game_selection == "RB1" else 22
        
        for _ in range(7):
            self.viewports.append(DEFAULT_TRANSFORM)
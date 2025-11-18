from dataclasses import dataclass, field
from . metadata import Metadata
from . draw import Draw

@dataclass
class OldMultiMeshInstance:
    old_mm_count: int = 0
    old_xfm_list: list[tuple] = field(default_factory=list)
    old_color_list: list[tuple] = field(default_factory=list)
    
    def read(self, reader, version: int):
        self.old_mm_count = reader.int32()

        for _ in range(self.old_mm_count):
            self.old_xfm_list.append(reader.matrix())

            if version > 6:
                self.old_color_list.append(reader.vec4f())

@dataclass
class CharDef:
    character: str = ""
    height: float = 0.0
    density: float = 0.0
    radius: float = 0.0
    use_random_color: bool = False
    
    def read(self, reader, version: int):
        self.character = reader.numstring()

        self.height = reader.float32()

        self.density = reader.float32()

        if version > 1:
            self.radius = reader.float32()

        if version > 8:
            self.use_random_color = reader.milo_bool()  

@dataclass
class WorldCrowd:
    version: int = 0
    draw: Draw = field(default_factory=Draw)
    target_mesh: str = ""
    characters: list[CharDef] = field(default_factory=list)
    environ: str = ""
    environ3D: str = ""
    old_mm: list[OldMultiMeshInstance] = field(default_factory=list)
    transforms: list[tuple] = field(default_factory=list)
    modify_stamp: int = 0
    force_3D_crowd: bool = False
    show_3D_only: bool = False
    focus: str = ""
    metadata: Metadata = field(default_factory=Metadata)

    def read(self, reader, directory_meta):
        self.version = reader.int32()

        self.draw.read(reader, directory_meta)

        self.target_mesh = reader.numstring()

        if self.version < 3:
            unk_int_1 = reader.uint32()

        num_characters = reader.uint32()

        if self.version < 8:
            unk_bool_1 = reader.milo_bool()

        char_count = reader.uint32()

        for _ in range(char_count):
            char_def = CharDef()
            char_def.read(reader, self.version)

            self.characters.append(char_def)

        if self.version > 6:
            self.environ = reader.numstring()

        if self.version > 9:
            self.environ3D = reader.numstring()

        if self.version > 1:
            if self.version < 14:
                for i in range(char_count):
                    old_multi_mesh_instance = OldMultiMeshInstance()
                    old_multi_mesh_instance.read(reader, self.version)
                    
                    self.old_mm.append(old_multi_mesh_instance)
            else:
                transform_count = []

                for i in range(char_count):
                    transform_count.append(reader.int32())

                    if transform_count[i] > 0:
                        transforms_list = []

                        for _ in range(transform_count[i]):
                            xfm = reader.matrix()

                            transforms_list.append(xfm)
                        
                        for transform in transforms_list:
                            self.transforms.append(transform)

        if self.version > 4:
            self.modify_stamp = reader.int32()

        if self.version > 12:
            self.force_3D_crowd = reader.milo_bool()

        if self.version > 5:
            self.show_3D_only = reader.milo_bool()

        if self.version > 11:
            self.focus = reader.numstring()     

        if self.version >= 16:
            always_ff = reader.uint32()

            some_int = reader.int32()

        self.metadata.read(reader)

        padding = reader.read_bytes(4)

        if padding != b"\xAD\xDE\xAD\xDE":
            raise Exception("Padding was not AD DE AD DE, read most likely failed.")
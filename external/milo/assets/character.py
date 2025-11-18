from enum import Enum
from dataclasses import dataclass, field
from . rnd_dir import RndDir

class ForceLODEnum(Enum):
    kLODPerFrame = -1
    kLOD0 = 0
    kLOD1 = 1
    kLOD2 = 2

@dataclass
class LOD:
    screen_size: float = 0.0
    group: str = ""
    trans_group: str = ""
    opaque_list: list[str] = field(default_factory=list)
    translucent_list: list[str] = field(default_factory=list)

    def read(self, reader, version: int):
        self.screen_size = reader.float32()

        if version < 18:
            self.group = reader.numstring()

            if version >= 15:
                self.trans_group = reader.numstring()
        else:
            opaque_count = reader.int32()

            for _ in range(opaque_count):
                self.opaque_list.append(reader.numstring())

            translucent_count = reader.int32()

            for _ in range(translucent_count):
                self.translucent_list.append(reader.numstring())

@dataclass
class CharacterTesting:
    version: int = 0
    driver: str = ""
    clip_1: str = ""
    clip_2: str = ""
    teleport_to: str = ""
    teleport_from: str = ""
    dist_map: str = "none"
    transition: int = 0
    cycle_transition: bool = False
    internal_transition: int = 0
    metronome: bool = False
    zero_travel: bool = False
    show_screen_size: bool = False
    foot_extents: bool = False
    clip_2_real_time: bool = False
    bpm: int = 120

    def read(self, reader):
        self.version = reader.int32()
        
        self.driver = reader.numstring()

        self.clip_1 = reader.numstring()
        self.clip_2 = reader.numstring()

        self.teleport_to = reader.numstring()
        self.teleport_from = reader.numstring()

        self.dist_map = reader.numstring()

        if self.version < 6:
            return
        
        self.transition = reader.uint32()
        self.cycle_transition = reader.milo_bool()
        self.internal_transition = reader.uint32()

        if self.version < 10:
            unk_1 = reader.uint32()

        self.metronome = reader.milo_bool()

        self.zero_travel = reader.milo_bool()

        self.show_screen_size = reader.milo_bool()

        if self.version < 12:
            unk_string = reader.numstring()

        self.foot_extents = reader.milo_bool()

        if self.version < 15:
            self.clip_2_real_time = reader.milo_bool()

            self.bpm = reader.int32()

        if self.version == 6:
            return
        
        if self.version < 14:
            unk_2 = reader.uint32()

            unk_float = reader.float32()

        if (self.version < 14) and (self.version > 9):
            unk_string_2 = reader.numstring()

@dataclass
class Character:
    version: int = 0
    rnd_dir: RndDir = field(default_factory=RndDir)
    lods: list[LOD] = field(default_factory=list)
    shadows: list[str] = field(default_factory=list)
    self_shadow: bool = False
    sphere_base: str = ""
    bounding: tuple = ()
    frozen: bool = False
    min_lod: ForceLODEnum = ForceLODEnum.kLODPerFrame
    translucent_group: str = ""
    char_test: CharacterTesting = field(default_factory=CharacterTesting)

    def read(self, reader, directory_meta, entry, super: bool):
        self.version = reader.int32()

        self.rnd_dir.read(reader, directory_meta, entry, True)

        if (self.version < 4) or (entry.is_proxy == False):
            lod_count = reader.int32()

            for _ in range(lod_count):
                lod = LOD()
                lod.read(reader, self.version)

                self.lods.append(lod)

            if self.version < 18:
                self.shadows.append(reader.numstring())
            else:
                shadow_count = reader.uint32()

                for _ in range(shadow_count):
                    self.shadows.append(reader.numstring())
            
            if self.version > 2:
                self.self_shadow = reader.milo_bool()

            if self.version > 4:
                self.sphere_base = reader.numstring()

            if self.version <= 9:
                return
            
            if self.version > 10:
                self.bounding = reader.vec4f()

            if self.version > 12:
                self.frozen = reader.milo_bool()

            if self.version > 14:
                self.min_lod = ForceLODEnum(reader.int32())

            if self.version > 16:
                self.translucent_group = reader.numstring()

            self.char_test.read(reader)
        elif self.version > 15:
            self.char_test.read(reader)

        if super == False:
            padding = reader.read_bytes(4)

            if padding != b"\xAD\xDE\xAD\xDE":
                raise Exception("Padding was not AD DE AD DE, read most likely failed.")

    def write(self, writer, super: bool):
        writer.int32(self.version)

        self.rnd_dir.write(writer)

        if super == False:
            writer.write_bytes(b"\xAD\xDE\xAD\xDE")

    def import_to_blender(self, name: str):
        import bpy
        
        character_obj = bpy.data.objects.get(name)

        if not character_obj:
            character_obj = bpy.data.objects.new(name, None)

            bpy.context.collection.objects.link(character_obj)
            
            character_obj.empty_display_size = 2
            character_obj.empty_display_type = "PLAIN_AXES"

    def from_blender(self, bpy_self):
        self.version = 12 if bpy_self.game_selection == "RB1" else 15

        self.rnd_dir.from_blender(bpy_self)

        self.self_shadow = True
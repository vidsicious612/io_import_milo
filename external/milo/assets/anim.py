from dataclasses import dataclass, field
from enum import Enum

class Rate(Enum):
    k30_fps = 0
    k480_fpb = 1
    k30_fps_ui = 2
    k1_fpb = 3
    k30_fps_tutorial = 4

@dataclass
class AnimEntry:
    name: str = ""
    f1: float = 0.0
    f2: float = 0.0

    def read(self, reader) -> None:
        self.name = reader.numstring()

        self.f1 = reader.float32()
        self.f2 = reader.float32()

    def write(self, writer):
        writer.numstring(self.name)

        writer.float32(self.f1)
        writer.float32(self.f2)

@dataclass
class Anim:
    version: int = 0
    frame: float = 0.0
    rate: Rate = Rate.k30_fps
    anim_entries: list[AnimEntry] = field(default_factory=list)
    anims: list[str] = field(default_factory=list)

    def read(self, reader) -> None:
        self.version = reader.int32()

        if self.version > 1:
            self.frame = reader.float32()
            
        if self.version < 4:
            if self.version > 2:
                uc = reader.ubyte()

                self.rate = Rate.k30_fps if uc == 0 else Rate.k480_fpb
        else:
            self.rate = Rate(reader.uint32())

            return
        
        if self.version < 1:
            anim_entry_count = reader.int32()

            for _ in range(anim_entry_count):
                anim_entry = AnimEntry()
                anim_entry.read(reader)

                self.anim_entries.append(anim_entry)
                
            anim_count = reader.int32()
            
            for _ in range(anim_count):
                self.anims.append(reader.numstring())

    def write(self, writer):
        writer.int32(self.version)

        if self.version > 1:
            writer.float32(self.frame)

        if self.version < 4:
            if self.version > 2:
                writer.ubyte(0 if self.rate == Rate.k30_fps else 1)
        else:
            writer.uint32(self.rate.value)

            return
        
        if self.version < 1:
            writer.int32(len(self.anim_entries))

            for anim_entry in self.anim_entries:
                anim_entry.write(writer)

            writer.int32(len(self.anims))

            for anim in self.anims:
                writer.numstring(anim)

    def from_blender(self, bpy_self):
        if bpy_self.game_selection != "GH1":
            self.version = 4
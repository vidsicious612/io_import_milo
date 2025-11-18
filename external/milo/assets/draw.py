from dataclasses import dataclass, field
from enum import Enum

class OverrideIncludeInDepthOnlyPass(Enum):
    kOverrideIncludeInDepthOnlyPass_None = 0
    kOverrideIncludeInDepthOnlyPass_Include = 1
    kOverrideIncludeInDepthOnlyPass_DontInclude = 2

@dataclass
class Draw:
    version: int = 0
    showing: bool = True
    draw_objects: list[str] = field(default_factory=list)
    sphere: tuple = (0.0, 0.0, 0.0, 0.0)
    draw_order: float = 0.0
    override_include_in_depth_only_pass: OverrideIncludeInDepthOnlyPass = OverrideIncludeInDepthOnlyPass.kOverrideIncludeInDepthOnlyPass_None

    def read(self, reader, directory_meta):
        self.version = reader.int32()

        self.showing = reader.milo_bool()

        if self.version < 2:
            draw_count = reader.int32()

            for _ in range(draw_count):
                if directory_meta.version <= 6:
                    self.draw_objects.append(reader.string())
                else:
                    self.draw_objects.append(reader.numstring())

        if self.version > 0:
            self.sphere = reader.vec4f()

        if self.version > 2:
            self.draw_order = reader.float32()

        if self.version >= 4:
            self.override_include_in_depth_only_pass = OverrideIncludeInDepthOnlyPass(reader.uint32())

    def write(self, writer):
        writer.int32(self.version)

        writer.milo_bool(self.showing)

        if self.version < 2:
            writer.int32(0)

        if self.version > 0:
            writer.vec4f(self.sphere)

        if self.version > 2:
            writer.float32(self.draw_order)

        if self.version >= 4:
            writer.uint32(self.override_include_in_depth_only_pass.value)

    def from_blender(self, bpy_self):
        if bpy_self.game_selection != "GH1":
            self.version = 3
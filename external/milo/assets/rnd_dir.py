from dataclasses import dataclass, field
from . anim import Anim
from . draw import Draw
from . object_dir import ObjectDir
from . poll import Poll
from . trans import Trans

@dataclass
class RndDir:
    version: int = 0
    object_dir: ObjectDir = field(default_factory=ObjectDir)
    anim: Anim = field(default_factory=Anim)
    draw: Draw = field(default_factory=Draw)
    trans: Trans = field(default_factory=Trans)
    poll: Poll = field(default_factory=Poll)
    environ: str = ""
    test_event: str = ""

    def read(self, reader, directory_meta, entry, super: bool):
        self.version = reader.int32()

        self.object_dir.read(reader, directory_meta, entry, True)

        if entry.is_proxy == True:
            return_list = ["RndDir", "Character"]

            if (entry.type == "WorldInstance") and (entry.obj.version == 0):
                return_list.append(entry.type)

            if entry.type not in return_list:
                return

        self.anim.read(reader)
        self.draw.read(reader, directory_meta)
        self.trans.read(reader, True, directory_meta)

        if self.version < 9:
            self.poll.read(reader)

            some_string_1 = reader.numstring()
            some_string_2 = reader.numstring()
        else:
            self.environ = reader.numstring()

            if self.version >= 10:
                self.test_event = reader.numstring()

        if self.version == 6:
            for _ in range(8):
                some_float = reader.float32()

        if super == False:
            padding = reader.read_bytes(4)
            
            if padding != b"\xAD\xDE\xAD\xDE":
                raise Exception("Padding was not AD DE AD DE, read most likely failed.")

    def write(self, writer, super: bool):
        writer.int32(self.version)

        self.object_dir.write(writer)

        self.anim.write(writer)
        self.draw.write(writer)
        self.trans.write(writer, True)

        if self.version > 9:
            writer.numstring(self.environ)

            if self.version >= 10:
                writer.numstring(self.test_eent)
        
        if super == False:
            writer.write_bytes(b"\xAD\xDE\xAD\xDE")

    def from_blender(self, bpy_self):
        import mathutils

        self.version = 10

        self.object_dir.from_blender(bpy_self)
        self.anim.from_blender(bpy_self)
        self.draw.from_blender(bpy_self)
         
        self.trans.from_blender(mathutils.Matrix.Identity(4), mathutils.Matrix.Identity(4), "", bpy_self)
from dataclasses import dataclass, field
from enum import Enum
from . metadata import Metadata
from .. default_transform import DEFAULT_TRANSFORM

class Constraint(Enum):
    kConstraintNone = 0
    kConstraintLocalRotate = 1
    kConstraintParentWorld = 2
    kConstraintLookAtTarget = 3
    kConstraintShadowTarget = 4
    kConstraintBillboardZ = 5
    kConstraintBillboardXZ = 6
    kConstraintBillboardXYZ = 7
    kConstraintFastBillboardXYZ = 8

@dataclass
class Trans:
    version: int = 0
    metadata: Metadata = field(default_factory=Metadata)
    local_xfm: tuple = DEFAULT_TRANSFORM
    world_xfm: tuple = DEFAULT_TRANSFORM
    trans_objects: list[str] = field(default_factory=list)
    constraint: Constraint = Constraint.kConstraintNone
    target: str = ""
    preserve_scale: bool = False
    parent: str = ""

    def read(self, reader, super: bool, directory_meta):
        self.version = reader.int32()
        
        if super == False:
            self.metadata.read(reader)

        self.local_xfm = reader.matrix()
        self.world_xfm = reader.matrix()

        if self.version < 9:
            trans_count = reader.int32()

            for _ in range(trans_count):
                if directory_meta.version <= 6:
                    self.trans_objects.append(reader.string())
                else:
                    self.trans_objects.append(reader.numstring())

        if self.version > 6:
            self.constraint = Constraint(reader.uint32())
        elif self.version == 6:
            self.constraint = reader.uint32()

        elif self.version < 3:
            if self.version > 0:
                some_number = reader.uint32()

        elif self.version in [3, 4, 5]:
            some_flags = reader.uint32()

        if self.version < 7:
            unknown_1 = reader.uint32()
            unknown_2 = reader.uint32()
            unknown_3 = reader.uint32()

        if self.version < 5:
            unknown_bool = reader.milo_bool()

        if self.version < 2:
            unknown_floats = reader.vec4f()

        if self.version > 7:
            self.target = reader.numstring()

        if self.version == 7:
            unknown = reader.float32()
            unknown_2 = reader.float32()
            unknown_3 = reader.float32()
            unknown_4 = reader.float32()
            unknown_5 = reader.float32()

        if self.version > 6:
            self.preserve_scale = reader.milo_bool()

        if self.version >= 7:
            self.parent = reader.numstring()

        if super == False:
            padding = reader.read_bytes(4)

            if padding != b"\xAD\xDE\xAD\xDE":
                raise Exception("Padding was not AD DE AD DE, read most likely failed.")

    def write(self, writer, super: bool):
        writer.int32(self.version)

        if super == False:
            self.metadata.write(writer)

        writer.matrix(*self.local_xfm)
        writer.matrix(*self.world_xfm)

        if self.version < 9:
            writer.int32(len(self.trans_objects))

            for trans_object in self.trans_objects:
                writer.numstring(trans_object)

        writer.uint32(self.constraint.value)

        writer.numstring(self.target)

        writer.milo_bool(self.preserve_scale)

        writer.numstring(self.parent)

    def get_matrix_4x3(self, matrix) -> tuple:
        flat_values = []

        for row in matrix:
            flat_values.extend(row[:3])

        return tuple(flat_values)
    
    def from_blender(self, local_matrix, world_matrix, parent: str, bpy_self, children: list = []):
        self.version = 8 if bpy_self.game_selection == "GH1" else 9

        self.local_xfm = self.get_matrix_4x3(local_matrix)
        self.world_xfm = self.get_matrix_4x3(world_matrix)

        if bpy_self.game_selection == "GH1":
            if len(children) > 0:
                for child in children:
                    self.trans_objects.append(child.name)
        
        self.parent = parent
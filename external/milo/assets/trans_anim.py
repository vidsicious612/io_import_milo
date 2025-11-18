from dataclasses import dataclass, field
from . anim import Anim
from . metadata import Metadata

trans_anims = {}

@dataclass
class TransAnim:
    version: int = 0
    metadata: Metadata = field(default_factory=Metadata)
    anim: Anim = field(default_factory=Anim)
    version_min: int = 0
    drawable: str = ""
    object: str = ""
    rot_keys: list[tuple] = field(default_factory=list)
    pos_keys: list[tuple] = field(default_factory=list)
    trans_anim_owner: str = ""
    trans_spline: int | bool = False
    repeat_trans: bool = False
    scale_keys: list[tuple] = field(default_factory=list)
    scale_spline: bool = False
    follow_path: bool = False
    rot_slerp: bool = False
    rot_spline: bool = False

    def read(self, reader, name: str):
        self.version = reader.int32()

        if self.version > 4:
            self.metadata.read(reader)

        self.anim.read(reader)

        if self.version < 6:
            self.version_min = reader.int32()

            unknown = reader.milo_bool()

            if self.version_min < 2:
                string_count = reader.int32()

                for _ in range(string_count):
                    some_string = reader.numstring()

            if self.version_min > 0:
                num_1 = reader.int32()
                num_2 = reader.int32()
                num_3 = reader.int32()
                num_4 = reader.int32()

            if self.version_min > 2:
                num_5 = reader.int32()

            if self.version_min > 3:
                self.drawable = reader.numstring()

        self.object = reader.numstring()

        if self.version != 2:
            rot_keys_count = reader.int32()

            self.rot_keys = [(reader.vec4f(), reader.float32()) for _ in range(rot_keys_count)]

            pos_keys_count = reader.int32()

            self.pos_keys = [(reader.vec3f(), reader.float32()) for _ in range(pos_keys_count)]
            
        self.trans_anim_owner = reader.numstring()

        if self.version < 4:
            self.trans_spline = reader.uint32()
        else:
            self.trans_spline = reader.milo_bool()

        self.repeat_trans = reader.milo_bool()

        if self.version >= 4:
            scale_keys_count = reader.int32()

            self.scale_keys = [(reader.vec3f(), reader.float32()) for _ in range(scale_keys_count)]

            self.scale_spline = reader.milo_bool()

        if self.version > 2:
            self.follow_path = reader.milo_bool()

        if self.version > 3:
            self.rot_slerp = reader.milo_bool()

        if self.version > 6:
            self.rot_spline = reader.milo_bool()

        trans_anims[name] = self

        padding = reader.read_bytes(4)

        if padding != b"\xAD\xDE\xAD\xDE":
            raise Exception("Padding was not AD DE AD DE, read most likely failed.")

    def import_to_blender(self):
        import bpy
        
        obj = bpy.data.objects.get(self.object)
        
        if obj:
            for key, pos in self.rot_keys:
                obj.rotation_mode = "QUATERNION"
                obj.rotation_quaternion = (key[3], key[0], key[1], key[2])
                obj.keyframe_insert("rotation_quaternion", frame=pos)

            for key, pos in self.pos_keys:
                obj.location = key
                obj.keyframe_insert("location", frame=pos)

            for key, pos in self.scale_keys:
                obj.scale = key
                obj.keyframe_insert("scale", frame=pos)
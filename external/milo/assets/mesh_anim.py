from dataclasses import dataclass, field
from . anim import Anim
from . metadata import Metadata

mesh_anims = {}

@dataclass
class VertPointKey:
    vertices: list[tuple] = field(default_factory=list)
    pos: float = 0.0

    def read(self, reader):
        count = reader.int32()

        for _ in range(count):
            self.vertices.append(reader.vec3f())

        self.pos = reader.float32()

@dataclass
class VertTextKey:
    texts: list[tuple] = field(default_factory=list)
    pos: float = 0.0

    def read(self, reader):
        count = reader.int32()

        for _ in range(count):
            self.texts.append(reader.vec2f())

        self.pos = reader.float32()

@dataclass
class VertColorKey:
    colors: list[tuple] = field(default_factory=list)
    pos: float = 0.0

    def read(self, reader):
        count = reader.int32()

        for _ in range(count):
            self.colors.append(reader.vec4f())

        self.pos = reader.float32()

@dataclass
class MeshAnim:
    version: int = 0
    metadata: Metadata = field(default_factory=Metadata)
    anim: Anim = field(default_factory=Anim)
    vert_point_keys: list[VertPointKey] = field(default_factory=list)
    vert_text_keys: list[VertPointKey] = field(default_factory=list)
    vert_color_keys: list[VertPointKey] = field(default_factory=list)
    keys_owner: str = ""

    def read(self, reader, name: str):
        self.version = reader.int32()

        if self.version >= 1:
            self.metadata.read(reader)

        self.anim.read(reader)

        self.mesh = reader.numstring()

        vert_point_keys_count = reader.uint32()

        for _ in range(vert_point_keys_count):
            vert_pk = VertPointKey()
            vert_pk.read(reader)

            self.vert_point_keys.append(vert_pk)

        vert_text_keys_count = reader.uint32()

        for _ in range(vert_text_keys_count):
            vert_tk = VertTextKey()
            vert_tk.read(reader)

            self.vert_point_keys.append(vert_tk)

        vert_color_keys_count = reader.uint32()

        for _ in range(vert_color_keys_count):
            vert_ck = VertColorKey()
            vert_ck.read(reader)

            self.vert_point_keys.append(vert_ck)

        self.keys_owner = reader.numstring()
        
        mesh_anims[name] = self

        padding = reader.read_bytes(4)

        if padding != b"\xAD\xDE\xAD\xDE":
            raise Exception("Padding was not AD DE AD DE, read most likely failed.")
    
    def import_to_blender(self):
        import bpy

        obj = bpy.data.objects.get(self.mesh)

        # GH2 x360 teapot doesn't have a mesh, but has data
        if not obj:
            mesh = bpy.data.meshes.new(name="Mesh")

            obj = bpy.data.objects.new("Mesh", mesh)

            bpy.data.collections["Meshes"].objects.link(obj)
            bpy.context.view_layer.objects.active = obj

            verts = [(0.0, 0.0, 0.0)] * len(self.vert_point_keys[0].vertices)

            mesh.from_pydata(verts, [], [])

        for vert_pk in self.vert_point_keys:
            for i in range(len(vert_pk.vertices)):
                obj.data.vertices[i].co = vert_pk.vertices[i]
                obj.data.vertices[i].keyframe_insert(data_path="co", frame=vert_pk.pos)
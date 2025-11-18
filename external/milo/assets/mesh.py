from dataclasses import dataclass, field
from enum import Enum
from . draw import Draw
from . metadata import Metadata
from . trans import Trans
from .. common import find_next_file
from .. platform import Platform
from .... bpy_util_funcs import invert_uv_map

# Credits: ihatecompvir
class SignedCompressedVec4:
    def __init__(self):
        self.value: int = 0
        self.x: float = 0.0
        self.y: float = 0.0
        self.z: float = 0.0
        self.w: float = 0.0
    
    def clamp(self, value, min_value, max_value):
        return max(min_value, min(value, max_value))

    def to_s_norm_bits(self, f: float, n: int) -> int:
        f = self.clamp(f, -1.0, 1.0)

        max_value = (1 << (n - 1)) - 1
        
        s = int(f * max_value)

        if s < 0:
            s += (1 << n)
        
        return s & ((1 << n) - 1)
    
    def from_s_norm_bits(self, bits: int, n: int) -> float:
        max_value = (1 << (n - 1)) - 1

        s = bits

        if s > max_value:
            s -= (1 << n)

        return max(s / float(max_value), -1.0)

    def read(self, reader):
        self.value = reader.uint32()

        x_bits = int(self.value & 0x3FF)
        y_bits = int((self.value >> 10) & 0x3FF)
        z_bits = int((self.value >> 20) & 0x3FF)
        w_bits = int((self.value >> 30) & 0x003)

        self.x = self.from_s_norm_bits(x_bits, 10)
        self.y = self.from_s_norm_bits(y_bits, 10)
        self.z = self.from_s_norm_bits(z_bits, 10)
        self.w = self.from_s_norm_bits(w_bits, 2)  
 
# Credits: ihatecompvir
class PS3SignedCompressedVec3:
    def __init__(self):
        self.value: int = 0
        self.x: float = 0.0
        self.y: float = 0.0
        self.z: float = 0.0
        self.w: float = 0.0
    
    def clamp(self, value, min_value, max_value):
        return max(min_value, min(value, max_value))

    def to_s_norm_bits(self, f: float, n: int) -> int:
        f = self.clamp(f, -1.0, 1.0)

        max_value = (1 << (n - 1)) - 1
        
        s = int(f * max_value)

        if s < 0:
            s += (1 << n)
        
        return s & ((1 << n) - 1)
    
    def from_s_norm_bits(self, bits: int, n: int) -> float:
        max_value = (1 << (n - 1)) - 1

        s = bits

        if s > max_value:
            s -= (1 << n)

        return max(s / float(max_value), -1.0)

    def read(self, reader):
        self.value = reader.uint32()

        x_bits = int(self.value & 0x7FF)
        y_bits = int((self.value >> 11) & 0x7FF)
        z_bits = int((self.value >> 22) & 0x3FF)

        self.x = self.from_s_norm_bits(x_bits, 11)
        self.y = self.from_s_norm_bits(y_bits, 11)
        self.z = self.from_s_norm_bits(z_bits, 10)

# Credits: ihatecompvir
class UnsignedCompressedVec4:
    def __init__(self):
        self.value: int = 0
        self.x: float = 0.0
        self.y: float = 0.0
        self.z: float = 0.0
        self.w: float = 0.0

    def read(self, reader):
        self.value = reader.uint32() 

        x_bits = int(self.value & 0x3FF)
        y_bits = int((self.value >> 10) & 0x3FF)
        z_bits = int((self.value >> 20) & 0x3FF)
        w_bits = int((self.value >> 30) & 0x003)

        self.x = x_bits / 1023.0
        self.y = y_bits / 1023.0
        self.z = z_bits / 1023.0
        self.w = w_bits / 3.0

# Credits: ihatecompvir
class PS3UnsignedCompressedVec3:
    def __init__(self):
        self.value: int = 0
        self.x: float = 0.0
        self.y: float = 0.0
        self.z: float = 0.0
        self.w: float = 0.0

    def read(self, reader):
        self.value = reader.uint32() 

        x_bits = int(self.value & 0x7FF)
        y_bits = int((self.value >> 11) & 0x7FF)
        z_bits = int((self.value >> 22) & 0x3FF)

        self.x = x_bits / 1023.0
        self.y = y_bits / 1023.0
        self.z = z_bits / 511.0

def flip_indices(indices: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    return (indices[3], indices[2], indices[1], indices[0])

class Mutable(Enum):
    kMutableNone = 0
    kMutableVerts = 31
    kMutableFaces = 32
    kMutableAll = 63

class Volume(Enum):
    kVolumeEmpty = 0
    kVolumeTriangles = 1
    kVolumeBSP = 2
    kVolumeBox = 3
    
class BSPNode:
    def __init__(self):
        self.has_tree: bool = False
        self.vec: tuple = (0.0, 0.0, 0.0, 0.0)
        self.left: BSPNode
        self.right: BSPNode

    def read(self, reader):
        self.has_tree = reader.milo_bool()

        if self.has_tree == False:
            return

        self.vec = reader.vec4f()

        self.left.read(reader)
        self.right.read(reader)

    def write(self, writer):
        writer.milo_bool(self.has_tree)

        if self.has_tree == False:
            return

        writer.vec4f(self.vec)

        self.left.write(writer)
        self.right.write(writer)

@dataclass
class Vertices:
    vertices: list[tuple] = field(default_factory=list)
    vertex_colors: list[tuple] = field(default_factory=list)
    normals: list[tuple] = field(default_factory=list)
    uvs: list[tuple] = field(default_factory=list)
    weights: list[tuple] = field(default_factory=list)
    indices: list[tuple] = field(default_factory=list)

    def read(self, reader, version: int, platform: Platform):
        if version == 0x60026:
            reader.little_endian = True

            # FF FF FF FF, probably padding or vertex color?
            padding = reader.read_bytes(4)

            unknown = reader.read_bytes(8)

        vertex_count = reader.int32()

        is_ng = False
        is_og_ng = False

        if version >= 36:
            is_ng = reader.milo_bool()

            if is_ng == True:
                vert_size = reader.int32()

                compression_type = reader.int32()

            if (platform != platform.Wii) and (is_ng == False) and (version < 38):
                is_og_ng = True

        if version <= 10:
            result = self.read_v0(reader, vertex_count)
        elif version <= 22:
            result = self.read_v11(reader, vertex_count)
        elif version <= 28:
            result = self.read_v23(reader, vertex_count)
        elif (version < 35) or (is_ng == False) or (is_og_ng == True):
            result = self.read_old_gen(reader, vertex_count, version, is_og_ng)
        else:
            result = self.read_new_gen(reader, vertex_count, platform, compression_type)

        if version == 0x60026:
            reader.little_endian = False

        return result

    def read_v0(self, reader, vertex_count: int):
        for _ in range(vertex_count):
            self.vertices.append(reader.vec3f())

            self.normals.append(reader.vec3f())

            self.uvs.append(invert_uv_map(reader.vec2f()))

            self.weights.append(reader.vec4f())

            self.indices.append(reader.vec4us())

    def read_v11(self, reader, vertex_count: int):
        for _ in range(vertex_count):
            self.vertices.append(reader.vec3f())

            weight_0, weight_1 = reader.vec2f()
            weight_2 = 1.0 - (weight_0 + weight_1)

            self.weights.append((weight_0, weight_1, weight_2))

            self.normals.append(reader.vec3f())

            unknown = reader.vec4f()

            self.uvs.append(invert_uv_map(reader.vec2f()))

            self.indices.append((0, 1, 2))

    def read_v23(self, reader, vertex_count: int):
        for _ in range(vertex_count):
            self.vertices.append(reader.vec3f())

            self.normals.append(reader.vec3f())

            self.weights.append(reader.vec4f())

            self.uvs.append(invert_uv_map(reader.vec2f()))

            self.indices.append((0, 1, 2, 3))

    def read_old_gen(self, reader, vertex_count: int, version: int, is_og_ng: bool):
        for _ in range(vertex_count):
            self.vertices.append(reader.vec3f())

            if (version == 34 and reader.little_endian == False) or (is_og_ng == True):
                w = reader.float32()

            if version == 38:
                packed_1 = reader.uint32()
                unknown_1 = reader.float32()

                packed_2 = reader.uint32()
                unknown_2 = reader.float32()

            self.normals.append(reader.vec3f())

            if (version == 34 and reader.little_endian == False) or (is_og_ng == True):
                nw = reader.float32()

            if version == 38:
                self.uvs.append(invert_uv_map(reader.vec2f()))

                self.weights.append(reader.vec4f())
            else:
                self.weights.append(reader.vec4f())

                self.uvs.append(invert_uv_map(reader.vec2f()))

            if version == 0x60026:
                unknown_vec = reader.vec4f()

            if version >= 33:
                self.indices.append(reader.vec4us())

                tangents = reader.vec4f()

    def read_new_gen(self, reader, vertex_count: int, platform: Platform, compression_type: int):
        for _ in range(vertex_count):
            self.vertices.append(reader.vec3f())

            if platform == Platform.X360:
                value = reader.uint32()

                self.vertex_colors.append(((value >> 24) & 0xFF, (value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF))

            self.uvs.append(invert_uv_map(reader.vec2hf()))

            if platform == Platform.X360:
                normals = SignedCompressedVec4()
                normals.read(reader)

                self.normals.append((normals.x, normals.y, normals.z))

                tangents = SignedCompressedVec4()
                tangents.read(reader)
                
                weights = UnsignedCompressedVec4()
                weights.read(reader)

                self.weights.append((weights.x, weights.y, weights.z, weights.w))

                self.indices.append(flip_indices(reader.vec4ub()))
            elif platform == Platform.PS3:
                normals = PS3SignedCompressedVec3()
                normals.read(reader)

                self.normals.append((normals.x, normals.y, normals.z))

                tangents = PS3SignedCompressedVec3()
                tangents.read(reader)
                
                weights = PS3UnsignedCompressedVec3()
                weights.read(reader)

                self.weights.append((weights.x, weights.y, weights.z, weights.w))

                if compression_type == 2:
                    value = reader.uint32()

                    self.vertex_colors.append(((value >> 24) & 0xFF, (value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF))

                self.indices.append(reader.vec4us())

    def write(self, writer, version: int):
        writer.int32(len(self.vertices))

        for i in range(len(self.vertices)):
            writer.vec3f(self.vertices[i])

            if version == 34:
                writer.float32(0.0)
            
            writer.vec3f(self.normals[i])

            if version == 34:
                writer.float32(0.0)

            writer.vec4f(self.weights[i])

            writer.vec2f(invert_uv_map(self.uvs[i]))

            if version == 34:
                writer.vec4us(self.indices[i])

@dataclass
class Faces:
    faces: list[tuple] = field(default_factory=list)

    def read(self, reader):
        face_count = reader.int32()

        self.faces = [reader.vec3us() for _ in range(face_count)]

    def write(self, writer):
        writer.int32(len(self.faces))

        for face in self.faces:
            writer.vec3us(*face)

@dataclass
class GroupSection:
    sections: list[int] = field(default_factory=list)
    vert_offsets: list[int] = field(default_factory=list)

    def read(self, reader, is_ag: bool, count: int = 0):
        if is_ag == True:
            count = reader.uint32()

        for _ in range(count):
            if is_ag == True:
                some_number = reader.uint32()

            if is_ag == True:
                vert_count = reader.uint32()

                for _ in range(vert_count):
                    self.vert_offsets.append(reader.ushort())

                section_count = reader.uint32()

                for _ in range(section_count):
                    self.sections.append(reader.int32())
            else:
                section_count = reader.int32()

                vert_count = reader.int32()

                for _ in range(section_count):
                    self.sections.append(reader.int32())

                for _ in range(vert_count):
                    self.vert_offsets.append(reader.ushort())

@dataclass
class BoneTransform:
    name: str = ""
    matrix: tuple = ()
    
    def read(self, reader, version: int):
        if version > 22:
            self.name = reader.numstring()
        
        if version >= 34:
            self.matrix = reader.matrix()

    def write(self, writer, version: int):
        if version > 22:
            writer.numstring(self.name)

        if version >= 34:
            writer.matrix(*self.matrix)

@dataclass
class Mesh:
    version: int = 0
    metadata: Metadata = field(default_factory=Metadata)
    trans: Trans = field(default_factory=Trans)
    draw: Draw = field(default_factory=Draw)
    mat: str = ""
    mat_2: str = ""
    geom_owner: str = ""
    alt_geom_owner: str = ""
    trans_parent: str = ""
    trans_1: str = ""
    trans_2: str = ""
    sphere: tuple = (0.0, 0.0, 0.0, 0.0)
    mutable: Mutable = Mutable.kMutableNone
    volume: Volume = Volume.kVolumeTriangles
    bsp_node: BSPNode = field(default_factory=BSPNode)
    vertices: Vertices = field(default_factory=Vertices)
    faces: Faces = field(default_factory=Faces)
    group_sizes: list[int] = field(default_factory=list)
    bone_names: list[BoneTransform] = field(default_factory=list)
    keep_mesh_data: bool = False
    exclude_from_self_shadow: bool = False
    has_ao_calculation: bool = False

    def read(self, reader, directory_meta):
        self.version = reader.int32()

        if self.version > 25:
            self.metadata.read(reader)

        self.trans.read(reader, True, directory_meta)
        self.draw.read(reader, directory_meta)

        if self.version < 15:
            always_0 = reader.uint32()

            bones_count = reader.int32()

            for _ in range(bones_count):
                if self.version <= 10:
                    bone = reader.string()
                else:
                    bone = reader.numstring()

        if self.version < 20:
            num_1 = reader.uint32()
            num_2 = reader.uint32()

        if self.version < 3:
            some_value = reader.numstring()

        if self.version <= 10:
            self.mat = reader.string()
        else:
            self.mat = reader.numstring()

        if self.version == 27:
            self.mat_2 = reader.numstring()

        if self.version <= 10:
            self.geom_owner = reader.string()
        else:
            self.geom_owner = reader.numstring()

        if self.version < 13:
            if self.version <= 10:
                self.alt_geom_owner = reader.string()
            else:
                self.alt_geom_owner = reader.numstring()

        if self.version < 15:
            if self.version <= 10:
                self.trans_parent = reader.string()
            else:
                self.trans_parent = reader.numstring()

        if self.version < 14:
            if self.version <= 10:
                self.trans_1 = reader.string()
                self.trans_2 = reader.string()
            else:
                self.trans_1 = reader.numstring()
                self.trans_2 = reader.numstring()

        if self.version < 3:
            some_vector = reader.vec3f()

        if self.version < 15:
            self.sphere = reader.vec4f()

        if self.version < 8:
            some_bool = reader.milo_bool()

        if self.version < 15:
            if self.version <= 10:
                some_string = reader.string()
            else:
                some_string = reader.numstring()

            some_float = reader.float32()

        if self.version < 16:
            if self.version > 11:
                some_bool = reader.milo_bool()
        else:
            self.mutable = Mutable(reader.uint32())

            if self.version == 17:
                unknown = reader.uint32()
                unknown_2 = reader.uint32()

        if self.version > 17:
            self.volume = Volume(reader.uint32())

        if self.version > 18:
            self.bsp_node.read(reader)

        if self.version == 7:
            some_bool = reader.milo_bool()

        if self.version < 11:
            some_number = reader.uint32()

        self.vertices.read(reader, self.version, directory_meta.platform)

        self.faces.read(reader)

        if self.version < 24:
            short_count = reader.uint32()

            for _ in range(short_count * 2):
                some_short = reader.ushort()

            if self.version >= 22:
                group_section = GroupSection()
                group_section.read(reader, True)

            if (self.version == 16) or (self.version == 17):
                unknown_3 = reader.numstring()

            if self.version <= 22:
                bone_1 = reader.numstring()

                bone_names = []
                bone_names.append(self.trans.parent)

                if len(bone_1) > 5:
                    bone_names.append(bone_1)

                    bone_2 = reader.numstring()

                    if len(bone_2) > 5:
                        bone_names.append(bone_2)

                    bone_1_xfm = reader.matrix()
                    bone_2_xfm = reader.matrix()

            if self.version >= 14:
                if self.version >= 25:
                    for _ in range(4):
                        self.bone_names.append(BoneTransform().read(reader, self.version))

                    for _ in range(4):
                        bone_transform = reader.matrix()

        group_sizes_count = reader.uint32()
        self.group_sizes = [reader.ubyte() for _ in range(group_sizes_count)]

        if self.version <= 28:
            bone_count = reader.int32()

            if bone_count > 0:
                reader.seek(-4)

                bone_count = 4
        else:
            bone_count = reader.int32()

        for _ in range(bone_count):
            bone_transform = BoneTransform()
            bone_transform.read(reader, self.version)
            
            self.bone_names.append(bone_transform)

        if (self.version <= 28) and (bone_count > 0):
            for _ in range(bone_count):
                bone_transform = reader.matrix()

        if self.version == 0x60026:
            find_next_file(reader)

            padding = reader.read_bytes(4)

            return

        if self.version >= 36:
            self.keep_mesh_data = reader.milo_bool()

        if self.version == 37:
            self.exclude_from_self_shadow = reader.milo_bool()

        if self.version >= 38:
            self.has_ao_calculation = reader.milo_bool()

        padding = reader.read_bytes(4)

        if padding != b"\xAD\xDE\xAD\xDE":
            if directory_meta.platform == Platform.PS2:
                reader.seek(-4)

                if (group_sizes_count > 0) and (self.group_sizes[0] > 0):
                    group_section = GroupSection()
                    group_section.read(reader, False, group_sizes_count)

                    padding = reader.read_bytes(4)

                    if padding != b"\xAD\xDE\xAD\xDE":
                        raise Exception("Padding was not AD DE AD DE, read most likely failed.")
            else:
                raise Exception("Padding was not AD DE AD DE, read most likely failed.")

    def write(self, writer):
        writer.int32(self.version)

        if self.version > 25:
            self.metadata.revision = 2
            self.metadata.write(writer)

        self.trans.write(writer, True)
        self.draw.write(writer)

        writer.numstring(self.mat)

        writer.numstring(self.geom_owner)

        writer.int32(self.mutable.value)
        writer.int32(self.volume.value)

        self.bsp_node.write(writer)

        self.vertices.write(writer, self.version)
        self.faces.write(writer, self.version)

        writer.int32(0)

        if (self.version > 25) and (len(self.bone_names) > 0):
            writer.int32(len(self.bone_names))
        elif (self.version == 25) and (len(self.bone_names) == 0):
            writer.int32(0)

        for bone in self.bone_names:
            bone.write(writer)

        writer.write_bytes(b"\xAD\xDE\xAD\xDE")

    def import_to_blender(self, name: str, bpy_self, directory_meta):
        import bpy
        import mathutils
        from .. platform import Platform
        
        meshes_collection = bpy.data.collections.get("Meshes")

        if not meshes_collection:
            meshes_collection = bpy.data.collections.new("Meshes")

            bpy.context.scene.collection.children.link(meshes_collection)

        if bpy_self.import_shadow == False:   
            if "shadow" in name:
                return
            
        if bpy_self.import_lod == False:
            if self.version == 37:
                if "LOD01" in name:
                    return
                
                if directory_meta.platform != Platform.Wii:
                    if "LOD02" in name:
                        return
            elif self.version == 38:
                if "lod" in name:
                    return
            else:
                if ("lod01" in name) or ("lod1" in name) or ("lod02" in name):
                    return
                
            if name.lower().startswith("blend"):
                return
            
        mesh = bpy.data.meshes.new(name=name)

        obj = bpy.data.objects.new(name, mesh)

        bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj

        meshes_collection.objects.link(obj)

        bpy.context.collection.objects.unlink(obj)

        if len(self.vertices.normals) > 0:
            mesh.from_pydata(self.vertices.vertices, [], self.faces.faces)
            mesh.normals_split_custom_set_from_vertices(self.vertices.normals)
        else:
            mesh.from_pydata(self.vertices.vertices, [], self.faces.faces, False)

        uv_map = mesh.uv_layers.new(name="UVMap")

        for loop in mesh.loops:
            uv_map.data[loop.index].uv = self.vertices.uvs[loop.vertex_index]

        if uv_map.data:
            mesh.calc_tangents()

        obj.matrix_local = mathutils.Matrix((
            (self.trans.local_xfm[0], self.trans.local_xfm[3], self.trans.local_xfm[6], self.trans.local_xfm[9]),
            (self.trans.local_xfm[1], self.trans.local_xfm[4], self.trans.local_xfm[7], self.trans.local_xfm[10]),
            (self.trans.local_xfm[2], self.trans.local_xfm[5], self.trans.local_xfm[8], self.trans.local_xfm[11]),
        )).to_4x4()

        obj.matrix_world = mathutils.Matrix((
            (self.trans.world_xfm[0], self.trans.world_xfm[3], self.trans.world_xfm[6], self.trans.world_xfm[9]),
            (self.trans.world_xfm[1], self.trans.world_xfm[4], self.trans.world_xfm[7], self.trans.world_xfm[10]),
            (self.trans.world_xfm[2], self.trans.world_xfm[5], self.trans.world_xfm[8], self.trans.world_xfm[11]),
        )).to_4x4()
        
        mat = bpy.data.materials.get(f"{self.mat}_{directory_meta.dir_name}")
        
        if mat:
            if obj.data.materials:
                obj.data.materials[0] = mat
            else:
                obj.data.materials.append(mat)

        # Character parenting
        parent_obj = bpy.data.objects.get(directory_meta.dir_name)
            
        if parent_obj:
            obj.parent = parent_obj

        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        
        final_weight_map = {}

        for vertex_index, (id_group, weight_group) in enumerate(zip(self.vertices.indices, self.vertices.weights)):
            for idx, wgt in zip(id_group, weight_group):
                if len(self.bone_names) == 0:
                    if "bone" in self.trans.parent:
                        group_name = self.trans.parent

                        if group_name not in final_weight_map:
                            new_vtx_group = obj.vertex_groups.new(name=group_name)
                            final_weight_map[group_name] = new_vtx_group
                        
                        if wgt > 0:
                            final_weight_map[group_name].add([vertex_index], wgt, "REPLACE")
                    else:
                        bpy.context.view_layer.objects.active = None
                        bpy.ops.object.select_all(action="DESELECT")

                        return
                elif len(self.bone_names) == 1:
                    group_name = self.bone_names[0].name

                    if group_name not in final_weight_map:
                        new_vtx_group = obj.vertex_groups.new(name=group_name)
                        final_weight_map[group_name] = new_vtx_group

                    if wgt > 0:
                        final_weight_map[group_name].add([vertex_index], wgt, "REPLACE")  
                elif len(self.bone_names) == 2:
                    max_group_name_idx = 2

                    for idx in range(min(len(self.bone_names), max_group_name_idx)):
                        group_name = self.bone_names[idx].name

                        if group_name not in final_weight_map:
                            new_vtx_group = obj.vertex_groups.new(name=group_name)
                            final_weight_map[group_name] = new_vtx_group

                        if wgt > 0:
                            final_weight_map[group_name].add([vertex_index], wgt, "REPLACE") 
                elif len(self.bone_names) == 3:
                    max_group_name_idx = 3

                    for idx in range(min(len(self.bone_names), max_group_name_idx)):
                        group_name = self.bone_names[idx].name

                        if group_name not in final_weight_map:
                            new_vtx_group = obj.vertex_groups.new(name=group_name)
                            final_weight_map[group_name] = new_vtx_group

                        if wgt > 0:
                            final_weight_map[group_name].add([vertex_index], wgt, "REPLACE") 
                else:
                    group_name = self.bone_names[idx].name

                    if group_name not in final_weight_map:
                        new_vtx_group = obj.vertex_groups.new(name=group_name)
                        final_weight_map[group_name] = new_vtx_group

                    if wgt > 0:
                        final_weight_map[group_name].add([vertex_index], wgt, "REPLACE")
        
        mesh.update()
        obj.select_set(False)

    def from_blender(self, obj, bpy_self):
        from .. default_transform import DEFAULT_TRANSFORM

        def get_weights_and_indices(obj) -> list:
            vertex_groups = obj.vertex_groups

            max_influences = 4

            bone_weights = []

            for v in obj.data.vertices:
                v_weights = []

                for g in v.groups:
                    group = vertex_groups[g.group]

                    weight = g.weight

                    if weight > 0:
                        v_weights.append((g.group, weight))

                v_weights.sort(key=lambda x: x[1], reverse=True)
                v_weights = v_weights[:max_influences]

                total_weight = sum(w for _, w in v_weights) or 1.0

                normalized = [(g, w / total_weight) for g, w in v_weights]

                indices = [g for g, _ in normalized]
                weights = [w for _, w in normalized]

                while len(indices) < max_influences:
                    indices.append(0)
                    weights.append(0.0)

                bone_weights.append((indices, weights))

            return bone_weights

        def get_vertices(mesh: Mesh, obj):
            mesh.vertices.vertices = [v.co for v in obj.data.vertices]

            mesh.vertices.normals = [v.normal for v in obj.data.vertices]

            uv_layer = mesh.uv_layers.active.data if mesh.uv_layers.active else None

            mesh.vertices.uvs = [None] * len(mesh.vertices)

            for poly in mesh.polygons:
                for loop_idx in poly.loop_indices:
                    vertex_index = mesh.loops[loop_idx].vertex_index

                    if uv_layer:
                        uv = uv_layer[loop_idx].uv

                        if mesh.vertices.uvs[vertex_index] is None:
                            mesh.vertices.uvs[vertex_index] = uv

            bone_weights = get_weights_and_indices(obj)

            mesh.vertices.weights = [weights for _, weights in bone_weights]
            mesh.vertices.indices = [indices for indices, _ in bone_weights]

        self.version = 25 if bpy_self.game_selection == "GH1" else 34

        self.trans.local_xfm = self.trans.get_matrix_4x3(obj.matrix_local)
        self.trans.world_xfm = self.trans.get_matrix_4x3(obj.matrix_world)
        self.trans.parent = obj.parent.name if obj.parent else ""
        self.draw.from_blender(bpy_self)

        if len(obj.data.materials) > 1:
            raise Exception("Mesh has more than one material assigned, please only use one.")

        if obj.data.materials:
            self.mat = obj.data.materials[0].name

        get_vertices(self, obj)

        self.faces.faces = [(tri.vertices[0], tri.vertices[1], tri.vertices[2]) for tri in obj.data.loop_triangles]

        if bpy_self.game_selection != "GH1":
            if len(obj.vertex_groups) > 40:
                raise Exception("Mesh has more than 40 vertex groups, please reduce the number of vertex groups.")
        else:
            if len(obj.vertex_groups) > 4:
                raise Exception("Mesh has more than 4 vertex groups, please reduce the number of vertex groups.")

        for vg in obj.vertex_groups:
            bone_transform = BoneTransform()

            bone_transform.name = vg.name
            bone_transform.matrix = DEFAULT_TRANSFORM

            self.bone_names.append(bone_transform)
from dataclasses import dataclass, field
from enum import Enum
from . metadata import Metadata
from .. common import find_next_file
from .. default_transform import DEFAULT_TRANSFORM

class Blend(Enum):
    kBlendDest = 0
    kBlendSrc = 1
    kBlendAdd = 2
    kBlendSrcAlpha = 3
    kBlendSrcAlphaAdd = 4
    kBlendSubtract = 5
    kBlendMultiply = 6
    kPreMultAlpha = 7

class MapType(Enum):
    kDiffuse = 0
    kEnviron = 2

class PerPixelLit(Enum):
    kPerPixelOff = 0
    kPerPixelXbox360Only = 1
    kPerPixelPS3Only = 2
    kPerPixelAllNGPlatforms = 3

class ShaderVariation(Enum):
    kShaderVariationNone = 0
    kShaderVariationSkin = 1
    kShaderVariationHair = 2

class StencilMode(Enum):
    kStencilIgnore = 0
    kStencilWrite = 1
    kStencilTest = 2

class TexGen(Enum):
    kTexGenNone = 0
    kTexGenXfm = 1
    kTexGenSphere = 2
    kTexGenProjected = 3
    kTexGenXfmOrigin = 4
    kTexGenEnviron = 5

class TexWrap(Enum):
    kTexWrapClamp = 0
    kTexWrapRepeat = 1
    kTexBorderBlack = 2
    kTexBorderWhite = 3
    kTexWrapMirror = 4

class ZMode(Enum):
    kZModeDisable = 0
    kZModeNormal = 1
    kZModeTransparent = 2
    kZModeForce = 3
    kZModeDecal = 4

@dataclass
class TextureEntry:
    map_type: MapType = MapType.kDiffuse
    tex_xfm: tuple = DEFAULT_TRANSFORM
    tex_wrap: int = 0
    tex_name: str = ""

    def read(self, reader, version: int):
        if version <= 21:
            unknown = reader.int32()

        self.map_type = reader.int32()

        self.tex_xfm = reader.matrix()

        if version <= 9:
            unknown = reader.read_bytes(13)

        if version > 9:
            self.tex_wrap = reader.int32()

        if version <= 7:
            self.tex_name = reader.string()
        else:
            self.tex_name = reader.numstring()

    def write(self, writer):
        writer.int32(self.map_type.value)

        writer.matrix(*self.tex_xfm)

        writer.int32(self.tex_wrap)

        writer.numstring(self.tex_name)

@dataclass
class Mat:
    version: int = 0
    metadata = Metadata()
    texture_entries: list[TextureEntry] = field(default_factory=list)
    blend: Blend = Blend.kBlendSrc
    diffuse_color: tuple = ()
    blend_2: Blend = Blend.kBlendSrc
    prelit: bool = True
    use_environ: bool = False
    z_mode: ZMode = ZMode.kZModeNormal
    alpha_cut: bool = False
    alpha_threshold: int = 0
    alpha_write: bool = False
    tex_gen: TexGen = TexGen.kTexGenNone
    tex_wrap: TexWrap = TexWrap.kTexWrapRepeat
    tex_xfm: tuple = ()
    diffuse_tex: str = ""
    next_pass: str = ""
    intensify: bool = False
    cull: bool = True
    recv_proj_lights: bool = False
    recv_point_cube_tex: bool = False
    ps3_force_trilinear: bool = False
    emissive_multiplier: float = 1.0
    specular_rgb: tuple = ()
    specular_power: float = 0.0
    normal_tex: str = ""
    emissive_map: str = ""
    specular_tex: str = ""
    environ_map: str = ""
    per_pixel_lit: bool | PerPixelLit = PerPixelLit.kPerPixelAllNGPlatforms
    stencil_mode: StencilMode = StencilMode.kStencilIgnore
    fur: str = ""
    de_normal: float = 0.0
    anisotropy: float = 0.0
    norm_detail_tiling: float = 0.0
    norm_detail_strength: float = 0.0
    norm_detail_map: str = ""
    point_lights: bool = False
    proj_lights: bool = False
    fog: bool = False
    fadeout: bool = False
    color_adjust: bool = False
    rim_rgb: tuple = ()
    rim_power: float = 0.0
    rim_map: str = ""
    rim_always_show: bool = False
    screen_aligned: bool = False
    shader_variation = int
    specular_2_rgb: tuple = ()
    specular_2_power: float = 0.0
    colors: list[tuple] = field(default_factory=list)
    alpha_mask: str = ""
    refract_enabled: bool = False
    refract_strength: float = 0.0
    refract_normal_map: str = ""

    def read(self, reader):
        self.version = reader.int32()

        if self.version <= 21:
            tex_count = reader.int32()

            for _ in range(tex_count):
                texture_entry = TextureEntry()
                texture_entry.read(reader, self.version)

                self.texture_entries.append(texture_entry)
        else:
            if self.version >= 70:
                always_5 = reader.uint32()

            self.metadata.read(reader)

        self.blend = Blend(reader.int32())

        if self.version <= 7:
            unknown = reader.read_bytes(30)

        self.diffuse_color = reader.vec4f()
        
        if self.version <= 7:
            some_float = reader.float32()

            f1 = reader.float32()
            f2 = reader.float32()
            f3 = reader.float32()

        if self.version <= 15:
            if self.version > 7:
                color_2 = reader.vec3f()
                alpha_2 = reader.float32()

                some_float = reader.float32()

                f1 = reader.float32()
                f2 = reader.float32()
                f3 = reader.float32()

                if self.version > 12:
                    some_bool = reader.milo_bool()

                zeros = reader.read_bytes(14)

                if (self.version > 9) and (self.version != 12):
                    unknown_num = reader.uint32()

                if self.version == 9:
                    some_bool = reader.milo_bool()
        elif self.version <= 21:
            always_1 = reader.byte()
            always_0 = reader.short()

            always_1_0 = reader.int32()
            always_0_0 = reader.short()

            self.blend_2 = Blend(reader.int32())

            always_0_1 = reader.short()

            padding = reader.read_bytes(4)

            if padding != b"\xAD\xDE\xAD\xDE":
                raise Exception("Padding was not AD DE AD DE, read most likely failed.")

            return
        if self.version <= 7:
            unknown_bool = reader.milo_bool()
            unknown_bool_2 = reader.milo_bool()

        self.prelit = reader.milo_bool()
        self.use_environ = reader.milo_bool()

        self.z_mode = ZMode(reader.int32())
        
        self.alpha_cut = reader.milo_bool()

        if self.version > 37:
            self.alpha_threshold = reader.int32()

        self.alpha_write = reader.milo_bool()

        self.tex_gen = TexGen(reader.uint32())
        self.tex_wrap = TexWrap(reader.uint32())

        if self.version <= 7:
            if padding != b"\xAD\xDE\xAD\xDE":
                raise Exception("Padding was not AD DE AD DE, read most likely failed.")

            return
        
        self.tex_xfm = reader.matrix()

        self.diffuse_tex = reader.numstring()

        self.next_pass = reader.numstring()

        self.intensify = reader.milo_bool()

        self.cull = reader.milo_bool()

        if self.version >= 70:
            self.recv_proj_lights = reader.milo_bool()
            self.recv_point_cube_tex = reader.milo_bool()

            self.ps3_force_trilinear = reader.milo_bool()

        self.emissive_multiplier = reader.float32()

        self.specular_rgb = reader.vec3f()
        self.specular_power = reader.float32()

        self.normal_map = reader.numstring()

        self.emissive_map = reader.numstring()

        self.specular_map = reader.numstring()

        if self.version < 51:
            some_string = reader.numstring()

        self.environ_map = reader.numstring()

        if self.version == 68:
            unk_short = reader.ushort()
        
        if (self.version <= 55) or (self.version != 56):
            self.per_pixel_lit = reader.milo_bool()
        elif self.version == 56:
            self.per_pixel_lit = PerPixelLit(reader.uint32())
        
        if (self.version >= 27) and (self.version < 50):
            ignored_bool = reader.milo_bool()

        if self.version > 27:
            self.stencil_mode = StencilMode(reader.uint32())

        if (self.version >= 29) and (self.version < 41):
            ignore_string = reader.numstring()

        if self.version > 33:
            self.fur = reader.numstring()

        if (self.version >= 34) and (self.version < 49):
            ignored_bool_2 = reader.milo_bool()
            ignored_color = reader.vec3f()
            ignored_alpha = reader.float32()

            if self.version > 34:
                some_string_2 = reader.numstring()

        if self.version <= 28:
            padding = reader.read_bytes(4)

            if padding != b"\xAD\xDE\xAD\xDE":
                raise Exception("Padding was not AD DE AD DE, read most likely failed.")
            
            return
                
        if self.version > 35:
            self.de_normal = reader.float32()

            self.anisotropy = reader.float32()

        if self.version > 38:
            if self.version < 42:
                ignored_bool_3 = reader.milo_bool()

            self.norm_detail_tiling = reader.float32()
            self.norm_detail_strength = reader.float32()

            if self.version < 42:
                for _ in range(5):
                    some_ignored_float = reader.float32()

            if self.version < 68:
                self.norm_detail_map = reader.numstring()

            if self.version < 42:
                some_string_3 = reader.numstring()

        if self.version > 42:
            if self.version < 45:
                some_bitfield = reader.uint32()
            else:
                self.point_lights = reader.milo_bool()

            self.proj_lights = reader.milo_bool()

            self.fog = reader.milo_bool()

            self.fade_out = reader.milo_bool()

            if self.version > 46:
                self.color_adjust = reader.milo_bool()

        if self.version >= 68:
            find_next_file(reader)

            padding = reader.read_bytes(4)

            if padding != b"\xAD\xDE\xAD\xDE":
                raise Exception("Padding was not AD DE AD DE, read most likely failed.")
            
            return

        if self.version > 47:
            self.rim_rgb = reader.vec3f()
            self.rim_power = reader.float32()

            self.rim_map = reader.numstring()
            self.rim_always_show = reader.milo_bool()

        if self.version > 48:
            self.screen_aligned = reader.milo_bool()

        if self.version == 50:
            legacy_shader_variation = reader.ubyte()
        elif self.version > 50:
            self.shader_variation = ShaderVariation(reader.uint32())
            
            self.specular2_rgb = reader.vec3f()
            self.specular2_power = reader.float32()

        if (self.version >= 52) and (self.version <= 67):
            if self.version == 52:
                unk_bool = reader.milo_bool()
            elif self.version < 54:
                unk_int = reader.int32()

            if (self.version >= 53) and (self.version <= 59):
                unk_color = reader.vec4f()

            if self.version >= 60:
                colors_count = reader.int32()

                for _ in range(colors_count):
                    self.colors.append(reader.vec4f())

        if (self.version >= 54) and (self.version <= 62):
            unk_float = reader.float32()
            
            self.alpha_mask = reader.numstring()
            
            self.ps3_force_trilinear = reader.milo_bool()

        if self.version > 62:
            self.recv_proj_lights = reader.milo_bool()
            self.recv_point_cube_tex = reader.milo_bool()

            self.ps3_force_trilinear = reader.milo_bool()

        if self.version > 63:
            self.refract_enabled = reader.milo_bool()
            self.refract_strength = reader.float32()
            self.refract_normal_map = reader.numstring()

        padding = reader.read_bytes(4)

        if padding != b"\xAD\xDE\xAD\xDE":
            raise Exception("Padding was not AD DE AD DE, read most likely failed.")

    def write(self, writer):
        writer.int32(self.version)

        if self.version <= 21:
            for texture_entry in self.texture_entries:
                texture_entry.write(writer)
        else:
            self.metadata.write(writer)

        writer.int32(self.blend.value)

        writer.vec4f(self.diffuse_color)

        if self.version <= 21:
            writer.byte(1)

            writer.short(0)

            writer.int32(1)

            writer.short(0)
        
            writer.int32(1)

            writer.short(0)

            return

        writer.milo_bool(self.prelit)
        writer.milo_bool(self.use_environ)

        writer.int32(self.z_mode.value)

        writer.milo_bool(self.alpha_cut)

        if self.version > 37:
            writer.int32(self.alpha_threshold)

        writer.milo_bool(self.alpha_write)

        writer.uint32(self.tex_gen.value)
        writer.uint32(self.tex_wrap.value)

        writer.matrix(*self.tex_xfm)

        writer.numstring(self.diffuse_tex)

        writer.numstring(self.next_pass)

        writer.milo_bool(self.intensify)

        writer.milo_bool(self.cull)

        writer.float32(self.emissive_multiplier)

        writer.vec3f(self.specular_rgb)
        writer.float32(self.specular_power)

        writer.numstring(self.normal_map)

        writer.numstring(self.emissive_map)

        writer.numstring(self.specular_map)

        writer.numstring(self.environ_map)

        writer.numstring("")

        writer.milo_bool(True)

    def import_to_blender(self, name: str, directory_meta):
        import bpy
        from .. platform import Platform

        mat = bpy.data.materials.get(f"{name}_{directory_meta.dir_name}")

        if mat is None:
            mat = bpy.data.materials.new(f"{name}_{directory_meta.dir_name}")

        mat.diffuse_color = self.diffuse_color
        
        diffuse_tex = None

        if self.version > 21:
            diffuse_tex = bpy.data.textures.get(self.diffuse_tex)
        else:
            if len(self.texture_entries) > 0:
                diffuse_tex = bpy.data.textures.get(self.texture_entries[0].tex_name)
        
        if diffuse_tex:
            if mat.use_nodes == False:
                mat.use_nodes = True

            bsdf = mat.node_tree.nodes.get("Principled BSDF")

            if bsdf:
                tex_node = mat.node_tree.nodes.new("ShaderNodeTexImage")
                tex_node.image = diffuse_tex.image
                tex_node.location = (-345.0820, 318.2288)

                links = mat.node_tree.links
                links.new(bsdf.inputs["Base Color"], tex_node.outputs["Color"])

                if self.blend == Blend.kBlendSrcAlpha:
                    links.new(bsdf.inputs["Alpha"], tex_node.outputs["Alpha"])

                image = diffuse_tex.image

                if image:
                    image.alpha_mode = "CHANNEL_PACKED"

        normal_tex = bpy.data.textures.get(self.normal_tex)

        if normal_tex:
            if mat.use_nodes == False:
                mat.use_nodes = True
                
            bsdf = mat.node_tree.nodes.get("Principled BSDF")

            if bsdf:
                normal_map_node = mat.node_tree.nodes.new("ShaderNodeNormalMap")
                normal_map_node.location = (-261.7965, 32.9038)

                tex_node = mat.node_tree.nodes.new("ShaderNodeTexImage")
                tex_node.image = normal_tex.image
                tex_node.location = (-1221.9069, -21.5945)

                separate_color = mat.node_tree.nodes.new("ShaderNodeSeparateColor")
                separate_color.location = (-742.4393, -75.2079)

                combine_color = mat.node_tree.nodes.new("ShaderNodeCombineColor")
                combine_color.location = (-511.2123, -73.1929)

                invert_color = mat.node_tree.nodes.new("ShaderNodeInvert")

                if directory_meta.platform == Platform.X360:
                    invert_color.location = (-744.0405, -237.4729)
                    invert_color_2 = mat.node_tree.nodes.new("ShaderNodeInvert")
                    invert_color_2.location = (-512.2188, -236.2577)
                else:
                    invert_color.location = (-629.6825, -237.2079)

                links = mat.node_tree.links
                
                links.new(tex_node.outputs["Color"], separate_color.inputs[0])
                links.new(separate_color.outputs[0], combine_color.inputs[0])

                if directory_meta.platform == Platform.X360:
                    links.new(separate_color.outputs[1], invert_color.inputs[1])
                    links.new(invert_color.outputs[0], combine_color.inputs[1])
                    links.new(separate_color.outputs[2], invert_color_2.inputs[1])
                    links.new(invert_color_2.outputs[0], combine_color.inputs[2])
                else:
                    links.new(separate_color.outputs[1], invert_color.inputs[1])
                    links.new(invert_color.outputs[0], combine_color.inputs[1])  
                    links.new(separate_color.outputs[2], combine_color.inputs[2])

                links.new(combine_color.outputs[0], normal_map_node.inputs[1])

                normal_map_node.uv_map = "UVMap"

                links.new(normal_map_node.outputs[0], bsdf.inputs["Normal"])

        specular_tex = bpy.data.textures.get(self.specular_tex)

        if specular_tex:
            if mat.use_nodes == False:
                mat.use_nodes = True

            bsdf = mat.node_tree.nodes.get("Principled BSDF")

            if bsdf:
                tex_node = mat.node_tree.nodes.new("ShaderNodeTexImage")
                tex_node.image = specular_tex.image
                tex_node.location = (-352.1719, -131.3825)

                bsdf.inputs[14].default_value = (self.specular_rgb[0], self.specular_rgb[1], self.specular_rgb[2], 1.0)

                links = mat.node_tree.links
                links.new(tex_node.outputs["Color"], bsdf.inputs[13])

                image = specular_tex.image

                if image:
                    image.alpha_mode = "CHANNEL_PACKED"
                    image.colorspace_settings.name = "Non-Color"

    def from_blender(mat_obj, bpy_self):
        bpy_self.version = 21 if bpy_self.game_selection == "GH1" else 47

        if bpy_self.game_selection == "GH1":
            texture_entry = TextureEntry()

            if mat_obj.use_nodes:
                for node in mat_obj.node_tree.nodes:
                    if node.type == "TEX_IMAGE":
                        texture_entry.tex_name = node.image.name
            
            bpy_self.texture_entries.append(texture_entry)

        if mat_obj.use_nodes:
            for node in mat_obj.node_tree.nodes:
                if (node.type == 'TEX_IMAGE') and (node.image):
                    mat_obj.diffuse_tex = node.image.name
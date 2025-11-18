from dataclasses import dataclass, field
from enum import Enum
from . bitmap import Bitmap
from . metadata import Metadata

class Type(Enum):
    kRegular = 1
    kRendered = 2
    kMovie = 4
    kBackBuffer = 8
    kFrontBuffer = 24
    kRenderedNoZ = 34
    kShadowMap = 66
    kDepthVolumeMap = 162
    kDensityMap = 290
    kScratch = 512
    kDeviceTexture = 4096

@dataclass
class Tex:
    version: int = 0
    metadata: Metadata = field(default_factory=Metadata)
    width: int = 0
    height: int = 0
    bpp: int = 0
    ext_path: str = ""
    mip_map_k: float = -8.0
    type: Type = Type.kRegular
    optimize_for_ps3: bool = False
    use_external_path: bool = False
    bitmap: Bitmap = field(default_factory=Bitmap)

    def read(self, reader):
        start_offset = reader.tell()

        self.version = reader.int32()

        if self.version > 8:
            self.metadata.read(reader)

        # Credits: C3 Con Tools
        if self.version == 11:
            reader.skip(start_offset + 32)

            gdrb = reader.byte()
            lrb = reader.byte()

            if (gdrb == 0) and (lrb != 0):
                gdrb = 1
                lrb = 0
            elif (gdrb == 0) and (lrb == 0):
                lrb = 4
            else:
                gdrb = 0
                lrb = 0
            
            reader.skip(start_offset + 17 + gdrb)

        self.width = reader.uint32()
        self.height = reader.uint32()

        self.bpp = reader.uint32()

        if self.version == 11:
            reader.seek(lrb)

        if self.version <= 4:
            self.ext_path = reader.string()
        else:
            self.ext_path = reader.numstring()

        if self.version >= 8:
            self.mip_map_k = reader.float32()

        tex_type = reader.uint32()

        try:
            self.type = Type(tex_type)
        except:
            pass

        if self.version == 7:
            self.use_external_path = reader.uint32()
        elif self.version > 7:
            self.use_external_path = reader.milo_bool()

        if self.version == 4:
            some_flags = reader.uint32()

        if (self.version == 11) or (self.version == 0x1000B):
            rb3 = reader.byte()

            # Only need to do the check for 360/PS3
            if self.version == 11:
                if rb3 != 0:
                    reader.seek(-1)

        if (self.version == 4) or (self.version == 5):
            padding = reader.read_bytes(4)

            if padding != b"\xAD\xDE\xAD\xDE":
                raise Exception("Padding was not AD DE AD DE, read most likely failed.")
            
            return

        if self.version == 0x1000B:
            unk_short = reader.short()

            reader.little_endian = True

        self.bitmap.read(reader)

        if self.version == 0x1000B:
            reader.little_endian = False

            always_negative_8 = reader.float32()

            always_1 = reader.int32()

            unknown_byte = reader.byte()
            unknown_byte_2 = reader.byte()
        
        padding = reader.read_bytes(4)

        if padding != b"\xAD\xDE\xAD\xDE":
            raise Exception("Padding was not AD DE AD DE, read most likely failed.")
        
    def write(self, writer):
        writer.int32(self.version)

        if self.version > 8:
            self.metadata.write(writer)

        writer.uint32(self.width)
        writer.uint32(self.height)

        writer.uint32(self.bpp)

        writer.numstring(self.ext_path)

        if self.version >= 8:
            writer.float32(self.mip_map_k)

        writer.uint32(self.type.value)

        writer.bool(self.use_external_path)

        self.bitmap.write(writer)

    def import_to_blender(self, name: str, filepath: str):
        import bpy
        from pathlib import Path

        tex = bpy.data.textures.new(name, type='IMAGE')

        dirname = Path(filepath).parent
        filename = Path(name).with_suffix(".png")
        texture_path = Path.joinpath(dirname, filename)
        
        img = bpy.data.images.load(str(texture_path), check_existing=True)
        tex.image = img

    def from_blender(self, image_path: str, bpy_self):
        from pathlib import Path
        try:
            from PIL import Image
        except:
            from .... install_modules import install
            install("pillow")

        image = Image.open(image_path)

        self.version = 8 if bpy_self.game_selection == "GH1" else 10

        self.width = image.size[0]
        self.height = image.size[1]

        self.ext_path = str(Path(image_path).name)

        is_alpha = True if image.mode in ["RGBA", "LA"] else False

        if (self.width % 4 != 0) or (self.height % 4 != 0):
            raise Exception("Image width and height must be multiples of 4, please resize and try again.")

        if bpy_self.game_selection == "GH1":
            self.bpp = 32
        else:
            self.bpp = 8 if image.mode in ["RGBA", "LA"] else 4

        self.bitmap.from_blender(image, is_alpha, bpy_self)
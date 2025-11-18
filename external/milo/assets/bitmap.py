from dataclasses import dataclass, field
from enum import Enum

class Encoding(Enum):
    RGBA = 0
    ARGB = 1
    RGBA_2 = 3
    RGBA_3 = 259
    RGBA_4 = 515
    DXT1 = 8
    DXT5 = 24
    ATI2 = 32
    CMP = 72
    CMP_ALPHA = 328
    CMP_2 = 583

@dataclass
class Bitmap:
    version: int = 1
    hash: int = 0
    bpp: int = 0
    encoding: Encoding = Encoding.ARGB
    mip_maps: int = 0
    width: int = 0
    height: int = 0
    bpl: int = 0
    wii_alpha_num: int = 0
    color_palette: memoryview = ()
    textures: list[memoryview] = field(default_factory=list)
    decoded_image: bytearray = field(default_factory=bytearray)

    def read(self, reader):
        self.version = reader.byte()

        is_alt_v2 = False

        bpp_test = reader.byte()
        reader.seek(-1)

        if bpp_test not in [4, 8, 24]:
            self.hash = reader.uint32()

            is_alt_v2 = True

        self.bpp = reader.byte()

        if self.version == 0:
            self.encoding = Encoding(reader.ushort())
        else:
            self.encoding = Encoding(reader.uint32())

        if self.version > 0:
            self.mip_maps = reader.byte()

        self.width = reader.ushort()
        self.height = reader.ushort()

        self.bpl = reader.ushort()

        if self.version > 0:
            self.wii_alpha_num = reader.ushort()

        if is_alt_v2 == True:
            padding = reader.read_bytes(13)
        else:
            if self.version == 0:
                padding = reader.read_bytes(6)         
            else:
                padding = reader.read_bytes(17)

        if (self.width == 0) and (self.height == 0):
            return
            
        if self.encoding in [Encoding.RGBA, Encoding.RGBA_2, Encoding.RGBA_3, Encoding.RGBA_4]:
            if (self.bpp == 4) or (self.bpp == 8):
                self.color_palette = reader.read_bytes(1 << (self.bpp + 2))

        i = 0

        w = self.width
        h = self.height

        while i <= self.mip_maps:
            self.textures.append(reader.read_bytes((w * h * self.bpp) // 8))

            w >>= 1
            h >>= 1

            i += 1

    def write(self, writer):
        writer.byte(self.version)

        writer.byte(self.bpp)

        writer.uint32(self.encoding.value)

        writer.byte(self.mip_maps)

        writer.ushort(self.width)
        writer.ushort(self.height)

        writer.ushort(self.bpl)

        writer.ushort(self.wii_alpha_num)

        writer.write_bytes(bytes([0] * 17))

        for texture in self.textures:
            writer.write_bytes(texture)

    def convert(self, platform):
        from .. platform import Platform
        from .. image_classes.dxtc import DXTC
        from .. image_classes.rgba import RGBA
        from .. image_classes.tpl import TPL
        from .. image_helpers.swap_x360_bytes import swap_x360_bytes

        if platform == Platform.X360:
            for i in range(len(self.textures)):
                self.textures[i] = swap_x360_bytes(self.textures[i])
        elif platform == Platform.Wii:
            if (self.encoding == Encoding.CMP) or (self.encoding == Encoding.CMP_2):
                tpl = TPL(image=self.textures[0], width=self.width, height=self.height)
                tpl.convert()
            else:
                rgb_bytes = self.textures[0][:len(self.textures[0]) // 2]
                alpha_bytes = self.textures[0][len(self.textures[0]) // 2:]

                rgb_tpl = TPL(image=rgb_bytes, width=self.width, height=self.height)
                alpha_tpl = TPL(image=alpha_bytes, width=self.width, height=self.height)

                rgb_tpl.convert()
                alpha_tpl.convert()

        if "RGBA" in str(self.encoding):
            if (self.bpp == 4) or (self.bpp == 8):
                color_palette = self.color_palette.tobytes()
            else:
                color_palette = None

            rgba = RGBA(image=self.textures[0], width=self.width, height=self.height, bpp=self.bpp, color_palette=color_palette)
            rgba.convert()

            self.decoded_image = rgba.decoded_image
        else:
            if platform == Platform.Wii:
                if (self.encoding == Encoding.CMP) or (self.encoding == Encoding.CMP_2):
                    dxtc = DXTC(image=tpl.shuffled_image, encoding="DXT1", width=self.width, height=self.height)
                    dxtc.decode()

                    self.decoded_image = dxtc.decoded_image
                else:
                    rgb_dxtc = DXTC(image=rgb_tpl.shuffled_image, encoding="DXT1", width=self.width, height=self.height)
                    alpha_dxtc = DXTC(image=alpha_tpl.shuffled_image, encoding="DXT1", width=self.width, height=self.height)

                    rgb_dxtc.decode()
                    alpha_dxtc.decode()

                    for i in range(0, len(rgb_dxtc.decoded_image), 4):
                        rgb_dxtc.decoded_image[i + 3] = alpha_dxtc.decoded_image[i + 1]

                    self.decoded_image = rgb_dxtc.decoded_image
            else:
                dxtc = DXTC(image=self.textures[0], encoding=str(self.encoding.name), width=self.width, height=self.height)
                dxtc.decode()

                self.decoded_image = dxtc.decoded_image

    def export_to_image(self, filepath: str):
        try:
            from PIL import Image
        except:
            from .... install_modules import install
            install("pillow")
        
        image = Image.frombytes("RGBA", (self.width, self.height), self.decoded_image)
        image.save(filepath)

    def from_blender(self, image, is_alpha: bool, bpy_self):
        from .. image_classes.dxtc import DXTC
        from .. image_helpers.swap_x360_bytes import swap_x360_bytes

        self.width = image.size[0]
        self.height = image.size[1]

        self.bpl = ((self.width * 8) // 8) if is_alpha == True else ((self.width * 4) // 8)

        if bpy_self.game_selection == "GH1":
            self.bpp = 32

            format = "RGBA"
        else:
            self.bpp = 8 if is_alpha == True else 4

            format = "DXT5" if is_alpha == True else "DXT1"

        if format == "RGBA":
            self.encoding == Encoding.RGBA
        elif format == "DXT1":
            self.encoding == Encoding.DXT1
        elif format == "DXT5":
            self.encoding == Encoding.DXT5
        
        if bpy_self.game_selection == "GH1":
            if image.mode not in ["RGBA", "LA"]:
                image = image.convert("RGBA")

            self.textures.append(image.tobytes())
        else:
            dxtc = DXTC(texture=image.tobytes(), encoding=format, width=self.width, height=self.height)
            dxtc.encode()

            if bpy_self.milo_extension == ".milo_ps3":
                self.textures.append(dxtc.encoded_image)
            elif bpy_self.milo_extension == ".milo_xbox":
                self.textures.append(swap_x360_bytes(dxtc.encoded_image))
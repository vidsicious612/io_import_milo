class RGBA:
    def __init__(self, image: bytes, width: int, height: int, bpp: int, color_palette: bytes = None):
        self.image: bytes = image
        self.width: int = width
        self.height: int = height
        self.bpp: int = bpp
        self.color_palette: bytes = color_palette
        self.decoded_image = bytearray(self.width * self.height * 4)

    def convert(self):
        self.decode()
        self.fix_alpha()

    def decode(self) -> bytearray:
        if self.bpp == 4:
            o = (len(self.color_palette) // 32) * 32

            texture = self.color_palette + self.image

            r = 0

            p1 = 0
            p2 = 0
            p3 = 0
            p4 = 0

            for i in range(0, len(self.decoded_image), 16):
                p1 = (texture[o + r] & 0x0F) << 2
                p2 = (texture[o + r] & 0xF0) >> 2
                p3 = (texture[o + r + 1] & 0X0F) << 2
                p4 = (texture[o + r + 1] & 0xF0) >> 2

                self.decoded_image[i] = self.color_palette[p1]
                self.decoded_image[i + 1] = self.color_palette[p1 + 1]
                self.decoded_image[i + 2] = self.color_palette[p1 + 2]
                self.decoded_image[i + 3] = self.color_palette[p1 + 3]
                self.decoded_image[i + 4] = self.color_palette[p2]
                self.decoded_image[i + 5] = self.color_palette[p2 + 1]
                self.decoded_image[i + 6] = self.color_palette[p2 + 2]
                self.decoded_image[i + 7] = self.color_palette[p2 + 3]            
                self.decoded_image[i + 8] = self.color_palette[p3]
                self.decoded_image[i + 9] = self.color_palette[p3 + 1]
                self.decoded_image[i + 10] = self.color_palette[p3 + 2]
                self.decoded_image[i + 11] = self.color_palette[p3 + 3]
                self.decoded_image[i + 12] = self.color_palette[p4]
                self.decoded_image[i + 13] = self.color_palette[p4 + 1]
                self.decoded_image[i + 14] = self.color_palette[p4 + 2]
                self.decoded_image[i + 15] = self.color_palette[p4 + 3]

                r += 2
        elif self.bpp == 8:
            o = (len(self.color_palette) // 32) * 32

            texture = self.color_palette + self.image

            r = 0

            p1 = 0
            p2 = 0
            p3 = 0
            p4 = 0    

            for i in range(0, len(self.decoded_image), 16):
                p1 = ((0xE7 & texture[o + r])) + ((0x08 & texture[o + r]) << 1) + ((0x10 & texture[o + r]) >> 1) << 2
                p2 = ((0xE7 & texture[o + r + 1])) + ((0x08 & texture[o + r + 1]) << 1) + ((0x10 & texture[o + r + 1]) >> 1) << 2
                p3 = ((0xE7 & texture[o + r + 2])) + ((0x08 & texture[o + r + 2]) << 1) + ((0x10 & texture[o + r + 2]) >> 1) << 2
                p4 = ((0xE7 & texture[o + r + 3])) + ((0x08 & texture[o + r + 3]) << 1) + ((0x10 & texture[o + r + 3]) >> 1) << 2

                self.decoded_image[i] = self.color_palette[p1]
                self.decoded_image[i + 1] = self.color_palette[p1 + 1]
                self.decoded_image[i + 2] = self.color_palette[p1 + 2]
                self.decoded_image[i + 3] = self.color_palette[p1 + 3]
                self.decoded_image[i + 4] = self.color_palette[p2]
                self.decoded_image[i + 5] = self.color_palette[p2 + 1]
                self.decoded_image[i + 6] = self.color_palette[p2 + 2]
                self.decoded_image[i + 7] = self.color_palette[p2 + 3]            
                self.decoded_image[i + 8] = self.color_palette[p3]
                self.decoded_image[i + 9] = self.color_palette[p3 + 1]
                self.decoded_image[i + 10] = self.color_palette[p3 + 2]
                self.decoded_image[i + 11] = self.color_palette[p3 + 3]
                self.decoded_image[i + 12] = self.color_palette[p4]
                self.decoded_image[i + 13] = self.color_palette[p4 + 1]
                self.decoded_image[i + 14] = self.color_palette[p4 + 2]
                self.decoded_image[i + 15] = self.color_palette[p4 + 3]

                r += 4
        elif self.bpp == 24:
            r = 0

            for i in range(0, len(self.decoded_image), 16):
                self.decoded_image[i] = self.image[r + 2]
                self.decoded_image[i + 1] = self.image[r + 1]
                self.decoded_image[i + 2] = self.image[r]
                self.decoded_image[i + 3] = 0xFF
                self.decoded_image[i + 4] = self.image[r + 5]
                self.decoded_image[i + 5] = self.image[r + 4]
                self.decoded_image[i + 6] = self.image[r + 3]
                self.decoded_image[i + 7] = 0xFF
                self.decoded_image[i + 8] = self.image[r + 8]
                self.decoded_image[i + 9] = self.image[r + 7]
                self.decoded_image[i + 10] = self.image[r + 6]
                self.decoded_image[i + 11] = 0xFF
                self.decoded_image[i + 12] = self.image[r + 11]
                self.decoded_image[i + 13] = self.image[r + 10]
                self.decoded_image[i + 14] = self.image[r + 9]
                self.decoded_image[i + 15] = 0xFF
                
                r += 12

    def fix_alpha(self):
        for i in range(3, len(self.decoded_image), 4):
            alpha = self.decoded_image[i]

            if alpha & 0x80:
                self.decoded_image[i] = 0xFF
            else:
                self.decoded_image[i] = alpha << 1
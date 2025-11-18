class DXTC:
    def __init__(self, image: bytes, encoding: str, width: int, height: int):
        self.image: bytes = image
        self.encoding: str = encoding
        self.width: int = width
        self.height: int = height
        self.decoded_image: bytearray = bytearray([0] * (width * height * 4))

    def linear_offset(self, x: int, y: int, w: int) -> int:
        return (y * (w << 2)) + (x << 2)

    def unpack_24_bit_indices(self, packed: int) -> list:
        indices = []

        indices.append(packed & 0b0111)
        indices.append(((packed & (0b0111 <<  3)) >>  3))
        indices.append(((packed & (0b0111 <<  6)) >>  6))
        indices.append(((packed & (0b0111 <<  9)) >>  9))
        indices.append(((packed & (0b0111 <<  12)) >>  12))
        indices.append(((packed & (0b0111 <<  15)) >>  15))
        indices.append(((packed & (0b0111 <<  18)) >>  18))
        indices.append(((packed & (0b0111 <<  21)) >>  21))

        return indices

    def interpolate_colors(self, c0: int, c1: int) -> list:
        colors = []

        if c0 > c1:
            colors.append(c0)
            colors.append(c1)

            colors.append(int(((6.0 / 7.0) * c0) + ((1.0 / 7.0) * c1)))
            colors.append(int(((5.0 / 7.0) * c0) + ((2.0 / 7.0) * c1)))
            colors.append(int(((4.0 / 7.0) * c0) + ((3.0 / 7.0) * c1)))
            colors.append(int(((3.0 / 7.0) * c0) + ((4.0 / 7.0) * c1)))
            colors.append(int(((2.0 / 7.0) * c0) + ((5.0 / 7.0) * c1)))
            colors.append(int(((1.0 / 7.0) * c0) + ((6.0 / 7.0) * c1)))
        else:
            colors.append(c0)
            colors.append(c1)

            colors.append(int(((4.0 / 5.0) * c0) + ((1.0 / 5.0) * c1)))
            colors.append(int(((3.0 / 5.0) * c0) + ((2.0 / 5.0) * c1)))
            colors.append(int(((2.0 / 5.0) * c0) + ((3.0 / 5.0) * c1)))
            colors.append(int(((1.0 / 5.0) * c0) + ((4.0 / 5.0) * c1)))

            colors.append(0x00)
            colors.append(0xFF)

        return colors

    def unpack_indexed_interpolated_colors(self, bitmap: bytes, i: int) -> list:
        pixels = [0] * 16

        colors = self.interpolate_colors(bitmap[i], bitmap[i + 1])

        packed_0 = (bitmap[i + 4] << 16) | (bitmap[i + 3] << 8) | (bitmap[i + 2])
        packed_1 = (bitmap[i + 7] << 16) | (bitmap[i + 6] << 8) | (bitmap[i + 5])

        indices = self.unpack_24_bit_indices(packed_0)

        pixels[0] = colors[indices[0]]
        pixels[1] = colors[indices[1]]
        pixels[2] = colors[indices[2]]
        pixels[3] = colors[indices[3]]
        pixels[4] = colors[indices[4]]
        pixels[5] = colors[indices[5]]
        pixels[6] = colors[indices[6]]
        pixels[7] = colors[indices[7]]

        indices = self.unpack_24_bit_indices(packed_1)

        pixels[8] = colors[indices[0]]
        pixels[9] = colors[indices[1]]
        pixels[10] = colors[indices[2]]
        pixels[11] = colors[indices[3]]
        pixels[12] = colors[indices[4]]
        pixels[13] = colors[indices[5]]
        pixels[14] = colors[indices[6]]
        pixels[15] = colors[indices[7]]
        
        return pixels

    def unpack_rgb565(self, c: int) -> tuple[int, int, int]:
        r = (c >> 11) & 0x1F
        g = (c >> 5) & 0x3F
        b = c & 0x1F

        r = (r << 3) | (r >> 2)
        g = (g << 2) | (g >> 4)
        b = (b << 3) | (b >> 2)

        return r, g, b

    def decode(self):
        if self.encoding == "DXT1":
            self.decode_dxt1()
        elif self.encoding == "DXT5":
            self.decode_dxt5()
        elif self.encoding == "ATI2":
            self.decode_ati2()

    def decode_dxt1(self):
        import struct

        offset = 0

        for y in range(0, self.height, 4):
            for x in range(0, self.width, 4):
                color_0, color_1, bits = struct.unpack_from('<HHI', self.image, offset); offset += 8

                r0, g0, b0 = self.unpack_rgb565(color_0)
                r1, g1, b1 = self.unpack_rgb565(color_1)

                for j in range(4):
                    for i in range(4):
                        control = bits & 3
                        bits = bits >> 2

                        if control == 0:
                            r, g, b = r0, g0, b0
                        elif control == 1:
                            r, g, b = r1, g1, b1
                        elif control == 2:
                            if color_0 > color_1:
                                r = (2 * r0 + r1) // 3
                                g = (2 * g0 + g1) // 3
                                b = (2 * b0 + b1) // 3
                            else:
                                r = (r0 + r1) // 2
                                g = (g0 + g1) // 2
                                b = (b0 + b1) // 2
                        elif control == 3:
                            if color_0 > color_1:
                                r = (2 * r1 + r0) // 3
                                g = (2 * g1 + g0) // 3
                                b = (2 * b1 + b0) // 3
                            else:
                                r, g, b = 0, 0, 0

                        idx = 4 * ((y + j) * self.width + x + i)

                        self.decoded_image[idx:idx + 4] = struct.pack("4B", r, g, b, 255)

    def decode_dxt5(self):
        import struct

        offset = 0

        for y in range(0, self.height, 4):
            for x in range(0, self.width, 4):
                alpha_0, alpha_1 = struct.unpack_from('<BB', self.image, offset); offset += 2

                bits = struct.unpack_from('<6B', self.image, offset); offset += 6

                color_0, color_1, code = struct.unpack_from('<HHI', self.image, offset); offset += 8

                alpha_c_0 = bits[2] | (bits[3] << 8) | (bits[4] << 16) | (bits[5] << 24)
                alpha_c_1 = bits[0] | (bits[1] << 8)

                r0, g0, b0 = self.unpack_rgb565(color_0)
                r1, g1, b1 = self.unpack_rgb565(color_1)

                for j in range(4):
                    for i in range(4):
                        alpha_code_index = 3 * (j * 4 + i)

                        if alpha_code_index <= 12:
                            alphacode = (alpha_c_1 >> alpha_code_index) & 0x07
                        elif alpha_code_index == 15:
                            alphacode = (alpha_c_1 >> 15) | ((alpha_c_0 << 1) & 0x06)
                        else:
                            alphacode = (alpha_c_0 >> (alpha_code_index - 16)) & 0x07

                        if alphacode == 0:
                            a = alpha_0
                        elif alphacode == 1:
                            a = alpha_1
                        elif alpha_0 > alpha_1:
                            a = ((8 - alphacode) * alpha_0 + (alphacode - 1) * alpha_1) // 7
                        elif alphacode == 6:
                            a = 0
                        elif alphacode == 7:
                            a = 255
                        else:
                            a = ((6 - alphacode) * alpha_0 + (alphacode - 1) * alpha_1) // 5

                        color_code = (code >> 2 * (4 * j + i)) & 0x03

                        if color_code == 0:
                            r, g, b = r0, g0, b0
                        elif color_code == 1:
                            r, g, b = r1, g1, b1
                        elif color_code == 2:
                            r = (2 * r0 + r1) // 3
                            g = (2 * g0 + g1) // 3
                            b = (2 * b0 + b1) // 3
                        elif color_code == 3:
                            r = (2 * r1 + r0) // 3
                            g = (2 * g1 + g0) // 3
                            b = (2 * b1 + b0) // 3

                        idx = 4 * ((y + j) * self.width + x + i)

                        self.decoded_image[idx:idx + 4] = struct.pack("4B", r, g, b, a)

    def decode_ati2(self):
        blocks_x = self.width >> 2
        blocks_y = self.height >> 2

        block_size = 8

        i = 0

        for by in range(blocks_y):
            for bx in range(blocks_x):
                x = bx << 2
                y = by << 2

                reds = self.unpack_indexed_interpolated_colors(self.image, i)
                greens = self.unpack_indexed_interpolated_colors(self.image, i + 8)

                normal_colors = [0] * 64

                for c in range(len(reds)):
                    normal_colors[(c << 2)] = reds[c]
                    normal_colors[(c << 2) + 1] = greens[c]
                    normal_colors[(c << 2) + 2] = 0x00
                    normal_colors[(c << 2) + 3] = 0xFF

                self.decoded_image[self.linear_offset(x, y, self.width):self.linear_offset(x, y, self.width) + 4] = normal_colors[0:4]
                self.decoded_image[self.linear_offset(x + 1, y, self.width):self.linear_offset(x + 1, y, self.width) + 4] = normal_colors[4:8]
                self.decoded_image[self.linear_offset(x + 2, y, self.width):self.linear_offset(x + 2, y, self.width) + 4] = normal_colors[8:12]
                self.decoded_image[self.linear_offset(x + 3, y, self.width):self.linear_offset(x + 3, y, self.width) + 4] = normal_colors[12:16]
                self.decoded_image[self.linear_offset(x, y + 1, self.width):self.linear_offset(x, y + 1, self.width) + 4] = normal_colors[16:20]
                self.decoded_image[self.linear_offset(x + 1, y + 1, self.width):self.linear_offset(x + 1, y + 1, self.width) + 4] = normal_colors[20:24]
                self.decoded_image[self.linear_offset(x + 2, y + 1, self.width):self.linear_offset(x + 2, y + 1, self.width) + 4] = normal_colors[24:28]
                self.decoded_image[self.linear_offset(x + 3, y + 1, self.width):self.linear_offset(x + 3, y + 1, self.width) + 4] = normal_colors[28:32]
                self.decoded_image[self.linear_offset(x, y + 2, self.width):self.linear_offset(x, y + 2, self.width) + 4] = normal_colors[32:36]
                self.decoded_image[self.linear_offset(x + 1, y + 2, self.width):self.linear_offset(x + 1, y + 2, self.width) + 4] = normal_colors[36:40]
                self.decoded_image[self.linear_offset(x + 2, y + 2, self.width):self.linear_offset(x + 2, y + 2, self.width) + 4] = normal_colors[40:44]
                self.decoded_image[self.linear_offset(x + 3, y + 2, self.width):self.linear_offset(x + 3, y + 2, self.width) + 4] = normal_colors[44:48]     
                self.decoded_image[self.linear_offset(x, y + 3, self.width):self.linear_offset(x, y + 3, self.width) + 4] = normal_colors[48:52]
                self.decoded_image[self.linear_offset(x + 1, y + 3, self.width):self.linear_offset(x + 1, y + 3, self.width) + 4] = normal_colors[52:56]
                self.decoded_image[self.linear_offset(x + 2, y + 3, self.width):self.linear_offset(x + 2, y + 3, self.width) + 4] = normal_colors[56:60]
                self.decoded_image[self.linear_offset(x + 3, y + 3, self.width):self.linear_offset(x + 3, y + 3, self.width) + 4] = normal_colors[60:64]    

                i += block_size << 1   
class TPL:
    def __init__(self, image: bytes, width: int, height: int, inverse: bool = False):
        self.image: bytes = image
        self.width: int = width
        self.height: int = height
        self.inverse: bool = inverse
        self.shuffled_image: bytearray = bytearray(len(self.image))

    def convert(self):
        self.shuffle_blocks()
        self.fix_colors_and_indices()

    def create_block_map(self, map: list) -> None:
        if self.inverse == False:
            bx = len(map)

            for i in range(bx):
                map[i] = (i // 2) + ((i % 2) * (bx // 2))
        else:
            half_size = len(map) // 2

            for i in range(half_size):
                map[i] = i * 2

            for i in range(half_size, len(map)):
                map[i] = ((i % half_size) * 2) + 1
            
    def shuffle_blocks(self):
        blocks_x = self.width // 4
        blocks_y = self.height // 4

        group_byte_size = 16

        total_grouped_blocks = (blocks_x * blocks_y) // 2

        group_blocks_in_2_rows = blocks_x

        block_map = [0] * group_blocks_in_2_rows
        self.create_block_map(block_map)

        orig_data = [0] * (group_blocks_in_2_rows * group_byte_size)

        for i in range(total_grouped_blocks):
            o = i // blocks_x
            x = i % blocks_x

            current_working_index = o * group_blocks_in_2_rows
            current_index = x * group_byte_size

            new_index = block_map[x] * group_byte_size

            if x == 0:
                working_start = o * len(orig_data)

                orig_data[:] = self.image[working_start:working_start + len(orig_data)]

            self.shuffled_image[current_working_index * group_byte_size + new_index:current_working_index * group_byte_size + new_index + group_byte_size] = orig_data[current_index:current_index + group_byte_size]

    def fix_colors_and_indices(self):
        buffer = [0] * 8
        
        for i in range(0, len(self.shuffled_image), 8):
            buffer[:] = self.shuffled_image[i:i + 4]

            self.shuffled_image[i + 0] = buffer[1]
            self.shuffled_image[i + 1] = buffer[0]
            self.shuffled_image[i + 2] = buffer[3]
            self.shuffled_image[i + 3] = buffer[2]

            buffer[:] = self.shuffled_image[i + 4:i + 8]

            self.shuffled_image[i + 4] = self.reverse_index_row(buffer[0])
            self.shuffled_image[i + 5] = self.reverse_index_row(buffer[1])
            self.shuffled_image[i + 6] = self.reverse_index_row(buffer[2])
            self.shuffled_image[i + 7] = self.reverse_index_row(buffer[3])

    def reverse_index_row(self, byte: int) -> int:
        return (((byte & 0b00_00_00_11) << 6) | ((byte & 0b00_00_11_00) << 2) | ((byte & 0b00_11_00_00) >> 2) | ((byte & 0b11_00_00_00) >> 6))
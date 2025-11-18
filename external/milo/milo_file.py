from dataclasses import dataclass, field
from enum import Enum
from . compression import *
from . directory_meta import DirectoryMeta
from . platform import Platform, get_platform
from ... readers import Reader
from ... writers import Writer

class Compression(Enum):
    Uncompressed = b"\xAF\xDE\xBE\xCA"
    ZLIB = b"\xAF\xDE\xBE\xCB"
    GZIP = b"\xAF\xDE\xBE\xCC"
    ZLIBAlt = b"\xAF\xDE\xBE\xCD"

@dataclass
class MiloFile:
    path: str = ""
    platform: Platform = Platform.PS3
    compression: Compression = Compression.Uncompressed
    start_offset: int = 0
    largest_uncompressed_block: int = 0
    block_sizes: list[int] = field(default_factory=list)
    dir_meta: DirectoryMeta = field(default_factory=DirectoryMeta)

    def read(self):
        reader = Reader(open(self.path, "rb").read())

        self.platform = get_platform(self.path)

        magic = reader.read_bytes(4).tobytes()

        if magic in [compression.value for compression in Compression]:
            self.compression = Compression(magic)
        else:
            reader.skip(0)

            self.dir_meta.read(reader)

        self.start_offset = reader.uint32()

        block_count = reader.uint32()

        self.largest_uncompressed_block = reader.uint32()

        self.block_sizes = [reader.uint32() for _ in range(block_count)]

        padding = reader.read_bytes(self.start_offset - reader.tell())

        if self.compression == Compression.Uncompressed:
            reader.skip(self.start_offset)

            self.dir_meta.platform = self.platform
            self.dir_meta.read(reader)
        elif self.compression == Compression.ZLIB:
            decompressed = []

            for size in self.block_sizes:
                block = reader.read_bytes(size)

                decompressed.append(decompress_zlib_deflate(block))
            
            decompressed_reader = Reader(b"".join(decompressed))
                
            self.dir_meta.platform = self.platform
            self.dir_meta.read(decompressed_reader)
        elif self.compression == Compression.GZIP:
            decompressed = []

            for size in self.block_sizes:
                block = reader.read_bytes(size)

                decompressed.append(decompress_gzip(block))

            decompressed_reader = Reader(b"".join(decompressed))

            self.dir_meta.platform = self.platform
            self.dir_meta.read(decompressed_reader)
        elif self.compression == Compression.ZLIBAlt:
            decompressed = []

            for size in self.block_sizes:
                compressed = (size & 0xFF000000) == 0

                block_size = size & 0x00FFFFFF

                block = reader.read_bytes(block_size)

                if compressed == True:
                    decompressed_block = decompress_zlib_deflate(block[4:])

                    decompressed.append(decompressed_block)
                else:
                    decompressed.append(block)
    
            decompressed_reader = Reader(b"".join(decompressed))

            self.dir_meta.platform = self.platform
            self.dir_meta.read(decompressed_reader)
    
    def write(self, dir_meta_little_endian: bool):
        with open(self.path, "wb") as f:
            writer = Writer(f)

            writer.write_bytes(self.compression.value)
            
            writer.uint32(self.start_offset)

            writer.uint32(1)

            writer.uint32(0)
            writer.uint32(0)

            writer.write_bytes(bytes([0] * (self.start_offset - writer.tell())))

            if dir_meta_little_endian == False:
                writer.little_endian = False
            
            self.dir_meta.write(writer)

            file_size = writer.tell()

            writer.skip(12)

            writer.little_endian = True
            
            writer.int32(file_size - self.start_offset)
            writer.int32(file_size - self.start_offset)

    def from_blender(self, bpy_self):
        self.start_offset = 528 if bpy_self.game_selection == "GH1" else 2064

        self.dir_meta.from_blender(bpy_self)
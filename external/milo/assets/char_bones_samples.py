from dataclasses import dataclass, field
from enum import Enum

def convert_pos_sample(sample: tuple[int, int, int]) -> tuple[float, float, float]:
    x = max(float(sample[0] / 32767.0), -1)
    y = max(float(sample[1] / 32767.0), -1)
    z = max(float(sample[2] / 32767.0), -1)

    return (x, y, z)

def convert_quat_sample(sample: tuple[int, int, int, int]) -> tuple[float, float, float, float]:
    x = max(float(sample[0] / 32767.0), -1)
    y = max(float(sample[1] / 32767.0), -1)
    z = max(float(sample[2] / 32767.0), -1)
    w = max(float(sample[3] / 32767.0), -1)

    return (x, y, z, w)

def convert_rotz_sample(x: int) -> float:
    x = max(float(x / 32767.0), -1)

    return x

def calc_bone_count_with_ext(char_bones_list: list, ext: str) -> int:
    if len(char_bones_list) == 0:
        return 0

    count = 0

    for i in range(len(char_bones_list)):
        if len(char_bones_list[i].symbol) == 0:
            continue

        ext_index = char_bones_list[i].symbol.find(ext)
        
        if ext_index > -1:
            count += 1
        
    return count

class CompressionEnum(Enum):
    kCompressNone = 0
    kCompressRots = 1
    kCompressVects = 2
    kCompressQuats = 3

@dataclass
class CharBone4Bone:
    symbol: str = ""
    weight: float = 1.0

    def read(self, reader, version: int):
        self.symbol = reader.numstring()

        if (version != -1) and (version <= 10):
            return
    
        self.weight = reader.float32()

    def write(self, writer, version: int):
        writer.numstring(self.symbol)

        if (version != -1) and (version <= 10):
            return
    
        writer.float32(self.weight)

@dataclass
class CharBones:
    bones: list[CharBone4Bone] = field(default_factory=list)

    def read(self, reader, version: int):
        bone_count = reader.int32()
        
        for _ in range(bone_count):
            bone = CharBone4Bone()
            bone.read(reader, version)

            self.bones.append(bone)      

    def write(self, writer, version: int):
        writer.int32(len(self.bones))

        for bone in self.bones:
            bone.write(writer, version)

@dataclass
class PosSample:
    sample: tuple = (0.0, 0.0, 0.0)
    bone_name: str = ""

    def read(self, reader, compression: CompressionEnum):
        if compression.value < 2:
            self.sample = reader.vec3f()
        else:
            sample = reader.vec3s()

            self.sample = convert_pos_sample(sample)

@dataclass
class QuatSample:
    sample: tuple = (0.0, 0.0, 0.0, 0.0)
    bone_name: str = ""

    def read(self, reader, compression: CompressionEnum):
        if compression.value == 0:
            self.sample = reader.vec4f()
        elif compression.value < 3:
            sample = reader.vec4s()

            self.sample = convert_quat_sample(sample)
        else:
            self.sample = reader.vec4b()

@dataclass
class RotSample:
    x: float = 0.0
    bone_name: str = ""

    def read(self, reader, compression: CompressionEnum):
        if compression.value == 0:
            self.x = reader.float32()
        else:
            sample = reader.short()

            self.sample = convert_rotz_sample(sample)

@dataclass
class Sample:
    samples: list = field(default_factory=list)

    def read(self, reader, char_bones_samples):
        pos_count = calc_bone_count_with_ext(char_bones_samples.char_bones.bones, ".pos")
        quat_count = calc_bone_count_with_ext(char_bones_samples.char_bones.bones, ".quat")
        rotz_count = calc_bone_count_with_ext(char_bones_samples.char_bones.bones, ".rotz")

        bone_index = 0

        start = reader.tell()

        for _ in range(pos_count):
            sample = PosSample()
            sample.read(reader, char_bones_samples.compression)

            sample.bone_name = char_bones_samples.char_bones.bones[bone_index].symbol

            self.samples.append(sample)

            bone_index += 1

        for _ in range(quat_count):
            sample = QuatSample()
            sample.read(reader, char_bones_samples.compression)

            sample.bone_name = char_bones_samples.char_bones.bones[bone_index].symbol

            self.samples.append(sample)

            bone_index += 1

        for _ in range(rotz_count):
            sample = RotSample()
            sample.read(reader, char_bones_samples.compression)

            sample.bone_name = char_bones_samples.char_bones.bones[bone_index].symbol

            self.samples.append(sample)

            bone_index += 1        

        end = reader.tell()

        diff = char_bones_samples.sample_size - (end - start)

        if char_bones_samples.version > 11:
            padding = reader.read_bytes(diff)

@dataclass
class CharBonesSamplesData:
    samples: list[Sample] = field(default_factory=list)
    
    def read(self, reader, char_bones_samples):
        if char_bones_samples.version == 14:
            some_bool = reader.milo_bool()

        for _ in range(char_bones_samples.num_samples):
            sample = Sample()
            sample.read(reader, char_bones_samples)

            for s in sample.samples:
                self.samples.append(s)

@dataclass
class CharBonesSamples:
    version: int = 0
    char_bones: CharBones = field(default_factory=CharBones)
    compression: CompressionEnum = None
    counts: list[int] = field(default_factory=list)
    computed_sizes: list[int] = field(default_factory=list)
    frames: list[float] = field(default_factory=list)
    char_bones_samples_data: CharBonesSamplesData = field(default_factory=CharBonesSamplesData)

    def get_type_size(self, index: int) -> int:
        if index < 2:
            return 16 if self.compression.value < 2 else 6
        
        if index != 2:
            return 4 if self.compression.value == 0 else 2
        
        if self.compression.value > 2:
            return 4
        
        if self.compression.value == 0:
            return 16
        
        return 8

    def recompute_sizes(self, count_size: int):
        self.computed_sizes[0] = 0

        i = 0

        curr_count = 0
        next_count = 0
        
        type_size = 0

        while i < count_size - 1:
            curr_count = self.counts[i]
            next_count = self.counts[i + 1]

            type_size = self.get_type_size(i)

            self.computed_sizes[i + 1] = self.computed_sizes[i] + (next_count - curr_count) * type_size

            i += 1
        
        self.sample_size = (self.computed_sizes[count_size - 1] + 0xF) & 0xFFFFFFF0

    def read(self, reader, fake_version: int):
        if fake_version == -1:
            self.version = reader.int32()
        else:
            self.version = fake_version

        if self.version > 15:
            count_size = 7
        else:
            count_size = 10

        self.char_bones.read(reader, self.version)

        for _ in range(count_size):
            self.counts.append(reader.uint32())

        self.compression = CompressionEnum(reader.uint32())

        self.num_samples = reader.uint32()

        self.computed_sizes = [0] * count_size
        self.recompute_sizes(7)

        if self.version > 11:
            num_frames = reader.uint32()

            self.frames = [reader.float32() for _ in range(num_frames)]

            self.char_bones_samples_data.read(reader, self)
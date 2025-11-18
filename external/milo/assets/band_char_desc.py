from dataclasses import dataclass, field
from enum import Enum

class CharInstrumentType(Enum):
    Guitar = 0
    Bass = 1
    Drum = 2
    Mic = 3
    Keyboard = 4
    NumInstruments = 5

class PatchCategory(Enum):
    kNone = 0
    kTattoo = 1
    kLogo = 2
    kAccessory = 3
    kFacePaint = 4

@dataclass
class OutfitPiece:
    name: str = ""
    colors: list[int] = field(default_factory=list)

    def read(self, reader):
        self.name = reader.numstring()

        for _ in range(3):
            self.colors.append(reader.byte())

@dataclass
class Outfit:
    eyebrows: OutfitPiece = field(default_factory=OutfitPiece)
    face_hair: OutfitPiece = field(default_factory=OutfitPiece)
    hair: OutfitPiece = field(default_factory=OutfitPiece)
    earrings: OutfitPiece = field(default_factory=OutfitPiece)
    glasses: OutfitPiece = field(default_factory=OutfitPiece)
    piercings: OutfitPiece = field(default_factory=OutfitPiece)
    feet: OutfitPiece = field(default_factory=OutfitPiece)
    hands: OutfitPiece = field(default_factory=OutfitPiece)
    legs: OutfitPiece = field(default_factory=OutfitPiece)
    rings: OutfitPiece = field(default_factory=OutfitPiece)
    torso: OutfitPiece = field(default_factory=OutfitPiece)
    wrist: OutfitPiece = field(default_factory=OutfitPiece)

    def read(self, reader):
        self.eyebrows.read(reader)
        self.face_hair.read(reader)
        self.hair.read(reader)
        self.earrings.read(reader)
        self.glasses.read(reader)
        self.piercings.read(reader)
        self.feet.read(reader)
        self.hands.read(reader)
        self.legs.read(reader)
        self.rings.read(reader)
        self.torso.read(reader)
        self.wrist.read(reader)

@dataclass
class Head:
    hide: bool = False
    eye_color: int = 0
    shape: int = 0
    chin: int = 0
    chin_width: float = 0.0
    chin_height: float = 0.0
    jaw_width: float = 0.0
    jaw_height: float = 0.0
    nose: int = 0
    nose_width: float = 0.0
    nose_height: float = 0.0
    eye: int = 0
    eye_separation: float = 0.0
    eye_height: float = 0.0
    eye_rotation: float = 0.0
    mouth: int = 0
    mouth_width: float = 0.0
    mouth_height: float = 0.0
    brow_separation: float = 0.0
    brow_height: float = 0.0

    def read(self, reader):
        self.hide = reader.milo_bool()

        self.eye_color = reader.int32()

        self.shape = reader.int32()

        self.chin = reader.int32()
        self.chin_width = reader.float32()
        self.chin_height = reader.float32()

        self.jaw_width = reader.float32()
        self.jaw_height = reader.float32()

        self.nose = reader.int32()
        self.nose_width = reader.float32()
        self.nose_height = reader.float32()

        self.eye = reader.int32()
        self.eye_separation = reader.float32()
        self.eye_height = reader.float32()
        self.eye_rotation = reader.float32()

        self.mouth = reader.int32()
        self.mouth_width = reader.float32()
        self.mouth_height = reader.float32()

        self.brow_separation = reader.float32()
        self.brow_height = reader.float32()

@dataclass
class InstrumentObject:
    guitar: OutfitPiece = field(default_factory=OutfitPiece)
    bass: OutfitPiece = field(default_factory=OutfitPiece)
    drum: OutfitPiece = field(default_factory=OutfitPiece)
    mic: OutfitPiece = field(default_factory=OutfitPiece)
    keyboard: OutfitPiece = field(default_factory=OutfitPiece)

    def read(self, reader):
        self.guitar.read(reader)
        self.bass.read(reader)
        self.drum.read(reader)
        self.mic.read(reader)
        self.keyboard.read(reader)

@dataclass
class Patch:
    texture: int = 0
    category: PatchCategory = PatchCategory.kNone
    mesh_name: str = ""
    uv: tuple = (0.0, 0.0)
    rotation: float = 0.0
    scale: tuple = (0.0, 0.0)

    def read(self, reader):
        self.texture = reader.int32()

        self.category = PatchCategory(reader.int32())

        self.mesh_name = reader.numstring()

        self.uv = reader.vec2f()

        self.rotation = reader.float32()

        self.scale = reader.vec2f()

@dataclass
class BandCharDesc:
    version: int = 0
    prefab: str = ""
    gender: str = ""
    skin_color: int = 0
    head: Head = field(default_factory=Head)
    instruments: InstrumentObject = field(default_factory=InstrumentObject)
    outfit: Outfit = field(default_factory=Outfit)
    patches: list[Patch] = field(default_factory=Patch)
    height: float = 0.0
    weight: float = 0.0
    muscle: float = 0.0
    unk_224: int = 0
    head_1: int = 0
    head_2: int = 0

    def read(self, reader):
        self.version = reader.int32()

        if self.version > 16:
            self.prefab = reader.numstring()

        self.gender = reader.numstring()

        if self.version != 0:
            self.skin_color = reader.int32()

            if self.version < 5:
                self.head_1 = reader.int32()
                self.head_2 = reader.int32()
            else:
                self.head.read(reader)
        
        self.outfit.read(reader)

        self.height = reader.float32()
        self.weight = reader.float32()
        self.muscle = reader.float32()

        self.instruments.read(reader)

        patch_count = reader.int32()

        for _ in range(patch_count):
            patch = Patch()

            self.patches.append(patch)

        padding = reader.read_bytes(4)

        if padding != b"\xAD\xDE\xAD\xDE":
            raise Exception("Padding was not AD DE AD DE, read most likely failed.")
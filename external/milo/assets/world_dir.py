from dataclasses import dataclass, field
from . panel_dir import PanelDir
from . trans import Trans

@dataclass
class BitmapOverride:
    original: str = ""
    replacement: str = ""

    def read(self, reader):
        self.original = reader.numstring()
        self.replacement = reader.numstring()

@dataclass
class MatOverride:
    mesh: str = ""
    mat: str = ""

    def read(self, reader):
        self.mesh = reader.numstring()
        self.mat = reader.numstring()

@dataclass
class PresetOverride:
    preset: str = ""
    hue: str = ""

    def read(self, reader):
        self.preset = reader.numstring()
        self.hue = reader.numstring()

@dataclass
class WorldDir:
    version: int = 0
    panel_dir: PanelDir = field(default_factory=PanelDir)
    cam: str = ""
    hud_filename: str = ""
    cam_filename: str = ""
    xfm: tuple = ()
    cam_trans: Trans = field(default_factory=Trans)
    hide_overrides: list[str] = field(default_factory=list)
    bitmap_overrides: list[BitmapOverride] = field(default_factory=list)
    mat_overrides: list[MatOverride] = field(default_factory=list)
    preset_overrides: list[PresetOverride] = field(default_factory=list)
    cam_shots_overrides: list[str] = field(default_factory=list)
    ps3_per_pixel_hides: list[str] = field(default_factory=list)
    ps3_per_pixel_shows: list[str] = field(default_factory=list)
    spotlight: str = ""
    m_test_preset_1: str = ""
    m_test_preset_2: str = ""
    m_test_animation_time: float = 0.0
    hud: str = ""

    def read(self, reader, directory_meta, entry, super: bool) -> None:
        self.version = reader.int32()

        if (self.version != 0) and (self.version < 5):
            self.cam = reader.numstring()

        if (self.version >= 2) and (self.version <= 20):
            always_0 = reader.float32()
            always_1 = reader.float32()

        if self.version > 9:
            self.hud_filename = reader.numstring()

        self.panel_dir.read(reader, directory_meta, entry, True)

        if self.version == 5:
            self.cam_reference = reader.numstring()

        if self.version < 25:
            if self.version > 10:
                self.xfm = reader.matrix()
            elif self.version > 6:
                self.cam_trans.read(reader, True, directory_meta)

        if self.version > 11:
            hide_override_count = reader.uint32()

            for _ in range(hide_override_count):
                self.hide_overrides.append(reader.numstring())

            bitmap_override_size = reader.int32()

            for _ in range(bitmap_override_size):
                bitmap_override = BitmapOverride()
                bitmap_override.read(reader)

                self.bitmap_overrides.append(bitmap_override)

        if self.version > 13:
            mat_override_size = reader.int32()

            for _ in range(mat_override_size):
                mat_override = MatOverride()
                mat_override.read(reader)

                self.mat_overrides.append(mat_override)

        if self.version > 14:
            preset_override_size = reader.int32()

            for _ in range(preset_override_size):
                preset_override = PresetOverride()
                preset_override.read(reader)
                
                self.preset_overrides.append(preset_override)

        if self.version > 15:
            cam_shot_override_count = reader.uint32()

            for _ in range(cam_shot_override_count):
                self.cam_shots_overrides.append(reader.numstring())

        if (self.version > 16) and (self.version != 23):
            ps3_per_pixel_hides_count = reader.uint32()

            for _ in range(ps3_per_pixel_hides_count):
                self.ps3_per_pixel_hides.append(reader.numstring())

            ps3_per_pixel_shows_count = reader.uint32()

            for _ in range(ps3_per_pixel_shows_count):
                self.ps3_per_pixel_shows.append(reader.numstring())

        if self.version in [18, 19, 20, 21]:
            self.spotlight = reader.numstring()

        if self.version > 18:
            self.m_test_preset_1 = reader.numstring()
            self.m_test_preset_2 = reader.numstring()
            
            self.m_test_animation_time = reader.float32()

        if self.version > 19:
            self.hud = reader.numstring()

        if self.version >= 65562:
            if self.version == 65565:
                unk_float = reader.float32()
            
            unk_int = reader.int32()

            unk_bool = reader.milo_bool()

        if super == False:
            padding = reader.read_bytes(4)

            if padding != b"\xAD\xDE\xAD\xDE":
                raise Exception("Padding was not AD DE AD DE, read most likely failed.")
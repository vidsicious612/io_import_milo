from dataclasses import dataclass, field
from . rnd_dir import RndDir

@dataclass
class PanelDir:
    version: int = 0
    rnd_dir: RndDir = field(default_factory=RndDir)
    cam: str = ""
    test_event: str = ""
    can_end_world: bool = True
    use_specified_cam: bool = False
    front_view_only_panels: list[str] = field(default_factory=list)
    back_view_only_panels: list[str] = field(default_factory=list)
    postprocs_before_draw: bool = False
    show_view_only_panels: bool = True

    def read(self, reader, directory_meta, entry, super: bool) -> None:
        self.version = reader.int32()

        self.rnd_dir.read(reader, directory_meta, entry, True)

        if entry.is_proxy == False:
            self.cam = reader.numstring()

        if self.version <= 1:
            return
        
        if self.version == 2:
            self.test_event = reader.numstring()
            
            return
        elif self.version <= 7:
            self.can_end_world = reader.milo_bool()
        else:
            self.use_specified_cam = reader.milo_bool()

        front_view_only_panel_count = reader.int32()

        for _ in range(front_view_only_panel_count):
            self.front_view_only_panels.append(reader.numstring())

        back_view_only_panel_count = reader.int32()
        
        for _ in range(back_view_only_panel_count):
            self.back_view_only_panels.append(reader.numstring())

        if self.version >= 8:
            self.postprocs_before_draw = reader.milo_bool()

        self.show_view_only_panels = reader.milo_bool()

        if super == False:
            padding = reader.read_bytes(4)

            if padding != b"\xAD\xDE\xAD\xDE":
                raise Exception("Padding was not AD DE AD DE, read most likely failed.")
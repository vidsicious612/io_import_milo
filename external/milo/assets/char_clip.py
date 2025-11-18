from dataclasses import dataclass, field
from . char_bones_samples import CharBonesSamples
from . metadata import Metadata
from .. common import find_next_file

@dataclass
class ClipNodeFloats:
    frame: float = 0.0
    weight: float = 0.0

    def read(self, reader):
        self.frame = reader.float32()
        self.weight = reader.float32()

    def write(self, writer):
        writer.float32(self.frame)
        writer.float32(self.weight)

@dataclass
class ClipNode:
    name: str = ""
    clip_node_floats: list[ClipNodeFloats] = field(default_factory=list)

    def read(self, reader):
        self.name = reader.numstring()
        
        float_count = reader.uint32()

        for _ in range(float_count):
            clip_node_floats = ClipNodeFloats()
            clip_node_floats.read(reader)

            self.clip_node_floats.append(clip_node_floats)
    
    def write(self, writer):
        writer.numstring(self.name)

        writer.uint32(len(self.clip_node_floats))

        for clip_node_float in self.clip_node_floats:
            clip_node_float.write(writer)

@dataclass
class ClipEvent:
    name: str = ""
    vector: list[tuple] = field(default_factory=list)

    def read(self, reader):
        self.name = reader.numstring()

        vector_count = reader.int32()

        for _ in range(vector_count):
            self.vector.append(reader.vec2f())

    def write(self, writer):
        writer.numstring(self.name)

        writer.int32(len(self.vector))

        for vec in self.vector:
            writer.vec2f(vec)

@dataclass
class FrameEvent:
    frame: float = 0.0
    script: str = ""

    def read(self, reader):
        self.frame = reader.float32()
        self.script = reader.numstring()

    def write(self, writer):
        writer.float32(self.frame)
        writer.numstring(self.script)

@dataclass
class CharClip:
    version: int = 0
    metadata: Metadata = field(default_factory=Metadata)
    start_beat: float = 0.0
    end_beat: float = 0.0
    beats_per_sec: float = 0.0
    transitions: list[str] = field(default_factory=list)
    full: CharBonesSamples = field(default_factory=CharBonesSamples)
    one: CharBonesSamples = field(default_factory=CharBonesSamples)
    flags: int = 0
    play_flags: int = 0
    blend_width: float = 0.0
    char_clip_range: float = 0.0
    relative: str = ""
    do_not_decompress: bool = False
    clip_nodes: list[ClipNode] = field(default_factory=list)
    enter_event: str = ""
    exit_event: str = ""
    frame_events: list[FrameEvent] = field(default_factory=list)

    def read(self, reader, super: bool):
        self.version = reader.int32()

        self.metadata.read(reader)

        self.start_beat = reader.float32()
        self.end_beat = reader.float32()

        self.beats_per_sec = reader.float32()

        if self.version >= 19:
            reader.seek(17)

            transition_count = reader.int32()

            for _ in range(transition_count):
                self.transitions.append(reader.numstring())

            self.full.read(reader, -1)
            self.one.read(reader, -1)

            find_next_file(reader)

            return
        
        self.flags = reader.uint32()
        self.play_flags = reader.uint32()

        self.blend_width = reader.float32()

        if self.version > 3:
            self.char_clip_range = reader.float32()

        if self.version == 5:
            unknown_bool_1 = reader.milo_bool()
        elif self.version > 5:
            self.relative = reader.numstring()

        if ((self.version - 9) < 2) and ((self.version - 9) > 0):
            unknown_bool_2 = reader.milo_bool()
        
        if self.version > 9:
            usually_neg_1 = reader.int32()

        if self.version > 11:
            self.do_not_decompress = reader.milo_bool()

        if self.version < 8:
            node_count = reader.uint32()

            for _ in range(node_count):
                clip_node = ClipNode()
                clip_node.read(reader)

                self.clip_nodes.append(clip_node)
        else:
            nodes_size = reader.uint32()
            node_count = reader.uint32()

            for _ in range(node_count):
                clip_node = ClipNode()
                clip_node.read(reader)

                self.clip_nodes.append(clip_node)

        if self.version < 3:
            some_string_count = reader.int32()
            
            for _ in range(some_string_count):
                reader.numstring()

        if self.version < 7:
            self.enter_event = reader.numstring()
            self.exit_event = reader.numstring()

        frame_event_count = reader.int32()

        for _ in range(frame_event_count):
            frame_event = FrameEvent()
            frame_event.read(reader)

            self.frame_events.append(frame_event)

        if super == False:
            padding = reader.read_bytes(4)

            if padding != b"\xAD\xDE\xAD\xDE":
                raise Exception("Padding was not AD DE AD DE, read most likely failed.")
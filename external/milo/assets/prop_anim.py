from dataclasses import dataclass, field
from enum import Enum
from . anim import Anim
from . dtb import DTB
from . metadata import Metadata

prop_anims = {}

class ExceptionID(Enum):
    kNoException = 0
    kTransQuat = 1
    kTransScale = 2
    kTransPos = 3
    kDirEvent = 4
    kHandleInterp = 5
    kMacro = 6

class Interpolation(Enum):
    kStep = 0
    kLinear = 1
    kSpline = 2
    kSlerp = 3
    kHermite = 4
    kEaseIn = 5
    kEaseOut = 6

class PropType(Enum):
    kPropFloat = 0
    kPropColor = 1
    kPropObject = 2
    kPropBool = 3
    kPropQuat = 4
    kPropVector3 = 5
    kPropSymbol = 6

@dataclass
class AnimEventFloat:
    value: float = 0.0
    pos: float = 0.0

    def read(self, reader):
        self.value = reader.float32()
        self.pos = reader.float32()

@dataclass
class AnimEventColor:
    value: tuple = (0.0, 0.0, 0.0, 0.0)
    pos: float = 0.0

    def read(self, reader):
        self.value = reader.vec4f()
        self.pos = reader.float32()

@dataclass
class AnimEventObject:
    text_1: str = ""
    text_2: str = ""

    pos: float = 0.0

    def read(self, reader):
        self.text_1 = reader.numstring()
        self.text_2 = reader.numstring()

        self.pos = reader.float32()

@dataclass
class AnimEventBool:
    value: bool = False
    pos: float = 0.0

    def read(self, reader):
        self.value = reader.milo_bool()
        self.pos = reader.float32()

@dataclass
class AnimEventQuat:
    value: tuple = (0.0, 0.0, 0.0, 0.0)
    pos: float = 0.0

    def read(self, reader):
        self.value = reader.vec4f()
        self.pos = reader.float32()

@dataclass
class AnimEventVec3:
    value: tuple = (0.0, 0.0, 0.0)
    pos: float = 0.0

    def read(self, reader):
        self.value = reader.vec3f()
        self.pos = reader.float32()

@dataclass
class AnimEventSymbol:
    value: str = ""
    pos: float = 0.0

    def read(self, reader):
        self.value = reader.numstring()
        self.pos = reader.float32()

@dataclass
class PropKey:
    type_1: PropType = PropType.kPropFloat
    type_2: PropType = PropType.kPropFloat
    target: str = ""
    dtb: DTB = field(default_factory=DTB)
    interpolation: Interpolation = Interpolation.kLinear
    interp_handler: str = ""
    exception_type: ExceptionID = ExceptionID.kNoException
    keys: list = field(default_factory=list)

    def read(self, reader, version: int):
        self.type_1 = PropType(reader.int32())
        self.type_2 = PropType(reader.int32())

        self.target = reader.numstring()

        self.dtb.read(reader)

        self.interpolation = Interpolation(reader.int32())
        self.interp_handler = reader.numstring()

        self.exception_type = ExceptionID(reader.int32())

        if version >= 13:
            unk_bool = reader.milo_bool()

        event_count = reader.int32()

        for _ in range(event_count):
            if self.type_1 == PropType.kPropFloat:
                anim_event_float = AnimEventFloat()
                anim_event_float.read(reader)

                self.keys.append(anim_event_float)
            elif self.type_1 == PropType.kPropColor:
                anim_event_color = AnimEventColor()
                anim_event_color.read(reader)

                self.keys.append(anim_event_color)
            elif self.type_1 == PropType.kPropObject:
                anim_event_object = AnimEventObject()
                anim_event_object.read(reader)

                self.keys.append(anim_event_object)
            elif self.type_1 == PropType.kPropBool:
                anim_event_bool = AnimEventBool()
                anim_event_bool.read(reader)

                self.keys.append(anim_event_bool)
            elif self.type_1 == PropType.kPropQuat:
                anim_event_quat = AnimEventQuat()
                anim_event_quat.read(reader)

                self.keys.append(anim_event_quat)
            elif self.type_1 == PropType.kPropVector3:
                anim_event_vec3 = AnimEventVec3()
                anim_event_vec3.read(reader)

                self.keys.append(anim_event_vec3)
            elif self.type_1 == PropType.kPropSymbol:
                anim_event_symbol = AnimEventSymbol()
                anim_event_symbol.read(reader)

                self.keys.append(anim_event_symbol)

@dataclass
class PropAnim:
    version: int = 0
    metadata: Metadata = field(default_factory=Metadata)
    anim: Anim = field(default_factory=Anim)
    prop_keys: list[PropKey] = field(default_factory=list)
    flow_labels: list[str] = field(default_factory=list)

    def read(self, reader, name: str):
        self.version = reader.int32()

        self.metadata.read(reader)

        self.anim.read(reader)

        prop_keys_count = reader.int32()

        for _ in range(prop_keys_count):
            prop_key = PropKey()
            prop_key.read(reader, self.version)

            self.prop_keys.append(prop_key)

        if self.version > 11:
            m_loop = reader.milo_bool()

        if self.version > 13:
            num_flow_labels = reader.int32()

            for _ in range(num_flow_labels):
                self.flow_labels.append(reader.numstring())

        if self.version > 14:
            m_intensity = reader.float32()

        prop_anims[name] = self

        padding = reader.read_bytes(4)

        if padding != b"\xAD\xDE\xAD\xDE":
            raise Exception("Padding was not AD DE AD DE, read most likely failed.")
        
    def import_to_blender(self):
        import bpy

        def change_prop_anim_material(key, obj):
            def change_material(scene):
                frame = scene.frame_current

                if frame == key.pos:
                    mat = bpy.data.materials.get(key.text_2)

                    if mat:
                        obj.material_slots[0].material = mat
                        obj.active_material = mat

            return change_material

        for prop_key in self.prop_keys:
            obj = bpy.data.objects.get(prop_key.target)

            if obj:
                if prop_key.type_1 == PropType.kPropObject:
                    for key in prop_key.keys:
                        material_function = change_prop_anim_material(key, obj)

                        bpy.app.handlers.frame_change_pre.append(material_function)
                elif prop_key.type_1 == PropType.kPropQuat:
                    for key in prop_key.keys:
                        obj.rotation_mode = "QUATERNION"
                        obj.rotation_quaternion = (key.value[3], key.value[0], key.value[1], key.value[2])
                        obj.keyframe_insert("rotation_quaternion", frame=key.pos)
                elif prop_key.type_1 == PropType.kPropVector3:
                    for key in prop_key.keys:
                        obj.location = key.value
                        obj.keyframe_insert("location", frame=key.pos)
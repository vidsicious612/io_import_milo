from dataclasses import dataclass, field
from .... readers import Reader

def convert_quat_sample(sample: tuple[int, int, int, int]) -> tuple[float, float, float, float]:
    x = max(float(sample[0] / 32767.0), -1)
    y = max(float(sample[1] / 32767.0), -1)
    z = max(float(sample[2] / 32767.0), -1)
    w = max(float(sample[3] / 32767.0), -1)

    return (x, y, z, w)

@dataclass
class SampleSetHeader:
    trans_names: list[str] = field(default_factory=list)
    count_per_sample: int = 0

    def read(self, reader: Reader):
        count = reader.int32()

        self.trans_names = [reader.numstring() for _ in range(count)]

        self.count_per_sample = reader.int32()

        always_1 = reader.int32()

@dataclass
class TransEntry:
    entry: tuple = ()

    def read(self, reader, trans_name: str):
        if ".pos" in trans_name:
            self.entry = reader.vec3f()
        elif ".quat" in trans_name:
            self.entry = convert_quat_sample(reader.vec4s())
        elif ".rotz" in trans_name:
            self.entry = reader.read_bytes(2)

@dataclass
class TransEntriesFrame:
    trans_entries: list[TransEntry] = field(default_factory=list)

    def read(self, reader, header: SampleSetHeader):
        for i in range(len(header.trans_names)):
            trans_entry = TransEntry()
            trans_entry.read(reader, header.trans_names[i])

            self.trans_entries.append(trans_entry)

@dataclass
class SampleSetData:
    trans_frames: list[TransEntriesFrame] = field(default_factory=list)

    def read(self, reader, header: SampleSetHeader):
        for _ in range(header.count_per_sample):
            trans_frame = TransEntriesFrame()
            trans_frame.read(reader, header)

            self.trans_frames.append(trans_frame)

@dataclass
class AnimClip:
    version: int = 0
    sample_header_1: SampleSetHeader = field(default_factory=SampleSetHeader)
    sample_header_2: SampleSetHeader = field(default_factory=SampleSetHeader)
    sample_data_1: SampleSetData = field(default_factory=SampleSetData)
    sample_data_2: SampleSetData = field(default_factory=SampleSetData)

    def read(self, reader):
        self.version = reader.int32()

        self.sample_header_1.read(reader)
        self.sample_header_2.read(reader)

        if len(self.sample_header_1.trans_names) > 0:
            self.sample_data_1.read(reader, self.sample_header_1)

        if len(self.sample_header_2.trans_names) > 0:
            self.sample_data_2.read(reader, self.sample_header_2)

@dataclass
class AnimClipSamples:
    anim_type: str = ""
    anim_name: str = ""
    version: int = 0
    anim_clip: AnimClip = field(default_factory=AnimClip)

    def read(self, filepath: str):
        reader = Reader(open(filepath, "rb").read())

        self.anim_type = reader.numstring()
        self.anim_name = reader.numstring()

        self.version = reader.int32()

        vec4 = reader.vec4f()

        unknown = reader.int32()

        max_1 = reader.float32()

        self.anim_clip.read(reader)
    
    def import_to_blender(self):
        import bpy
        import mathutils
        from .... import_export_helpers.bones_importer import bone_local_matrices

        def add_constraints(source_armature, target_armature):
            bone_names = set()

            for bone_name in self.anim_clip.sample_header_1.trans_names:
                new_bone_name = bone_name.replace(".pos", ".mesh")

                if bone_name not in bone_names:
                    bone_names.add(new_bone_name)

            for bone_name in self.anim_clip.sample_header_1.trans_names:
                new_bone_name = bone_name.replace(".quat", ".mesh")

                if new_bone_name not in bone_names:
                    bone_names.add(new_bone_name)   

            for bone_name in bone_names:
                if bone_name in source_armature.pose.bones:
                    pb = target_armature.pose.bones[bone_name]
                    
                    for c in pb.constraints:
                        if c.name == "RetargetConstraint":
                            pb.constraints.remove(c)
                    
                    constraint = pb.constraints.new('COPY_TRANSFORMS')
                    constraint.name = "RetargetConstraint"
                    constraint.target = source_armature
                    constraint.subtarget = bone_name
                    constraint.owner_space = 'WORLD'
                    constraint.target_space = 'WORLD'

        def duplicate_armature(armature):
            if "Armature 2" in bpy.data.objects:
                return bpy.data.objects["Armature 2"]

            armature_dup = armature.copy()
            armature_dup.name = "Armature 2"
            armature_dup.data = armature.data.copy()
            armature_dup.data.name = "Armature 2"
            bpy.context.collection.objects.link(armature_dup)

            bpy.context.view_layer.objects.active = armature_dup
            bpy.ops.object.mode_set(mode="EDIT")

            for bone in armature_dup.data.edit_bones:
                bone.matrix = mathutils.Matrix.Identity(4)

            bpy.ops.object.mode_set(mode="POSE")

            for bone in armature_dup.pose.bones:
                if bone.name in bone_local_matrices:
                    bone.matrix_basis = bone_local_matrices[bone.name]

            bpy.ops.object.mode_set(mode="OBJECT")

            return armature_dup

        armature = bpy.context.active_object

        armature_dup = duplicate_armature(armature)

        for x, frame in enumerate(self.anim_clip.sample_data_1.trans_frames):
            for i, entry in enumerate(frame.trans_entries):
                bone_name = self.anim_clip.sample_header_1.trans_names[i]

                if bone_name.endswith(".pos"):
                    bone = armature_dup.pose.bones.get(bone_name.replace(".pos", ".mesh"))

                    if bone:
                        bone.location = entry.entry
                        bone.keyframe_insert("location", frame=x)
                elif bone_name.endswith(".quat"):
                    bone = armature_dup.pose.bones.get(bone_name.replace(".quat", ".mesh"))

                    if bone:
                        bone.rotation_quaternion = (entry.entry[3], entry.entry[0], entry.entry[1], entry.entry[2])
                        bone.keyframe_insert("rotation_quaternion", frame=x)

        add_constraints(armature_dup, armature)

        armature_dup.hide_viewport = True
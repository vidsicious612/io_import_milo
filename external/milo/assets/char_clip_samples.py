from dataclasses import dataclass, field
from . char_bones_samples import CharBonesSamples, CharBonesSamplesData, CharBones, PosSample, QuatSample
from . char_clip import CharClip

char_clip_samples = {}

@dataclass
class CharClipSamples:
    version: int = 0
    char_clip: CharClip = field(default_factory=CharClip)
    full: CharBonesSamples = field(default_factory=CharBonesSamples)
    one: CharBonesSamples = field(default_factory=CharBonesSamples)
    ignore: CharBonesSamples = field(default_factory=CharBonesSamples)
    full_data: CharBonesSamplesData = field(default_factory=CharBonesSamplesData)
    one_data: CharBonesSamplesData = field(default_factory=CharBonesSamplesData)
    char_bones: CharBones = field(default_factory=CharBones)

    def read(self, reader, name: str):
        from .. common import find_next_file

        self.version = reader.int32()

        self.char_clip.read(reader, True)

        if self.version >= 16:
            some_bool = reader.milo_bool()
        
        if self.version < 13:
            self.full.read(reader, self.version)
            self.one.read(reader, self.version)

            if self.version > 7:
                self.ignore.read(reader, self.version)
            
            self.full_data.read(reader, self.full)
            self.one_data.read(reader, self.one)

            self.full.char_bones_samples_data.samples = self.full_data.samples
            self.one.char_bones_samples_data.samples = self.one_data.samples
        else:
            self.full.read(reader, -1)
            self.one.read(reader, -1)

        if self.version > 14:
            self.char_bones.read(reader, self.version)

        char_clip_samples[name] = self

        padding = reader.read_bytes(4)

        if padding != b"\xAD\xDE\xAD\xDE":
            raise Exception("Padding was not AD DE AD DE, read most likely failed.")
        
    def import_to_blender(self):
        import bpy
        import mathutils
        from .... import_export_helpers.bones_importer import bone_local_matrices

        def add_constraints(source_armature, target_armature):
            bone_names = set()

            for sample in self.full.char_bones_samples_data.samples:
                new_bone_name = sample.bone_name.replace(".pos", ".mesh")

                if new_bone_name not in bone_names:
                    bone_names.add(new_bone_name)

            for sample in self.full.char_bones_samples_data.samples:
                new_bone_name = sample.bone_name.replace(".quat", ".mesh")

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
            armature_dup = bpy.data.objects.get("Armature 2")

            index = 0

            if armature_dup:
                armature_dup.name = armature_dup.name + f"_{index}"
                index += 1

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

        for i, sample in enumerate(self.full.char_bones_samples_data.samples):
            if isinstance(sample, PosSample):
                bone = sample.bone_name.replace(".pos", ".mesh")
                bone = armature_dup.pose.bones.get(bone)

                if bone:
                    bone.location = sample.sample
                    bone.keyframe_insert("location", frame=i)
            elif isinstance(sample, QuatSample):
                bone = sample.bone_name.replace(".quat", ".mesh")
                bone = armature_dup.pose.bones.get(bone)

                if bone:
                    bone.rotation_quaternion = (sample.sample[3], sample.sample[0], sample.sample[1], sample.sample[2])
                    bone.keyframe_insert("rotation_quaternion", frame=i)

        add_constraints(armature_dup, armature)

        armature_dup.hide_viewport = True
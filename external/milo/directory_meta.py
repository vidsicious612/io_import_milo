from dataclasses import dataclass, field
from . assets.band_character import BandCharacter
from . assets.character import Character
from . assets.char_clip_samples import CharClipSamples
from . assets.char_clip_set import CharClipSet
from . assets.flow import Flow
from . assets.mat import Mat
from . assets.mesh_anim import MeshAnim
from . assets.mesh import Mesh
from . assets.p9_waypoint_configuration import P9WaypointConfiguration
from . assets.panel_dir import PanelDir
from . assets.prop_anim import PropAnim
from . assets.rnd_dir import RndDir
from . assets.synth_dir import SynthDir
from . assets.synth_sample import SynthSample
from . assets.tex import Tex
from . assets.trans_anim import TransAnim
from . assets.trans import Trans
from . assets.world_crowd import WorldCrowd
from . assets.world_dir import WorldDir
from . assets.world_instance import WorldInstance, PersistentObjects
from . common import find_next_file

@dataclass
class Object:
    type: str
    name: str
    obj = None
    dir = None
    is_proxy: bool = False

@dataclass
class DirectoryMeta:
    platform = None
    version: int = 0
    string_table_count: int = 0
    string_table_size: int = 0
    dir_type: str = ""
    dir_name: str = ""
    directory = None
    external_resources: list[str] = field(default_factory=list)
    entries: list[Object] = field(default_factory=list)
    inline_entries: list[Object] = field(default_factory=list)

    def read_directory(self, reader):
        from . assets.object_dir import ObjectDir

        print(f"Reading directory: {self.dir_type, self.dir_name} at offset: {reader.tell()}")

        if self.dir_type == "BandCharacter":
            band_character = BandCharacter()
            band_character.read(reader, self, Object(self.dir_type, self.dir_name), False)

            self.directory = band_character
        elif self.dir_type == "Character":
            character = Character()
            character.read(reader, self, Object(self.dir_type, self.dir_name), False)

            self.directory = character
        elif self.dir_type == "CharClipSet":
            char_clip_set = CharClipSet()
            char_clip_set.read(reader, self, Object(self.dir_type, self.dir_name), False)

            self.directory = char_clip_set
        elif self.dir_type == "ObjectDir":
            object_dir = ObjectDir()
            object_dir.read(reader, self, Object(self.dir_type, self.dir_name), False)

            self.directory = object_dir
        elif (self.dir_type == "UIPanel") or (self.dir_type == "PanelDir"):
            panel_dir = PanelDir()
            panel_dir.read(reader, self, Object(self.dir_type, self.dir_name), False)

            self.directory = panel_dir
        elif (self.dir_type == "EndingBonusDir") or (self.dir_type == "RndDir"):
            rnd_dir = RndDir()
            rnd_dir.read(reader, self, Object(self.dir_type, self.dir_name), False)

            self.directory = rnd_dir
        elif self.dir_type == "SynthDir":
            synth_dir = SynthDir()
            synth_dir.read(reader, self, Object(self.dir_type, self.dir_name), False)

            self.directory = synth_dir
        elif self.dir_type == "WorldDir":
            world_dir = WorldDir()
            world_dir.read(reader, self, Object(self.dir_type, self.dir_name), False)

            self.directory = world_dir
        elif self.dir_type == "WorldInstance":
            world_instance = WorldInstance()
            world_instance.read(reader, self, Object(self.dir_type, self.dir_name), False)

            self.directory = world_instance
        else:
            find_next_file(reader)
                
            padding = reader.read_bytes(4)

            if padding != b"\xAD\xDE\xAD\xDE":
                raise Exception("Padding was not AD DE AD DE, read most likely failed.")

    def write_directory(self, writer):
        if self.dir_type == "Character":
            self.directory.write(writer, False)
    
    def read_entry(self, reader, entry: Object):
        from . assets.object_dir import ObjectDir

        print(f"Reading entry: {entry.type, entry.name} at offset: {reader.tell()}")

        if entry.type == "BandCharacter":
            entry.is_proxy = True

            entry.obj = BandCharacter()
            entry.obj.read(reader, self, entry, False)

            dir = DirectoryMeta()
            dir.platform = self.platform
            dir.read(reader)

            entry.dir = dir
            
            for e in dir.entries:
                self.inline_entries.append(e)
        elif entry.type == "Character":
            entry.is_proxy = True

            entry.obj = Character()
            entry.obj.read(reader, self, entry, False)

            if len(entry.obj.rnd_dir.object_dir.proxy_file) > 0:
                dir = DirectoryMeta()
                dir.platform = self.platform
                dir.read(reader)

                entry.dir = dir
                
                for e in dir.entries:
                    self.inline_entries.append(e)
        elif entry.type == "CharClipSet":
            entry.is_proxy = True

            version = reader.int32()

            entry.obj = ObjectDir()
            entry.obj.read(reader, self, entry, False)

            dir = DirectoryMeta()
            dir.platform = self.platform
            dir.read(reader)

            entry.dir = dir
            
            for e in dir.entries:
                self.inline_entries.append(e)
        elif entry.type == "ObjectDir":
            entry.is_proxy = True

            entry.obj = ObjectDir()
            entry.obj.read(reader, self, entry, False)

            if (entry.obj.inline_proxy == True) and (len(entry.obj.proxy_file) > 0):
                dir = DirectoryMeta()
                dir.platform = self.platform
                dir.read(reader)

                entry.dir = dir
                
                for e in dir.entries:
                    self.inline_entries.append(e)
        elif (entry.type == "UIPanel") or (entry.type == "PanelDir"):
            entry.is_proxy = True

            entry.obj = PanelDir()
            entry.obj.read(reader, self, entry, False)

            dir = DirectoryMeta()
            dir.platform = self.platform
            dir.read(reader)

            entry.dir = dir
            
            for e in dir.entries:
                self.inline_entries.append(e)
        elif (entry.type == "EndingBonusDir") or (entry.type == "RndDir"):
            entry.is_proxy = True

            entry.obj = RndDir()
            entry.obj.read(reader, self, entry, False)

            if (entry.obj.object_dir.version > 17 and entry.obj.object_dir.inline_proxy == True) and (len(entry.obj.object_dir.proxy_file) > 0):
                dir = DirectoryMeta()
                dir.platform = self.platform
                dir.read(reader)

                entry.dir = dir
                
                for e in dir.entries:
                    self.inline_entries.append(e)
        elif entry.type == "SynthDir":
            entry.is_proxy = True

            entry.obj = SynthDir()
            entry.obj.read(reader, self, entry, False)

            dir = DirectoryMeta()
            dir.platform = self.platform
            dir.read(reader)

            entry.dir = dir
            
            for e in dir.entries:
                self.inline_entries.append(e)
        elif entry.type == "WorldDir":
            entry.is_proxy = True

            entry.obj = WorldDir()
            entry.obj.read(reader, self, entry, False)

            dir = DirectoryMeta()
            dir.platform = self.platform
            dir.read(reader)

            entry.dir = dir
            
            for e in dir.entries:
                self.inline_entries.append(e)
        elif entry.type == "WorldInstance":
            entry.is_proxy = True

            entry.obj = WorldInstance()
            entry.obj.read(reader, self, entry, True)

            if entry.obj.version > 0:
                if entry.obj.has_persistent_objects == False:
                    dir = DirectoryMeta()
                    dir.platform = self.platform
                    dir.read(reader)

                    entry.dir = dir

                    if (entry.dir != None) and (entry.dir.dir_type == "WorldInstance"):
                        if dir.directory.has_persistent_objects == True:
                            persistent_objects = PersistentObjects()
                            persistent_objects.read(reader, self, entry, entry.obj.version)

                            dir.directory.persistent_objects = persistent_objects
                    else:
                        persistent_objects = PersistentObjects()
                        persistent_objects.read(reader, self, entry, entry.obj.version)

                        entry.obj.persistent_objects = persistent_objects
                    
                    for e in dir.entries:
                        self.inline_entries.append(e)
                else:
                    persistent_objects = PersistentObjects()
                    persistent_objects.read(reader, self, entry, entry.obj.version)

                    entry.obj.persistent_objects = persistent_objects
        elif entry.type == "CharClipSamples":
            entry.obj = CharClipSamples()
            entry.obj.read(reader, entry.name)

            entry.dir = self
        elif entry.type == "Mat":
            entry.obj = Mat()
            entry.obj.read(reader)

            entry.dir = self
        elif entry.type == "Mesh":
            entry.obj = Mesh()
            entry.obj.read(reader, self)

            entry.dir = self
        elif entry.type == "MeshAnim":
            entry.obj = MeshAnim()
            entry.obj.read(reader, entry.name)

            entry.dir = self
        elif entry.type == "PropAnim":
            entry.obj = PropAnim()
            entry.obj.read(reader, entry.name)

            entry.dir = self
        elif entry.type == "P9WaypointConfiguration":
            entry.obj = P9WaypointConfiguration()
            entry.obj.read(reader, self)

            entry.dir = self
        elif entry.type == "SynthSample":
            entry.obj = SynthSample()
            entry.obj.read(reader)

            entry.dir = self
        elif entry.type == "Tex":
            entry.obj = Tex()
            entry.obj.read(reader)

            entry.dir = self
        elif entry.type == "Trans":
            entry.obj = Trans()
            entry.obj.read(reader, False, self)

            entry.dir = self
        elif entry.type == "TransAnim":
            entry.obj = TransAnim()
            entry.obj.read(reader, entry.name)

            entry.dir = self
        elif entry.type == "WorldCrowd":
            entry.obj = WorldCrowd()
            entry.obj.read(reader, self)

            entry.dir = self
        else:
            find_next_file(reader)
                
            padding = reader.read_bytes(4)

            if padding != b"\xAD\xDE\xAD\xDE":
                raise Exception("Padding was not AD DE AD DE, read most likely failed.")
            
    def write_entry(self, writer, entry: Object):
        if entry.type == "Mat":
            entry.obj = Mat()
            entry.obj.write(writer)
        elif entry.type == "Mesh":
            entry.obj = Mesh()
            entry.obj.write(writer)
        elif entry.type == "Tex":
            entry.obj = Tex()
            entry.obj.write(writer)
        elif entry.type == "Trans":
            entry.obj = Trans()
            entry.obj.write(writer, False)

    def read(self, reader):
        reader.get_endian()

        self.version = reader.int32()

        if self.version > 10:
            self.dir_type = reader.numstring()
            self.dir_name = reader.numstring()

            self.string_table_count = reader.uint32()
            self.string_table_size = reader.uint32()

            if self.version >= 32:
                unknown = reader.milo_bool()

        entry_count = reader.int32()

        for _ in range(entry_count):
            if self.version == 6:
                entry = Object(reader.string(), reader.string())
            else:
                entry = Object(reader.numstring(), reader.numstring())

            if self.version == 6:
                unknown = reader.milo_bool()

            self.entries.append(entry)

        if self.version == 10:
            external_resource_count = reader.int32()

            for _ in range(external_resource_count):
                self.external_resources.append(reader.numstring())

        if self.version > 10:
            self.read_directory(reader)

        for entry in self.entries:
            self.read_entry(reader, entry)

        for inline_entry in self.inline_entries:
            self.entries.append(inline_entry)

    def write(self, writer):
        writer.int32(self.version)

        if self.version > 10:
            writer.numstring(self.dir_type)
            writer.numstring(self.dir_name)

            writer.uint32(self.string_table_count)
            writer.uint32(self.string_table_size)

        writer.int32(len(self.entries))

        for entry in self.entries:
            writer.numstring(entry.type)
            writer.numstring(entry.name)
        
        if self.version == 10:
            writer.int32(len(self.external_resources))

            for ext_resource in self.external_resources:
                writer.numstring(ext_resource)
        else:
            self.write_directory(writer)

        for entry in self.entries:
            self.write_entry(writer, entry)

    def import_files(self, bpy_self, filepath: str):
        from pathlib import Path
        from ... import_export_helpers.bones_importer import import_bones, import_mesh_bones
        from ... import_export_helpers.mesh_parenting import parent_meshes
        from ... import_export_helpers.world_crowd_importer import import_world_crowd

        # Convert textures + audio
        for entry in self.entries:
            if entry.type == "Tex":
                if (entry.obj.bitmap.width != 0) and (entry.obj.bitmap.height != 0):
                    entry.obj.bitmap.convert(self.platform)

                    texture_filepath = Path.joinpath(Path(filepath).parent, Path(entry.name).with_suffix(".png"))

                    entry.obj.bitmap.export_to_image(texture_filepath)
            elif entry.type == "SynthSample":
                sample_filepath = Path.joinpath(Path(filepath).parent, Path(entry.name))

                entry.obj.sample_data.convert(sample_filepath)

        # Import characters
        for entry in self.entries:
            if entry.type == "Character":
                entry.obj.import_to_blender(entry.name)

        # Import bones
        bones = {}
        mesh_bones = {}

        for entry in self.entries:
            if entry.type == "Trans":
                bones.setdefault(entry.dir.dir_name, []).append(entry)
            elif (entry.type == "Mesh") and ("bone" in entry.name):
                mesh_bones.setdefault(entry.dir.dir_name, []).append(entry)

        for char_name, bone_set in bones.items():
            import_bones(bone_set, char_name)
        for char_name, bone_set in mesh_bones.items():
            import_mesh_bones(bone_set, char_name)

        # Convert + import textures
        for entry in self.entries:
            if entry.type == "Tex":
                if (entry.obj.bitmap.width != 0) and (entry.obj.bitmap.height != 0):
                    entry.obj.import_to_blender(entry.name, filepath)

        # Import materials
        for entry in self.entries:
            if entry.type == "Mat":
                entry.obj.import_to_blender(entry.name, entry.dir)

        # Import meshes
        for entry in self.entries:
            if (entry.type == "Mesh") and not ("bone" in entry.name):
                entry.obj.import_to_blender(entry.name, bpy_self, entry.dir)

        # Import WorldInstance files
        for entry in self.entries:
            if entry.type == "WorldInstance":
                entry.obj.import_to_blender(entry, filepath, bpy_self)

        # Import P9WaypointConfiguration files
        for entry in self.entries:
            if entry.type == "P9WaypointConfiguration":
                entry.obj.import_to_blender()

        # Import WorldCrowd files
        world_crowds = []

        for entry in self.entries:
            if entry.type == "WorldCrowd":
                world_crowds.append(entry)
        
        if (len(world_crowds) > 0) and (bpy_self.import_wc == True):
            import_world_crowd(world_crowds)
        
        # Set geom_owner
        meshes = []

        for entry in self.entries:
            if entry.type == "Mesh":
                meshes.append(entry)

        parent_meshes(meshes)

    def from_blender(self, bpy_self):
        import bpy
        from . assets.character import Character

        def get_mesh_user(mesh):
            for obj in bpy.data.objects:
                if (obj.type == "MESH") and (obj.data == mesh):
                    return obj

        def get_objects() -> tuple[set, set, set, set]:
            num_materials = 0
            num_meshes = 0
            num_bones = 0

            materials = set()
            meshes = set()
            bones = set()
            
            for mesh in bpy.data.meshes:
                if (mesh.users > 0) and not (mesh.name in meshes):
                    obj = get_mesh_user(mesh)

                    meshes.add(obj)

                    if len(obj.material_slots) > 0:
                        if (obj.material_slots[0].material) and not (obj.material_slots[0].material.name in materials):
                            materials.add(obj.material_slots[0].material)

                            num_materials += 1

                    num_meshes += 1

            for obj in bpy.data.objects:
                if obj.type == "ARMATURE":
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.mode_set(mode="EDIT")

                    for bone in obj.data.edit_bones:
                        if not (bone.name) in bones:
                            bones.append(bone)

                            num_bones += 1

                    bpy.ops.object.mode_set(mode="OBJECT")

            return bones, meshes, materials

        bones, meshes, materials = get_objects()

        self.version = 10 if bpy_self.game_selection == "GH1" else 25

        if self.version == 25:
            if bpy_self.milo_type == "Character":
                self.dir_type = "Character"

                self.directory = Character()
                self.directory.from_blender(bpy_self)
            else:
                self.dir_type = "RndDir"

                self.directory = RndDir()
                self.directory.from_blender(bpy_self)

            self.dir_name = bpy_self.dir_name             
        
        for mat in materials:
            entry = Object(type="Mat", name=mat.name)

            mat_obj = Mat()
            mat_obj.from_blender(mat, bpy_self)

            entry.obj = mat

            self.entries.append(entry)

        for mesh in meshes:
            entry = Object(type="Mesh", name=mesh.name)

            mesh_obj = Mesh()
            mesh_obj.from_blender(mesh, bpy_self)

            entry.obj = mesh

            self.entries.append(entry)

        for bone in bones:
            entry = Object(type="Trans", name=bone.name)

            trans = Trans()
            trans.from_blender(mesh, bpy_self)

            entry.obj = trans

            self.entries.append(entry)
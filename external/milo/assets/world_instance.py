from dataclasses import dataclass, field
from . anim import Anim
from . draw import Draw
from . mesh import Mesh
from . rnd_dir import RndDir
from . trans import Trans

@dataclass
class PersistentObjects:
    anim: Anim = field(default_factory=Anim)
    draw: Draw = field(default_factory=Draw)
    trans: Trans = field(default_factory=Trans)
    environ: str = ""
    test_event: str = ""
    string_table_count: int = 0
    string_table_size: int = 0
    per_objs: list = field(default_factory=list)

    def read(self, reader, directory_meta, entry, version: int):
        from .. directory_meta import Object

        if entry.is_proxy == True:
            empty = reader.read_bytes(13)

            self.anim.read(reader)
            self.draw.read(reader, directory_meta)
            self.trans.read(reader, True, directory_meta)

            self.environ = reader.numstring()
            self.test_event = reader.numstring()

            if version > 1:
                if version > 2:
                    self.string_table_count = reader.uint32()
                    self.string_table_size = reader.uint32()

                object_count = reader.int32()

                for _ in range(object_count):
                    self.per_objs.append(Object(reader.numstring(), reader.numstring))

                for i in range(object_count):
                    if self.per_objs[i].type == "Mesh":
                        mesh = Mesh()
                        mesh.read(reader, directory_meta)

                        self.per_objs[i].obj = mesh

        padding = reader.read_bytes(4)

        if padding != b"\xAD\xDE\xAD\xDE":
            raise Exception("Padding was not AD DE AD DE, read most likely failed.")

class WorldInstance:
    def __init__(self):
        self.version: int = 0
        self.rnd_dir = RndDir()
        self.file_path: str = ""
        self.has_persistent_objects: bool = False
        self.persistent_objects = PersistentObjects()
                      
    def read(self, reader, directory_meta, entry, super: bool):
        self.version = reader.int32()
            
        self.file_path = reader.numstring()

        self.rnd_dir.read(reader, directory_meta, entry, True)

        if self.rnd_dir.object_dir.version > 20:
            self.has_persistent_objects = entry.has_persistent_objects
        else:
            self.has_persistent_objects = True

        if ((super == False) and (entry.is_proxy == False)) or (self.version == 0):
            padding = reader.read_bytes(4)

            if padding != b"\xAD\xDE\xAD\xDE":
                raise Exception("Padding was not AD DE AD DE, read most likely failed.")
    
    def import_to_blender(self, entry, filepath: str, bpy_self):
        import bpy
        import mathutils
        from .. milo_file import MiloFile

        instances_collection = bpy.data.collections.get("Instances")

        if not instances_collection:
            instances_collection = bpy.data.collections.new("Instances")

            bpy.context.scene.collection.children.link(instances_collection)

        instance_obj = bpy.data.objects.new(entry.name, None)

        bpy.context.collection.objects.link(instance_obj)
        instances_collection.objects.link(instance_obj)
        bpy.context.collection.objects.unlink(instance_obj)

        instance_obj.empty_display_size = 2
        instance_obj.empty_display_type = "PLAIN_AXES"

        if self.version == 0:
            matrix_4x3 = mathutils.Matrix((
                (self.rnd_dir.trans.world_xfm[0], self.rnd_dir.trans.world_xfm[3], self.rnd_dir.trans.world_xfm[6], self.rnd_dir.trans.world_xfm[9]),
                (self.rnd_dir.trans.world_xfm[1], self.rnd_dir.trans.world_xfm[4], self.rnd_dir.trans.world_xfm[7], self.rnd_dir.trans.world_xfm[10]),
                (self.rnd_dir.trans.world_xfm[2], self.rnd_dir.trans.world_xfm[5], self.rnd_dir.trans.world_xfm[8], self.rnd_dir.trans.world_xfm[11]),
            ))
        else:
            if entry.dir:
                if hasattr(entry.dir, "directory"):
                    matrix_4x3 = mathutils.Matrix((
                        (entry.dir.directory.persistent_objects.trans.world_xfm[0], entry.dir.directory.persistent_objects.trans.world_xfm[3], entry.dir.directory.persistent_objects.trans.world_xfm[6], entry.dir.directory.persistent_objects.trans.world_xfm[9]),
                        (entry.dir.directory.persistent_objects.trans.world_xfm[1], entry.dir.directory.persistent_objects.trans.world_xfm[4], entry.dir.directory.persistent_objects.trans.world_xfm[7], entry.dir.directory.persistent_objects.trans.world_xfm[10]),
                        (entry.dir.directory.persistent_objects.trans.world_xfm[2], entry.dir.directory.persistent_objects.trans.world_xfm[5], entry.dir.directory.persistent_objects.trans.world_xfm[8], entry.dir.directory.persistent_objects.trans.world_xfm[11]),
                    ))
                else:
                    matrix_4x3 = mathutils.Matrix((
                        (self.persistent_objects.trans.world_xfm[0], self.persistent_objects.trans.world_xfm[3], self.persistent_objects.trans.world_xfm[6], self.persistent_objects.trans.world_xfm[9]),
                        (self.persistent_objects.trans.world_xfm[1], self.persistent_objects.trans.world_xfm[4], self.persistent_objects.trans.world_xfm[7], self.persistent_objects.trans.world_xfm[10]),
                        (self.persistent_objects.trans.world_xfm[2], self.persistent_objects.trans.world_xfm[5], self.persistent_objects.trans.world_xfm[8], self.persistent_objects.trans.world_xfm[11]),
                    ))            
                        
                instance_obj.matrix_world = matrix_4x3.to_4x4()

                for obj in bpy.data.objects:
                    for e in entry.dir.entries:
                        if (e.name in obj.name) and not (obj.parent):
                            obj.parent = instance_obj
            else:
                matrix_4x3 = mathutils.Matrix((
                    (self.persistent_objects.trans.world_xfm[0], self.persistent_objects.trans.world_xfm[3], self.persistent_objects.trans.world_xfm[6], self.persistent_objects.trans.world_xfm[9]),
                    (self.persistent_objects.trans.world_xfm[1], self.persistent_objects.trans.world_xfm[4], self.persistent_objects.trans.world_xfm[7], self.persistent_objects.trans.world_xfm[10]),
                    (self.persistent_objects.trans.world_xfm[2], self.persistent_objects.trans.world_xfm[5], self.persistent_objects.trans.world_xfm[8], self.persistent_objects.trans.world_xfm[11]),
                ))
                    
                instance_obj.matrix_world = matrix_4x3.to_4x4()

                instance_file_path = self.rnd_dir.object_dir.get_dir_path(self.file_path, filepath)
                instance_milo = MiloFile(path=instance_file_path)
                instance_milo.read()
                instance_milo.dir_meta.import_files(bpy_self, instance_file_path)
                
                for obj in bpy.data.objects:
                    for e in instance_milo.dir_meta.entries:
                        if (e.name in obj.name) and not (obj.parent):
                            obj.parent = instance_obj
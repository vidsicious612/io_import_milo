from dataclasses import dataclass, field
from . metadata import Metadata
from . trans import Trans

@dataclass
class WaypointMatrix:
    matrix: tuple = ()

    def read(self, reader, version: int):
        self.matrix = reader.matrix()

        some_bool = reader.milo_bool()
        
        if version == 12:
            unknown = reader.vec2f()

@dataclass
class SpawnPoint:
    target: str = ""
    waypoint_matrices: list[WaypointMatrix] = field(default_factory=list)

    def read(self, reader, version: int, matrix_count: int):
        self.target = reader.numstring()

        for _ in range(matrix_count):
            waypoint_matrix = WaypointMatrix()
            waypoint_matrix.read(reader, version)

            self.waypoint_matrices.append(waypoint_matrix)

@dataclass
class P9WaypointConfiguration:
    version: int = 0
    metadata: Metadata = field(default_factory=Metadata)
    spawn_points: list[SpawnPoint] = field(default_factory=list)
    trans: Trans = ()
    strings: list[str] = field(default_factory=list)
    
    def read(self, reader, directory_meta):
        self.version = reader.int32()

        self.metadata.read(reader)

        unknown = reader.int32()

        matrix_count = reader.int32()

        if self.version == 3:
            reader.seek(17)

            self.trans.read(reader, True, directory_meta)
        else:
            points_count = reader.int32()

            for _ in range(points_count):
                spawn_point = SpawnPoint()
                spawn_point.read(reader, self.version, matrix_count)

                self.spawn_points.append(spawn_point)

        if self.version > 3:
            for _ in range(matrix_count):
                self.strings.append(reader.numstring())
        else:
            reader.seek(20)

        padding = reader.read_bytes(4)

        if padding != b"\xAD\xDE\xAD\xDE":
            raise Exception("Padding was not AD DE AD DE, read most likely failed.")

    def import_to_blender(self):
        import bpy
        import mathutils

        waypoints_collection = bpy.data.collections.get("Waypoints")

        if not waypoints_collection:
            waypoints_collection = bpy.data.collections.new("Waypoints")

            bpy.context.scene.collection.children.link(waypoints_collection)

        for spawn_point in self.spawn_points:
            waypoint_obj = bpy.data.objects.new(spawn_point.target, None)

            bpy.context.collection.objects.link(waypoint_obj)
            waypoints_collection.objects.link(waypoint_obj)
            bpy.context.collection.objects.unlink(waypoint_obj)

            waypoint_obj.empty_display_size = 2
            waypoint_obj.empty_display_type = "PLAIN_AXES"

            matrix_4x3 = mathutils.Matrix((
                (spawn_point.waypoint_matrices[-1].matrix[0], spawn_point.waypoint_matrices[-1].matrix[3], spawn_point.waypoint_matrices[-1].matrix[6], spawn_point.waypoint_matrices[-1].matrix[9]),
                (spawn_point.waypoint_matrices[-1].matrix[1], spawn_point.waypoint_matrices[-1].matrix[4], spawn_point.waypoint_matrices[-1].matrix[7], spawn_point.waypoint_matrices[-1].matrix[10]),
                (spawn_point.waypoint_matrices[-1].matrix[2], spawn_point.waypoint_matrices[-1].matrix[5], spawn_point.waypoint_matrices[-1].matrix[8], spawn_point.waypoint_matrices[-1].matrix[11]),
            ))
            
            waypoint_obj.matrix_world = matrix_4x3.to_4x4()
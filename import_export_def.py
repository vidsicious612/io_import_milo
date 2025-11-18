import time

from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator, Panel
from . external.milo.milo_file import MiloFile
from . external.milo.assets.anim_clip_samples import AnimClipSamples
from . external.milo.assets.char_clip_samples import char_clip_samples
from . external.milo.assets.mesh_anim import mesh_anims
from . external.milo.assets.prop_anim import prop_anims
from . external.milo.assets.trans_anim import trans_anims

class LoadCharClipSamples(Operator):
    bl_idname = "wm.load_char_clip_samples"
    bl_label = "Load CharClipSamples"

    sample_key: StringProperty() # type: ignore

    def execute(self, context):
        char_clip_sample = char_clip_samples.get(self.sample_key, {})
        char_clip_sample.import_to_blender()

        self.report({'INFO'}, f"CharClipSample '{self.sample_key}' loaded!")

        return {'FINISHED'}

class LoadMeshAnim(Operator):
    bl_idname = "wm.load_mesh_anim"
    bl_label = "Load MeshAnim"

    mesh_anim_key: StringProperty() # type: ignore

    def execute(self, context):
        mesh_anim = mesh_anims.get(self.mesh_anim_key, {})
        mesh_anim.import_to_blender()

        self.report({'INFO'}, f"MeshAnim '{self.mesh_anim_key}' loaded!")

        return {'FINISHED'}
    
class LoadPropAnim(Operator):
    bl_idname = "wm.load_prop_anim"
    bl_label = "Load PropAnim"

    prop_anim_key: StringProperty() # type: ignore

    def execute(self, context):
        prop_anim = prop_anims.get(self.prop_anim_key, {})
        prop_anim.import_to_blender()

        self.report({'INFO'}, f"PropAnim '{self.prop_anim_key}' loaded!")

        return {'FINISHED'}
      
class LoadTransAnim(Operator):
    bl_idname = "wm.load_trans_anim"
    bl_label = "Load TransAnim"

    trans_anim_key: StringProperty() # type: ignore

    def execute(self, context):
        trans_anim = trans_anims.get(self.trans_anim_key, {})
        trans_anim.import_to_blender()

        self.report({'INFO'}, f"TransAnim '{self.trans_anim_key}' loaded!")

        return {'FINISHED'}

class AnimPanel(Panel):
    bl_label = "Animation Panel"
    bl_idname = "PT_AnimationPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Load Animations'

    def draw(self, context):
        layout = self.layout

        if len(char_clip_samples) > 0:
            for char_clip_sample in char_clip_samples:
                op = layout.operator("wm.load_char_clip_samples", text=f"Load {char_clip_sample}")
                op.sample_key = char_clip_sample

        if len(mesh_anims) > 0:
            for mesh_anim in mesh_anims:
                op = layout.operator("wm.load_mesh_anim", text=f"Load {mesh_anim}")
                op.mesh_anim_key = mesh_anim

        if len(trans_anims) > 0:
            for trans_anim in trans_anims:
                op = layout.operator("wm.load_trans_anim", text=f"Load {trans_anim}")
                op.trans_anim_key = trans_anim

        if len(prop_anims) > 0:
            for prop_anim in prop_anims:
                op = layout.operator("wm.load_prop_anim", text=f"Load {prop_anim}")
                op.prop_anim_key = prop_anim

class ImportMilo(Operator, ImportHelper):
    """Import a milo file into Blender."""
    bl_idname = "import.milo"
    bl_label = "Import Milo"

    filepath = StringProperty(subtype="FILE_PATH")

    filter_glob: StringProperty(
        default="*.milo_ps3;*.milo_xbox;*.milo_wii;*.rnd_ps2;*.milo_ps2;*.rnd",
        options={"HIDDEN"},
    ) # type: ignore

    import_shadow: BoolProperty(
        name="Import Shadow Mesh",
        description="Import shadow mesh from character models.",
        default=False,
    ) # type: ignore

    import_lod: BoolProperty(
        name="Import LOD Meshes",
        description="Import lower quality LOD meshes.",
        default=False,
    ) # type: ignore

    import_wc: BoolProperty(
        name="Import WorldCrowd",
        description="Import WorldCrowd files from venues.",
        default=True,
    ) # type: ignore

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "import_shadow")
        layout.prop(self, "import_lod")
        layout.prop(self, "import_wc")

    def execute(self, context):
        start = time.time()
        
        milo = MiloFile(path=self.filepath)
        milo.read()
        milo.dir_meta.import_files(self, self.filepath)

        end = time.time()
        total_time = end - start

        self.report({"INFO"}, f"Successfully imported milo in {total_time} seconds!")

        return {"FINISHED"} 

class ExportMilo(Operator, ExportHelper):
    """Export a Blender scene to a milo file."""
    bl_idname = "export.milo"
    bl_label = "Export Milo"

    filepath = StringProperty(subtype="FILE_PATH")

    filter_glob: StringProperty(
        default="*.rnd_ps2;*.milo_xbox;*.milo_ps3",
        options={"HIDDEN"},
    ) # type: ignore

    game_selection: EnumProperty(
        name="Game Selection",
        description="Select the game from which you're exporting.",
        items=[
            ("GH1", "GH1", "Export a milo for GH1."),
            ("RB1", "RB1", "Export a milo for RB1."),
            ("TBRB", "TBRB", "Export a milo for TBRB.")
        ]
    ) # type: ignore

    milo_extension: EnumProperty(
        name="Milo Extension",
        description="Select the extension for the milo to export to.",
        items=[
            (".milo_xbox", ".milo_xbox", "Export a milo to milo_xbox."),
            (".milo_ps3", ".milo_ps3", "Export a milo to milo_ps3."),
        ]
    ) # type: ignore

    milo_type: EnumProperty(
        name="Milo Type",
        description="Select the type of milo to export to.",
        items=[
            ("Character", "Character", "Export a character milo."),
            ("Venue", "Venue", "Export a venue milo."),
        ]
    ) # type: ignore

    dir_name: StringProperty(
        name="Directory Name",
        description="The milo directory name.",
        default="" 
    ) # type: ignore

    @property
    def filename_ext(self):
        if self.game_selection == "GH1":
            return ".rnd_ps2"
        else:
            return self.milo_extension
    
    def draw(self, context):
        layout = self.layout

        layout.prop(self, "game_selection")

        if self.game_selection != "GH1":
            layout.prop(self, "milo_extension")
            layout.prop(self, "dir_name")

            if self.game_selection == "RB1":
                layout.prop(self, "milo_type")

    def execute(self, context):
        start = time.time()
        
        milo = MiloFile(path=self.filepath)
        milo.from_blender(self)
        milo.write(self.filepath, True if self.game_selection == "GH1" else False)

        end = time.time()
        total_time = end - start

        self.report({"INFO"}, f"Successfully exported milo in {total_time} seconds!")

        return {"FINISHED"}
    
class ImportACP(Operator, ImportHelper):
    """Import an ACP animation into Blender."""
    bl_idname = "import.acp"
    bl_label = "Import ACP"

    filepath = StringProperty(subtype="FILE_PATH")

    filter_glob: StringProperty(
        default="*.acp",
        options={"HIDDEN"},
    ) # type: ignore

    def execute(self, context):
        anim_clip_samples = AnimClipSamples()
        anim_clip_samples.read(self.filepath)
        anim_clip_samples.import_to_blender()

        self.report({"INFO"}, "Successfully imported ACP animation!")

        return {"FINISHED"}
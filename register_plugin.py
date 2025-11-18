import bpy
import os

from pathlib import Path
from . import_export_def import *

class MiloImportMenu(bpy.types.Menu):
    bl_label = "Milo Engine Modding"

    def draw(self, context):
        add_import_options(self.layout)

class MiloExportMenu(bpy.types.Menu):
    bl_label = "Milo Engine Modding"

    def draw(self, context):
        add_export_options(self.layout)

# Credits: Dodylectable
def register_icons():
    import bpy.utils.previews
    global custom_icons

    script_dir = Path(__file__).parent
    icon_dir = Path.joinpath(script_dir, "icons")

    pcoll = bpy.utils.previews.new()

    image_file_list = os.listdir(icon_dir)

    for image in image_file_list:
        shorthand = image.split(".")[0]

        print("Loading icon:", image)

        pcoll.load(shorthand, os.path.join(icon_dir, shorthand + ".jpg"), 'IMAGE')

    custom_icons = pcoll

# Credits: Dodylectable
def unregister_icons():
    if custom_icons:
        bpy.utils.previews.remove(custom_icons)

def get_icon_by_id(icon_name: str):
    return custom_icons[icon_name].icon_id

def add_import_sub_menu(self, context):
    self.layout.menu("MiloImportMenu", text = "Harmonix Milo Engine", icon_value = get_icon_by_id("HMX"))

def add_export_sub_menu(self, context):
    self.layout.menu("MiloExportMenu", text = "Harmonix Milo Engine", icon_value = get_icon_by_id("HMX"))

def add_import_options(layout):
    hmx_icon = get_icon_by_id("HMX")
    gh1_icon = get_icon_by_id("GH1")

    layout.operator(ImportMilo.bl_idname, text="Milo Scene (.milo, .rnd)", icon_value = hmx_icon)
    layout.operator(ImportACP.bl_idname, text="GH1 Animation (.acp)", icon_value = gh1_icon)

def add_export_options(layout):
    hmx_icon = get_icon_by_id("HMX")

    layout.operator(ExportMilo.bl_idname, text="Milo Scene (.milo, .rnd)", icon_value = hmx_icon)

def register_menus():
    bpy.types.TOPBAR_MT_file_import.append(add_import_sub_menu)
    bpy.types.TOPBAR_MT_file_export.append(add_export_sub_menu)

def unregister_menus():
    bpy.types.TOPBAR_MT_file_import.remove(add_import_sub_menu)
    bpy.types.TOPBAR_MT_file_export.remove(add_export_sub_menu)

def register_classes():
    bpy.utils.register_class(MiloImportMenu)
    bpy.utils.register_class(MiloExportMenu)
    bpy.utils.register_class(ImportMilo)
    bpy.utils.register_class(ImportACP)
    bpy.utils.register_class(ExportMilo)
    bpy.utils.register_class(LoadCharClipSamples)
    bpy.utils.register_class(LoadMeshAnim)
    bpy.utils.register_class(LoadPropAnim)
    bpy.utils.register_class(LoadTransAnim)
    bpy.utils.register_class(AnimPanel)

def unregister_classes():
    bpy.utils.unregister_class(MiloImportMenu)
    bpy.utils.unregister_class(MiloExportMenu)
    bpy.utils.unregister_class(ImportMilo)
    bpy.utils.unregister_class(ImportACP)
    bpy.utils.unregister_class(ExportMilo)
    bpy.utils.unregister_class(LoadCharClipSamples)
    bpy.utils.unregister_class(LoadMeshAnim)
    bpy.utils.unregister_class(LoadPropAnim)
    bpy.utils.unregister_class(LoadTransAnim)
    bpy.utils.unregister_class(AnimPanel)
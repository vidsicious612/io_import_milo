from . import_export_def import *
from . register_plugin import *

bl_info = {
    "name": "Milo Engine Modding Plugin",
    "description": "A plugin to import and export files from GH/RB games.",
    "author": "alliwantisyou3471",
    "blender": (4, 5, 0),
    "version": (1, 0, 0),
    "location": "File > Import-Export",
    "doc_url": "",
    "support": "COMMUNITY",
    "category": "Import-Export"
}

def register():
    register_icons()
    register_classes()
    register_menus()

def unregister():
    unregister_icons()
    unregister_classes()
    unregister_menus()

if __name__ == "__main__":
    register()
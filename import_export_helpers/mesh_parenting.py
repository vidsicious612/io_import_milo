import bpy

def parent_meshes(meshes):
    for mesh in meshes:
        if mesh.obj.version == 25:
            parent_obj = bpy.data.objects.get(mesh.obj.trans.parent)

            child_obj = bpy.data.objects.get(mesh.name)
                    
            if (parent_obj) and (parent_obj.name != child_obj.name):
                child_obj.parent = parent_obj

    # Geom owner
    for mesh in meshes:
        if (len(mesh.obj.vertices.vertices) == 0) and (mesh.obj.geom_owner != mesh.name):
            for obj in bpy.data.objects:
                if mesh.name in obj.name:
                    geom_owner_obj = bpy.data.objects.get(mesh.obj.geom_owner)
            
                    if geom_owner_obj:
                        obj.data = geom_owner_obj.data
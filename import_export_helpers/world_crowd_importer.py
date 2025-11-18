import bpy
import mathutils

def import_world_crowd(world_crowds: list):
    crowd_collection = bpy.data.collections.get("Crowds")

    if not crowd_collection:
        crowd_collection = bpy.data.collections.new("Crowds")

        bpy.context.scene.collection.children.link(crowd_collection)

    characters_dict = {}

    # Copy character objects, delete originals, and then store
    for world_crowd in world_crowds:
        for char in world_crowd.obj.characters:
            char_obj = bpy.data.objects.get(char.character)

            if char_obj:
                char_obj_name = char_obj.name

                obj_copy = char_obj.copy()
                
                for child in char_obj.children:
                    child_name = child.name

                    child_copy = child.copy()
                    child_copy.data = child.data.copy()
                    child_copy.parent = obj_copy

                    bpy.data.objects.remove(child, do_unlink=True)

                    child_copy.name = child_name
                
                bpy.data.objects.remove(char_obj, do_unlink=True)

                obj_copy.name = char_obj_name

                characters_dict[char.character] = obj_copy   

    # Now, spawn them all
    for world_crowd in world_crowds:
        if ("fill" in world_crowd.name) or (world_crowd.name.startswith("double_")) or (world_crowd.name.startswith("triple_")):
            continue

        if world_crowd.obj.version < 14:
            for i, old_mm in enumerate(world_crowd.obj.old_mm):
                character_obj = characters_dict.get(world_crowd.obj.characters[i].character)

                if character_obj:
                    for x in range(old_mm.old_mm_count):
                        character_dup = character_obj.copy()
                        character_dup.name = character_obj.name

                        bpy.context.collection.objects.link(character_dup)
                        bpy.context.view_layer.objects.active = character_dup

                        crowd_collection.objects.link(character_dup)
                        
                        bpy.context.collection.objects.unlink(character_dup)

                        for child in character_obj.children:
                            child_dup = child.copy()
                            child_dup.data = child.data.copy()
                            child_dup.parent = character_dup

                            bpy.context.collection.objects.link(child_dup)
                            bpy.context.view_layer.objects.active = child_dup

                            crowd_collection.objects.link(child_dup)
                            
                            bpy.context.collection.objects.unlink(child_dup)
                        
                        character_dup.matrix_world = mathutils.Matrix((
                            (old_mm.old_xfm_list[x][0], old_mm.old_xfm_list[x][3], old_mm.old_xfm_list[x][6], old_mm.old_xfm_list[x][9]),
                            (old_mm.old_xfm_list[x][1], old_mm.old_xfm_list[x][4], old_mm.old_xfm_list[x][7], old_mm.old_xfm_list[x][10]),
                            (old_mm.old_xfm_list[x][2], old_mm.old_xfm_list[x][5], old_mm.old_xfm_list[x][8], old_mm.old_xfm_list[x][11] - world_crowd.obj.characters[i].height / 2),
                        )).to_4x4()
import bpy
import mathutils

bone_local_matrices = {}

def compute(bone, world_matrices: dict):
    if bone.name in world_matrices:
        return world_matrices[bone.name]
    
    if bone.obj.parent is None:
        world = bone.obj.local_xfm
    else:
        if bone.obj.parent != bone.name:
            parent_world = compute(bone.obj.parent, world_matrices)

            world = parent_world @ bone.obj.local_xfm
        else:
            world = bone.obj.world_xfm

    return world

def add_twist_constraint(armature, main_bone: str, twist_bone: str):
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode="POSE")

    twist_pbone = armature.pose.bones[twist_bone]

    constraint = twist_pbone.constraints.new("COPY_ROTATION")
    constraint.target = armature
    constraint.subtarget = main_bone
    constraint.owner_space = "LOCAL"
    constraint.target_space = "LOCAL"
    constraint.influence = 1.0

def import_bones(bones: list, character_name: str):
    armature_data = bpy.data.armatures.new("Armature")
    armature_obj = bpy.data.objects.new("Armature", armature_data)

    bpy.context.collection.objects.link(armature_obj)  
    bpy.context.view_layer.objects.active = armature_obj

    for bone in bones:
        local_matrix = mathutils.Matrix((
            (bone.obj.local_xfm[0], bone.obj.local_xfm[3], bone.obj.local_xfm[6], bone.obj.local_xfm[9]),
            (bone.obj.local_xfm[1], bone.obj.local_xfm[4], bone.obj.local_xfm[7], bone.obj.local_xfm[10]),
            (bone.obj.local_xfm[2], bone.obj.local_xfm[5], bone.obj.local_xfm[8], bone.obj.local_xfm[11]),
        ))

        bone.obj.local_xfm = local_matrix.to_4x4()          
        
        bone_local_matrices[bone.name] = local_matrix.to_4x4()

        world_matrix = mathutils.Matrix((
            (bone.obj.world_xfm[0], bone.obj.world_xfm[3], bone.obj.world_xfm[6], bone.obj.world_xfm[9]),
            (bone.obj.world_xfm[1], bone.obj.world_xfm[4], bone.obj.world_xfm[7], bone.obj.world_xfm[10]),
            (bone.obj.world_xfm[2], bone.obj.world_xfm[5], bone.obj.world_xfm[8], bone.obj.world_xfm[11]),
        ))        

        bone.obj.world_xfm = world_matrix.to_4x4()

    bones_by_name = {bone.name: bone for bone in bones}

    for bone in bones:
        parent_name = bone.obj.parent

        if parent_name is None:
            bone.obj.parent = None
        else:
            bone.obj.parent = bones_by_name.get(parent_name)

    world_matrices = {}

    for bone in bones:
        # Hair bones seem to not need computing
        if not bone.name.startswith("bone_hair"):
            world_matrix = compute(bone, world_matrices)
        else:
            world_matrix = bone.obj.world_xfm
        
        world_matrices[bone.name] = world_matrix

    bpy.ops.object.mode_set(mode="EDIT")

    for bone in bones:
        edit_bone = armature_obj.data.edit_bones.new(bone.name)       

        edit_bone.head = (0, 0, 0)
        edit_bone.tail = (0, 1, 0)

        edit_bone.use_deform = True

        edit_bone.matrix = world_matrices[bone.name]
    
    for bone in bones:
        if hasattr(bone.obj, "trans.trans_objects"):
            for trans_object in bone.obj.trans.trans_objects:
                edit_bone = armature_data.edit_bones.get(bone.name)

                child_bone = armature_data.edit_bones.get(trans_object)

                if (edit_bone) and (child_bone):
                    child_bone.parent = edit_bone
        else:
            edit_bone = armature_data.edit_bones.get(bone.name)

            parent_bone = armature_data.edit_bones.get(bone.obj.parent.name) if bone.obj.parent else None

            if (parent_bone) and (edit_bone):
                edit_bone.parent = parent_bone

    # Left arm upper twist constraints
    left_arm_upper = bones_by_name.get("bone_L-upperArm.mesh")
    left_arm_upper_twist = bones_by_name.get("bone_L-upperTwist1.mesh")

    if (left_arm_upper) and (left_arm_upper_twist):
        add_twist_constraint(armature_obj, left_arm_upper.name, left_arm_upper_twist.name)

    # Right arm upper twist constraints
    right_arm_upper = bones_by_name.get("bone_R-upperArm.mesh")
    right_arm_upper_twist = bones_by_name.get("bone_R-upperTwist1.mesh")

    if (right_arm_upper) and (right_arm_upper_twist):
        add_twist_constraint(armature_obj, right_arm_upper.name, right_arm_upper_twist.name)

    # Left arm fore twist constraints
    left_arm_fore = bones_by_name.get("bone_L-foreArm.mesh")
    left_arm_fore_twist = bones_by_name.get("bone_L-foreTwist1.mesh")

    if (left_arm_fore) and (left_arm_fore_twist):
        add_twist_constraint(armature_obj, left_arm_fore.name, left_arm_fore_twist.name)

    # Right arm fore twist constraints
    right_arm_fore = bones_by_name.get("bone_R-foreArm.mesh")
    right_arm_fore_twist = bones_by_name.get("bone_R-foreTwist1.mesh")

    if (right_arm_fore) and (right_arm_fore_twist):
        add_twist_constraint(armature_obj, right_arm_fore.name, right_arm_fore_twist.name)

    bpy.ops.object.mode_set(mode="OBJECT")

    # Character parenting
    parent_obj = bpy.data.objects.get(character_name)           
        
    if parent_obj:
        armature_obj.parent = parent_obj

def import_mesh_bones(bones: list, character_name: str):
    armature_data = bpy.data.armatures.new("Armature")
    armature_obj = bpy.data.objects.new("Armature", armature_data)

    bpy.context.collection.objects.link(armature_obj)  
    bpy.context.view_layer.objects.active = armature_obj

    for bone in bones:
        local_matrix = mathutils.Matrix((
            (bone.obj.trans.local_xfm[0], bone.obj.trans.local_xfm[3], bone.obj.trans.local_xfm[6], bone.obj.trans.local_xfm[9]),
            (bone.obj.trans.local_xfm[1], bone.obj.trans.local_xfm[4], bone.obj.trans.local_xfm[7], bone.obj.trans.local_xfm[10]),
            (bone.obj.trans.local_xfm[2], bone.obj.trans.local_xfm[5], bone.obj.trans.local_xfm[8], bone.obj.trans.local_xfm[11]),
        ))

        bone.obj.trans.local_xfm = local_matrix.to_4x4()            
        
        bone_local_matrices[bone.name] = local_matrix.to_4x4()

        world_matrix = mathutils.Matrix((
            (bone.obj.trans.world_xfm[0], bone.obj.trans.world_xfm[3], bone.obj.trans.world_xfm[6], bone.obj.trans.world_xfm[9]),
            (bone.obj.trans.world_xfm[1], bone.obj.trans.world_xfm[4], bone.obj.trans.world_xfm[7], bone.obj.trans.world_xfm[10]),
            (bone.obj.trans.world_xfm[2], bone.obj.trans.world_xfm[5], bone.obj.trans.world_xfm[8], bone.obj.trans.world_xfm[11]),
        ))        

        bone.obj.trans.world_xfm = world_matrix.to_4x4()

    bones_by_name = {bone.name: bone for bone in bones}

    world_matrices = {}

    for bone in bones:
        world_matrices[bone.name] = bone.obj.trans.world_xfm

    bpy.ops.object.mode_set(mode="EDIT")

    for bone in bones:
        edit_bone = armature_obj.data.edit_bones.new(bone.name)       

        edit_bone.head = (0, 0, 0)
        edit_bone.tail = (0, 1, 0)

        edit_bone.use_deform = True

        edit_bone.matrix = world_matrices[bone.name]
    
    for bone in bones:
        if (hasattr(bone.obj, "trans")) and (hasattr(bone.obj.trans, "trans_objects")):
            for trans_object in bone.obj.trans.trans_objects:
                edit_bone = armature_data.edit_bones.get(bone.name)

                child_bone = armature_data.edit_bones.get(trans_object)

                if (edit_bone) and (child_bone):
                    child_bone.parent = edit_bone
        else:
            edit_bone = armature_data.edit_bones.get(bone.name)

            parent_bone = armature_data.edit_bones.get(bone.obj.trans.parent)

            if (parent_bone) and (edit_bone):
                edit_bone.parent = parent_bone

    # Left arm upper twist constraints
    left_arm_upper = bones_by_name.get("bone_L-upperArm.mesh")
    left_arm_upper_twist = bones_by_name.get("bone_L-upperTwist1.mesh")

    if (left_arm_upper) and (left_arm_upper_twist):
        add_twist_constraint(armature_obj, left_arm_upper.name, left_arm_upper_twist.name)

    # Right arm upper twist constraints
    right_arm_upper = bones_by_name.get("bone_R-upperArm.mesh")
    right_arm_upper_twist = bones_by_name.get("bone_R-upperTwist1.mesh")

    if (right_arm_upper) and (right_arm_upper_twist):
        add_twist_constraint(armature_obj, right_arm_upper.name, right_arm_upper_twist.name)

    # Left arm fore twist constraints
    left_arm_fore = bones_by_name.get("bone_L-foreArm.mesh")
    left_arm_fore_twist = bones_by_name.get("bone_L-foreTwist1.mesh")

    if (left_arm_fore) and (left_arm_fore_twist):
        add_twist_constraint(armature_obj, left_arm_fore.name, left_arm_fore_twist.name)

    # Right arm fore twist constraints
    right_arm_fore = bones_by_name.get("bone_R-foreArm.mesh")
    right_arm_fore_twist = bones_by_name.get("bone_R-foreTwist1.mesh")

    if (right_arm_fore) and (right_arm_fore_twist):
        add_twist_constraint(armature_obj, right_arm_fore.name, right_arm_fore_twist.name)

    bpy.ops.object.mode_set(mode="OBJECT")

    # Character parenting
    parent_obj = bpy.data.objects.get(character_name)           
        
    if parent_obj:
        armature_obj.parent = parent_obj
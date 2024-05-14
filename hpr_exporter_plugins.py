bl_info = {
    "name": "NFSHP/NFSHPR Exporter Plugins",
    "author": "Enthuse",
    "version": (1, 0),
    "blender": (3, 6, 11),
    "location": "3D View > Add > HP Exporter Plugins",
    "description": "Makes your life easier while setting up scene for exporting HP/HPR models",
    "category": "Miscellaneous",
    "support": "COMMUNITY"
}

import bpy
import math
import os
from bpy.types import Operator
from bpy.props import BoolProperty, StringProperty


def clear_scene():
	for block in bpy.data.objects:
		#if block.users == 0:
		bpy.data.objects.remove(block, do_unlink = True)

	for block in bpy.data.meshes:
		if block.users == 0:
			bpy.data.meshes.remove(block)

	for block in bpy.data.materials:
		if block.users == 0:
			bpy.data.materials.remove(block)

	for block in bpy.data.textures:
		if block.users == 0:
			bpy.data.textures.remove(block)

	for block in bpy.data.images:
		if block.users == 0:
			bpy.data.images.remove(block)
	
	for block in bpy.data.cameras:
		if block.users == 0:
			bpy.data.cameras.remove(block)
	
	for block in bpy.data.lights:
		if block.users == 0:
			bpy.data.lights.remove(block)
	
	for block in bpy.data.armatures:
		if block.users == 0:
			bpy.data.armatures.remove(block)
	
	for block in bpy.data.collections:
		if block.users == 0:
			bpy.data.collections.remove(block)
		else:
			bpy.data.collections.remove(block, do_unlink=True)
            
            
def import_default_hp_textures(self):
    script_directory = os.path.dirname(__file__)
    directory = os.path.join(script_directory, "HP_DefaultTextures")

    if os.path.exists(directory) and os.path.isdir(directory):
        files = os.listdir(directory)
        dds_files = [f for f in files if f.endswith('.dds')]

        for dds_file in dds_files:
            filepath = os.path.join(directory, dds_file)
            bpy.ops.image.open(filepath=filepath)
            image = bpy.data.images.get(dds_file)
            image.is_shared_asset = True
    else:
        self.report({'ERROR'}, "Could not find folder HP_DefaultTextures.")
        
        
def setup_vehicle_id(car_id, self):
    vehicle_collection_name = "VEH_" + car_id + "_MS"
    
    if vehicle_collection_name not in bpy.data.collections:
        vehicle_collection = bpy.data.collections.new(vehicle_collection_name)
        vehicle_collection["resource_type"] = "GraphicsSpec"
        
        #Sub-Collection (graphics)
        graphics_collection_name = car_id + "_Graphics"
        graphics_collection = bpy.data.collections.new(graphics_collection_name)
        graphics_collection["resource_type"] = "GraphicsSpec"
        vehicle_collection.children.link(graphics_collection)
        
        #Sub-Collection (wheels)
        wheels_collection_name = car_id + "_Wheels"
        wheels_collection = bpy.data.collections.new(wheels_collection_name)
        wheels_collection["resource_type"] = "WheelGraphicsSpec"
        vehicle_collection.children.link(wheels_collection)
        
        bpy.context.scene.collection.children.link(vehicle_collection)
    else:
        self.report({'ERROR'}, "Collection already exists")
        
        
def get_meshes_based_on_state(include_hidden):
    if include_hidden:
        return [obj for obj in bpy.data.objects if obj.type == "MESH"]
    else:
        return [obj for obj in bpy.data.objects if obj.type == "MESH" and obj.visible_get()]
        
        
def apply_mesh_rotation(include_hidden, delete_empty_parent, self):
    meshes = get_meshes_based_on_state(include_hidden)
    
    #Unlink parent while retaining transformation
    for mesh in meshes:
        if mesh.parent:
            parent_temp = mesh.parent
            
            #If mesh is not hidden then directly unlink
            if not mesh.hide_get():
                mesh.select_set(True)
                bpy.ops.object.parent_clear(type = "CLEAR_KEEP_TRANSFORM")
                bpy.ops.object.transform_apply(location = True, rotation = True, scale = True)
                mesh.select_set(False)
            else: #If it's hidden, show -> unlink -> hide
                mesh.hide_set(False)
                mesh.select_set(True)
                bpy.ops.object.parent_clear(type = "CLEAR_KEEP_TRANSFORM")
                bpy.ops.object.transform_apply(location = True, rotation = True, scale = True)
                mesh.select_set(False)
                mesh.hide_set(True)
                
            #If parent empty, delete parent
            if parent_temp.type == 'EMPTY' and len(parent_temp.children) == 0 and delete_empty_parent:
                bpy.data.objects.remove(parent_temp)
                
        #If mesh not in a parent then directly apply transformation        
        else:
            mesh.select_set(True)
            bpy.ops.object.transform_apply(location = True, rotation = True, scale = True)
            mesh.select_set(False)
            
    #Create parent
    for mesh in meshes:
        empty_name = "Empty_" + mesh.name
        bpy.ops.object.empty_add(type = "PLAIN_AXES")
        empty = bpy.context.active_object
        empty.name = empty_name
        
        #If mesh is not hidden do
        if not mesh.hide_get():
            mesh.rotation_euler = (math.radians(-90), 0.0, 0.0)
            mesh.select_set(True)
            bpy.ops.object.transform_apply(location = False, rotation = True, scale = False)
            empty.select_set(True)
            bpy.context.view_layer.objects.active = empty
            bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = True)
            empty.rotation_euler = (math.radians(90), 0.0, 0.0)
        else:
            mesh.hide_set(False)
            mesh.rotation_euler = (math.radians(-90), 0.0, 0.0)
            mesh.select_set(True)
            bpy.ops.object.transform_apply(location = False, rotation = True, scale = False)
            empty.select_set(True)
            bpy.context.view_layer.objects.active = empty
            bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = True)
            empty.rotation_euler = (math.radians(90), 0.0, 0.0)
            mesh.hide_set(True)
        
        mesh.select_set(False)
        empty.select_set(False)
        
        self.report({'INFO'}, "Finished")
        
        
#Main Menu
class MAIN_MENU_HP_EXPORTER_PLUGINS(bpy.types.Menu):
    
    bl_idname = "MAIN_MENU_HP_EXPORTER_PLUGINS"
    bl_label = "HP Exporter Plugins"
    
    def draw(self, context):
        layout = self.layout
        layout.menu("SUB_MENU_CAR", icon = "AUTO")
        
        
#Sub Menu
class SUB_MENU_CAR(bpy.types.Menu):

    bl_idname = "SUB_MENU_CAR"
    bl_label = "Vehicle"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("initialize.scene", icon = "OUTLINER_COLLECTION")
        layout.operator("assign.empty", icon = "EMPTY_AXIS")


#Operators
class Initialize_Scene(bpy.types.Operator):
    
    bl_idname = "initialize.scene"
    bl_label = "Prepare Collection"
    bl_description = "Creates a main collection for the vehicle while importing default textures"
    
    clear_scene: BoolProperty(
        name = "Clear Scene",
        description = "Deletes everything in scene",
        default = True,
    )
    
    import_default_textures : BoolProperty(
        name = "Import default Hot Pursuit Vehicle Textures",
        description = "Import the default textures in VEHICLETEX.BIN",
        default = True,
    )
    
    car_id : StringProperty(
        name = "Vehicle ID",
        description = "Enter the Car ID you wish to set the scene up for",
        default = "0",
    )
        
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False  # No animation.
        
        ##
        box = layout.box()
        split = box.split(factor=0.75)
        col = split.column(align=True)
        col.label(text="Preferences", icon="OPTIONS")
        
        box.prop(self, "clear_scene")
        box.prop(self, "import_default_textures")
        
        if self.clear_scene:
            box.prop(self, "car_id")
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width = 250)
    
    def execute(self, context):
        if self.clear_scene:
            clear_scene()
            setup_vehicle_id(self.car_id, self)
            
        if self.import_default_textures:
            import_default_hp_textures(self)
            
        return {'FINISHED'}
        
        
class Assign_Empty(bpy.types.Operator):
    
    bl_idname = "assign.empty"
    bl_label = "Assign parent to all mesh"
    bl_description = "Auto assign each mesh a parent with the correct rotation."
    
    include_hidden: BoolProperty(
        name = "Include hidden meshes",
        description = "Assigns a empty to each mesh while retaining their transformation",
        default = True,
    )
    
    delete_empty_parent: BoolProperty(
        name = "Delete empty parent",
        description = "Delete parent with 0 meshes",
        default = True,
    )
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False  # No animation.
        
        ##
        box = layout.box()
        split = box.split(factor=0.75)
        col = split.column(align=True)
        col.label(text="Preferences", icon="OPTIONS")
        
        box.prop(self, "include_hidden")
        box.prop(self, "delete_empty_parent")
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width = 250)   
        
    def execute(self, context):
        apply_mesh_rotation(self.include_hidden, self.delete_empty_parent, self)
            
        return {'FINISHED'}
        
        
register_classes = (
    MAIN_MENU_HP_EXPORTER_PLUGINS,
    SUB_MENU_CAR,
    Initialize_Scene,
    Assign_Empty,
)

def menu_func(self, context):
    self.layout.menu(MAIN_MENU_HP_EXPORTER_PLUGINS.bl_idname)


def register():
    for items in register_classes:
        bpy.utils.register_class(items)
    bpy.types.VIEW3D_MT_add.append(menu_func)


def unregister():
    bpy.types.VIEW3D_MT_add.remove(menu_func)
    for items in register_classes:
        bpy.utils.unregister_class(items)
        
        

        
        
        
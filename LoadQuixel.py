import bpy
import os
from bpy.props import StringProperty

class DecalLoader(bpy.types.Operator):
    """Load Decals from Quixel Textures"""
    bl_idname = "object.decal_loader"
    bl_label = "Load Decals"
    filepath : StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        # Use the filepath property to access the path to the textures
        texture_path = self.filepath
        print(texture_path)
        
        # Create a new material
        new_material = bpy.data.materials.new(name="Decal Material")
        new_material.use_nodes = True
        new_material.blend_method = 'HASHED'
        new_material.shadow_method = 'HASHED'
        node_tree = new_material.node_tree        
        # Get the active object
        obj = context.active_object        
        # Assign the new material to the active object
        if obj.data.materials:
            # assign to 1st material slot
            obj.data.materials[0] = new_material
        else:
            # no slots
            obj.data.materials.append(new_material)
        
        # Clear default nodes
        node_tree.nodes.clear()        
        # Create output node
        output_node = node_tree.nodes.new(type='ShaderNodeOutputMaterial')
        output_node.location = (600, 0)
        # Create principled BSDF node
        principled_node = node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
        principled_node.location = (0, 0)
                # Create normal map node
        normal_map_node = node_tree.nodes.new(type='ShaderNodeNormalMap')
        normal_map_node.location = (-200, -600)        
        # Create displacement map node
        displacement_map_node = node_tree.nodes.new(type='ShaderNodeDisplacement')
        displacement_map_node.location = (400, -600)
        # Create a mix shader node for AO
        mix_RGB_node = node_tree.nodes.new(type='ShaderNodeMixRGB')
        mix_RGB_node.location = (-200, -100)
        mix_RGB_node.blend_type = 'MULTIPLY'
        mix_RGB_node.inputs[0].default_value = 1
        # Create a transparent shader node for AO
        # Iterate through all files in the texture_path directory
        for file in os.listdir(texture_path):
        # Check if the file is an image
            if file.endswith(".jpg") or file.endswith(".png"):
                # create a new image texture node
                image_node = node_tree.nodes.new(type='ShaderNodeTexImage')
                image_node.location = (-200,0)
                image_node.location = (-500, -1279)  
                # set the image path 
                image_path = os.path.join(texture_path, file)
                image_node.image = bpy.data.images.load(image_path)                
                # link the output of the image node to the principled bsdf node
                # check the suffix of the file and link the output to the corresponding slot
            if "_Albedo" in file:
                print("yes")
                node_tree.links.new(image_node.outputs[0], principled_node.inputs[0])
                node_tree.links.new(image_node.outputs[0], mix_RGB_node.inputs[1])
                image_node.location = (-500, 100)                
            elif "_Normal" in file:
                node_tree.links.new(image_node.outputs[0], normal_map_node.inputs[1])
                node_tree.links.new(normal_map_node.outputs[0], principled_node.inputs[22])
                image_node.location = (-500, -879)
            elif "_Roughness" in file:
                node_tree.links.new(image_node.outputs[0], principled_node.inputs[9])
                image_node.location = (-500, -279)
                 
            elif "_Opacity" in file:
                node_tree.links.new(image_node.outputs[0], principled_node.inputs[21])
                image_node.location = (-500, -579)
            elif "_AO" in file:
                node_tree.links.new(image_node.outputs[0], mix_RGB_node.inputs[2])
                image_node.location = (-500, 400)
            elif "_Preview" in file:
                image_node.location = (100, 400)
            elif "_Displacement" in file:
                node_tree.links.new(image_node.outputs[0], displacement_map_node.inputs[0])                            
        node_tree.links.new(mix_RGB_node.outputs[0], output_node.inputs[0])
        node_tree.links.new(displacement_map_node.outputs[0], output_node.inputs[2])
        node_tree.links.new(mix_RGB_node.outputs[0],principled_node.inputs[0])
        node_tree.links.new(principled_node.outputs[0],output_node.inputs[0])        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class DecalPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Decal Loader"
    bl_idname = "OBJECT_PT_decal"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.decal_loader")

def register():
    bpy.utils.register_class(DecalLoader)
    bpy.utils.register_class(DecalPanel)

def unregister():
    bpy.utils.unregister_class(DecalLoader)
    bpy.utils.unregister_class(DecalPanel)

if __name__ == "__main__":
    register()

import bpy
import json
import math
import os

def hex_color_to_rgba(hex_color):
    hex_color = hex_color[1:]

    red = int(hex_color[:2], base=16)
    srgb_red = red / 255
    linear_red = convert_srbg_to_linear_rgb(srgb_red)
    
    green = int(hex_color[2:4], base=16)
    srgb_green = green / 255
    linear_green = convert_srbg_to_linear_rgb(srgb_green)
    
    blue = int(hex_color[4:6], base=16)
    srgb_blue = blue / 255
    linear_blue = convert_srbg_to_linear_rgb(srgb_blue)
    return tuple([linear_red, linear_green, linear_blue, 1.0])

def convert_srbg_to_linear_rgb(srgb_color_component):
    if srgb_color_component <= 0.04045:
        linear_color_componet = srgb_color_component / 12.92
    else:
        linear_color_componet = math.pow((srgb_color_component + 0.055) / 1.055, 2.4)
    return linear_color_componet


#FILE EXTRACTION + DETERMINING WHICH SHAPE TO CREATE
def makeVisualization(filepath):
    f = open(filepath)
    data = json.load(f)
    for i in range(len(data['Buildings'])):
        if data['Buildings'][i]['Shape'] == "Rectangle":
            for j in range(data['Buildings'][i]['Height']):
                V0 = data['Buildings'][i]['V0']
                V1 = data['Buildings'][i]['V1']
                V2 = data['Buildings'][i]['V2']
                V3 = data['Buildings'][i]['V3']
                verts = [(V0[0],V0[1],0),(V1[0],V1[1],0),(V3[0],V3[1],0),(V2[0],V2[1],0),(V0[0],V0[1],1),(V1[0],V1[1],1),(V3[0],V3[1],1),(V2[0],V2[1],1)]
                faces = [(0,1,3,2),(0,1,5,4),(0,2,6,4),(6,7,3,2),(1,3,7,5),(7,5,4,6)]
                mesh = bpy.data.meshes.new("Rectangle")
                object = bpy.data.objects.new("Rectangle", mesh)
                bpy.context.collection.objects.link(object)
                object.location = (0,0,j)
                mesh.from_pydata(verts,[],faces)
                hex_color = data['Buildings'][i]['Color'] 
                rgba_color = hex_color_to_rgba(hex_color)
                material = bpy.data.materials.new(name=f"hex_color_{hex_color}")
                material.diffuse_color = rgba_color
                object.data.materials.append(material)
        elif data['Buildings'][i]['Shape'] == "Triangle":
            for j in range(data['Buildings'][i]['Height']):
                V0 = data['Buildings'][i]['V0']
                V1 = data['Buildings'][i]['V1']
                V2 = data['Buildings'][i]['V2']
                verts = [(V0[0],V0[1],0),(V1[0],V1[1],0),(V2[0],V2[1],0),(V0[0],V0[1],2),(V1[0],V1[1],2),(V2[0],V2[1],2)]
                faces = [(0,1,2),(2,1,4,5),(4,3,0,1),(5,3,0,2),(5,4,3)]
                mesh = bpy.data.meshes.new("Triangle")
                object = bpy.data.objects.new("Triangle", mesh)
                bpy.context.collection.objects.link(object)
                object.location = (0,0,2*j)
                mesh.from_pydata(verts,[],faces)
                hex_color = data['Buildings'][i]['Color'] 
                rgba_color = hex_color_to_rgba(hex_color)
                material = bpy.data.materials.new(name=f"hex_color_{hex_color}")
                material.diffuse_color = rgba_color
                object.data.materials.append(material)
        elif data['Buildings'][i]['Shape'] == "Circle":
            for j in range(data['Buildings'][i]['Height']):
                Center = data['Buildings'][i]['Center']
                r = data['Buildings'][i]['Radius'] 
                bpy.ops.mesh.primitive_cylinder_add(radius = r, location=(Center[0], Center[1], j+0.5), vertices = 16,depth = 1.0)
                cylinder = bpy.context.active_object
                hex_color = data['Buildings'][i]['Color'] 
                rgba_color = hex_color_to_rgba(hex_color)
                material = bpy.data.materials.new(name=f"hex_color_{hex_color}")
                material.diffuse_color = rgba_color
                cylinder.data.materials.append(material)
    f.close()

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
makeVisualization("F:\AGorkemDepo\Documents\Blender Files\ScriptTest\data.json")
blendFile = "C:\\Users\\revas\\The Library\\School\\CAPSTONE\\SELF_DOCS\\Visualization.blend"
bpy.ops.wm.save_as_mainfile(filepath=blendFile)
os.startfile(blendFile)
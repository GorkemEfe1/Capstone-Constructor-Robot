import bpy
import os

# Function to read parameters from Data.txt
def read_parameters(file_path):
    params = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if '=' in line:
                key, value = line.split('=', 1)
                if ',' in value:
                    params[key] = tuple(map(float, value.split(',')))
                else:
                    try:
                        params[key] = int(value)
                    except ValueError:
                        try:
                            params[key] = float(value)
                        except ValueError:
                            params[key] = value
    return params

# Read parameters from Data.txt
params = read_parameters("F:\\AGorkemDepo\\Documents\\Blender Files\\3DVisualization\\Data.txt")

# Delete all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Define parameters
num_stacks = params['num_stacks']
blend_file_path = params['blend_file_path']

# Create cube stacks
for stack in range(num_stacks):
    # Generate x and y coordinates for the stack location
    x_location = params[f'stack_{stack}_x']
    y_location = params[f'stack_{stack}_y']
    n = params[f'stack_{stack}_n']
    for i in range(n):
        # Add a cube in the stack at a specific x, y and z for each level
        z_location = 2 * i
        #z_location = params[f'stack_{stack}_cube_{i}_z']
        bpy.ops.mesh.primitive_cube_add(size=2, location=(x_location, y_location, z_location))

# Save the current scene to the .blend file
bpy.ops.wm.save_as_mainfile(filepath=blend_file_path)

# Open the saved .blend file
os.startfile(blend_file_path)



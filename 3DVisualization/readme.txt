The directory for the script is 
"F:\AGorkemDepo\Documents\Blender Files\3DVisualization\3DVis.py"
How to run from the command prompt? (Run as Administrator)
blender --background --python "F:\AGorkemDepo\Documents\Blender Files\3DVisualization\3DVis.py"




A previous version using random values
import bpy
import random
import os

# Print confirmation
print("Script is running")

# Delete all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Define parameters
num_stacks = 5  # Number of cube stacks
n_range = (1, 5)          # Number of cubes per stack
x_range = (-20, 20)   # x-axis range for random placement
y_range = (-20, 20) # y-axis range for random placement

# Create cube stacks
for stack in range(num_stacks):
    # Generate random x and y coordinates for the stack location
    x_location = random.uniform(*x_range)
    y_location = random.uniform(*y_range)
    n = random.randint(*n_range)
    for i in range(n):
        # Add a cube in the stack at a random x, y and increasing z for each level
        bpy.ops.mesh.primitive_cube_add(size=2, location=(x_location, y_location, i * 2))

# Define the path for saving the .blend file in the desired directory
blend_file_path = "F:\\AGorkemDepo\\Documents\\Blender Files\\3DVisualization\\CubeScene.blend"

# Save the current scene to the .blend file
bpy.ops.wm.save_as_mainfile(filepath=blend_file_path)

# Open the saved .blend file
os.startfile(blend_file_path)





Original Text Filesnum_stacks=5
stack_0_x=-10.5
stack_0_y=15.2
stack_0_n=3
stack_0_cube_0_z=0
stack_0_cube_1_z=2
stack_0_cube_2_z=4
stack_1_x=5.0
stack_1_y=-12.3
stack_1_n=2
stack_1_cube_0_z=0
stack_1_cube_1_z=2
stack_2_x=0.0
stack_2_y=3.0
stack_2_n=4
stack_2_cube_0_z=0
stack_2_cube_1_z=2
stack_2_cube_2_z=4
stack_2_cube_3_z=6
stack_3_x=-5.0
stack_3_y=7.0
stack_3_n=5
stack_3_cube_0_z=0
stack_3_cube_1_z=2
stack_3_cube_2_z=4
stack_3_cube_3_z=6
stack_3_cube_4_z=8
stack_4_x=10.0
stack_4_y=12.0
stack_4_n=1
stack_4_cube_0_z=0


blend_file_path=F:\AGorkemDepo\Documents\Blender Files\3DVisualization\CubeScene.blend
import subprocess

# Define the path to the Blender executable
blender_executable = "C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe"

# Define the path to the Python script you want to run in Blender
script_path = "F:\\AGorkemDepo\\Documents\\Blender Files\\3DVisualization\\3DVis.py"

# Construct the command to run Blender in background mode with the specified script
command = [blender_executable, "--background", "--python", script_path]

# Run the command
subprocess.run(command)
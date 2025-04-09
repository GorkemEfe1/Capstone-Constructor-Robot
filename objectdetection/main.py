import ImageProcessor as ip
import subprocess

blender_executable = "C:\\Program Files\\Blender Foundation\\Blender 4.3\\blender.exe"
script_path = "C:\\Users\\revas\\Repos\\Capstone-Constructor-Robot\\Capstone-Constructor-Robot\\3DVisualization\\GORKEM.py"
command = [blender_executable, "--background", "--python", script_path]

processor = ip.ImageProcessor("objectdetection/img.png")
processor.extract_building_details()
processor.show_final()
processor.export_json()
subprocess.run(command)
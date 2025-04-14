import subprocess

# Define the command to run the script
command = ['python','C:\Program Files\Data Transmission_script.py']

# Create a subprocess to run the script
try:
    result = subprocess.run(command, check=True, text=True, capture_output=True)
    print("Output:", result.stdout)  # Output from the script
    print("Error (if any):", result.stderr)  # Error message (if any)
except subprocess.CalledProcessError as e:
    print(f"Error occurred while running the script: {e}")

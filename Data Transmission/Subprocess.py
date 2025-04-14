import subprocess

def send_data_to_lcd():
    try:
        # Run the script using subprocess
        result = subprocess.run(['python', 'Tester.py'], check=True, capture_output=True, text=True)

        # Output the results
        print("Script output:")
        print(result.stdout)

    except subprocess.CalledProcessError as e:
        print("There was an error running the script:")
        print(e.stderr)

if __name__ == "__main__":
    send_data_to_lcd()


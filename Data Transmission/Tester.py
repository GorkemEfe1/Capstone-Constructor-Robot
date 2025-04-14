import serial
import time
import json

# Specify the serial port and baud rate for communication with Arduino
arduino_port = 'COM3'  # Change to your Arduino's port
baud_rate = 9600

# File containing building data
file_path = 'C:\\Users\\revas\\Repos\\Capstone-Constructor-Robot\\Capstone-Constructor-Robot\\Data Transmission\\Data.json'

def read_building_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)  # Load JSON data
    
    buildings = data.get("Buildings", [])
    formatted_data = []
    
    for b in buildings:
        shape = b["Shape"]
        color = b["Color"]
        height = b["Height"]
        
        if shape == "Triangle":
            v0, v1, v2 = b["V0"], b["V1"], b["V2"]
            formatted_data.append(f"{b['Id']},{shape},{v0},{v1},{v2},{color},{height}")
        elif shape == "Circle":
            center, radius = b["Center"], b["Radius"]
            formatted_data.append(f"{b['Id']},{shape},{center},{radius},{color},{height}")
        elif shape == "Rectangle":
            v0, v1, v2, v3 = b["V0"], b["V1"], b["V2"], b["V3"]
            formatted_data.append(f"{b['Id']},{shape},{v0},{v1},{v2},{v3},{color},{height}")
    
    return formatted_data

def send_data_to_arduino(data):
    try:
        with serial.Serial(arduino_port, baud_rate, timeout=1) as ser:
            time.sleep(2)  # Allow time for Arduino to reset
            for entry in data:
                print(f"Sending: {entry}")
                ser.write((entry + '\n').encode())
                time.sleep(1)  # Wait for Arduino to process
    except serial.SerialException as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    building_data = read_building_data(file_path)
    if building_data:
        send_data_to_arduino(building_data)
    else:
        print("No data found in the JSON file.")

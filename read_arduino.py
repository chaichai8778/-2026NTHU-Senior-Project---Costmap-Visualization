import serial
import time

COM_PORT = 'COM5'  
BAUD_RATE = 115200  
SENSOR_OFFSET = 11.5 #cm

def decode(data_string):
    input_array = data_string.split(",")

    if len(input_array) < 3:
        return None, None, None
    val_str1 = input_array[0].replace('\r', '').strip()
    val_str2 = input_array[1].replace('\r', '').strip()
    val_str3 = input_array[-1].replace('\r', '').strip()

    # if val_str1 and val_str2 are not empty, convert to float
    if not (val_str1 and val_str2 and val_str3):
        return None, None, None
    
    try:
        obstacle_distance = float(val_str1) + SENSOR_OFFSET
        deltaSL = float(val_str2)
        deltaSR = float(val_str3)

        return obstacle_distance, deltaSL, deltaSR
    
    except ValueError:
        print("Error occurred while converting values to float.")

        return None, None, None

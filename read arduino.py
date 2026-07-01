import serial
import time

COM_PORT = 'COM5'  
BAUD_RATE = 115200  

try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    print(f"成功連結 {COM_PORT}")
    
    time.sleep(2) 

    while True:
        if ser.in_waiting > 0:
            raw_data = ser.readline()
            try:
                data_string = raw_data.decode('utf-8').strip()
                
                input_array = data_string.split(",")  
                obstacle_distance = float(input_array[0]) 
                absolute_angle = float(input_array[1])  
                    
            except UnicodeDecodeError:
                pass
        print(f" {obstacle_distance} m/{absolute_angle} deg")

except serial.SerialException as e:
    print(f"無法開啟序列埠 {COM_PORT}，原因: {e}")
    print("提示：請確認 VS Code 的 Serial Monitor 已經關閉！")
except KeyboardInterrupt:
    print("\n程式被使用者中止。")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("序列埠已關閉。")
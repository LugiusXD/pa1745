import serial
from datetime import datetime, timedelta
import string

# Change 'COM3' to the correct port for your Arduino (check in Arduino IDE)
ser = serial.Serial('COM7', 9600, timeout=1)

with open("button_log.txt", "a") as file:
    while True:
        #Might not be a good idea to skip errors
        line = ser.readline().decode("utf-8", errors="ignore").strip()
        clean_line = ''.join(filter(lambda x: x in string.printable, line))

        if line:
            print(clean_line)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f'{clean_line} : {current_time}"\n"')
            file.flush()  # Ensure the text is written immediately

#f.write(f'Task: {task_name}\nStart Time: {start_time.strftime("%Y-%m-%d %H:%M:%S")}\nStop Time: {stop_time.strftime("%Y-%m-%d %H:%M:%S")}\nElapsed Time: {elapsed_time_str}\n\n')


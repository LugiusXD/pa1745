import serial
from datetime import datetime
import string
import pandas as pd
from app import times_file
# Serial setup
ser = serial.Serial('COM7', 9600, timeout=1)

# Dictionary to track start times for each task
task_start_times = {}

# Open the file in append mode
with open(times_file, "a") as file:
    # Uncomment the next line if you want to add column headers (only once)
    # file.write("Task,Start,Stop,Elapsed\n")

    while True:
        line = ser.readline().decode("utf-8", errors="ignore").strip()
        clean_line = ''.join(filter(lambda x: x in string.printable, line))

        if clean_line:
            print(clean_line)
            current_time = datetime.now()

            try:
                # Expecting format like: "Task 1: START"
                task_part, status = clean_line.split(":")
                task = task_part.strip()
                status = status.strip().upper()

                if status == "START":
                    task_start_times[task] = current_time

                elif status == "STOP":
                    if task in task_start_times:
                        start_time = task_start_times.pop(task)
                        elapsed = current_time - start_time
                        # Write row to file
                        file.write(f"{task},{start_time},{current_time},{elapsed}\n")
                        file.flush()

                    else:
                        print(f"Warning: STOP received for {task} with no matching START")

            except ValueError:
                print("Invalid format:", clean_line)

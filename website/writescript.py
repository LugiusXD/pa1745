import os
import serial
from serial.serialutil import SerialException
from datetime import datetime
import string
import pandas as pd
import csv
import sys


# Path to times.csv
times_file = os.path.join('times.csv')

# Ensure the file exists
if not os.path.exists(times_file):
    with open(times_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Task', 'Start Time', 'Stop Time', 'Elapsed Time'])  # Write header

# Serial setup
try:
    ser = serial.Serial('COM3', 9600, timeout=1)
except SerialException as e:
    print(f"Error: Could not open serial port: {e}")
    ser = None

# Dictionary to track start times for each task
task_start_times = {}

# Function to log time to times.csv
def log_time(task, start_time, stop_time, elapsed_time):
    with open(times_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([task, start_time, stop_time, elapsed_time])

# Open the file in append mode
if ser:
    while True:
        line = ser.readline().decode("utf-8", errors="ignore").strip()
        clean_line = ''.join(filter(lambda x: x in string.printable, line))

        if clean_line:
            print(clean_line)
            current_time = datetime.now().replace(microsecond=0)

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
                        log_time(task, start_time, current_time, elapsed)

                    else:
                        print(f"Warning: STOP received for {task} with no matching START")

            except ValueError:
                print("Invalid format:", clean_line)


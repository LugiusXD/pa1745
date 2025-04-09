import time
import tkinter as tk
from tkinter import messagebox

class TaskTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Timer App")

        self.timers = {}
        self.active_task = None
        self.running = False

        # Create timer label
        self.timer_label = tk.Label(root, text="00:00:00", font=("Helvetica", 24))
        self.timer_label.pack(pady=20)

        # Create buttons for tasks
        self.task_buttons = []
        for i in range(1, 4):  # Add buttons for Task 1, Task 2, Task 3
            button = tk.Button(root, text=f"Start Task {i}", command=lambda i=i: self.toggle_task_timer(f"Task {i}"), font=("Helvetica", 16))
            button.pack(pady=10)
            self.task_buttons.append(button)

        # Create a quit button
        self.quit_button = tk.Button(root, text="Quit", command=root.quit, font=("Helvetica", 16))
        self.quit_button.pack(pady=10)

        # Update the timer
        self.update_timer()

    def toggle_task_timer(self, task_name):
        # If a task is already running, stop it
        if self.running and self.active_task == task_name:
            elapsed_time = time.time() - self.timers[task_name]
            self.save_time(task_name, elapsed_time)
            self.running = False
            self.active_task = None
            self.update_buttons("Start")  # Reset buttons to "Start"
        else:
            # Stop any other running task
            if self.running and self.active_task:
                elapsed_time = time.time() - self.timers[self.active_task]
                self.save_time(self.active_task, elapsed_time)

            # Start the selected task timer
            self.timers[task_name] = time.time()
            self.running = True
            self.active_task = task_name
            self.update_buttons("Stop", task_name)  # Change button to "Stop"

    def update_buttons(self, label, active_task=None):
        # Update all task buttons based on the active task
        for button in self.task_buttons:
            if active_task and button.cget("text").startswith(f"Start {active_task}"):
                button.config(text=f"Stop {active_task}")
            else:
                button.config(text=f"Start {button.cget('text').split()[-1]}")

    def update_timer(self):
        if self.running and self.active_task:
            elapsed_time = time.time() - self.timers[self.active_task]
            self.display_time(elapsed_time)
        self.root.after(100, self.update_timer)

    def display_time(self, elapsed_time):
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)
        self.timer_label.config(text=f"{hours:02}:{minutes:02}:{seconds:02}")

    def save_time(self, task_name, elapsed_time):
        with open("times.txt", "a") as file:
            file.write(f"{task_name}: {elapsed_time:.2f} seconds\n")
        messagebox.showinfo("Time Saved", f"{task_name} - Elapsed time: {elapsed_time:.2f} seconds saved to times.txt")

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskTimerApp(root)
    root.mainloop()

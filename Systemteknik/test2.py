import time
import tkinter as tk
from tkinter import messagebox

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Timer App")

        self.start_time = None
        self.running = False

        # Create a label to display the timer
        self.timer_label = tk.Label(root, text="00:00:00", font=("Helvetica", 24))
        self.timer_label.pack(pady=20)

        # Create a button to start/stop the timer
        self.button = tk.Button(root, text="Start Timer", command=self.toggle_timer, font=("Helvetica", 16))
        self.button.pack(pady=10)

        # Create a quit button
        self.quit_button = tk.Button(root, text="Quit", command=root.quit, font=("Helvetica", 16))
        self.quit_button.pack(pady=10)

        # Update timer display
        self.update_timer()

    def toggle_timer(self):
        if not self.running:
            # Start the timer
            self.start_time = time.time()
            self.running = True
            self.button.config(text="Stop Timer")
        else:
            # Stop the timer and save the time
            elapsed_time = time.time() - self.start_time
            self.running = False
            self.button.config(text="Start Timer")
            self.save_time(elapsed_time)

    def update_timer(self):
        if self.running:
            elapsed_time = time.time() - self.start_time
            self.display_time(elapsed_time)
        self.root.after(100, self.update_timer)

    def display_time(self, elapsed_time):
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)
        self.timer_label.config(text=f"{hours:02}:{minutes:02}:{seconds:02}")

    def save_time(self, elapsed_time):
        with open("times.txt", "a") as file:
            file.write(f"{elapsed_time:.2f} seconds\n")
        messagebox.showinfo("Time Saved", f"Elapsed time: {elapsed_time:.2f} seconds saved to times.txt")

if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()

import time

def start_timer():
    start_time = time.time()
    print("Timer started. Press Enter to stop the timer.")
    
    # Wait for user to stop the timer
    input()
    
    elapsed_time = time.time() - start_time
    print(f"Timer stopped at {elapsed_time:.2f} seconds.")
    return elapsed_time

def save_time_to_file(elapsed_time, filename="times.txt"):
    with open(filename, "a") as file:
        file.write(f"{elapsed_time:.2f} seconds\n")
    print(f"Time saved to {filename}.")

def main():
    while True:
        print("Press 's' to start the timer or 'q' to quit:")
        user_input = input().lower()

        if user_input == 's':
            elapsed_time = start_timer()
            save_time_to_file(elapsed_time)
        elif user_input == 'q':
            print("Exiting...")
            break
        else:
            print("Invalid input, please press 's' to start or 'q' to quit.")

if __name__ == "__main__":
    main()

from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for
from datetime import datetime, timedelta
import os
import csv
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json

app = Flask(
    __name__,
    static_folder=os.path.join('web'),
    template_folder=os.path.join('web')
)

tasks = {}
total_times = {}
removed_tasks = {}

# Add a dictionary to store aliases
task_aliases = {}

# Add a dictionary to store task colors
task_colors = {
    "Task 1": "#FF6384",
    "Task 2": "#36A2EB",
    "Task 3": "#FFCE56",
    "Task 4": "#4BC0C0",
    "Task 5": "#9966FF",
    "Task 6": "#FF9F40"
}

times_file = os.path.join(os.path.dirname(__file__), 'times.csv')
assigned_tasks_file = os.path.join(os.path.dirname(__file__), 'assigned_tasks.csv')


@app.route('/api/last-task')
def last_task():
    with open(times_file, 'r') as f:
        lines = f.readlines()
        last_line = lines[-1] if lines else ''
    return last_line


@app.route('/')
def index():
    # Serve the new index.html from the web folder
    return send_from_directory(app.template_folder, 'index.html')


@app.route('/<path:filename>')
def serve_static_files(filename):
    # Serve other static files (CSS, JS, HTML) from the web folder
    return send_from_directory(app.static_folder, filename)


@app.route('/add_task', methods=['POST'])
def add_task():
    try:
        print("Received request to /add_task")
        data = request.get_json()
        task_slot = data.get('task_slot')  # e.g., "Task 1"
        task_name = data.get('task_name')  # e.g., "My Custom Task"

        if not task_slot or not task_name:
            return jsonify({'message': 'Task slot and task name are required.'}), 400

        print(f"Assigning task: {task_name} to slot: {task_slot}")

        # Check if the task slot already has a task assigned
        if task_slot in tasks:
            print(f"Task slot {task_slot} already has a task assigned.")
            previous_task_name = tasks[task_slot]['name']

            # Calculate total elapsed time for the previous task from times.csv
            total_elapsed_time = 0
            updated_rows = []
            with open(times_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['Task'] == task_slot:
                        elapsed_time_parts = list(map(int, row['Elapsed Time'].split(":")))
                        total_elapsed_time += elapsed_time_parts[0] * 3600 + elapsed_time_parts[1] * 60 + elapsed_time_parts[2]
                    else:
                        updated_rows.append(row)

            # Write back the updated rows to times.csv
            with open(times_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['Task', 'Start Time', 'Stop Time', 'Elapsed Time'])
                writer.writeheader()
                writer.writerows(updated_rows)

            # Transfer the previous task to previous_tasks.csv only if it was removed from times.csv
            if total_elapsed_time > 0:
                elapsed_time_str = str(timedelta(seconds=total_elapsed_time))
                print(f"Transferring task {previous_task_name} to previous_tasks.csv with elapsed time {elapsed_time_str}")

                previous_tasks_file = os.path.join(os.path.dirname(__file__), 'previous_tasks.csv')
                write_header = not os.path.exists(previous_tasks_file)  # Check if the file exists

                try:
                    with open(previous_tasks_file, 'a', newline='') as f:
                        writer = csv.writer(f)
                        if write_header:
                            writer.writerow(['Task', 'Name', 'Elapsed Time'])  # Write the header if the file is new
                        writer.writerow([task_slot, previous_task_name, elapsed_time_str])  # Write the task data
                    print(f"Task {previous_task_name} successfully written to previous_tasks.csv.")
                except Exception as e:
                    print(f"Error writing to previous_tasks.csv: {str(e)}")
            else:
                print(f"Task {previous_task_name} has no tracked time and will not be transferred.")

            # Remove the task from memory
            tasks.pop(task_slot, None)
            total_times.pop(task_slot, None)

        # Assign the new task
        tasks[task_slot] = {'name': task_name, 'start_time': None}
        task_aliases[task_slot] = task_name  # Save the alias
        save_task_aliases()  # <-- Add this line
        print(f"New task {task_name} assigned to slot {task_slot}")
        return jsonify({'message': f'Task {task_name} assigned to {task_slot}.', 'tasks': tasks})

    except Exception as e:
        print(f"Error in /add_task: {str(e)}")
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500


@app.route('/remove_task', methods=['POST'])
def remove_task():
    data = request.get_json()
    task_id = data['task_id']
    if task_id in tasks:
        removed_tasks[task_id] = tasks[task_id]
        del tasks[task_id]
        return jsonify({'message': f'Task with ID {task_id} removed'})
    else:
        return jsonify({'message': 'Task ID not found'}), 400


@app.route('/start_timer', methods=['POST'])
def start_timer():
    data = request.get_json()
    task_id = data['task_id']
    task_name = data['task_name']
    start_time = datetime.now()
    tasks[task_id]['start_time'] = start_time
    return jsonify({'message': f'Timer started for {task_name}', 'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S')})


@app.route('/stop_timer', methods=['POST'])
def stop_timer():
    data = request.get_json()
    task_slot = data.get('task_slot')

    if task_slot not in tasks or tasks[task_slot]['start_time'] is None:
        return jsonify({'message': 'No active timer for this task slot.'}), 400

    start_time = tasks[task_slot]['start_time']
    elapsed_time = (datetime.now() - start_time).total_seconds()
    total_times[task_slot] = total_times.get(task_slot, 0) + elapsed_time

    tasks[task_slot]['start_time'] = None
    print(f"Timer stopped for {task_slot}. Total time: {total_times[task_slot]} seconds.")
    return jsonify({'message': f'Timer stopped for {task_slot}.', 'elapsed_time': elapsed_time})


@app.route('/sort_times', methods=['POST'])
def sort_times():
    all_times = {**total_times, **{task_id: 0 for task_id in removed_tasks if task_id not in total_times}}
    sorted_times = sorted(all_times.items(), key=lambda x: x[1], reverse=True)
    sorted_times_str = '\n'.join([f'{tasks.get(task_id, removed_tasks.get(task_id))["name"]}: {str(timedelta(seconds=time))}' for task_id, time in sorted_times])
    with open(times_file, 'a') as f:
        f.write(f'Sorted times:\n{sorted_times_str}\n\n')
    return jsonify({'message': f'Sorted times:\n{sorted_times_str}'})


@app.route('/get_times', methods=['GET'])
def get_times():
    if not os.path.exists(times_file):
        return jsonify({'message': 'Times file not found'}), 404

    times_data = {}
    try:
        # Read completed sessions from times.csv
        with open(times_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                task_name = row['Task']
                elapsed_time = row['Elapsed Time']
                elapsed_seconds = sum(
                    int(x) * 60 ** i for i, x in enumerate(reversed(elapsed_time.split(':')))
                )
                times_data[task_name] = times_data.get(task_name, 0) + elapsed_seconds

        # **Removed previous_tasks.csv auto-transfer to avoid moving active/unassigned tasks**
        # Transfer of completed tasks should only happen in the assignment or stop endpoints.

    except Exception as e:
        print(f"Error in /get_times: {e}")
        return jsonify({'message': f'Error reading times file: {e}'}), 500

    # Prepare response
    parsed_times = []
    for task, elapsed_seconds in times_data.items():
        assigned_name = tasks.get(task, {}).get('name', task)
        parsed_times.append({
            'task': assigned_name,
            'elapsed_time': str(timedelta(seconds=int(elapsed_seconds)))
        })

    print("Returning times data...")
    return jsonify({'times': parsed_times})



@app.route('/api/times', methods=['GET'])
def get_times_from_csv():
    week = request.args.get('week', type=int)
    if not os.path.exists(times_file):
        return jsonify({'message': 'Times file not found'}), 404

    times_data = []
    try:
        with open(times_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                start_time = datetime.strptime(row['Start Time'], "%Y-%m-%d %H:%M:%S")
                if week and start_time.isocalendar()[1] != week:
                    continue

                task_id = row['Task']
                assigned_name = tasks.get(task_id, {}).get('name', task_id)
                times_data.append({
                    'task': assigned_name,
                    'start_time': row['Start Time'],
                    'stop_time': row['Stop Time'],
                    'elapsed_time': row['Elapsed Time'],
                    'color': task_colors.get(task_id, "#FF0084")
                })
    except Exception as e:
        return jsonify({'message': f'Error reading times file: {str(e)}'}), 500

    return jsonify(times_data)


@app.route('/graph_data')
def graph_data():
    try:
        with open(times_file, 'r') as f:
            lines = f.readlines()

        task_times = {}  # t.ex. {'Task 3 | 2025-04-09': total_seconds}

        current_starts = {}  # håller starttider per task

        for line in lines:
            line = line.strip()
            if "START" in line:
                try:
                    task = line.split(":")[0].strip()
                    time_str = line.split("START :")[1].strip()
                    start_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                    current_starts[task] = start_time
                except Exception:
                    continue

            elif "STOP" in line:
                try:
                    task = line.split(":")[0].strip()
                    time_str = line.split("STOP :")[1].strip()
                    stop_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

                    start_time = current_starts.get(task)
                    if start_time:
                        elapsed = (stop_time - start_time).total_seconds()
                        date = start_time.strftime('%Y-%m-%d')
                        key = f"{task} | {date}"
                        task_times[key] = task_times.get(key, 0) + elapsed
                        del current_starts[task]  # ta bort så vi inte använder den igen
                except Exception:
                    continue

        # Format till frontend-vänlig JSON
        data = [{"label": k, "seconds": v} for k, v in task_times.items()]
        return jsonify(data)

    except FileNotFoundError:
        return jsonify({'message': 'Times file not found'}), 404


@app.route('/get_task_aliases', methods=['GET'])
def get_task_aliases():
    # Return a mapping of task slots to their aliases, default names, and colors
    all_slots = ["Task 1", "Task 2", "Task 3", "Task 4", "Task 5", "Task 6"]
    return jsonify({
        slot: {
            "alias": task_aliases.get(slot, ""),
            "default": slot,
            "color": task_colors[slot]
        }
        for slot in all_slots
    })


@app.route('/get_available_weeks', methods=['GET'])
def get_available_weeks():
    if not os.path.exists(times_file):
        return jsonify([])

    weeks = set()
    try:
        with open(times_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                start_time = datetime.strptime(row['Start Time'], "%Y-%m-%d %H:%M:%S")
                week_number = start_time.isocalendar()[1]
                weeks.add(week_number)
    except Exception as e:
        return jsonify({'message': f'Error reading times file: {str(e)}'}), 500

    return jsonify(sorted(weeks))


@app.route('/generate_pdf', methods=['GET'])
def generate_pdf():
    week = request.args.get('week', type=int)
    if not week:
        return jsonify({'message': 'Week parameter is required'}), 400

    # Filter data for the selected week
    filtered_data = []
    task_summary = {}
    completed_tasks = {}
    try:
        with open(times_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                start_time = datetime.strptime(row['Start Time'], "%Y-%m-%d %H:%M:%S")
                if start_time.isocalendar()[1] == week:
                    filtered_data.append(row)
                    task_name = row['Task']
                    elapsed_time = row['Elapsed Time']
                    # Convert elapsed time to seconds
                    elapsed_seconds = sum(
                        int(x) * 60 ** i for i, x in enumerate(reversed(elapsed_time.split(":")))
                    )
                    task_summary[task_name] = task_summary.get(task_name, 0) + elapsed_seconds
    except Exception as e:
        return jsonify({'message': f'Error reading times file: {str(e)}'}), 500

    # Generate PDF
    pdf_path = f"week_{week}_report.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.drawString(100, 750, f"Time Report for Week {week}")

    # Add task details
    y = 700
    c.setFont("Helvetica", 10)
    for row in filtered_data:
        c.drawString(100, y, f"Task: {row['Task']}, Start: {row['Start Time']}, Stop: {row['Stop Time']}, Elapsed: {row['Elapsed Time']}")
        y -= 15
        if y < 50:  # Create a new page if space runs out
            c.showPage()
            y = 750

    # Add legend with task summary
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, y - 20, "Task Summary:")
    y -= 40
    c.setFont("Helvetica", 10)
    for task, total_seconds in task_summary.items():
        elapsed_time_str = str(timedelta(seconds=total_seconds))
        c.drawString(100, y, f"Task: {task}, Total Time: {elapsed_time_str}")
        y -= 15
        if y < 50:  # Create a new page if space runs out
            c.showPage()
            y = 750

    c.save()

    return send_from_directory(os.getcwd(), pdf_path, as_attachment=True)


@app.route('/api/previous-tasks', methods=['GET'])
def get_previous_tasks():
    previous_tasks_file = os.path.join(os.path.dirname(__file__), 'previous_tasks.csv')
    tasks = []

    if os.path.exists(previous_tasks_file):
        with open(previous_tasks_file, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Skip completely empty or incomplete rows
                if not row.get('Task') or not row.get('Name') or not row.get('Elapsed Time'):
                    continue
                # Skip zero-duration entries
                if row['Elapsed Time'] == "0:00:00":
                    continue

                tasks.append({
                    'task': row['Task'],
                    'name': row['Name'],
                    'elapsed_time': row['Elapsed Time']
                })

    # Dedupe by (task, name, elapsed_time)
    unique_tasks = []
    seen = set()
    for t in tasks:
        key = (t['task'], t['name'], t['elapsed_time'])
        if key not in seen:
            seen.add(key)
            unique_tasks.append(t)

    return jsonify({'tasks': unique_tasks})


def save_task_aliases():
    with open(assigned_tasks_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Task', 'Alias'])
        for slot, alias in task_aliases.items():
            writer.writerow([slot, alias])

def load_task_aliases():
    if os.path.exists(assigned_tasks_file):
        with open(assigned_tasks_file, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                slot = row['Task']
                alias = row['Alias']
                task_aliases[slot] = alias
                # Optionally, also restore to tasks dict:
                if slot not in tasks:
                    tasks[slot] = {'name': alias, 'start_time': None}


# Load aliases from file at startup
load_task_aliases()

if __name__ == '__main__':
    app.run(debug=True)

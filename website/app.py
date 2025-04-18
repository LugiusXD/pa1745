from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime, timedelta
import os
import csv
import pandas as pd
app = Flask(
    __name__,
    static_folder='web',  # Serve static files from the 'web' folder
    template_folder='web'  # Serve HTML files from the 'web' folder
)

tasks = {}
total_times = {}
removed_tasks = {}
times_file = os.path.join(os.path.dirname(__file__), 'times.csv')

# test = False
# times_file = None

# if test:
#     times_file = 'mock_times.csv'
# else:
#     times_file = 'times.csv'

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
    data = request.get_json()
    task_slot = data.get('task_slot')  # e.g., "Task 1"
    task_name = data.get('task_name')  # e.g., "My Custom Task"

    if not task_slot or not task_name:
        return jsonify({'message': 'Task slot and task name are required.'}), 400

    # Update or assign the task name for the given slot
    tasks[task_slot] = {'name': task_name, 'start_time': None}
    return jsonify({'message': f'Task {task_name} assigned to {task_slot}.', 'tasks': tasks})

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
    task_id = data['task_id']
    task_name = data['task_name']
    stop_time = datetime.now()
    start_time = tasks[task_id].get('start_time')
    if start_time:
        elapsed_time = (stop_time - start_time).total_seconds()
        total_times[task_id] = total_times.get(task_id, 0) + elapsed_time
        elapsed_time_str = str(timedelta(seconds=elapsed_time))
        
        # Write to CSV file
        write_header = not os.path.exists(times_file)  # Check if the file exists
        with open(times_file, 'a', newline='') as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(['Task', 'Start Time', 'Stop Time', 'Elapsed Time'])  # Write header
            writer.writerow([task_name, start_time.strftime("%Y-%m-%d %H:%M:%S"), stop_time.strftime("%Y-%m-%d %H:%M:%S"), elapsed_time_str])
        
        tasks[task_id]['start_time'] = None
        return jsonify({
            'message': f'Timer stopped for {task_name}',
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'stop_time': stop_time.strftime('%Y-%m-%d %H:%M:%S'),
            'time': elapsed_time_str
        })
    
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
        with open(times_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                task_name = row['Task']
                elapsed_time = row['Elapsed Time']
                # Convert elapsed time to seconds
                elapsed_seconds = sum(
                    int(x) * 60 ** i for i, x in enumerate(reversed(elapsed_time.split(":")))
                )
                if task_name in times_data:
                    times_data[task_name] += elapsed_seconds
                else:
                    times_data[task_name] = elapsed_seconds

    except Exception as e:
        return jsonify({'message': f'Error reading times file: {str(e)}'}), 500

    # Map task names to their assigned names
    parsed_times = []
    for task, elapsed_time in times_data.items():
        assigned_name = tasks.get(task, {}).get('name', task)  # Use assigned name if available
        parsed_times.append({
            "task": assigned_name,
            "elapsed_time": str(timedelta(seconds=int(elapsed_time)))
        })

    return jsonify({'times': parsed_times})


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


if __name__ == '__main__':
    app.run(debug=True)

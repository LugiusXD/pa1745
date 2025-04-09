from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime, timedelta
import os

app = Flask(
    __name__,
    static_folder='web',  # Serve static files from the 'web' folder
    template_folder='web'  # Serve HTML files from the 'web' folder
)

tasks = {}
total_times = {}
removed_tasks = {}
times_file = 'times.txt'

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

    # Check if the task slot is already assigned
    if task_slot in tasks:
        tasks[task_slot]['name'] = task_name  # Update the task name
        return jsonify({'message': f'Task {task_name} updated in {task_slot}.'})
    
    # Assign a new task to the slot
    tasks[task_slot] = {'name': task_name, 'start_time': None}
    return jsonify({'message': f'Task {task_name} assigned to {task_slot}.'})

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
        with open(times_file, 'a') as f:
            f.write(f'Task: {task_name}\nStart Time: {start_time.strftime("%Y-%m-%d %H:%M:%S")}\nStop Time: {stop_time.strftime("%Y-%m-%d %H:%M:%S")}\nElapsed Time: {elapsed_time_str}\n\n')
        tasks[task_id]['start_time'] = None
        return jsonify({
            'message': f'Timer stopped for {task_name}',
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'stop_time': stop_time.strftime('%Y-%m-%d %H:%M:%S'),
            'time': elapsed_time_str
        })
    else:
        return jsonify({'message': 'No active timer for this task'}), 400

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
    times_data = {}
    try:
        with open(times_file, 'r') as f:
            lines = f.readlines()
            task_name = None
            start_time = None

            for line in lines:
                line = line.strip().strip('"')  # Remove leading/trailing whitespace and quotes
                if "Task" in line and "START" in line:
                    # Extract task name and start time
                    task_name = line.split(":")[0].strip()
                    start_time_str = line.split("START :")[1].strip()
                    start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
                elif "Task" in line and "STOP" in line:
                    # Extract stop time and calculate elapsed time
                    stop_time_str = line.split("STOP :")[1].strip()
                    stop_time = datetime.strptime(stop_time_str, "%Y-%m-%d %H:%M:%S")
                    if start_time:
                        elapsed_time = stop_time - start_time
                        if task_name in times_data:
                            times_data[task_name] += elapsed_time
                        else:
                            times_data[task_name] = elapsed_time
                        start_time = None  # Reset start time for the next interval

            # Convert timedelta to string for each task
            parsed_times = [
                {"task": task, "elapsed_time": str(elapsed_time) if elapsed_time.total_seconds() > 0 else "0:00:01"}
                for task, elapsed_time in times_data.items()
            ]

    except FileNotFoundError:
        return jsonify({'message': 'Times file not found'}), 404

    # Merge parsed times with the `tasks` dictionary
    for task_slot, task_info in tasks.items():
        # Check if the task slot is already in the parsed times
        existing_task = next((t for t in parsed_times if t['task'] == task_slot), None)
        if existing_task:
            # Update the task name if it exists in the parsed times
            existing_task['name'] = task_info['name']
        else:
            # Add the task slot with a default elapsed time if not in parsed times
            parsed_times.append({
                "task": task_slot,
                "elapsed_time": "0:00:00",
                "name": task_info['name']
            })

    return jsonify({'times': parsed_times})

if __name__ == '__main__':
    app.run(debug=True)

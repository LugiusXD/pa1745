from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime, timedelta
import os
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(
    __name__,
    static_folder='web',
    template_folder='web'
)

tasks = {}
total_times = {}
removed_tasks = {}

# Aliases and colors
task_aliases = {}
task_colors = {
    "Task 1": "#FF6384",
    "Task 2": "#36A2EB",
    "Task 3": "#FFCE56",
    "Task 4": "#4BC0C0",
    "Task 5": "#9966FF",
    "Task 6": "#FF9F40"
}

test = True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

times_file = os.path.join(BASE_DIR, 'mock_times.csv') if test else os.path.join(BASE_DIR, 'times.csv')
previous_tasks_file = os.path.join(BASE_DIR, 'previous_tasks.csv')

print("Times file path:", times_file)
print("Previous tasks file path:", previous_tasks_file)

@app.route('/api/last-task')
def last_task():
    if not os.path.exists(times_file):
        return "No times recorded yet.", 404
    with open(times_file, 'r') as f:
        lines = f.readlines()
        last_line = lines[-1] if lines else ''
    return last_line

@app.route('/')
def index():
    return send_from_directory(app.template_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static_files(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/add_task', methods=['POST'])
def add_task():
    data = request.get_json()
    task_slot = data.get('task_slot')
    task_name = data.get('task_name')

    if not task_slot or not task_name:
        return jsonify({'message': 'Task slot and task name are required.'}), 400

    old_name = None
    if task_slot in tasks:
        old_name = tasks[task_slot]['name']

    if old_name and old_name != task_name:
        total_time = calculate_total_time(old_name)

        rows = []
        updated = False

        # Read previous_tasks.csv if exists
        if os.path.exists(previous_tasks_file):
            with open(previous_tasks_file, newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and row[0] == task_slot and row[1] == old_name:
                        row[2] = total_time  # Update time
                        updated = True
                    rows.append(row)

        # If file was empty or no matching row found, add new entry
        if not updated:
            if not rows:
                rows.append(['Task Slot', 'Task Name', 'Total Time'])  # Add header
            rows.append([task_slot, old_name, total_time])

        # Write back updated CSV
        with open(previous_tasks_file, 'w', newline='') as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)

    # Update the assignment
    tasks[task_slot] = {'name': task_name, 'start_time': None}
    task_aliases[task_slot] = task_name

    return jsonify({'message': f'Task {task_name} assigned to {task_slot}.', 'tasks': tasks})

@app.route('/remove_task', methods=['POST'])
def remove_task():
    data = request.get_json()
    task_id = data['task_id']
    if task_id in tasks:
        removed_tasks[task_id] = tasks[task_id]
        del tasks[task_id]
        return jsonify({'message': f'Task {task_id} removed'})
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
        elapsed = (stop_time - start_time).total_seconds()
        total_times[task_id] = total_times.get(task_id, 0) + elapsed
        elapsed_str = str(timedelta(seconds=elapsed))

        write_header = not os.path.exists(times_file)
        with open(times_file, 'a', newline='') as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(['Task', 'Start Time', 'Stop Time', 'Elapsed Time'])
            writer.writerow([task_name, start_time.strftime("%Y-%m-%d %H:%M:%S"),
                             stop_time.strftime("%Y-%m-%d %H:%M:%S"), elapsed_str])

        tasks[task_id]['start_time'] = None
        return jsonify({
            'message': f'Timer stopped for {task_name}',
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'stop_time': stop_time.strftime('%Y-%m-%d %H:%M:%S'),
            'time': elapsed_str
        })

@app.route('/sort_times', methods=['POST'])
def sort_times():
    all_times = {**total_times, **{task_id: 0 for task_id in removed_tasks if task_id not in total_times}}
    sorted_times = sorted(all_times.items(), key=lambda x: x[1], reverse=True)
    sorted_str = '\n'.join([f'{tasks.get(task_id, removed_tasks.get(task_id))["name"]}: {str(timedelta(seconds=time))}'
                            for task_id, time in sorted_times])
    with open(times_file, 'a') as f:
        f.write(f'Sorted times:\n{sorted_str}\n\n')
    return jsonify({'message': f'Sorted times:\n{sorted_str}'})

@app.route('/get_times')
def get_times():
    if not os.path.exists(times_file):
        return jsonify({'message': 'Times file not found'}), 404

    times_data = {}
    try:
        with open(times_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                task = row['Task']
                elapsed = sum(int(x) * 60 ** i for i, x in enumerate(reversed(row['Elapsed Time'].split(":"))))
                times_data[task] = times_data.get(task, 0) + elapsed
    except Exception as e:
        return jsonify({'message': str(e)}), 500

    parsed = []
    for task, secs in times_data.items():
        name = tasks.get(task, {}).get('name', task)
        parsed.append({"task": name, "elapsed_time": str(timedelta(seconds=secs))})

    return jsonify({'times': parsed})

@app.route('/api/times')
def get_times_from_csv():
    week = request.args.get('week', type=int)
    if not os.path.exists(times_file):
        return jsonify({'message': 'Times file not found'}), 404

    data = []
    try:
        with open(times_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                start_time = datetime.strptime(row['Start Time'], "%Y-%m-%d %H:%M:%S")
                if week and start_time.isocalendar()[1] != week:
                    continue

                task_id = row['Task']
                assigned_name = tasks.get(task_id, {}).get('name', task_id)
                data.append({
                    'task': assigned_name,
                    'start_time': row['Start Time'],
                    'stop_time': row['Stop Time'],
                    'elapsed_time': row['Elapsed Time'],
                    'color': task_colors.get(task_id, "#FF0084")
                })
    except Exception as e:
        return jsonify({'message': str(e)}), 500

    return jsonify(data)

@app.route('/api/previous_tasks')
def api_previous_tasks():
    previous = []
    if os.path.exists(previous_tasks_file):
        with open(previous_tasks_file, newline='') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            for row in reader:
                previous.append({
                    "task_id": row[0],
                    "name": row[1],
                    "time": row[2]
                })
    return jsonify(previous)

@app.route('/get_task_aliases')
def get_task_aliases():
    return jsonify({
        slot: {
            "alias": alias,
            "default": slot,
            "color": task_colors[slot]
        }
        for slot, alias in task_aliases.items()
    })

@app.route('/get_available_weeks')
def get_available_weeks():
    if not os.path.exists(times_file):
        return jsonify([])

    weeks = set()
    try:
        with open(times_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                start = datetime.strptime(row['Start Time'], "%Y-%m-%d %H:%M:%S")
                weeks.add(start.isocalendar()[1])
    except:
        pass
    return jsonify(sorted(weeks))

@app.route('/generate_pdf')
def generate_pdf():
    week = request.args.get('week', type=int)
    if not week:
        return jsonify({'message': 'Week required'}), 400

    summary = {}
    rows = []
    with open(times_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            start = datetime.strptime(row['Start Time'], "%Y-%m-%d %H:%M:%S")
            if start.isocalendar()[1] != week:
                continue
            rows.append(row)
            task = row['Task']
            seconds = sum(int(x) * 60 ** i for i, x in enumerate(reversed(row['Elapsed Time'].split(":"))))
            summary[task] = summary.get(task, 0) + seconds

    pdf_path = f"week_{week}_report.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.drawString(100, 750, f"Time Report for Week {week}")

    y = 700
    c.setFont("Helvetica", 10)
    for row in rows:
        c.drawString(100, y, f"{row['Task']}, Start: {row['Start Time']}, Stop: {row['Stop Time']}, Elapsed: {row['Elapsed Time']}")
        y -= 15
        if y < 50:
            c.showPage()
            y = 750

    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, y, "Summary:")
    y -= 20
    c.setFont("Helvetica", 10)
    for task, secs in summary.items():
        c.drawString(100, y, f"{task}: {str(timedelta(seconds=secs))}")
        y -= 15

    c.save()
    return send_from_directory(os.getcwd(), pdf_path, as_attachment=True)

def calculate_total_time(task_name):
    total_seconds = 0
    if os.path.exists(times_file):
        with open(times_file, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Task'] == task_name:
                    h, m, s = map(int, row['Elapsed Time'].split(':'))
                    total_seconds += h * 3600 + m * 60 + s
    return str(timedelta(seconds=total_seconds))

if __name__ == '__main__':
    app.run(debug=True)

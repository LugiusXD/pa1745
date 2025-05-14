document.addEventListener("DOMContentLoaded", function () {
    if (document.querySelector(".banner h1").textContent === "Track Your Time") {
        initializeStartPage();
    }
});

function initializeStartPage() {

    function updateTaskDropdown() {
        fetch('/get_task_aliases')
            .then(response => response.json())
            .then(taskAliases => {
                const taskSlotSelect = document.getElementById("task-slot");
                taskSlotSelect.innerHTML = "";

                const allTaskSlots = ["Task 1", "Task 2", "Task 3", "Task 4", "Task 5", "Task 6"];
                allTaskSlots.forEach(slot => {
                    const option = document.createElement("option");
                    option.value = slot;
                    option.textContent = `${slot} (${taskAliases[slot]?.alias || "Unassigned"})`;
                    taskSlotSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error("Error fetching task aliases:", error);
                alert("An error occurred while updating the task dropdown.");
            });
    }

    updateTaskDropdown();
    updateTimes();
    updatePreviousTasks();

    document.getElementById("assign-task").addEventListener("click", () => {
        const taskSlot = document.getElementById("task-slot").value;
        const taskName = document.getElementById("task-name").value;

        if (!taskName) {
            alert("Please enter a task name.");
            return;
        }

        fetch('/add_task', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task_slot: taskSlot, task_name: taskName })
        })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    alert(data.message);
                    document.getElementById("task-name").value = "";
                    updateTaskDropdown();
                    updateTimes();
                    updatePreviousTasks();
                } else {
                    alert("Failed to assign task.");
                }
            })
            .catch(error => {
                console.error("Error assigning task:", error);
                alert("An error occurred while assigning the task.");
            });
    });

    document.getElementById("update-times").addEventListener("click", () => {
        updateTimes();
        updatePreviousTasks();
    });

    function updateTimes() {
        fetch('/get_times')
            .then(response => response.json())
            .then(data => {
                const tableBody = document.getElementById("times-table-body");
                tableBody.innerHTML = "";

                if (data.times) {
                    data.times.forEach(task => {
                        const row = document.createElement("tr");
                        const taskCell = document.createElement("td");
                        const timeCell = document.createElement("td");

                        taskCell.textContent = task.task;
                        timeCell.textContent = task.elapsed_time;

                        row.appendChild(taskCell);
                        row.appendChild(timeCell);
                        tableBody.appendChild(row);
                    });
                } else {
                    const row = document.createElement("tr");
                    const cell = document.createElement("td");
                    cell.colSpan = 2;
                    cell.textContent = "No times found.";
                    row.appendChild(cell);
                    tableBody.appendChild(row);
                }
            })
            .catch(error => {
                console.error("Error fetching times:", error);
                alert("An error occurred while fetching times.");
            });
    }

    function updatePreviousTasks() {
        fetch('/api/previous_tasks')
            .then(response => response.json())
            .then(previousTasks => {
                const list = document.getElementById("previous-tasks-list");
                list.innerHTML = "";

                previousTasks.forEach(task => {
                    const li = document.createElement("li");
                    li.textContent = `${task.task_id} - ${task.name}: ${task.time}`;
                    li.style.marginBottom = "8px";
                    list.appendChild(li);
                });
            })
            .catch(error => {
                console.error("Error fetching previous tasks:", error);
            });
    }
}

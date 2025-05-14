document.addEventListener("DOMContentLoaded", function () {
    // Check if we are on the start page
    if (document.querySelector(".banner h1").textContent === "Track Your Time") {
        initializeStartPage();
    }
});

function initializeStartPage() {
    // Fetch and populate the task dropdown
    function updateTaskDropdown() {
        fetch('/get_task_aliases')
            .then(response => response.json())
            .then(taskAliases => {
                const taskSlotSelect = document.getElementById("task-slot");
                taskSlotSelect.innerHTML = ""; // Clear existing options

                // Ensure all task slots are present in the dropdown
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

    // Call the function to update the dropdown on page load
    updateTaskDropdown();

    // Assign a task to a slot
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
                } else {
                    alert("Failed to assign task.");
                }

                // Clear the input field
                document.getElementById("task-name").value = "";

                // Update the task dropdown
                updateTaskDropdown();
            })
            .catch(error => {
                console.error("Error assigning task:", error);
                alert("An error occurred while assigning the task.");
            });
    });

    // Update times from server
    document.getElementById("update-times").addEventListener("click", () => {
        fetch('/get_times')
            .then(response => response.json())
            .then(data => {
                if (data.times) {
                    const tableBody = document.getElementById("times-table-body");
                    tableBody.innerHTML = ""; // Clear existing rows
                    data.times.forEach(task => {
                        const row = document.createElement("tr");
                        const taskCell = document.createElement("td");
                        const timeCell = document.createElement("td");

                        taskCell.textContent = task.task; // Task name
                        timeCell.textContent = task.elapsed_time; // Elapsed time

                        row.appendChild(taskCell);
                        row.appendChild(timeCell);
                        tableBody.appendChild(row);
                    });
                } else {
                    alert("No times found.");
                }
            })
            .catch(error => {
                console.error("Error fetching times:", error);
                alert("An error occurred while fetching times.");
            });
    });
}

    // Add a new task
    document.getElementById("add-task").addEventListener("click", () => {
        if (!activeDevice) {
            alert("No device selected.");
            return;
        }
        const taskName = prompt("Enter the name of the new task:");
        if (taskName && !devices[activeDevice].tasks[taskName]) {
            devices[activeDevice].tasks[taskName] = { time: 0 };
            devices[activeDevice].activeTask = taskName;
            updateUI();
        } else {
            alert("Task already exists or invalid name.");
        }
    });

    // Delete the current task
    document.getElementById("delete-task").addEventListener("click", () => {
        if (!activeDevice || !devices[activeDevice].activeTask) {
            alert("No active task to delete.");
            return;
        }
        const taskName = devices[activeDevice].activeTask;
        if (confirm(`Are you sure you want to delete the task "${taskName}"?`)) {
            delete devices[activeDevice].tasks[taskName];
            devices[activeDevice].activeTask = null;
            updateUI();
        }
    });

    // Complete the current task
    document.getElementById("complete-task").addEventListener("click", () => {
        if (!activeDevice || !devices[activeDevice].activeTask) {
            alert("No active task to complete.");
            return;
        }
        const taskName = devices[activeDevice].activeTask;
        const task = devices[activeDevice].tasks[taskName];
        devices[activeDevice].previousTasks.push({ name: taskName, time: task.time });
        delete devices[activeDevice].tasks[taskName];
        devices[activeDevice].activeTask = null;
        updateUI();
    });

    // Cancel the current task
    document.getElementById("cancel-task").addEventListener("click", () => {
        if (!activeDevice || !devices[activeDevice].activeTask) {
            alert("No active task to cancel.");
            return;
        }
        if (confirm("Are you sure you want to cancel the current task?")) {
            devices[activeDevice].activeTask = null;
            updateUI();
        }
    });

    // Update the list of previous tasks
    function updatePreviousTasks() {
        const list = document.getElementById("previous-tasks-list");
        list.innerHTML = "";
        if (!activeDevice) return;

        devices[activeDevice].previousTasks.forEach((task) => {
            const li = document.createElement("li");
            li.textContent = `${task.name} - ${task.time}s`;

            const btn = document.createElement("button");
            btn.textContent = "Continue";
            btn.addEventListener("click", () => {
                devices[activeDevice].tasks[task.name] = { time: task.time };
                devices[activeDevice].activeTask = task.name;
                devices[activeDevice].previousTasks = devices[activeDevice].previousTasks.filter(
                    (t) => t.name !== task.name
                );
                updateUI();
            });

            li.appendChild(btn);
            list.appendChild(li);
        });
    }


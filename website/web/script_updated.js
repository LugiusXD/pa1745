document.addEventListener("DOMContentLoaded", function () {
  // Ensure this only runs on the start page
  if (document.querySelector(".banner h1").textContent === "Track Your Time") {
    initializeStartPage();
  }
});

function initializeStartPage() {
  // --- Update the dropdown list using alias info ---
  function updateTaskDropdown() {
    fetch('/get_task_aliases')
      .then(response => response.json())
      .then(taskAliases => {
        const taskSlotSelect = document.getElementById("task-slot");
        taskSlotSelect.innerHTML = ""; // Clear existing options

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

  // --- Assign a task to a slot ---
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
        alert(data.message || "Failed to assign task.");
        document.getElementById("task-name").value = "";
        updateTaskDropdown();
        updatePreviousTasks();
      })
      .catch(error => {
        console.error("Error assigning task:", error);
        alert("An error occurred while assigning the task.");
      });
  });

  // --- Update times table from backend ---
  document.getElementById("update-times").addEventListener("click", () => {
    fetch('/get_times')
      .then(response => response.json())
      .then(data => {
        if (data.message) {
          alert(data.message);
        } else {
          const tableBody = document.getElementById("times-table-body");
          tableBody.innerHTML = "";

          data.times.forEach(time => {
            const row = document.createElement("tr");
            const taskCell = document.createElement("td");
            const elapsedTimeCell = document.createElement("td");

            taskCell.textContent = time.task;
            elapsedTimeCell.textContent = time.elapsed_time;

            row.appendChild(taskCell);
            row.appendChild(elapsedTimeCell);
            tableBody.appendChild(row);
          });

          updatePreviousTasks();
        }
      })
      .catch(error => {
        console.error("Error updating times:", error);
        alert("An error occurred while updating times.");
      });
  });

  // --- Fetch and display previous tasks as table (NO dropdown or reassign) ---
  function updatePreviousTasks() {
    fetch('/api/previous-tasks')
      .then(response => response.json())
      .then(data => {
        const tableBody = document.getElementById("previous-tasks-body");
        tableBody.innerHTML = "";

        data.tasks.forEach(task => {
          const row = document.createElement("tr");
          const taskCell = document.createElement("td");
          const elapsedTimeCell = document.createElement("td");

          taskCell.textContent = `${task.task} – ${task.name}`;
          elapsedTimeCell.textContent = task.elapsed_time;

          row.appendChild(taskCell);
          row.appendChild(elapsedTimeCell);
          tableBody.appendChild(row);
        });
      })
      .catch(error => {
        console.error("Error fetching previous tasks:", error);
      });
  }

  updatePreviousTasks();

  // --- Highlight active cube side ---
  const taskToSideId = {
    "Task 1": "side1",
    "Task 2": "side2",
    "Task 3": "side3",
    "Task 4": "side4",
    "Task 5": "side5",
    "Task 6": "side6"
  };

  let lastActiveSide = null;

  function updateActiveSide() {
    fetch('/api/last-task')
      .then(response => response.text())
      .then(text => {
        const lines = text.trim().split("\n");
        const lastLine = lines[lines.length - 1];
        const [task] = lastLine.split(",", 3);
        const sideId = taskToSideId[task.trim()];

        if (sideId && sideId !== lastActiveSide) {
          if (lastActiveSide) {
            const oldEl = document.getElementById(lastActiveSide);
            if (oldEl) oldEl.classList.remove("active");
          }

          const newEl = document.getElementById(sideId);
          if (newEl) newEl.classList.add("active");

          lastActiveSide = sideId;
        }

        document.getElementById("active-task-display").textContent = "Active: " + task.trim();
      })
      .catch(error => {
        console.error("Error updating active task:", error);
      });
  }

  updateActiveSide();
  setInterval(updateActiveSide, 2000);
}

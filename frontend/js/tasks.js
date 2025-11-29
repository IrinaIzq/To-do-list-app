const API = "https://irina-todoapp-backend-eug6ghdxh2cra6du.westeurope-01.azurewebsites.net";
const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "index.html";
}

async function loadTasks() {
    const res = await fetch(`${API}/tasks`, {
        headers: { "Authorization": "Bearer " + token }
    });

    const list = document.getElementById("task-list");
    list.innerHTML = "";

    if (!res.ok) {
        list.innerHTML = "<li>Error loading tasks</li>";
        return;
    }

    const tasks = await res.json();

    tasks.forEach(t => {
        const li = document.createElement("li");
        li.textContent = `${t.title} (Priority ${t.priority})`;
        list.appendChild(li);
    });
}

async function createTask() {
    const title = document.getElementById("task-title").value;
    const description = document.getElementById("task-desc").value;
    const priority = parseInt(document.getElementById("task-priority").value);
    const hours = parseInt(document.getElementById("task-hours").value);
    const category = parseInt(document.getElementById("task-category").value);

    const res = await fetch(`${API}/tasks`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({
            title,
            description,
            priority,
            hours,
            category_id: category
        })
    });

    const data = await res.json();
    const msg = document.getElementById("task-msg");

    if (res.ok) {
        msg.textContent = "Task created!";
        loadTasks();
    } else {
        msg.textContent = data.error || "Error creating task";
    }
}

function logout() {
    localStorage.removeItem("token");
    window.location.href = "index.html";
}

// First load
loadTasks();
const API_URL = "http://127.0.0.1:5000";
let token = null;

// Save token in memory and localStorage
function setToken(newToken) {
    token = newToken;
    localStorage.setItem("jwt", newToken);
}

function getToken() {
    if (!token) token = localStorage.getItem("jwt");
    return token;
}

// -------------------- AUTH --------------------

async function register() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const res = await fetch(`${API_URL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await res.json();
    alert(JSON.stringify(data));
}

async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const res = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await res.json();
    if (data.token) {
        setToken(data.token);
        alert("Login successful!");
        loadCategories();
        loadTasks();
    } else {
        alert("Login failed!");
    }
}

function logout() {
    token = null;
    localStorage.removeItem("jwt");
    alert("Logged out!");
}

// -------------------- CATEGORIES --------------------

async function createCategory() {
    const name = document.getElementById("categoryName").value;
    const description = document.getElementById("categoryDescription").value;

    const res = await fetch(`${API_URL}/categories`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "x-access-token": getToken()
        },
        body: JSON.stringify({ name, description })
    });

    const data = await res.json();
    alert(JSON.stringify(data));
    loadCategories();
}

async function loadCategories() {
    const res = await fetch(`${API_URL}/categories`, {
        headers: { "x-access-token": getToken() }
    });
    const categories = await res.json();

    const list = document.getElementById("categoryList");
    list.innerHTML = "";
    categories.forEach(cat => {
        const li = document.createElement("li");
        li.textContent = `${cat.name} - ${cat.description}`;
        list.appendChild(li);
    });
}

// -------------------- TASKS --------------------

async function createTask() {
    const task = {
        title: document.getElementById("taskTitle").value,
        description: document.getElementById("taskDescription").value,
        category: document.getElementById("taskCategory").value,
        estimated_hours: parseInt(document.getElementById("taskHours").value),
        due_date: document.getElementById("taskDueDate").value,
        priority: document.getElementById("taskPriority").value
    };

    const res = await fetch(`${API_URL}/tasks`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "x-access-token": getToken()
        },
        body: JSON.stringify(task)
    });

    const data = await res.json();
    alert(JSON.stringify(data));
    loadTasks();
}

async function loadTasks() {
    const res = await fetch(`${API_URL}/tasks`, {
        headers: { "x-access-token": getToken() }
    });
    const tasks = await res.json();

    const list = document.getElementById("taskList");
    list.innerHTML = "";
    tasks.forEach(t => {
        const li = document.createElement("li");
        li.textContent = `${t.title} (${t.category}) - ${t.status} [${t.priority}]`;
        list.appendChild(li);
    });
}

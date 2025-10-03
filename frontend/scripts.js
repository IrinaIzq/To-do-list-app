const API_URL = "http://127.0.0.1:5000";
let token = null;

// ---------- AUTH ----------
async function login() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const res = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();
  if (res.ok) {
    token = data.token;
    document.getElementById("auth-section").style.display = "none";
    document.getElementById("main-section").style.display = "block";
    loadCategories();
    loadTasks();
  } else {
    alert(data.error || "Login failed");
  }
}

async function register() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const res = await fetch(`${API_URL}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();
  if (res.ok) {
    alert("User registered! Now log in.");
  } else {
    alert(data.error || "Registration failed");
  }
}

// ---------- CATEGORIES ----------
async function createCategory() {
  const name = document.getElementById("categoryName").value;
  const description = document.getElementById("categoryDesc").value;

  if (!name) {
    alert("Category name is required");
    return;
  }

  const res = await fetch(`${API_URL}/categories`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ name, description })
  });

  const data = await res.json();
  if (res.ok) {
    document.getElementById("categoryName").value = "";
    document.getElementById("categoryDesc").value = "";
    loadCategories();
  } else {
    alert(data.error || "Error creating category");
  }
}

async function loadCategories() {
  const res = await fetch(`${API_URL}/categories`, {
    headers: { "Authorization": `Bearer ${token}` }
  });
  const categories = await res.json();
  const list = document.getElementById("categoriesList");
  list.innerHTML = "";
  categories.forEach(c => {
    const li = document.createElement("li");
    li.textContent = `${c.name}: ${c.description || 'No description'}`;
    list.appendChild(li);
  });
}

// ---------- TASKS ----------
async function createTask() {
  const title = document.getElementById("taskTitle").value;
  const description = document.getElementById("taskDesc").value;
  const category_name = document.getElementById("taskCategory").value;

  if (!title) {
    alert("Task title is required");
    return;
  }

  const res = await fetch(`${API_URL}/tasks`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ title, description, category_name })
  });

  const data = await res.json();
  if (res.ok) {
    document.getElementById("taskTitle").value = "";
    document.getElementById("taskDesc").value = "";
    document.getElementById("taskCategory").value = "";
    loadTasks();
  } else {
    alert(data.error || "Error creating task");
  }
}

async function loadTasks() {
  const res = await fetch(`${API_URL}/tasks`, {
    headers: { "Authorization": `Bearer ${token}` }
  });
  const tasks = await res.json();
  const list = document.getElementById("tasksList");
  list.innerHTML = "";
  tasks.forEach(t => {
    const li = document.createElement("li");
    li.textContent = `${t.title} ${t.category ? '(' + t.category + ')' : ''} - ${t.description || 'No description'} - Status: ${t.status}`;
    list.appendChild(li);
  });
}
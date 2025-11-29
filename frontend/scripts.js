const API_URL = window.location.origin;
let token = null;

window.addEventListener('beforeunload', function(e) {
  console.error("⚠️ PAGE IS RELOADING!");
  console.trace();
});

window.addEventListener('load', function() {
  console.log("✅ Page loaded successfully");
  
  document.addEventListener('submit', function(e) {
    console.error("⚠️ Form submit detected - PREVENTED");
    e.preventDefault();
    e.stopPropagation();
    return false;
  });
  
  document.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT')) {
      console.log("Enter key prevented on input");
      e.preventDefault();
      return false;
    }
  });
});

// AUTHENTICATION
async function login() {
  console.log("🔑 Login function called");
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  try {
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
      await loadCategories();
      await loadTasks();
      console.log("✅ Login successful");
    } else {
      alert(data.error || "Login failed");
    }
  } catch (error) {
    alert("Network error: " + error.message);
  }
}

async function register() {
  console.log("📝 Register function called");
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  try {
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
  } catch (error) {
    alert("Network error: " + error.message);
  }
}

function logout() {
  console.log("👋 Logout function called");
  token = null;
  document.getElementById("auth-section").style.display = "block";
  document.getElementById("main-section").style.display = "none";
  document.getElementById("username").value = "";
  document.getElementById("password").value = "";
}

// CATEGORIES 
async function createCategory() {
  console.log("📁 Create category function called");
  const name = document.getElementById("categoryName").value;
  const description = document.getElementById("categoryDesc").value;

  if (!name) {
    alert("Category name is required");
    return;
  }

  try {
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
      await loadCategories();
      console.log("✅ Category created");
    } else {
      alert(data.error || "Error creating category");
    }
  } catch (error) {
    alert("Network error: " + error.message);
  }
}

async function loadCategories() {
  try {
    const res = await fetch(`${API_URL}/categories`, {
      headers: { "Authorization": `Bearer ${token}` }
    });

    if (!res.ok) {
      const data = await res.json();
      if (res.status === 401) {
        alert("Session expired. Please login again.");
        logout();
      }
      return;
    }

    const categories = await res.json();
    const list = document.getElementById("categoriesList");
    list.innerHTML = "";
    
    if (categories.length === 0) {
      list.innerHTML = "<li>No categories yet</li>";
    } else {
      categories.forEach(c => {
        const li = document.createElement("li");
        li.textContent = `${c.name}: ${c.description || 'No description'}`;
        list.appendChild(li);
      });
    }
  } catch (error) {
    console.error("Error loading categories:", error);
  }
}

// TASKS
async function createTask() {
  console.log("📝 Create task function called");
  const title = document.getElementById("taskTitle").value.trim();
  const description = document.getElementById("taskDesc").value;
  const category_name = document.getElementById("taskCategory").value.trim();
  const due_date = document.getElementById("taskDueDate").value;
  const estimated_hours = document.getElementById("taskEstimatedHours").value;
  const priority = document.getElementById("taskPriority").value;

  if (!title) {
    alert("Task title is required");
    return;
  }

  if (!category_name) {
    alert("Category is required");
    return;
  }

  const taskData = {
    title,
    description,
    category_name,
    due_date: due_date || null,
    estimated_hours: estimated_hours ? parseFloat(estimated_hours) : null,
    priority: priority || null
  };

  try {
    const res = await fetch(`${API_URL}/tasks`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify(taskData)
    });

    const data = await res.json();
    if (res.ok) {
      document.getElementById("taskTitle").value = "";
      document.getElementById("taskDesc").value = "";
      document.getElementById("taskCategory").value = "";
      document.getElementById("taskDueDate").value = "";
      document.getElementById("taskEstimatedHours").value = "";
      document.getElementById("taskPriority").value = "";
      await loadTasks();
      console.log("✅ Task created");
    } else {
      alert(data.error || "Error creating task");
    }
  } catch (error) {
    alert("Network error: " + error.message);
  }
}

async function loadTasks() {
  try {
    const res = await fetch(`${API_URL}/tasks`, {
      headers: { "Authorization": `Bearer ${token}` }
    });

    if (!res.ok) {
      const data = await res.json();
      if (res.status === 401) {
        alert("Session expired. Please login again.");
        logout();
      }
      return;
    }

    const tasks = await res.json();
    const list = document.getElementById("tasksList");
    list.innerHTML = "";
    
    if (tasks.length === 0) {
      list.innerHTML = "<li>No tasks yet</li>";
    } else {
      tasks.forEach(t => {
        const li = document.createElement("li");
        if (t.status === "Completed") {
          li.className = "task-completed";
        }
        
        const taskInfo = document.createElement("div");
        taskInfo.className = "task-info";
        
        const taskTitle = document.createElement("div");
        taskTitle.className = "task-title";
        taskTitle.textContent = t.title;
        
        const taskDetails = document.createElement("div");
        taskDetails.className = "task-details";
        let details = [];
        details.push(`Category: ${t.category}`);
        if (t.description) details.push(`Description: ${t.description}`);
        if (t.due_date) details.push(`Due: ${t.due_date}`);
        if (t.estimated_hours) details.push(`Est. Hours: ${t.estimated_hours}`);
        if (t.priority) details.push(`Priority: ${t.priority}`);
        details.push(`Status: ${t.status}`);
        taskDetails.textContent = details.join(" | ");
        
        taskInfo.appendChild(taskTitle);
        taskInfo.appendChild(taskDetails);
        
        const taskActions = document.createElement("div");
        taskActions.className = "task-actions";
        
        if (t.status !== "Completed") {
          const completeBtn = document.createElement("button");
          completeBtn.type = "button";
          completeBtn.textContent = "✓ Complete";
          completeBtn.className = "btn-complete";
          completeBtn.onclick = function(e) {
            if (e) {
              e.preventDefault();
              e.stopPropagation();
            }
            markTaskComplete(t.id);
            return false;
          };
          taskActions.appendChild(completeBtn);
        }
        
        const editBtn = document.createElement("button");
        editBtn.type = "button";
        editBtn.textContent = "✎ Edit";
        editBtn.className = "btn-edit";
        editBtn.onclick = function(e) {
          if (e) {
            e.preventDefault();
            e.stopPropagation();
          }
          openEditModal(t);
          return false;
        };
        taskActions.appendChild(editBtn);
        
        const deleteBtn = document.createElement("button");
        deleteBtn.type = "button";
        deleteBtn.textContent = "✕ Delete";
        deleteBtn.className = "btn-delete";
        deleteBtn.onclick = function(e) {
          if (e) {
            e.preventDefault();
            e.stopPropagation();
          }
          deleteTask(t.id);
          return false;
        };
        taskActions.appendChild(deleteBtn);
        
        li.appendChild(taskInfo);
        li.appendChild(taskActions);
        list.appendChild(li);
      });
    }
  } catch (error) {
    console.error("Error loading tasks:", error);
  }
}

async function markTaskComplete(taskId) {
  console.log("✓ Mark complete function called for task:", taskId);
  try {
    const res = await fetch(`${API_URL}/tasks/${taskId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({ status: "Completed" })
    });

    if (res.ok) {
      await loadTasks();
      console.log("✅ Task marked as complete");
    } else {
      const data = await res.json();
      alert(data.error || "Error completing task");
    }
  } catch (error) {
    alert("Network error: " + error.message);
  }
}

async function deleteTask(taskId) {
  console.log("🗑️ Delete task function called for task:", taskId);
  if (!confirm("Are you sure you want to delete this task?")) {
    return;
  }

  try {
    const res = await fetch(`${API_URL}/tasks/${taskId}`, {
      method: "DELETE",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (res.ok) {
      await loadTasks();
      console.log("✅ Task deleted");
    } else {
      const data = await res.json();
      alert(data.error || "Error deleting task");
    }
  } catch (error) {
    alert("Network error: " + error.message);
  }
}

// EDIT MODAL
function openEditModal(task) {
  console.log("✎ Open edit modal for task:", task.id);
  document.getElementById("editTaskId").value = task.id;
  document.getElementById("editTaskTitle").value = task.title;
  document.getElementById("editTaskDesc").value = task.description || "";
  document.getElementById("editTaskCategory").value = task.category || "";
  document.getElementById("editTaskDueDate").value = task.due_date || "";
  document.getElementById("editTaskEstimatedHours").value = task.estimated_hours || "";
  document.getElementById("editTaskPriority").value = task.priority || "";
  document.getElementById("editTaskStatus").value = task.status;
  
  document.getElementById("editModal").style.display = "block";
}

function closeEditModal() {
  console.log("✕ Close edit modal");
  document.getElementById("editModal").style.display = "none";
}

async function saveTask() {
  console.log("💾 Save task function called");
  const taskId = document.getElementById("editTaskId").value;
  const title = document.getElementById("editTaskTitle").value.trim();
  const description = document.getElementById("editTaskDesc").value;
  const category_name = document.getElementById("editTaskCategory").value.trim();
  const due_date = document.getElementById("editTaskDueDate").value;
  const estimated_hours = document.getElementById("editTaskEstimatedHours").value;
  const priority = document.getElementById("editTaskPriority").value;
  const status = document.getElementById("editTaskStatus").value;

  if (!title) {
    alert("Task title is required");
    return;
  }

  if (!category_name) {
    alert("Category is required");
    return;
  }

  const taskData = {
    title,
    description,
    category_name,
    due_date: due_date || null,
    estimated_hours: estimated_hours ? parseFloat(estimated_hours) : null,
    priority: priority || null,
    status
  };

  try {
    const res = await fetch(`${API_URL}/tasks/${taskId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify(taskData)
    });

    if (res.ok) {
      closeEditModal();
      await loadTasks();
      console.log("✅ Task saved successfully");
    } else {
      const data = await res.json();
      alert(data.error || "Error updating task");
    }
  } catch (error) {
    alert("Network error: " + error.message);
  }
}
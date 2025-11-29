// API base URL - use relative paths since frontend is served by backend
const API_BASE = '';

// Store token in memory (not localStorage in artifacts)
let authToken = null;

// Helper function to make API calls
async function apiCall(endpoint, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };
  
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }
  
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers
  });
  
  return response;
}

// Register function
async function register(username, password) {
  try {
    const response = await apiCall('/register', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      alert('Registration successful! Please login.');
      showLoginForm();
    } else {
      alert(`Error: ${data.error || 'Registration failed'}`);
    }
  } catch (error) {
    console.error('Registration error:', error);
    alert('Network error. Please try again.');
  }
}

// Login function
async function login(username, password) {
  try {
    const response = await apiCall('/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });
    
    const data = await response.json();
    
    if (response.ok && data.token) {
      authToken = data.token;
      alert('Login successful!');
      showMainApp();
      loadCategories();
      loadTasks();
    } else {
      alert(`Error: ${data.error || 'Login failed'}`);
    }
  } catch (error) {
    console.error('Login error:', error);
    alert('Network error. Please try again.');
  }
}

// Load categories
async function loadCategories() {
  try {
    const response = await apiCall('/categories');
    const categories = await response.json();
    
    const categorySelect = document.getElementById('taskCategory');
    if (categorySelect) {
      categorySelect.innerHTML = '<option value="">Select category...</option>';
      categories.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat.id;
        option.textContent = cat.name;
        categorySelect.appendChild(option);
      });
    }
  } catch (error) {
    console.error('Error loading categories:', error);
  }
}

// Load tasks
async function loadTasks() {
  try {
    const response = await apiCall('/tasks');
    const tasks = await response.json();
    
    const tasksList = document.getElementById('tasksList');
    if (tasksList) {
      tasksList.innerHTML = '';
      tasks.forEach(task => {
        const li = document.createElement('li');
        li.className = 'task-item';
        li.innerHTML = `
          <strong>${task.title}</strong>
          <span>Priority: ${task.priority}</span>
          <span>Hours: ${task.estimated_hours || task.hours}</span>
          <span>Status: ${task.status}</span>
        `;
        tasksList.appendChild(li);
      });
    }
  } catch (error) {
    console.error('Error loading tasks:', error);
  }
}

// Create category
async function createCategory(name, description) {
  try {
    const response = await apiCall('/categories', {
      method: 'POST',
      body: JSON.stringify({ name, description })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      alert('Category created!');
      loadCategories();
    } else {
      alert(`Error: ${data.error || 'Failed to create category'}`);
    }
  } catch (error) {
    console.error('Error creating category:', error);
    alert('Network error. Please try again.');
  }
}

// Create task
async function createTask(taskData) {
  try {
    const response = await apiCall('/tasks', {
      method: 'POST',
      body: JSON.stringify(taskData)
    });
    
    const data = await response.json();
    
    if (response.ok) {
      alert('Task created!');
      loadTasks();
    } else {
      alert(`Error: ${data.error || 'Failed to create task'}`);
    }
  } catch (error) {
    console.error('Error creating task:', error);
    alert('Network error. Please try again.');
  }
}

// UI Functions
function showLoginForm() {
  document.getElementById('authSection').style.display = 'block';
  document.getElementById('mainApp').style.display = 'none';
  document.getElementById('registerForm').style.display = 'none';
  document.getElementById('loginForm').style.display = 'block';
}

function showRegisterForm() {
  document.getElementById('authSection').style.display = 'block';
  document.getElementById('mainApp').style.display = 'none';
  document.getElementById('loginForm').style.display = 'none';
  document.getElementById('registerForm').style.display = 'block';
}

function showMainApp() {
  document.getElementById('authSection').style.display = 'none';
  document.getElementById('mainApp').style.display = 'block';
}

function logout() {
  authToken = null;
  showLoginForm();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  // Check health endpoint
  fetch('/health')
    .then(r => r.json())
    .then(data => {
      console.log('Backend health:', data);
    })
    .catch(e => {
      console.error('Backend connection failed:', e);
      alert('Cannot connect to backend');
    });
  
  // Setup login form
  const loginBtn = document.getElementById('loginBtn');
  if (loginBtn) {
    loginBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const username = document.getElementById('loginUsername').value;
      const password = document.getElementById('loginPassword').value;
      login(username, password);
    });
  }
  
  // Setup register form
  const registerBtn = document.getElementById('registerBtn');
  if (registerBtn) {
    registerBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const username = document.getElementById('registerUsername').value;
      const password = document.getElementById('registerPassword').value;
      register(username, password);
    });
  }
  
  // Setup show register link
  const showRegisterLink = document.getElementById('showRegister');
  if (showRegisterLink) {
    showRegisterLink.addEventListener('click', (e) => {
      e.preventDefault();
      showRegisterForm();
    });
  }
  
  // Setup show login link
  const showLoginLink = document.getElementById('showLogin');
  if (showLoginLink) {
    showLoginLink.addEventListener('click', (e) => {
      e.preventDefault();
      showLoginForm();
    });
  }
  
  // Setup category form
  const createCategoryBtn = document.getElementById('createCategoryBtn');
  if (createCategoryBtn) {
    createCategoryBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const name = document.getElementById('categoryName').value;
      const description = document.getElementById('categoryDescription').value;
      createCategory(name, description);
    });
  }
  
  // Setup task form
  const createTaskBtn = document.getElementById('createTaskBtn');
  if (createTaskBtn) {
    createTaskBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const taskData = {
        title: document.getElementById('taskTitle').value,
        description: document.getElementById('taskDescription').value,
        category_id: parseInt(document.getElementById('taskCategory').value),
        priority: document.getElementById('taskPriority').value,
        estimated_hours: parseFloat(document.getElementById('taskHours').value) || 0,
        due_date: document.getElementById('taskDueDate').value
      };
      createTask(taskData);
    });
  }
  
  // Setup logout button
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', logout);
  }
  
  // Show login form by default
  showLoginForm();
});
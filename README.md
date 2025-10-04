# To-Do List Manager

A simple task manager application that allows users to create, organize, and prioritize tasks.  
Each task includes a title, description, category, due date, estimated hours, and status.  
The app is built with **Python (Flask) for the backend**, **SQLite for persistent storage**, and **HTML/CSS/JavaScript for the frontend**.  

---

## Features
- Create, read, update, and delete (CRUD) tasks and categories
- User authentication with JWT tokens
- Assign mandatory categories to group tasks (e.g., Work, Personal, Study)
- Add estimated hours, due dates, and priority levels to tasks
- Mark tasks as completed
- Tasks automatically sorted by: Due Date → Priority (High → Medium → Low) → Estimated Hours (High → Low)
- Store all data persistently in an SQLite database
- Simple web interface with forms and task lists.

---

## Tech Stack
- **Backend:** Python (Flask), Flask-SQLAlchemy, Flask-CORS, PyJWT
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript
- **Version Control:** Git & GitHub

---

## Project Structure
todo-list-app/
│
├── backend/                 # Backend logic
│   ├── app.py              # Main entry point (Flask server)
│   ├── database.py         # Database models and setup
│   ├── routes.py           # Flask routes for CRUD operations
│   └── utils.py            # Helper functions (JWT tokens)
│
├── frontend/               # Frontend files
│   ├── index.html         # Main page (task list and forms)
│   ├── styles.css         # Styles for the interface
│   └── scripts.js         # JavaScript for dynamic behavior
│
├── data/                   # Data folder
│   └── tasks.db           # SQLite database file (auto-generated)
│
├── docs/                   # Documentation
│   ├── schema.png         # UML/architecture diagram
│   └── report.pdf          # Report text
│
├── tests/                  # Automated tests
│   └── test_tasks.py      # Unit tests
│
├── requirements.txt        # Project dependencies
├── .gitignore             # Files and folders to ignore in Git
└── README.md              # Project instructions

---

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR-USERNAME/todo-list-app.git
   cd todo-list-app

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Mac/Linux
   venv\Scripts\activate      # Windows

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt

6. **Run the backend**
   ```bash
   python backend/app.py
The Flask backend will start on http://127,0.0.1:5000
Keep his terminal open while using the application.

8. **Open the frontend**
   ```bash
   cd frontend
   python -m http.server 8000
The frontend will be available at http://localhost:8000
*Important:* Do NOT use VS Code Live Server as it can cause page reload issues. Use the Python HTTP server as shown above.

9. **Access the application**
   Open your web browser and navigate to: http://localhost:8000
  
---

## Usage
1. **Creating categories**
   - After logging in, use the "Create Category" section
   - Enter a category name (required) and optional description
   - Click "Add Category"
  
2. **Creating tasks**
   - Use the "Create Task" section
   - Fill in:
      · Task Title (required)
      · Description (optional)
      · Category (required) - must match an existing category name
      · Due Date (optional)
      · Estimated Hours (optional)
      · Priority (optional): Low, Medium, or High
   - Click "Add Task"
  
3.. **Managing tasks**
   - Complete a task: Click the "Complete" button
   - Edit a task: Click the "Edit" button to open the edit modal
   - Delete a task: Click the "Delete" button (with confirmation)

4. **Task sorting**
   Tasks are automatically sorted by:
   1.  Due Date (earliest first, tasks without dates appear last)
   2. Priority (High → Medium → Low → No priority)
   3. Estimated Hours (highest to lowest)

---

## Requirements
- Python 3.10+
- pip 

---

## Dependencies
The following Python packages are required (see requirements.txt):
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-CORS==4.0.0
PyJWT==2.8.0
Werkzeug==3.0.1

---

## License
This project is for educational purposes.

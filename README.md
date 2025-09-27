# To-Do List Manager

A simple task manager application that allows users to create, organize, and prioritize tasks.  
Each task includes a title, description, category, due date, estimated hours, and status.  
The app is built with **Python (Flask) for the backend**, **SQLite for persistent storage**, and **HTML/CSS/JavaScript for the frontend**.  

---

## Features
- Create, read, update, and delete (CRUD) tasks.
- Assign categories to group tasks (e.g., Work, Personal, Study).
- Add estimated hours to tasks and calculate total workload.
- Prioritize tasks based on due dates and estimated hours.
- Store all data persistently in an SQLite database.
- Simple web interface with forms and task lists.

---

## Tech Stack
- **Backend:** Python (Flask)
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript
- **Version Control:** Git & GitHub

---

## Project Structure
todo-list-app/
│
├── backend/ # Backend logic
│ ├── app.py # Main entry point (Flask server)
│ ├── database.py # Database connection and setup
│ ├── models.py # Database schema and queries
│ ├── routes.py # Flask routes for CRUD operations
│ └── utils.py # Helper functions (e.g., prioritization)
│
├── frontend/ # Frontend files
│ ├── index.html # Main page (task list and forms)
│ ├── styles.css # Styles for the interface
│ └── scripts.js # JavaScript for dynamic behavior
│
├── data/ # Data folder
│ └── tasks.db # SQLite database file
│
├── docs/ # Documentation
│ ├── schema.png # UML/architecture diagram
│ └── report.md # Report text
│
├── tests/ # Automated tests
│ └── test_tasks.py # Unit tests
│
├── requirements.txt # Project dependencies
├── .gitignore # Files and folders to ignore in Git
└── README.md # Project instructions

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

8. **Open the frontend**
   Open frontend/index.html directly in your browser. The frontend will communicate with the Flask backend.
  
---

## Requirements
- Python 3.10+
- pip 

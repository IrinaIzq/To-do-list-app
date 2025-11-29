const API = "https://irina-todoapp-backend-eug6ghdxh2cra6du.westeurope-01.azurewebsites.net";

async function login() {
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    const res = await fetch(`${API}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await res.json();
    const msg = document.getElementById("msg");

    if (res.ok) {
        localStorage.setItem("token", data.token);
        window.location.href = "tasks.html";
    } else {
        msg.textContent = data.error || "Login failed";
    }
}

async function registerUser() {
    const username = document.getElementById("register-username").value;
    const password = document.getElementById("register-password").value;

    const res = await fetch(`${API}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await res.json();
    const msg = document.getElementById("msg");

    if (res.ok) {
        msg.textContent = "Registered successfully! Now login.";
    } else {
        msg.textContent = data.error || "Registration failed";
    }
}

// If already logged in → redirect
if (localStorage.getItem("token") && window.location.pathname.endsWith("index.html")) {
    window.location.href = "tasks.html";
}
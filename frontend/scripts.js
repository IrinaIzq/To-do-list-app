// URL del backend Flask en Azure
const API_URL = "https://irina-todoapp-backend-eug6ghdxh2cra6du.westeurope-01.azurewebsites.net";

// Cargar estado inicial
async function load() {
  try {
    const res = await fetch(`${API_URL}/api/hello`);
    const data = await res.json();
    document.getElementById("status").innerText =
      `Backend: ${data.version}`;
  } catch (e) {
    document.getElementById("status").innerText =
      "No se pudo conectar al backend";
  }
}

// Añadir una nueva tarea
document.getElementById("add").addEventListener("click", async () => {
  const title = document.getElementById("newtask").value;
  if (!title) return;

  const res = await fetch(`${API_URL}/api/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title })
  });

  const item = await res.json();
  const li = document.createElement("li");
  li.textContent = item.title;

  document.getElementById("tasks").appendChild(li);

  document.getElementById("newtask").value = "";
});

load();
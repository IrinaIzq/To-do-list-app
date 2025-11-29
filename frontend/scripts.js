async function load() {
  try {
    // Endpoint '/api/hello' puede no existir; intentamos el endpoint base y /health
    let res;
    try {
      res = await fetch('/api/hello');
      if (!res.ok) throw new Error('no /api/hello');
    } catch (e) {
      res = await fetch('/health');
    }

    const data = await res.json();
    // si la respuesta de /health tiene 'version' o 'status'
    const version = data.version || data.APP_VERSION || data.status || 'unknown';
    document.getElementById('status').innerText = `Backend: ${version}`;
  } catch (e) {
    document.getElementById('status').innerText = 'No se pudo conectar al backend';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  load();

  const addBtn = document.getElementById('add');
  if (addBtn) {
    addBtn.addEventListener('click', async () => {
      const titleEl = document.getElementById('newtask');
      const title = titleEl ? titleEl.value.trim() : '';
      if (!title) return;
      try {
        const res = await fetch('/tasks', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({title})
        });
        if (!res.ok) {
          alert('Error al crear tarea');
          return;
        }
        const item = await res.json();
        const li = document.createElement('li');
        li.textContent = item.title || JSON.stringify(item);
        const list = document.getElementById('tasks');
        if (list) list.appendChild(li);
        if (titleEl) titleEl.value = '';
      } catch (e) {
        alert('No se pudo conectar al backend');
      }
    });
  }
});
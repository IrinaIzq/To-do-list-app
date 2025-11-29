async function load() {
  try {
    const res = await fetch('/api/hello');
    const data = await res.json();
    document.getElementById('status').innerText = `Backend: ${data.version}`;
  } catch(e) {
    document.getElementById('status').innerText = 'No se pudo conectar al backend';
  }
}

document.getElementById('add').addEventListener('click', async () => {
  const title = document.getElementById('newtask').value;
  if(!title) return;
  const res = await fetch('/api/tasks', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({title})
  });
  const item = await res.json();
  const li = document.createElement('li');
  li.textContent = item.title;
  document.getElementById('tasks').appendChild(li);
  document.getElementById('newtask').value = '';
});

load();
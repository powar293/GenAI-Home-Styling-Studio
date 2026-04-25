
function showToast(msg, type) {
  const c = document.getElementById('toast-container');
  const d = document.createElement('div');
  d.className = 'toast toast-' + (type || 'info');
  d.textContent = msg;
  c.appendChild(d);
  setTimeout(() => d.remove(), 3500);
}
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('collapsed');
}

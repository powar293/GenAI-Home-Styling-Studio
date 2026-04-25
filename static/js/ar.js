
let arStream = null, arItems = [], selectedItem = null;
const video = () => document.getElementById('ar-video');
const canvas = () => document.getElementById('ar-canvas');

function startAR() {
  navigator.mediaDevices.getUserMedia({video: {facingMode:'environment'}})
    .then(s => {
      arStream = s;
      video().srcObject = s;
      document.getElementById('ar-start-prompt').style.display = 'none';
      resizeCanvas();
      requestAnimationFrame(drawAR);
    }).catch(() => showToast('Camera access denied', 'error'));
}

function resizeCanvas() {
  const v = video(), c = canvas();
  c.width = v.offsetWidth; c.height = v.offsetHeight;
}

const ICONS = {'Seating':'🛋️','Tables':'🪑','Lighting':'💡','Storage':'📚','Bedroom':'🛏️','Decor':'🌿'};

function drawAR() {
  const c = canvas(), ctx = c.getContext('2d');
  ctx.clearRect(0, 0, c.width, c.height);
  arItems.forEach(item => {
    ctx.save();
    ctx.font = `${item.size}px serif`;
    ctx.textAlign = 'center';
    ctx.fillText(item.icon, item.x, item.y);
    ctx.font = '14px sans-serif';
    ctx.fillStyle = 'rgba(255,255,255,0.9)';
    ctx.fillRect(item.x - 60, item.y + 5, 120, 22);
    ctx.fillStyle = '#111';
    ctx.fillText(item.name, item.x, item.y + 20);
    ctx.restore();
  });
  if (arStream) requestAnimationFrame(drawAR);
}

function placeItem(name, cat, price) {
  const c = canvas();
  const item = {
    id: Date.now(), name, cat, price,
    icon: ICONS[cat] || '🪑',
    x: 100 + Math.random() * (c.width - 200),
    y: 100 + Math.random() * (c.height - 200),
    size: 60
  };
  arItems.push(item);
  selectedItem = item;
  showSelectedInfo(item);
  showToast(`${name} placed!`, 'success');
}

function showSelectedInfo(item) {
  const el = document.getElementById('ar-selected-info');
  el.style.display = 'block';
  el.innerHTML = `<strong>${item.name}</strong> — ₹${item.price.toLocaleString('en-IN')}`;
}

function arClearAll() { arItems = []; selectedItem = null; document.getElementById('ar-selected-info').style.display='none'; }

async function arBookSelected() {
  if (!selectedItem) { showToast('Select an item first', 'error'); return; }
  const res = await fetch('/api/furniture');
  const items = await res.json();
  const found = items.find(i => i.name.toLowerCase().includes(selectedItem.name.split(' ')[0].toLowerCase()));
  if (!found) { showToast('Item not in catalog', 'error'); return; }
  const r = await fetch('/api/book', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({furniture_id: found.id})});
  const d = await r.json();
  showToast(d.message || '✅ Booked!', d.success ? 'success' : 'error');
}

function arSnapshot() {
  const c = canvas(), v = video();
  const tmp = document.createElement('canvas');
  tmp.width = v.videoWidth || c.width; tmp.height = v.videoHeight || c.height;
  const ctx = tmp.getContext('2d');
  ctx.drawImage(v, 0, 0, tmp.width, tmp.height);
  arItems.forEach(item => {
    ctx.font = `${item.size}px serif`; ctx.textAlign = 'center';
    ctx.fillText(item.icon, item.x, item.y);
  });
  const url = tmp.toDataURL('image/jpeg');
  document.getElementById('snapshot-img').src = url;
  document.getElementById('snapshot-dl').href = url;
  document.getElementById('ar-snapshot-preview').classList.remove('hidden');
}

// Drag on canvas
let dragging = null, dragOffX = 0, dragOffY = 0;
document.addEventListener('DOMContentLoaded', () => {
  const c = canvas();
  c.addEventListener('mousedown', e => {
    const r = c.getBoundingClientRect();
    const mx = e.clientX - r.left, my = e.clientY - r.top;
    dragging = [...arItems].reverse().find(i => Math.abs(i.x-mx)<40 && Math.abs(i.y-my)<40);
    if (dragging) { dragOffX = mx - dragging.x; dragOffY = my - dragging.y; selectedItem = dragging; showSelectedInfo(dragging); }
  });
  c.addEventListener('mousemove', e => {
    if (!dragging) return;
    const r = c.getBoundingClientRect();
    dragging.x = e.clientX - r.left - dragOffX;
    dragging.y = e.clientY - r.top - dragOffY;
  });
  c.addEventListener('mouseup', () => dragging = null);
  window.addEventListener('resize', resizeCanvas);
});

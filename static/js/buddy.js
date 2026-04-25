
function addMessage(text, role, extra) {
  const c = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = `message ${role}-message`;
  const time = new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
  let body = `<div class="msg-text">${text}</div>`;
  if (extra && extra.booking_confirmed && extra.furniture) {
    body += `<div class="booking-card-mini">
      <div>📦 <strong>${extra.furniture.name}</strong> — ₹${Number(extra.furniture.price).toLocaleString('en-IN')}</div>
      <div class="status-confirmed">✅ Booked Successfully!</div>
    </div>`;
  }
  if (extra && extra.intent === 'view_bookings') {
    body += `<a href="/bookings" class="btn-sm" style="margin-top:8px;display:inline-block;">📋 View Bookings</a>`;
  }
  div.innerHTML = (role === 'bot' ? '<div class="msg-avatar">🤖</div>' : '<div class="msg-avatar user-av">👤</div>') +
    `<div class="msg-body">${body}<div class="msg-time">${time}</div></div>`;
  c.appendChild(div);
  c.scrollTop = c.scrollHeight;
}

function showTyping(v) {
  document.getElementById('typing').classList.toggle('hidden', !v);
  const c = document.getElementById('chat-messages');
  c.scrollTop = c.scrollHeight;
}

async function sendMessage() {
  const inp = document.getElementById('chat-input');
  const msg = inp.value.trim();
  if (!msg) return;
  inp.value = '';
  addMessage(msg, 'user');
  showTyping(true);
  try {
    const r = await fetch('/api/buddy/chat', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({message: msg, lang: currentLang})
    });
    const d = await r.json();
    showTyping(false);
    addMessage(d.response || 'Sorry, I could not understand.', 'bot', d);
    if (d.response) speakText(d.response);
  } catch(e) {
    showTyping(false);
    addMessage('Connection error. Please try again.', 'bot');
  }
}

function sendQuick(msg) {
  document.getElementById('chat-input').value = msg;
  sendMessage();
}

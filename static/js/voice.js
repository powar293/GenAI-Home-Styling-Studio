
let currentLang = 'en', sarvamLang = 'en-IN';
let mediaRecorder = null, audioChunks = [];

function setLang(btn) {
  document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  currentLang = btn.dataset.lang;
  sarvamLang = btn.dataset.sarvam;
}

async function toggleVoice() {
  const btn = document.getElementById('mic-btn');
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop();
    btn.textContent = '🎙️'; btn.classList.remove('recording');
    return;
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({audio: true});
    audioChunks = [];
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
    mediaRecorder.onstop = async () => {
      stream.getTracks().forEach(t => t.stop());
      const blob = new Blob(audioChunks, {type: 'audio/wav'});
      const fd = new FormData();
      fd.append('audio', blob, 'voice.wav');
      fd.append('lang', sarvamLang);
      showToast('Processing voice…', 'info');
      try {
        const r = await fetch('/api/voice/stt', {method:'POST', body: fd});
        const d = await r.json();
        if (d.success && d.transcript) {
          document.getElementById('chat-input').value = d.transcript;
          sendMessage();
        } else showToast('Could not understand. Try again.', 'error');
      } catch(e) { showToast('Voice error', 'error'); }
    };
    mediaRecorder.start();
    btn.textContent = '⏹️'; btn.classList.add('recording');
    showToast('Recording… Click ⏹️ to stop', 'info');
  } catch(e) { showToast('Microphone access denied', 'error'); }
}

async function speakText(text) {
  try {
    const r = await fetch('/api/voice/tts', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({text, lang: sarvamLang})
    });
    const d = await r.json();
    if (d.success && d.audio) {
      const bytes = atob(d.audio);
      const buf = new Uint8Array(bytes.length);
      for (let i = 0; i < bytes.length; i++) buf[i] = bytes.charCodeAt(i);
      const blob = new Blob([buf], {type:'audio/wav'});
      const url = URL.createObjectURL(blob);
      new Audio(url).play();
    }
  } catch(e) { console.warn('TTS error', e); }
}

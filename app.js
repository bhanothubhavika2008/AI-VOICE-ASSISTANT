const input = document.getElementById('transcript');
const micButton = document.getElementById('micButton');
const micLabel = document.getElementById('micLabel');
const statusBadge = document.getElementById('statusBadge');
const resultBox = document.getElementById('result');
const historyBox = document.getElementById('history');
const wave = document.getElementById('wave');
let historyItems = [];

function showResult(message, kind='') {
  resultBox.textContent = message;
  resultBox.className = 'result' + (kind ? ' ' + kind : '');
}
function setBusy(busy, label='READY') {
  statusBadge.textContent = busy ? 'WORKING' : label;
  statusBadge.classList.toggle('busy', busy);
}
function renderHistory() {
  if (!historyItems.length) { historyBox.innerHTML = '<div class="empty">Your executed commands will appear here.</div>'; return; }
  historyBox.innerHTML = historyItems.map(item => `<div class="history-item"><div class="history-icon">${item.ok ? '✓' : '!'}</div><div><strong>${escapeHtml(item.command)}</strong><small>${escapeHtml(item.message)} · ${item.time}</small></div><span class="mark ${item.ok ? '' : 'fail'}">${item.ok ? 'DONE' : 'FAILED'}</span></div>`).join('');
}
function escapeHtml(value) { return String(value).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch])); }
async function runCommand(command) {
  const clean = String(command || '').trim();
  if (!clean) { showResult('Enter a command first.', 'error'); return; }
  input.value = clean;
  setBusy(true);
  showResult('Sending command to your local PC…');
  try {
    const response = await fetch('/api/command', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({command:clean})});
    const data = await response.json();
    showResult(data.message || 'No response received.', data.ok ? 'success' : 'error');
    historyItems.unshift({command:clean, message:data.message || '', ok:!!data.ok, time:new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit',second:'2-digit'})});
    historyItems = historyItems.slice(0,30); renderHistory();
    setBusy(false, data.ok ? 'ACTION COMPLETE' : 'NOT EXECUTED');
  } catch (error) {
    showResult('Cannot reach the local Python backend. Make sure app.py is running at 127.0.0.1:5000.', 'error');
    setBusy(false, 'BACKEND OFFLINE');
  }
}
document.getElementById('runButton').addEventListener('click', () => runCommand(input.value));
input.addEventListener('keydown', e => { if (e.key === 'Enter') runCommand(input.value); });
document.querySelectorAll('[data-command]').forEach(button => button.addEventListener('click', () => runCommand(button.dataset.command)));
document.getElementById('clearHistory').addEventListener('click', () => { historyItems = []; renderHistory(); });

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
if (SpeechRecognition) {
  recognition = new SpeechRecognition();
  recognition.lang = 'en-IN';
  recognition.interimResults = true;
  recognition.continuous = false;
  recognition.onstart = () => { micButton.classList.add('listening'); wave.classList.add('active'); micLabel.textContent = 'Listening…'; setBusy(true, 'LISTENING'); showResult('Listening. Speak one supported command.'); };
  recognition.onresult = event => {
    let finalText = '';
    let interim = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      if (event.results[i].isFinal) finalText += event.results[i][0].transcript;
      else interim += event.results[i][0].transcript;
    }
    input.value = finalText || interim;
    if (finalText.trim()) runCommand(finalText.trim());
  };
  recognition.onerror = event => {
    const messages = { 'not-allowed':'Microphone permission was denied. Allow microphone access for localhost in your browser.', 'network':'Online speech recognition failed. Check your internet connection.', 'no-speech':'No speech detected. Try again and speak clearly.' };
    showResult(messages[event.error] || `Speech recognition error: ${event.error}`, 'error');
  };
  recognition.onend = () => { micButton.classList.remove('listening'); wave.classList.remove('active'); micLabel.textContent = 'Start listening'; if (statusBadge.textContent === 'LISTENING') setBusy(false, 'READY'); };
  micButton.addEventListener('click', () => { try { recognition.start(); } catch (_) { showResult('Voice recognition is already active. Wait a moment and try again.', 'error'); } });
} else {
  micButton.disabled = true;
  micLabel.textContent = 'Speech recognition unavailable';
  document.getElementById('hint').textContent = 'This browser does not expose Web Speech Recognition. Try a recent Chrome or Edge browser; typed commands still execute through the local backend.';
  micButton.style.opacity = '.55';
}
fetch('/api/status').then(r => r.json()).then(data => { if (data.ok) document.querySelector('.local-pill').innerHTML = `<i></i> LOCAL ${escapeHtml(data.os.toUpperCase())} CONNECTED`; }).catch(() => { setBusy(false, 'BACKEND OFFLINE'); });

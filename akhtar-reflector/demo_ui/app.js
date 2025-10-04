const api = "http://localhost:7860";
let sessionId = null;

async function newSession() {
  const res = await fetch(`${api}/api/session/new`, { method: "POST" });
  const { id } = await res.json();
  sessionId = id;
  document.getElementById('conversation').innerHTML = '';
  document.getElementById('rds').textContent = '–';
  document.getElementById('tabove').textContent = '0 turns';
}

async function ensureSession() {
  if (!sessionId) await newSession();
}

function renderTurn(user, bot){
  const c = document.getElementById('conversation');
  c.insertAdjacentHTML('beforeend', `<div class="u">You: ${escapeHtml(user)}</div><div class="b">Reflector: ${escapeHtml(bot)}</div>`);
  c.scrollTop = c.scrollHeight;
}

function escapeHtml(s){ return s.replace(/[&<>]/g, c=>({ '&':'&amp;','<':'&lt;','>':'&gt;' }[c])); }

async function sendTurn(){
  await ensureSession();
  const text = document.getElementById('userText').value.trim();
  const depth = +document.getElementById('depth').value;
  const mem = document.getElementById('mem').checked;
  const pause = document.getElementById('pause').checked;
  const safety = document.getElementById('safety').checked;
  if (!text) return;

  const res = await fetch(`${api}/api/respond`, {
    method:"POST", headers:{ "Content-Type":"application/json" },
    body: JSON.stringify({ session_id: sessionId, text, depth, mem, pause, safety })
  });
  const data = await res.json();
  renderTurn(text, data.reply);

  const m = await (await fetch(`${api}/api/metrics/${sessionId}`)).json();
  document.getElementById('rds').textContent = m.rds_window.toFixed(2);
  document.getElementById('tabove').textContent = `${m.turns_above_tau} turns`;
  document.getElementById('userText').value = '';
  document.getElementById('userText').focus();
}

async function exportSession(){
  if (!sessionId) return;
  const res = await fetch(`${api}/api/session/${sessionId}`);
  const blob = new Blob([JSON.stringify(await res.json(), null, 2)], { type:'application/json' });
  const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: `session_${sessionId}.json` });
  a.click();
}

document.getElementById('send').onclick = sendTurn;
document.getElementById('export').onclick = exportSession;
document.getElementById('new').onclick = newSession;

newSession();

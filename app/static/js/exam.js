const data = window.__EXAM_DATA__;
let idx = 0;
let remaining = data.remaining;
let enterTs = Date.now();

function current() { return data.answers[idx]; }

function renderGrid() {
  const grid = document.getElementById('questionGrid');
  grid.innerHTML = '';
  data.answers.forEach((a, i) => {
    const b = document.createElement('button');
    b.className = 'btn btn-sm m-1 ' + (i === idx ? 'btn-primary' : a.marked ? 'btn-warning' : hasAnswer(a) ? 'btn-success' : a.visited ? 'btn-secondary' : 'btn-light border');
    b.innerText = i + 1;
    b.title = `${a.question_id}`;
    b.setAttribute('aria-label', `Question ${i+1} ${i===idx?'current':a.marked?'marked for review':hasAnswer(a)?'answered':a.visited?'visited unanswered':'unvisited'}`);
    b.onclick = () => { saveAndGo(i); };
    grid.appendChild(b);
  });
}

function hasAnswer(a) {
  return Array.isArray(a.selected) ? a.selected.length > 0 : a.selected !== null && a.selected !== undefined && a.selected !== '';
}

function renderQuestion() {
  const q = current();
  q.visited = true;
  fetch('/api/visit', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({question_id:q.question_id})});
  let html = `<div class="card"><div class="card-body"><h5>Q${idx+1}. ${q.text}</h5>`;
  if (q.type === 'single_choice' || q.type === 'true_false') {
    q.options.forEach(opt => {
      const checked = q.selected === opt || (q.type==='true_false' && String(q.selected)===String(opt==='True'));
      html += `<div class="form-check"><input class="form-check-input" type="radio" name="ans" value="${opt}" ${checked?'checked':''}><label class="form-check-label">${opt}</label></div>`;
    });
  } else {
    q.options.forEach(opt => {
      const checked = Array.isArray(q.selected) && q.selected.includes(opt);
      html += `<div class="form-check"><input class="form-check-input" type="checkbox" name="ans" value="${opt}" ${checked?'checked':''}><label class="form-check-label">${opt}</label></div>`;
    });
  }
  html += `</div></div>`;
  document.getElementById('examPanel').innerHTML = html;
  renderGrid();
  updateSummary();
}

function captureAnswer() {
  const q = current();
  const inputs = [...document.querySelectorAll('input[name="ans"]:checked')].map(i => i.value);
  if (q.type === 'multiple_choice') {
    q.selected = inputs;
  } else if (q.type === 'true_false') {
    q.selected = inputs.length ? inputs[0] === 'True' : null;
  } else {
    q.selected = inputs[0] || null;
  }
}

function saveCurrent() {
  captureAnswer();
  const q = current();
  const spent = Math.floor((Date.now() - enterTs) / 1000);
  q.timeSpent = (q.timeSpent || 0) + spent;
  enterTs = Date.now();
  return fetch('/api/answer', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({question_id:q.question_id, answer:q.selected, marked_review:q.marked, time_spent:q.timeSpent||0})
  });
}

function saveAndGo(nextIdx) {
  saveCurrent().finally(() => {
    idx = Math.max(0, Math.min(data.answers.length - 1, nextIdx));
    renderQuestion();
  });
}

function updateTimer() {
  const el = document.getElementById('timer');
  const m = Math.floor(Math.max(0, remaining) / 60).toString().padStart(2, '0');
  const s = (Math.max(0, remaining) % 60).toString().padStart(2, '0');
  el.textContent = `${m}:${s}`;
  const warn = document.getElementById('warn');
  warn.textContent = remaining <= 30 ? 'Final 30 seconds' : remaining <= 60 ? '1 minute remaining' : remaining <= 300 ? '5 minutes remaining' : '';
  if (remaining <= 0) {
    fetch('/autosubmit', {method:'POST'}).then(r=>r.json()).then(j=>location.href=j.redirect);
    return;
  }
  remaining -= 1;
}

function updateSummary() {
  const answered = data.answers.filter(a => hasAnswer(a)).length;
  const marked = data.answers.filter(a => a.marked).length;
  const unanswered = data.answers.length - answered;
  document.getElementById('summary').textContent = `Answered: ${answered}, Unanswered: ${unanswered}, Marked for review: ${marked}`;
}

document.getElementById('nextBtn').onclick = () => saveAndGo(idx + 1);
document.getElementById('prevBtn').onclick = () => saveAndGo(idx - 1);
document.getElementById('clearBtn').onclick = () => { current().selected = null; saveCurrent().then(renderQuestion); };
document.getElementById('markBtn').onclick = () => { current().marked = !current().marked; saveCurrent().then(renderQuestion); };
document.getElementById('submitNow').onclick = () => { saveCurrent().finally(() => { const f = document.createElement('form'); f.method='POST'; f.action='/submit'; document.body.appendChild(f); f.submit(); }); };

renderQuestion();
setInterval(updateTimer, 1000);
updateTimer();

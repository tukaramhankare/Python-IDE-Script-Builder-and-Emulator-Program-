/* ═══════════════════════════════════════════════════════
   PyEmulate v2 — app.js
   Author: Tukaram Hankare
   Fixed, self-contained. Runs on page load.
   ═══════════════════════════════════════════════════════ */
'use strict';

/* ────────────────────────────────────────────────────────
   STARTER SCRIPTS
──────────────────────────────────────────────────────── */
const STARTERS = [
  {
    name: 'hello.py',
    code: `# Hello World — PyEmulate by Tukaram Hankare
print("Hello, World! 🐍")
print("Python is running in your browser — offline!")

name = "Tukaram"
lang = "Python"
year = 2025
print(f"\\nWelcome, {name}!")
print(f"Running {lang} since {year}")

numbers = [1, 2, 3, 4, 5]
total = sum(numbers)
print(f"\\nSum of {numbers} = {total}")
print(f"Average = {total / len(numbers)}")
`
  },
  {
    name: 'loops.py',
    code: `# Loops & Data Structures — PyEmulate
print("=== FOR LOOP ===")
fruits = ["mango", "banana", "apple", "cherry"]
for i, fruit in enumerate(fruits, 1):
    print(f"  {i}. {fruit.upper()}")

print("\\n=== WHILE LOOP ===")
n = 1
while n <= 5:
    print(f"  2^{n} = {2**n}")
    n += 1

print("\\n=== DICTIONARY ===")
person = {"name": "Tukaram", "city": "Solapur", "skill": "Python"}
for key, val in person.items():
    print(f"  {key:8s} → {val}")

print("\\n=== LIST COMPREHENSION ===")
squares = [x**2 for x in range(1, 10)]
evens   = [x for x in range(1, 20) if x % 2 == 0]
print(f"  Squares : {squares}")
print(f"  Evens   : {evens}")
`
  },
  {
    name: 'functions.py',
    code: `# Functions & Classes — PyEmulate
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}! 👋"

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n):
    a, b = 0, 1
    result = []
    for _ in range(n):
        result.append(a)
        a, b = b, a + b
    return result

# Test functions
print(greet("Tukaram"))
print(greet("World", "Namaste"))

print("\\n=== Factorials ===")
for i in range(1, 9):
    print(f"  {i}! = {factorial(i)}")

print("\\n=== Fibonacci ===")
print(fibonacci(12))

# Class example
class Circle:
    PI = 3.14159265

    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return self.PI * self.radius ** 2

    def perimeter(self):
        return 2 * self.PI * self.radius

    def __str__(self):
        return f"Circle(r={self.radius})"

print("\\n=== Circles ===")
for r in [1, 3, 5, 7]:
    c = Circle(r)
    print(f"  {c} → area={c.area():.2f}, perimeter={c.perimeter():.2f}")
`
  },
  {
    name: 'math_demo.py',
    code: `# Math Demo — PyEmulate
import math

print("=== MATH CONSTANTS ===")
print(f"  π  = {math.pi:.10f}")
print(f"  e  = {math.e:.10f}")
print(f"  τ  = {math.tau:.10f}")

print("\\n=== POWERS & ROOTS ===")
for n in [2, 3, 4, 8, 16, 25, 64, 100]:
    print(f"  sqrt({n:4d}) = {math.sqrt(n):.6f}")

print("\\n=== PRIMES (Sieve of Eratosthenes) ===")
def sieve(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(math.sqrt(limit)) + 1):
        if is_prime[i]:
            for j in range(i*i, limit+1, i):
                is_prime[j] = False
    return [x for x in range(2, limit+1) if is_prime[x]]

primes = sieve(60)
print(f"  {primes}")
print(f"  Count: {len(primes)}")

print("\\n=== TRIG TABLE ===")
print(f"  {'Deg':>5}  {'sin':>8}  {'cos':>8}  {'tan':>10}")
print("  " + "-"*40)
for deg in range(0, 91, 15):
    r = math.radians(deg)
    tan_val = f"{math.tan(r):10.4f}" if deg != 90 else "  ∞"
    print(f"  {deg:>5}°  {math.sin(r):8.4f}  {math.cos(r):8.4f}  {tan_val}")
`
  },
  {
    name: 'input_demo.py',
    code: `# Input Demo — PyEmulate (uses input())
print("=== INTERACTIVE DEMO ===")
print("This script will ask for your input.\\n")

name = input("What is your name? ")
print(f"Nice to meet you, {name}!")

age_str = input("How old are you? ")
try:
    age = int(age_str)
    print(f"\\nIn 10 years you will be {age + 10} years old.")
    if age >= 18:
        print("You are an adult. ✅")
    else:
        print(f"You will be an adult in {18 - age} year(s). 🕐")
except ValueError:
    print("That doesn't look like a number, but that's okay!")

city = input("\\nWhich city are you from? ")
print(f"\\n{city} sounds like a wonderful place!")
print(f"Thanks for chatting, {name} from {city}! 👋")
`
  }
];

/* ────────────────────────────────────────────────────────
   STATE
──────────────────────────────────────────────────────── */
const S = {
  files: [],         // [{id, name, code, modified}]
  active: null,      // active file id
  cm: null,          // CodeMirror instance
  running: false,
  lineN: 0,
  theme: 'dark',
  inspOpen: true,
  inputResolve: null,
  runStart: 0,
};

function uid(){ return Math.random().toString(36).slice(2,9) }

/* ────────────────────────────────────────────────────────
   FILE MANAGEMENT
──────────────────────────────────────────────────────── */
function fileNew(name, code=''){
  const f = {id:uid(), name, code, modified:false};
  S.files.push(f);
  return f;
}
function fileActive(){ return S.files.find(f=>f.id===S.active)||null }

function fileActivate(id){
  const f = S.files.find(f=>f.id===id);
  if(!f) return;
  // Save current CM value before switching
  if(S.cm && S.active && S.active !== id){
    const cur = S.files.find(f=>f.id===S.active);
    if(cur) cur.code = S.cm.getValue();
  }
  S.active = id;
  renderTabs();
  renderFiles();
  // Load into editor
  if(S.cm){
    S.cm.setValue(f.code);
    S.cm.clearHistory();
    S.cm.focus();
  }
  document.getElementById('footerFile').textContent = f.name;
}

function fileDelete(id){
  if(S.files.length<=1){ toast('Cannot delete the only file'); return }
  if(!confirm(`Delete "${S.files.find(f=>f.id===id)?.name}"?`)) return;
  S.files = S.files.filter(f=>f.id!==id);
  if(S.active===id) fileActivate(S.files[0].id);
  else { renderTabs(); renderFiles(); }
}

function fileSave(){
  const f = fileActive();
  if(!f){ toast('No file open'); return }
  if(S.cm) f.code = S.cm.getValue();
  const blob = new Blob([f.code],{type:'text/plain'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = f.name;
  a.click();
  URL.revokeObjectURL(a.href);
  f.modified = false;
  renderTabs();
  toast(`Saved: ${f.name}`);
}

/* ────────────────────────────────────────────────────────
   RENDER TABS
──────────────────────────────────────────────────────── */
function renderTabs(){
  const bar = document.getElementById('tabBar');
  bar.innerHTML = '';
  S.files.forEach(f=>{
    const t = document.createElement('div');
    t.className = 'tab'+(f.id===S.active?' active':'')+(f.modified?' modified':'');
    t.dataset.id = f.id;
    t.innerHTML = `
      <svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
      <span class="tab-dot"></span>
      <span style="overflow:hidden;text-overflow:ellipsis;max-width:110px" title="${esc(f.name)}">${esc(f.name)}</span>
      <button class="tab-x" data-id="${f.id}" title="Close">×</button>`;
    t.addEventListener('click', e=>{
      if(e.target.closest('.tab-x')) return;
      fileActivate(f.id);
    });
    t.querySelector('.tab-x').addEventListener('click', e=>{
      e.stopPropagation();
      fileDelete(f.id);
    });
    bar.appendChild(t);
  });
  // + button
  const add = document.createElement('button');
  add.className = 'tab-add';
  add.title = 'New File';
  add.textContent = '+';
  add.addEventListener('click', promptNewFile);
  bar.appendChild(add);
}

/* ────────────────────────────────────────────────────────
   RENDER FILE SIDEBAR (not used in 3-file layout — kept for compatibility)
──────────────────────────────────────────────────────── */
function renderFiles(){ /* tabs are the nav — no sidebar needed */ }

/* ────────────────────────────────────────────────────────
   CODEMIRROR INIT
──────────────────────────────────────────────────────── */
function initEditor(){
  const host = document.getElementById('editorHost');
  const ta = document.createElement('textarea');
  host.appendChild(ta);

  S.cm = CodeMirror.fromTextArea(ta, {
    mode: 'python',
    theme: 'pyemulate',
    lineNumbers: true,
    indentUnit: 4,
    tabSize: 4,
    indentWithTabs: false,
    lineWrapping: false,
    matchBrackets: true,
    autoCloseBrackets: true,
    styleActiveLine: true,
    extraKeys: {
      'Tab':        cm => cm.execCommand('indentMore'),
      'Shift-Tab':  cm => cm.execCommand('indentLess'),
      'Ctrl-Enter': ()  => runCode(),
      'Cmd-Enter':  ()  => runCode(),
      'Ctrl-/':     cm => cm.execCommand('toggleComment'),
      'Ctrl-S':     ()  => fileSave(),
      'Cmd-S':      ()  => fileSave(),
    }
  });

  S.cm.on('change', ()=>{
    const f = fileActive();
    if(!f) return;
    f.code = S.cm.getValue();
    if(!f.modified){ f.modified=true; renderTabs(); }
  });

  S.cm.on('cursorActivity', ()=>{
    const c = S.cm.getCursor();
    document.getElementById('footerCursor').textContent =
      `Ln ${c.line+1}, Col ${c.ch+1}`;
  });

  // Load first file
  const f = fileActive();
  if(f){ S.cm.setValue(f.code); S.cm.clearHistory(); }

  // Force refresh after layout
  setTimeout(()=>S.cm.refresh(), 60);
}

/* ────────────────────────────────────────────────────────
   CONSOLE OUTPUT
──────────────────────────────────────────────────────── */
function outEl(){ return document.getElementById('consoleOut') }

function clearConsole(){
  outEl().innerHTML = '';
  S.lineN = 0;
  clearVars();
}

function printLine(text, cls='stdout'){
  const out = outEl();
  const n = ++S.lineN;
  const d = document.createElement('div');
  d.className = `cline cline-${cls}`;
  d.innerHTML = `<span class="cline-n">${n}</span><span class="cline-t">${esc(text)}</span>`;
  out.appendChild(d);
  out.scrollTop = out.scrollHeight;
}

function printErr(text){
  const out = outEl();
  const d = document.createElement('div');
  d.className = 'err-block';
  d.textContent = text;
  out.appendChild(d);
  out.scrollTop = out.scrollHeight;
}

function printInfo(t){ printLine(t,'info') }
function printOk(t)  { printLine(t,'ok')   }
function printWarn(t){ printLine(t,'warn')  }

/* ────────────────────────────────────────────────────────
   VARIABLE INSPECTOR
──────────────────────────────────────────────────────── */
const SKIP = new Set(['__name__','__doc__','__package__','__spec__',
  '__loader__','__builtins__','__build_class__','__import__']);

function clearVars(){
  document.getElementById('varBody').innerHTML =
    '<tr><td colspan="3" class="var-empty">No variables yet</td></tr>';
}

function updateVars(mod){
  if(!mod || !mod.$d){ clearVars(); return }
  const rows = [];
  for(const k in mod.$d){
    if(SKIP.has(k) || k.startsWith('_')) continue;
    const val = mod.$d[k];
    const typeName = val && val.tp$name ? val.tp$name : typeof val;
    let strVal = '';
    try{
      const js = Sk.ffi.remapToJs(val);
      strVal = typeof js==='object' ? JSON.stringify(js) : String(js);
    } catch{ strVal = val ? val.toString() : '?' }
    rows.push([k, typeName, strVal]);
  }
  const body = document.getElementById('varBody');
  if(!rows.length){ clearVars(); return }
  body.innerHTML = '';
  rows.slice(0,60).forEach(([n,t,v])=>{
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td title="${esc(n)}">${esc(n)}</td>
      <td>${esc(t)}</td>
      <td title="${esc(v)}">${esc(v.slice(0,100))}</td>`;
    body.appendChild(tr);
  });
}

/* ────────────────────────────────────────────────────────
   STATUS BAR
──────────────────────────────────────────────────────── */
function setStatus(state, msg, time=''){
  const dot  = document.getElementById('statusDot');
  const txt  = document.getElementById('statusText');
  const tm   = document.getElementById('statusTime');
  dot.className  = `status-dot ${state}`;
  txt.textContent = msg;
  tm.textContent  = time;
}

/* ────────────────────────────────────────────────────────
   INPUT MODAL
──────────────────────────────────────────────────────── */
function requestInput(prompt){
  return new Promise(resolve=>{
    S.inputResolve = resolve;
    document.getElementById('modalPrompt').textContent = prompt || 'Enter value:';
    document.getElementById('modalInput').value = '';
    document.getElementById('overlay').style.display = 'flex';
    setTimeout(()=>document.getElementById('modalInput').focus(), 60);
  });
}

function submitInput(){
  const v = document.getElementById('modalInput').value;
  document.getElementById('overlay').style.display = 'none';
  printLine(`${document.getElementById('modalPrompt').textContent}${v}`, 'input');
  if(S.inputResolve){ S.inputResolve(v); S.inputResolve=null }
}

/* ────────────────────────────────────────────────────────
   SKULPT RUNNER  ← The Fixed Core
──────────────────────────────────────────────────────── */
async function runCode(){
  if(S.running) return;

  // Engine check
  if(typeof Sk === 'undefined'){
    clearConsole();
    printErr(
      'Skulpt engine not loaded.\n\n'+
      'Please check your internet connection and reload the page.\n'+
      'The emulator requires Skulpt and CodeMirror from CDN on first load.\n\n'+
      'After that it works offline via browser cache.'
    );
    return;
  }

  const f = fileActive();
  if(!f){ printWarn('No file active. Create a file first.'); return }

  // Always sync editor → file before running
  if(S.cm) f.code = S.cm.getValue();
  const code = f.code.trim();
  if(!code){ printWarn('File is empty. Write some code first.'); return }

  S.running = true;
  S.runStart = performance.now();
  document.getElementById('btnRun').disabled  = true;
  document.getElementById('btnStop').disabled = false;
  clearConsole();
  setStatus('running', `Running ${f.name}…`);
  printInfo(`▶  ${f.name}`);

  // Configure Skulpt
  Sk.configure({
    __future__: Sk.python3,
    execLimit: 30000,
    killableWhile: true,
    killableFor: true,

    output(text){
      // Skulpt sends text with \n — split and emit per line
      const parts = text.split('\n');
      parts.forEach((line, i)=>{
        // Don't emit empty trailing chunk from the final \n
        if(i < parts.length - 1 || line !== ''){
          printLine(line, 'stdout');
        }
      });
    },

    read(x){
      if(Sk.builtinFiles && Sk.builtinFiles.files[x] !== undefined)
        return Sk.builtinFiles.files[x];
      throw new Error(`File not found: '${x}'`);
    },

    inputfun(prompt){ return requestInput(prompt) },
    inputfunTakesPrompt: true,
  });

  let mod = null;
  try{
    mod = await Sk.misceval.asyncToPromise(()=>
      Sk.importMainWithBody('<stdin>', false, code, true)
    );
    const elapsed = ((performance.now()-S.runStart)/1000).toFixed(3);
    printOk(`\n✔  Finished in ${elapsed}s`);
    setStatus('ok', `Done`, `${elapsed}s`);
    updateVars(mod);

  } catch(err){
    const elapsed = ((performance.now()-S.runStart)/1000).toFixed(3);
    let msg = '';
    if(err instanceof Sk.builtin.BaseException){
      // Skulpt exception — extract clean message
      try{ msg = err.toString() } catch{ msg = String(err) }
    } else {
      msg = err.message || String(err);
    }
    printErr('✖  ' + msg);
    setStatus('err', `Error`, `${elapsed}s`);
    clearVars();

  } finally {
    S.running = false;
    // Reset exec limit for next run
    Sk.execLimit = 30000;
    document.getElementById('btnRun').disabled  = false;
    document.getElementById('btnStop').disabled = true;
    document.getElementById('overlay').style.display = 'none';
    S.inputResolve = null;
  }
}

function stopCode(){
  if(!S.running) return;
  Sk.execLimit = 0;          // Skulpt checks this flag internally
  S.running = false;
  document.getElementById('btnRun').disabled  = false;
  document.getElementById('btnStop').disabled = true;
  document.getElementById('overlay').style.display = 'none';
  S.inputResolve = null;
  printWarn('\n⏹  Stopped by user.');
  setStatus('', 'Stopped');
  setTimeout(()=>{ Sk.execLimit = 30000 }, 150);
}

/* ────────────────────────────────────────────────────────
   COPY OUTPUT
──────────────────────────────────────────────────────── */
function copyOutput(){
  const lines = Array.from(
    document.getElementById('consoleOut').querySelectorAll('.cline-t,.err-block')
  ).map(el=>el.textContent).join('\n');
  navigator.clipboard.writeText(lines)
    .then(()=>toast('Output copied!'))
    .catch(()=>{
      const ta=document.createElement('textarea');
      ta.value=lines; document.body.appendChild(ta);
      ta.select(); document.execCommand('copy'); ta.remove();
      toast('Output copied!');
    });
}

/* ────────────────────────────────────────────────────────
   THEME
──────────────────────────────────────────────────────── */
function toggleTheme(){
  S.theme = S.theme==='dark'?'light':'dark';
  document.documentElement.setAttribute('data-theme', S.theme);
  localStorage.setItem('pye_theme', S.theme);
  const ic = document.getElementById('themeIcon');
  ic.innerHTML = S.theme==='light'
    ? '<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>'
    : '<path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>';
  if(S.cm) setTimeout(()=>S.cm.refresh(),50);
}

/* ────────────────────────────────────────────────────────
   TOAST
──────────────────────────────────────────────────────── */
function toast(msg){
  let t=document.querySelector('.toast');
  if(!t){ t=document.createElement('div'); t.className='toast'; document.body.appendChild(t) }
  t.textContent=msg; t.classList.add('show');
  clearTimeout(t._t);
  t._t=setTimeout(()=>t.classList.remove('show'),2000);
}

/* ────────────────────────────────────────────────────────
   ESCAPE
──────────────────────────────────────────────────────── */
function esc(s){
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

/* ────────────────────────────────────────────────────────
   RESIZE DIVIDER
──────────────────────────────────────────────────────── */
function initResize(){
  const div  = document.getElementById('divider');
  const out  = document.getElementById('paneOutput');
  const ws   = document.getElementById('workspace');
  let drag=false, startX=0, startW=0;

  div.addEventListener('mousedown', e=>{
    drag=true; startX=e.clientX; startW=out.offsetWidth;
    div.classList.add('dragging');
    document.body.style.cursor='col-resize';
    document.body.style.userSelect='none';
  });
  document.addEventListener('mousemove', e=>{
    if(!drag) return;
    const delta = startX - e.clientX;
    const newW  = Math.max(220, Math.min(ws.offsetWidth*0.7, startW+delta));
    out.style.width = newW+'px';
    if(S.cm) S.cm.refresh();
  });
  document.addEventListener('mouseup', ()=>{
    if(!drag) return;
    drag=false;
    div.classList.remove('dragging');
    document.body.style.cursor='';
    document.body.style.userSelect='';
    if(S.cm) S.cm.refresh();
  });

  // Touch resize
  div.addEventListener('touchstart', e=>{
    drag=true; startX=e.touches[0].clientX; startW=out.offsetWidth;
  },{passive:true});
  document.addEventListener('touchmove', e=>{
    if(!drag) return;
    const delta = startX - e.touches[0].clientX;
    const newW  = Math.max(220, Math.min(ws.offsetWidth*0.7, startW+delta));
    out.style.width = newW+'px';
  },{passive:true});
  document.addEventListener('touchend', ()=>{ drag=false });
}

/* ────────────────────────────────────────────────────────
   PROMPT NEW FILE
──────────────────────────────────────────────────────── */
function promptNewFile(){
  const name = prompt('New file name:', 'script.py');
  if(!name) return;
  const safe = name.endsWith('.py')?name:name+'.py';
  const f = fileNew(safe, `# ${safe}\n# Author: Tukaram Hankare\n\n`);
  renderTabs();
  fileActivate(f.id);
}

/* ────────────────────────────────────────────────────────
   INSPECTOR TOGGLE
──────────────────────────────────────────────────────── */
function initInspector(){
  document.getElementById('inspectorHead').addEventListener('click', ()=>{
    S.inspOpen = !S.inspOpen;
    const el = document.getElementById('inspector');
    el.classList.toggle('collapsed', !S.inspOpen);
  });
}

/* ────────────────────────────────────────────────────────
   KEYBOARD SHORTCUTS
──────────────────────────────────────────────────────── */
document.addEventListener('keydown', e=>{
  const mod = e.ctrlKey || e.metaKey;
  if(!mod) return;
  switch(e.key.toLowerCase()){
    case 'n': e.preventDefault(); promptNewFile(); break;
    case 'o': e.preventDefault(); document.getElementById('fileInput').click(); break;
    case 's': e.preventDefault(); fileSave(); break;
    case 'enter': e.preventDefault(); runCode(); break;
  }
});

/* ────────────────────────────────────────────────────────
   OPEN FILE
──────────────────────────────────────────────────────── */
document.getElementById('fileInput').addEventListener('change', e=>{
  const file = e.target.files[0];
  if(!file) return;
  const reader = new FileReader();
  reader.onload = ev=>{
    const existing = S.files.find(f=>f.name===file.name);
    if(existing){
      existing.code = ev.target.result;
      fileActivate(existing.id);
    } else {
      const f = fileNew(file.name, ev.target.result);
      renderTabs();
      fileActivate(f.id);
    }
  };
  reader.readAsText(file);
  e.target.value='';
});

/* ────────────────────────────────────────────────────────
   INIT
──────────────────────────────────────────────────────── */
function init(){
  // Theme
  const saved = localStorage.getItem('pye_theme');
  if(saved && saved !== 'dark'){
    S.theme = 'light';
    document.documentElement.setAttribute('data-theme','light');
    document.getElementById('themeIcon').innerHTML =
      '<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>';
  }

  // Create starter files
  let firstId = null;
  STARTERS.forEach((s,i)=>{
    const f = fileNew(s.name, s.code);
    if(i===0) firstId=f.id;
  });

  // Activate first
  S.active = firstId;
  renderTabs();

  // Init editor
  initEditor();

  // Init resize
  initResize();

  // Init inspector
  initInspector();

  // Status
  if(typeof Sk !== 'undefined'){
    setStatus('', 'Ready — Skulpt loaded');
    document.getElementById('footerLang').textContent = 'Python 3 · Skulpt ✓';
  } else {
    setStatus('err', 'Skulpt not loaded — check internet connection');
    document.getElementById('footerLang').textContent = 'Engine missing ✗';
  }

  // Button bindings
  document.getElementById('btnRun').addEventListener('click',  runCode);
  document.getElementById('btnStop').addEventListener('click', stopCode);
  document.getElementById('btnNew').addEventListener('click',  promptNewFile);
  document.getElementById('btnSave').addEventListener('click', fileSave);
  document.getElementById('btnOpen').addEventListener('click', ()=>document.getElementById('fileInput').click());
  document.getElementById('btnTheme').addEventListener('click', toggleTheme);
  document.getElementById('btnClear').addEventListener('click', clearConsole);
  document.getElementById('btnCopy').addEventListener('click',  copyOutput);

  // Modal input
  document.getElementById('modalOk').addEventListener('click', submitInput);
  document.getElementById('modalInput').addEventListener('keydown', e=>{
    if(e.key==='Enter') submitInput();
  });
  document.getElementById('overlay').addEventListener('click', e=>{
    if(e.target===e.currentTarget) submitInput();
  });
}

// Run after DOM ready
if(document.readyState==='loading'){
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

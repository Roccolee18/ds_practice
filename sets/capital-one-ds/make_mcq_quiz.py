"""Generates mcq_quiz.html (an Artifact-ready page) from mcq_bank.py."""
import html
import json
import os
import re

import mcq_bank as M

HERE = os.path.dirname(os.path.abspath(__file__))


def md(text: str) -> str:
    """Minimal markdown -> HTML for the explanation prose."""
    t = text.strip().replace("\\$", "$")
    t = html.escape(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    paras = [re.sub(r"\s*\n\s*", " ", p).strip() for p in re.split(r"\n\s*\n", t)]
    return "".join(f"<p>{p}</p>" for p in paras if p)


def plain(text: str) -> str:
    t = text.strip().replace("\\$", "$")
    t = html.escape(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    paras = [re.sub(r"\s*\n\s*", " ", p).strip() for p in re.split(r"\n\s*\n", t)]
    return "".join(f"<p>{p}</p>" for p in paras if p)


DATA = [{
    "id": q["id"],
    "topic": q["topic"],
    "sub": q["subtopic"],
    "diff": q["difficulty"],
    "q": plain(q["q"]),
    "options": [plain(o) for o in q["options"]],
    "answer": q["answer"],
    "why": md(q["why"]),
} for q in M.QUESTIONS]

PAGE = """<title>Data Science Screen Drills</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
:root{
  --ground:#F5F7FA; --surface:#FFFFFF; --surface-2:#EEF1F6;
  --ink:#17202D; --muted:#5B6B80; --faint:#8A99AC;
  --line:#DCE2EB; --line-strong:#C3CCD9;
  --accent:#2C4C8C; --accent-soft:#E7EDF8; --on-accent:#FFFFFF;
  --good:#1B6F45; --good-soft:#E3F2E9; --good-line:#8CC2A6;
  --bad:#A62F1C; --bad-soft:#FBE8E4; --bad-line:#DDA093;
  --warn:#8A5D0F;
  --shadow:0 1px 2px rgba(23,32,45,.06), 0 8px 24px -12px rgba(23,32,45,.18);
  --radius:10px;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#0E141C; --surface:#161E29; --surface-2:#1D2733;
    --ink:#E6EBF3; --muted:#9BABBF; --faint:#6D7D92;
    --line:#26313F; --line-strong:#354354;
    --accent:#7FA0DC; --accent-soft:#1B2739; --on-accent:#0E141C;
    --good:#5BC28D; --good-soft:#132A20; --good-line:#2F6A4C;
    --bad:#E88670; --bad-soft:#2C1713; --bad-line:#7A3629;
    --warn:#D9A544;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -12px rgba(0,0,0,.6);
  }
}
:root[data-theme="dark"]{
  --ground:#0E141C; --surface:#161E29; --surface-2:#1D2733;
  --ink:#E6EBF3; --muted:#9BABBF; --faint:#6D7D92;
  --line:#26313F; --line-strong:#354354;
  --accent:#7FA0DC; --accent-soft:#1B2739; --on-accent:#0E141C;
  --good:#5BC28D; --good-soft:#132A20; --good-line:#2F6A4C;
  --bad:#E88670; --bad-soft:#2C1713; --bad-line:#7A3629;
  --warn:#D9A544;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -12px rgba(0,0,0,.6);
}

*{box-sizing:border-box}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:"Source Serif 4",Georgia,serif; font-size:16px; line-height:1.6;
  -webkit-font-smoothing:antialiased;
}
.wrap{max-width:760px; margin:0 auto; padding-inline:16px; padding-block:0 56px}

/* ---------- header ---------- */
.bar{
  position:sticky; top:env(safe-area-inset-top,0px); z-index:20;
  background:color-mix(in srgb, var(--ground) 92%, transparent);
  backdrop-filter:blur(8px);
  border-bottom:1px solid var(--line);
}
.bar-in{max-width:760px; margin:0 auto; padding:10px 16px}
.bar-top{display:flex; align-items:baseline; gap:12px; flex-wrap:wrap}
h1{
  font-family:Archivo,system-ui,sans-serif; font-weight:700; font-size:16px;
  letter-spacing:-.01em; margin:0; text-wrap:balance;
}
.counts{
  margin-left:auto; font-family:"JetBrains Mono",ui-monospace,monospace;
  font-size:12px; color:var(--muted); font-variant-numeric:tabular-nums;
  display:flex; gap:12px;
}
.counts b{color:var(--ink); font-weight:600}
.track{height:3px; background:var(--line); border-radius:99px; margin-top:9px; overflow:hidden}
.fill{height:100%; background:var(--accent); width:0%; transition:width .28s ease}

/* ---------- modes ---------- */
.modes{display:flex; gap:6px; flex-wrap:wrap; margin:16px 0 4px}
.chip{
  font-family:Archivo,system-ui,sans-serif; font-size:12px; font-weight:600;
  letter-spacing:.02em; padding:5px 11px; border-radius:99px;
  border:1px solid var(--line-strong); background:var(--surface); color:var(--muted);
  cursor:pointer; transition:.15s;
}
.chip:hover{border-color:var(--accent); color:var(--ink)}
.chip[aria-pressed="true"]{background:var(--accent); border-color:var(--accent); color:var(--on-accent)}
.chip:disabled{opacity:.4; cursor:not-allowed}

/* ---------- card ---------- */
.card{
  background:var(--surface); border:1px solid var(--line);
  border-radius:var(--radius); box-shadow:var(--shadow);
  padding:22px; margin-top:14px;
}
.eyebrow{
  display:flex; align-items:center; gap:9px; flex-wrap:wrap;
  font-family:"JetBrains Mono",ui-monospace,monospace; font-size:11px;
  color:var(--faint); letter-spacing:.04em; margin-bottom:14px;
}
.eyebrow .qid{color:var(--accent); font-weight:600}
.eyebrow .sep{color:var(--line-strong)}
.diff{
  font-family:Archivo,system-ui,sans-serif; font-size:10px; font-weight:700;
  text-transform:uppercase; letter-spacing:.08em; padding:2px 7px; border-radius:4px;
  background:var(--surface-2); color:var(--muted);
}
.diff.hard{color:var(--warn); background:color-mix(in srgb, var(--warn) 12%, transparent)}
.qtext{font-size:17px; line-height:1.55}
.qtext p{margin:0 0 10px} .qtext p:last-child{margin-bottom:0}
.qtext code{font-family:"JetBrains Mono",monospace; font-size:.88em; background:var(--surface-2); padding:1px 5px; border-radius:4px}

.opts{display:flex; flex-direction:column; gap:8px; margin-top:18px}
.opt{
  display:flex; gap:11px; align-items:flex-start; text-align:left; width:100%;
  font-family:"Source Serif 4",Georgia,serif; font-size:15px; line-height:1.5; color:var(--ink);
  background:var(--surface); border:1px solid var(--line-strong); border-radius:8px;
  padding:12px 14px; cursor:pointer; transition:.13s;
}
.opt:hover:not(:disabled){border-color:var(--accent); background:var(--accent-soft)}
.opt:disabled{cursor:default}
.opt .key{
  flex:none; font-family:"JetBrains Mono",monospace; font-size:11px; font-weight:600;
  width:20px; height:20px; border-radius:5px; display:grid; place-items:center;
  background:var(--surface-2); color:var(--muted); margin-top:2px;
}
.opt p{margin:0}
.opt.correct{background:var(--good-soft); border-color:var(--good-line)}
.opt.correct .key{background:var(--good); color:var(--surface)}
.opt.wrong{background:var(--bad-soft); border-color:var(--bad-line)}
.opt.wrong .key{background:var(--bad); color:var(--surface)}
.opt.dim{opacity:.55}

/* ---------- explanation ---------- */
.why{margin-top:16px; border-top:1px solid var(--line); padding-top:16px}
.verdict{
  font-family:Archivo,system-ui,sans-serif; font-size:12px; font-weight:700;
  text-transform:uppercase; letter-spacing:.07em; margin-bottom:9px;
}
.verdict.ok{color:var(--good)} .verdict.no{color:var(--bad)}
.why-body{font-size:15px; color:var(--muted)}
.why-body p{margin:0 0 11px} .why-body p:last-child{margin-bottom:0}
.why-body strong{color:var(--ink); font-weight:600}
.why-body code{font-family:"JetBrains Mono",monospace; font-size:.87em; background:var(--surface-2); padding:1px 5px; border-radius:4px; color:var(--ink)}

.actions{display:flex; gap:9px; margin-top:18px; align-items:center; flex-wrap:wrap}
.btn{
  font-family:Archivo,system-ui,sans-serif; font-size:13px; font-weight:600;
  padding:9px 18px; border-radius:7px; border:1px solid var(--accent);
  background:var(--accent); color:var(--on-accent); cursor:pointer; transition:.15s;
}
.btn:hover{filter:brightness(1.08)}
.btn:focus-visible,.opt:focus-visible,.chip:focus-visible{outline:2px solid var(--accent); outline-offset:2px}
.btn.ghost{background:transparent; color:var(--muted); border-color:var(--line-strong)}
.btn.ghost:hover{color:var(--ink); border-color:var(--accent)}
.hint{font-family:"JetBrains Mono",monospace; font-size:11px; color:var(--faint); margin-left:auto}

/* ---------- results ---------- */
.res-head{font-family:Archivo,system-ui,sans-serif; font-size:22px; font-weight:700; margin:0 0 4px; letter-spacing:-.01em}
.res-sub{color:var(--muted); font-size:15px; margin:0 0 20px}
.big{font-family:"JetBrains Mono",monospace; font-size:44px; font-weight:600; font-variant-numeric:tabular-nums; line-height:1; color:var(--accent)}
.rows{display:flex; flex-direction:column; gap:1px; background:var(--line); border:1px solid var(--line); border-radius:8px; overflow:hidden; margin-top:18px}
.row{display:flex; align-items:center; gap:12px; background:var(--surface); padding:11px 14px; font-size:14px}
.row .nm{font-family:Archivo,system-ui,sans-serif; font-weight:600; font-size:13px}
.row .bar2{flex:1; height:5px; background:var(--surface-2); border-radius:99px; overflow:hidden; min-width:50px}
.row .bar2 i{display:block; height:100%; background:var(--accent)}
.row .pc{font-family:"JetBrains Mono",monospace; font-size:12px; font-variant-numeric:tabular-nums; color:var(--muted); min-width:58px; text-align:right}
.missed{margin-top:18px; font-size:14px; color:var(--muted)}
.missed code{font-family:"JetBrains Mono",monospace; font-size:12px; background:var(--surface-2); padding:2px 6px; border-radius:4px; margin-right:4px; display:inline-block; color:var(--ink)}
.note{font-size:13px; color:var(--faint); margin-top:22px; padding-top:14px; border-top:1px solid var(--line)}

@media (max-width:480px){
  .card{padding:16px}
  .qtext{font-size:16px}
  .hint{display:none}
  .counts{width:100%; margin-left:0}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
</style>

<div class="bar">
  <div class="bar-in">
    <div class="bar-top">
      <h1>Data Science Screen Drills</h1>
      <div class="counts">
        <span>Q <b id="c-pos">1</b>/<b id="c-tot">40</b></span>
        <span>correct <b id="c-ok">0</b></span>
        <span>acc <b id="c-acc">—</b></span>
      </div>
    </div>
    <div class="track"><div class="fill" id="fill"></div></div>
  </div>
</div>

<div class="wrap">
  <div class="modes" id="modes"></div>
  <div id="stage"></div>
  <p class="note">
    40 scenario questions, weighted like CodeSignal's published Data Science Framework —
    roughly 6 ML-fundamentals items for every 2 probability and statistics items.
    Keys <b>1</b>–<b>4</b> answer, <b>Enter</b> advances. Missed questions are remembered on this
    device, so “Missed” picks up where you left off.
  </p>
</div>

<script>
const Q = __DATA__;

const MODES = [
  {id:"all",   label:"All",             f:q=>true},
  {id:"ml",    label:"ML fundamentals", f:q=>q.topic==="ML"},
  {id:"stats", label:"Probability & stats", f:q=>q.topic!=="ML"},
  {id:"hard",  label:"Hard only",       f:q=>q.diff==="hard"},
  {id:"miss",  label:"Missed",          f:q=>missed.has(q.id)},
];

let missed = new Set();
try{ const s = localStorage.getItem("dsdrills.missed"); if(s) missed = new Set(JSON.parse(s)); }catch(e){}
function saveMissed(){ try{ localStorage.setItem("dsdrills.missed",JSON.stringify([...missed])); }catch(e){} }

let mode="all", order=[], i=0, answered=null, ok=0, done=0, log=[];

function shuffle(a){ for(let j=a.length-1;j>0;j--){const k=Math.floor(Math.random()*(j+1));[a[j],a[k]]=[a[k],a[j]];} return a; }

function start(m){
  mode=m;
  const def = MODES.find(x=>x.id===m);
  order = shuffle(Q.filter(def.f).slice());
  i=0; ok=0; done=0; log=[]; answered=null;
  renderModes(); render();
}

function renderModes(){
  document.getElementById("modes").innerHTML = MODES.map(m=>{
    const n = Q.filter(m.f).length;
    const dis = n===0 ? " disabled" : "";
    return `<button class="chip" data-m="${m.id}" aria-pressed="${m.id===mode}"${dis}>${m.label} <span style="opacity:.6">${n}</span></button>`;
  }).join("");
}

function stats(){
  document.getElementById("c-pos").textContent = Math.min(i+1, order.length||1);
  document.getElementById("c-tot").textContent = order.length;
  document.getElementById("c-ok").textContent = ok;
  document.getElementById("c-acc").textContent = done ? Math.round(ok/done*100)+"%" : "—";
  document.getElementById("fill").style.width = order.length ? (done/order.length*100)+"%" : "0%";
}

function render(){
  const stage = document.getElementById("stage");
  if(order.length===0){
    stage.innerHTML = `<div class="card"><p class="res-sub" style="margin:0">Nothing to drill in this set — you haven't missed anything yet. Pick another mode.</p></div>`;
    stats(); return;
  }
  if(i>=order.length){ results(); stats(); return; }

  const q = order[i];
  stage.innerHTML = `
    <div class="card">
      <div class="eyebrow">
        <span class="qid">${q.id}</span><span class="sep">/</span>
        <span>${q.topic}</span><span class="sep">/</span>
        <span>${q.sub}</span>
        <span class="diff ${q.diff}">${q.diff}</span>
      </div>
      <div class="qtext">${q.q}</div>
      <div class="opts" id="opts">
        ${q.options.map((o,n)=>`<button class="opt" data-n="${n}"><span class="key">${n+1}</span><span>${o}</span></button>`).join("")}
      </div>
      <div id="tail"></div>
    </div>`;
  document.querySelectorAll(".opt").forEach(b=>b.addEventListener("click",()=>answer(+b.dataset.n)));
  answered=null; stats();
}

function answer(n){
  if(answered!==null) return;
  const q = order[i];
  answered=n; done++;
  const right = n===q.answer;
  if(right){ ok++; missed.delete(q.id); } else { missed.add(q.id); }
  saveMissed();
  log.push({q, right});

  document.querySelectorAll(".opt").forEach(b=>{
    const bn=+b.dataset.n; b.disabled=true;
    if(bn===q.answer) b.classList.add("correct");
    else if(bn===n) b.classList.add("wrong");
    else b.classList.add("dim");
  });
  document.getElementById("tail").innerHTML = `
    <div class="why">
      <div class="verdict ${right?"ok":"no"}">${right?"Correct":"Not quite — the answer is "+String.fromCharCode(65+q.answer)}</div>
      <div class="why-body">${q.why}</div>
      <div class="actions">
        <button class="btn" id="next">${i+1>=order.length?"See results":"Next question"}</button>
        <span class="hint">Enter</span>
      </div>
    </div>`;
  document.getElementById("next").addEventListener("click",next);
  document.getElementById("next").focus();
  stats();
}

function next(){ i++; render(); window.scrollTo({top:0,behavior:"smooth"}); }

function results(){
  const byTopic={};
  log.forEach(({q,right})=>{
    byTopic[q.topic] ??= {n:0,ok:0};
    byTopic[q.topic].n++; if(right) byTopic[q.topic].ok++;
  });
  const wrong = log.filter(x=>!x.right).map(x=>x.q.id);
  const pc = done? Math.round(ok/done*100):0;
  document.getElementById("stage").innerHTML = `
    <div class="card">
      <div class="big">${pc}%</div>
      <h2 class="res-head">${ok} of ${done}</h2>
      <p class="res-sub">${pc>=85?"Strong. These topics are holding up under pressure."
        :pc>=70?"Solid. Work the misses below, then come back to this set tomorrow."
        :"Worth a second pass. Read the explanations on everything you missed before re-running."}</p>
      <div class="rows">
        ${Object.entries(byTopic).sort((a,b)=>a[1].ok/a[1].n-b[1].ok/b[1].n).map(([t,v])=>`
          <div class="row">
            <span class="nm">${t}</span>
            <span class="bar2"><i style="width:${Math.round(v.ok/v.n*100)}%"></i></span>
            <span class="pc">${v.ok}/${v.n} · ${Math.round(v.ok/v.n*100)}%</span>
          </div>`).join("")}
      </div>
      ${wrong.length?`<div class="missed"><strong>Missed:</strong><br>${wrong.map(id=>`<code>${id}</code>`).join("")}</div>`:""}
      <div class="actions">
        ${wrong.length?`<button class="btn" id="drill">Drill the ${wrong.length} missed</button>`:""}
        <button class="btn ghost" id="again">Restart this set</button>
      </div>
    </div>`;
  document.getElementById("again").addEventListener("click",()=>start(mode));
  const d=document.getElementById("drill");
  if(d) d.addEventListener("click",()=>start("miss"));
}

document.getElementById("modes").addEventListener("click",e=>{
  const b=e.target.closest(".chip"); if(!b||b.disabled) return; start(b.dataset.m);
});
document.addEventListener("keydown",e=>{
  if(e.target.tagName==="INPUT") return;
  if(e.key>="1"&&e.key<="4"&&answered===null){ const b=document.querySelector(`.opt[data-n="${+e.key-1}"]`); if(b) b.click(); }
  if(e.key==="Enter"&&answered!==null){ const n=document.getElementById("next"); if(n){e.preventDefault(); n.click();} }
});

start("all");
</script>
"""

out = os.path.join(HERE, "mcq_quiz.html")
with open(out, "w") as f:
    f.write(PAGE.replace("__DATA__", json.dumps(DATA, ensure_ascii=False)))
print(f"wrote {out} ({os.path.getsize(out)/1024:.0f} KB, {len(DATA)} questions)")

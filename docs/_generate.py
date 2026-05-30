#!/usr/bin/env python3
"""Generate docs/index.html — a Modrinth-style listing of all mods in the pack.
Reads ../mods/*.pw.toml, fetches metadata from Modrinth, writes a static page.
"""
import glob, html, json, os, re, sys, urllib.parse, urllib.request
from datetime import datetime, timezone

ROOT      = os.path.dirname(os.path.abspath(__file__))            # .../docs
PACK_ROOT = os.path.dirname(ROOT)                                  # .../squirrelpack
MODS_DIR  = os.path.join(PACK_ROOT, "mods")
OUT_HTML  = os.path.join(ROOT, "index.html")
UA        = {"User-Agent": "squirrelpack-site/1.0 (kevin.euerle@gmail.com)"}

# Hand-written entries for non-Modrinth (CurseForge-only) mods.
# Keyed by the pw.toml basename slug.
MANUAL = {
    "coolrain": {
        "title": "Cool Rain",
        "author": "JaiZ",
        "description": "Adds realistic dynamic rain visuals with depth and atmosphere.",
        "categories": ["decoration", "vanilla-like"],
        "url": "https://www.curseforge.com/minecraft/mc-mods/cool-rain",
        "icon": "",
    },
    "swaying-garden": {
        "title": "Swaying Garden",
        "author": "Furtif",
        "description": "Makes plants and crops gently sway in the wind for added immersion.",
        "categories": ["decoration"],
        "url": "https://www.curseforge.com/minecraft/mc-mods/swaying-garden",
        "icon": "",
    },
}

def http_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

def parse_pw_toml(path):
    """Tiny TOML reader — only the fields we need from packwiz metafiles."""
    with open(path) as f:
        t = f.read()
    out = {}
    def grab(field):
        m = re.search(rf'^{field}\s*=\s*"(.+?)"', t, re.M)
        return m.group(1) if m else None
    out["name"]     = grab("name")
    out["filename"] = grab("filename")
    out["side"]     = grab("side") or "both"
    m = re.search(r'\[update\.modrinth\][^\[]*?mod-id\s*=\s*"(.+?)"', t, re.S)
    if m: out["project_id"] = m.group(1)
    out["slug_file"] = os.path.basename(path)[:-8]  # strip .pw.toml
    return out

# 1. Read all metafiles
mods = [parse_pw_toml(f) for f in sorted(glob.glob(os.path.join(MODS_DIR, "*.pw.toml")))]
print(f"read {len(mods)} metafiles")

# 2. Bulk-fetch Modrinth projects
project_ids = [m["project_id"] for m in mods if m.get("project_id")]
projects = {}
for i in range(0, len(project_ids), 100):
    batch = project_ids[i:i+100]
    q = urllib.parse.quote(json.dumps(batch, separators=(",", ":")))
    for p in http_json(f"https://api.modrinth.com/v2/projects?ids={q}"):
        projects[p["id"]] = p
print(f"fetched {len(projects)} project entries from Modrinth")

# 3. Bulk-fetch teams to resolve author (owner) usernames
team_ids_ordered, seen = [], set()
for p in projects.values():
    tid = p.get("team")
    if tid and tid not in seen:
        team_ids_ordered.append(tid); seen.add(tid)
team_authors = {}
for i in range(0, len(team_ids_ordered), 50):
    batch = team_ids_ordered[i:i+50]
    q = urllib.parse.quote(json.dumps(batch, separators=(",", ":")))
    data = http_json(f"https://api.modrinth.com/v2/teams?ids={q}")
    for tid, members in zip(batch, data):
        owner = next((m for m in members if str(m.get("role","")).lower() == "owner"),
                     members[0] if members else None)
        team_authors[tid] = (owner["user"]["username"] if owner else "?")
print(f"resolved {len(team_authors)} team owners")

# 4. Build card data
cards = []
for m in mods:
    pid = m.get("project_id")
    side = m.get("side", "both")
    if pid and pid in projects:
        p = projects[pid]
        cards.append({
            "title":   p["title"],
            "slug":    p["slug"],
            "author":  team_authors.get(p.get("team"), "?"),
            "desc":    (p.get("description") or "").strip(),
            "icon":    p.get("icon_url") or "",
            "dl":      p.get("downloads", 0),
            "followers": p.get("followers", 0),
            "upd":     p.get("updated", ""),
            "chips":   (p.get("categories") or [])[:3] + ([side] if side != "both" else []),
            "url":     f"https://modrinth.com/mod/{p['slug']}",
        })
    elif m["slug_file"] in MANUAL:
        manual = MANUAL[m["slug_file"]]
        cards.append({
            "title": manual["title"], "slug": m["slug_file"], "author": manual["author"],
            "desc": manual["description"], "icon": manual.get("icon",""),
            "dl": 0, "followers": 0, "upd": "",
            "chips": manual["categories"] + ([side] if side != "both" else []),
            "url": manual["url"],
        })
    else:
        # Anything unmapped — show as a stub
        cards.append({
            "title": m.get("name") or m["slug_file"], "slug": m["slug_file"],
            "author": "?", "desc": "", "icon": "",
            "dl": 0, "followers": 0, "upd": "",
            "chips": [side] if side != "both" else [],
            "url": "#",
        })

cards.sort(key=lambda c: c["title"].lower())

total_dl = sum(c["dl"] for c in cards)
ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# 5. Render HTML
HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>squirrelpack — mod list</title>
<style>
:root {
  --bg: #16181c; --card: #1e2024; --card-h: #4a4d54; --border: #2c2e33;
  --text: #e6e6e6; --dim: #8e9197; --accent: #1bd96a; --chip: #2c2e33;
}
* { box-sizing: border-box; }
body { margin:0; padding:24px 16px; background:var(--bg); color:var(--text);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; }
.wrap { max-width: 1100px; margin: 0 auto; }
header { margin-bottom: 24px; }
h1 { font-size: 1.9em; margin: 0 0 6px; }
.meta { color: var(--dim); font-size: 0.95em; }
.meta a { color: var(--accent); text-decoration: none; }
.controls { display:flex; gap:10px; margin: 20px 0; flex-wrap:wrap; }
.controls input, .controls select {
  background:var(--card); border:1px solid var(--border); color:var(--text);
  padding:9px 12px; border-radius:8px; font-size:0.95em; font-family:inherit;
}
.controls input { flex:1; min-width:220px; }
.controls input:focus, .controls select:focus { outline:none; border-color:var(--accent); }
#count { color: var(--dim); font-size: 0.9em; margin-bottom: 10px; }
.card { display:flex; background:var(--card); border:1px solid var(--border);
  border-radius:10px; padding:16px; margin-bottom:10px; text-decoration:none;
  color:inherit; transition:border-color .15s; }
.card:hover { border-color: var(--card-h); }
.icon { width:64px; height:64px; border-radius:8px; margin-right:16px;
  flex-shrink:0; background:#0a0b0d; object-fit:cover; }
.icon-placeholder { display:flex; align-items:center; justify-content:center;
  font-weight:700; font-size:1.4em; color:var(--dim); }
.body { flex:1; min-width:0; }
.row1 { display:flex; align-items:baseline; gap:8px; flex-wrap:wrap; }
.title { font-size:1.15em; font-weight:700; }
.author { color: var(--dim); font-size: 0.95em; }
.desc { color:var(--text); font-size:0.95em; margin:6px 0 10px; line-height:1.4;
  display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical;
  overflow:hidden; }
.chips { display:flex; gap:6px; flex-wrap:wrap; }
.chip { background:var(--chip); color:var(--dim); padding:3px 9px;
  border-radius:999px; font-size:0.78em; }
.chip.client { background:#3a2530; color:#ffb4c2; }
.chip.server { background:#1f3548; color:#9ec5f0; }
.stats { text-align:right; color:var(--dim); font-size:0.85em; flex-shrink:0;
  margin-left:16px; min-width:130px; }
.stats .num { color:var(--text); font-weight:700; }
.stats .stat { margin-bottom:3px; }
footer { color:var(--dim); font-size:0.85em; margin-top:30px; text-align:center; }
@media (max-width: 640px) {
  .stats { display:none; } .icon { width:48px; height:48px; margin-right:12px; }
}
</style>
</head>
<body>
<div class="wrap">
<header>
<h1>squirrelpack</h1>
<div class="meta">NeoForge __MC__ · __NMODS__ mods · __DLS__ combined Modrinth downloads ·
<a href="https://github.com/keuerle/squirrelpack">GitHub</a> ·
<a href="https://github.com/keuerle/squirrelpack/raw/main/squirrelpack-prism-instance.zip">Download Prism instance</a></div>
</header>
<div class="controls">
<input id="q" type="search" placeholder="Search by name, description, or author…" />
<select id="sort">
  <option value="name">Sort: name (A-Z)</option>
  <option value="dl">Sort: downloads</option>
  <option value="upd">Sort: recently updated</option>
</select>
</div>
<div id="count"></div>
<div id="list"></div>
<footer>Generated __TS__ · click any card to open the mod's page</footer>
</div>
<script>
const mods = __MODS_JSON__;
const list = document.getElementById('list');
const q = document.getElementById('q');
const sort = document.getElementById('sort');
const cnt = document.getElementById('count');
const fmt = n => n.toLocaleString();
const esc = s => (s==null?'':String(s)).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const initial = t => (t||'?').replace(/[^a-z]/i,'').charAt(0).toUpperCase() || '?';
function render() {
  const term = q.value.toLowerCase().trim();
  let arr = mods.filter(m => !term ||
    (m.title + ' ' + m.desc + ' ' + (m.author||'')).toLowerCase().includes(term));
  const s = sort.value;
  if (s === 'dl') arr.sort((a,b) => b.dl - a.dl);
  else if (s === 'upd') arr.sort((a,b) => (b.upd||'').localeCompare(a.upd||''));
  else arr.sort((a,b) => a.title.toLowerCase().localeCompare(b.title.toLowerCase()));
  cnt.textContent = `${arr.length} of ${mods.length} mods`;
  list.innerHTML = arr.map(m => `
    <a class="card" href="${esc(m.url)}" target="_blank" rel="noopener">
      ${m.icon
        ? `<img class="icon" src="${esc(m.icon)}" loading="lazy" alt="" onerror="this.outerHTML='<div class=&quot;icon icon-placeholder&quot;>'+'${initial(m.title)}'+'</div>'">`
        : `<div class="icon icon-placeholder">${esc(initial(m.title))}</div>`}
      <div class="body">
        <div class="row1">
          <div class="title">${esc(m.title)}</div>
          <div class="author">by ${esc(m.author)}</div>
        </div>
        <div class="desc">${esc(m.desc)}</div>
        <div class="chips">${m.chips.map(c => {
          const cls = (c==='client'||c==='server') ? ` ${c}` : '';
          return `<span class="chip${cls}">${esc(c)}</span>`;
        }).join('')}</div>
      </div>
      <div class="stats">
        ${m.dl ? `<div class="stat"><span class="num">${fmt(m.dl)}</span> downloads</div>` : ''}
        ${m.followers ? `<div class="stat"><span class="num">${fmt(m.followers)}</span> followers</div>` : ''}
        ${m.upd ? `<div class="stat">${new Date(m.upd).toISOString().slice(0,10)}</div>` : ''}
      </div>
    </a>`).join('');
}
q.addEventListener('input', render);
sort.addEventListener('change', render);
render();
</script>
</body>
</html>
"""

out = (HTML
       .replace("__MC__", "1.21.1")
       .replace("__NMODS__", str(len(cards)))
       .replace("__DLS__", f"{total_dl:,}")
       .replace("__TS__", ts)
       .replace("__MODS_JSON__", json.dumps(cards, separators=(",",":")).replace("</", "<\\/")))

with open(OUT_HTML, "w") as f:
    f.write(out)
print(f"wrote {OUT_HTML} ({os.path.getsize(OUT_HTML):,} bytes, {len(cards)} cards, {total_dl:,} total downloads)")

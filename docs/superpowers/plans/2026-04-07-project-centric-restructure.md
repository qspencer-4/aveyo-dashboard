# Project-Centric Restructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the Aveyo dashboard bottom nav into 9 scrollable tabs (Home + 7 PM responsibilities + Knowledge), each showing a filtered queue list with consistent design patterns and an app-wide 3-color status system.

**Architecture:** Single HTML file PWA (aveyo-dashboard.html). All changes are in-place edits to the existing file — new CSS classes, new HTML view divs, new JS functions for each tab. Each tab lazy-loads its Podio data on first tap, caches per session. Existing project detail view, Home dashboard, and Knowledge tab stay untouched.

**Tech Stack:** Vanilla HTML/CSS/JS, Podio REST API, existing fetchAllItems() utility

---

## File Structure

All changes are in a single file:
- **Modify:** `aveyo-dashboard.html` — CSS, HTML views, JS functions
- **Modify:** `sw.js` — version bump per task

No new files created. The existing file has these sections (by line number ranges, approximate):
- CSS: lines 15-1270
- HTML views: lines 1277-1480
- JS constants/state: lines 1490-1560
- JS functions: lines 1560-5600+

---

### Task 1: Scrollable Bottom Nav with Badge Counts

**Files:**
- Modify: `aveyo-dashboard.html` (CSS ~line 580, HTML ~line 1417, JS ~line 1585)
- Modify: `sw.js:1`

- [ ] **Step 1: Add CSS for scrollable nav and badge counts**

Find the existing `.bnav` CSS (around line 580) and add after it:

```css
/* Scrollable bottom nav */
.bnav{overflow-x:auto!important;-webkit-overflow-scrolling:touch;scrollbar-width:none;gap:0!important;padding:0 4px!important}
.bnav::-webkit-scrollbar{display:none}
.bnav-btn{flex-shrink:0!important;min-width:auto!important;padding:8px 10px!important;gap:0!important}
.bnav-btn svg{display:none!important}
.bnav-btn span{font-size:7px!important;letter-spacing:.12em!important;white-space:nowrap!important}
.bnav-badge{font-size:6px;font-weight:700;padding:1px 4px;min-width:14px;text-align:center;margin-left:4px;display:inline-block}
.bnav-badge.normal{background:rgba(255,255,255,.15);color:#fff}
.bnav-badge.warn{background:#C9A96E;color:#000}
.bnav-badge.crit{background:#C97850;color:#000}
```

- [ ] **Step 2: Replace bottom nav HTML**

Replace the entire `<div class="bnav" id="bnav">` block (lines ~1417-1436) with:

```html
<div class="bnav" id="bnav" style="display:none">
  <button class="bnav-btn active" id="nav-home"><span>HOME</span></button>
  <button class="bnav-btn" id="nav-tickets"><span>TICKETS</span><span class="bnav-badge normal" id="badge-tickets"></span></button>
  <button class="bnav-btn" id="nav-comms"><span>COMMS</span><span class="bnav-badge normal" id="badge-comms"></span></button>
  <button class="bnav-btn" id="nav-sow"><span>SOW</span><span class="bnav-badge normal" id="badge-sow"></span></button>
  <button class="bnav-btn" id="nav-preinstall"><span>PRE-INSTALL</span><span class="bnav-badge normal" id="badge-preinstall"></span></button>
  <button class="bnav-btn" id="nav-review"><span>REVIEW</span><span class="bnav-badge normal" id="badge-review"></span></button>
  <button class="bnav-btn" id="nav-change"><span>CHANGE</span><span class="bnav-badge normal" id="badge-change"></span></button>
  <button class="bnav-btn" id="nav-roof"><span>ROOF</span><span class="bnav-badge normal" id="badge-roof"></span></button>
  <button class="bnav-btn" id="nav-kb"><span>KB</span></button>
</div>
```

- [ ] **Step 3: Add view divs for new tabs**

After the existing `view-kb` div, add empty view containers for each new tab:

```html
<div id="view-tickets" class="view">
  <div class="resp-filter" id="tickets-filters"></div>
  <div class="resp-loading" id="tickets-loading" style="display:none"><div class="spinner"></div>Loading...</div>
  <div class="resp-list" id="tickets-list"></div>
</div>
<div id="view-comms" class="view">
  <div class="resp-filter" id="comms-filters"></div>
  <div class="resp-loading" id="comms-loading" style="display:none"><div class="spinner"></div>Loading...</div>
  <div class="resp-list" id="comms-list"></div>
</div>
<div id="view-sowresp" class="view">
  <div class="resp-filter" id="sowresp-filters"></div>
  <div class="resp-loading" id="sowresp-loading" style="display:none"><div class="spinner"></div>Loading...</div>
  <div class="resp-list" id="sowresp-list"></div>
</div>
<div id="view-preinstall" class="view">
  <div class="resp-filter" id="preinstall-filters"></div>
  <div class="resp-loading" id="preinstall-loading" style="display:none"><div class="spinner"></div>Loading...</div>
  <div class="resp-list" id="preinstall-list"></div>
</div>
<div id="view-review" class="view">
  <div class="resp-filter" id="review-filters"></div>
  <div class="resp-loading" id="review-loading" style="display:none"><div class="spinner"></div>Loading...</div>
  <div class="resp-list" id="review-list"></div>
</div>
<div id="view-change" class="view">
  <div class="resp-filter" id="change-filters"></div>
  <div class="resp-loading" id="change-loading" style="display:none"><div class="spinner"></div>Loading...</div>
  <div class="resp-list" id="change-list"></div>
</div>
<div id="view-roof" class="view">
  <div class="resp-filter" id="roof-filters"></div>
  <div class="resp-loading" id="roof-loading" style="display:none"><div class="spinner"></div>Loading...</div>
  <div class="resp-list" id="roof-list"></div>
</div>
```

- [ ] **Step 4: Add shared CSS for responsibility tab views**

```css
/* Responsibility tab shared styles */
.resp-filter{padding:8px 16px;display:flex;gap:5px;border-bottom:1px solid rgba(255,255,255,.04);overflow-x:auto;-webkit-overflow-scrolling:touch}
.resp-chip{font-size:7px;letter-spacing:.1em;padding:4px 6px;white-space:nowrap;flex-shrink:0;cursor:pointer;border:1px solid rgba(255,255,255,.08);color:rgba(255,255,255,.3);background:transparent;font-family:'PPTelegraf',sans-serif;text-transform:uppercase}
.resp-chip.active{color:#fff;border-color:transparent;border-bottom:2px solid #fff}
.resp-chip.urgent{color:#E88B8B;border-color:rgba(232,139,139,.25)}
.resp-chip.good{color:#ADD8E6;border-color:rgba(173,216,230,.25)}
.resp-list{padding:0}
.resp-loading{padding:2rem;text-align:center}
.resp-row{padding:14px 16px;border-bottom:1px solid rgba(255,255,255,.04);cursor:pointer;transition:background .1s}
.resp-row:active{background:rgba(255,255,255,.03)}
.resp-row-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:4px}
.resp-row-id{color:#fff;font-size:13px;font-weight:700;letter-spacing:.02em}
.resp-row-name{color:#fff;font-size:12px;font-weight:600;margin-bottom:3px}
.resp-row-meta{color:rgba(255,255,255,.35);font-size:9px;letter-spacing:.04em;margin-bottom:5px}
.resp-row-desc{color:rgba(255,255,255,.55);font-size:10px;line-height:1.4;margin-bottom:8px}
.resp-row-bottom{display:flex;justify-content:space-between;align-items:center}
.resp-row-creator{color:rgba(255,255,255,.25);font-size:9px}
.resp-row-creator b{color:rgba(255,255,255,.5);font-weight:400}
.resp-timer{font-size:9px;font-weight:700;letter-spacing:.04em}
.resp-timer.fresh{color:#ADD8E6}
.resp-timer.moderate{color:#fff}
.resp-timer.overdue{color:#E88B8B}
.resp-badge{font-size:6px;font-weight:700;padding:2px 8px;letter-spacing:.1em;text-transform:uppercase;white-space:nowrap}
.resp-badge.good{background:rgba(173,216,230,.12);color:#ADD8E6;border:1px solid rgba(173,216,230,.2)}
.resp-badge.neutral{background:rgba(255,255,255,.06);color:rgba(255,255,255,.5);border:1px solid rgba(255,255,255,.1)}
.resp-badge.urgent{background:rgba(232,139,139,.12);color:#E88B8B;border:1px solid rgba(232,139,139,.2)}
.resp-check{font-size:7px;letter-spacing:.06em}
.resp-check.good{color:#ADD8E6}
.resp-check.bad{color:#E88B8B}
.resp-check.pending{color:rgba(255,255,255,.2)}
```

- [ ] **Step 5: Update setActiveNav to handle new tabs**

Replace the existing `setActiveNav` function:

```javascript
function setActiveNav(tab){
  document.querySelectorAll('.bnav-btn').forEach(b=>b.classList.remove('active'));
  const el = document.getElementById('nav-'+tab);
  if(el) el.classList.add('active');
}
```

- [ ] **Step 6: Update SUBS and showView for new views**

Update the SUBS constant to include new tab subtitles:

```javascript
const SUBS={home:'Dashboard',projects:'My Projects',wlist:'',detail:'Project Detail',auth:'Sign In',tickets:'Support Tickets',comms:'Communications',sowresp:'Scope of Work',preinstall:'Pre-Install',review:'Project Review',change:'Change Orders',roof:'Roof Reviews',kb:'Knowledge Base'};
```

Update `showView` — add the new view names to the refresh button logic:

```javascript
document.getElementById('btn-refresh').style.display=(v==='home'||v==='projects'||v==='tickets'||v==='comms'||v==='sowresp'||v==='preinstall'||v==='review'||v==='change'||v==='roof')?'block':'none';
```

- [ ] **Step 7: Wire nav button click handlers**

Add event listeners for all new nav buttons. Each one calls setActiveNav, showView, and a load function (to be implemented in subsequent tasks — stub them for now):

```javascript
document.getElementById('nav-home').addEventListener('click',()=>{setActiveNav('home');showView('home');loadHome();});
document.getElementById('nav-tickets').addEventListener('click',()=>{setActiveNav('tickets');showView('tickets');loadTickets();});
document.getElementById('nav-comms').addEventListener('click',()=>{setActiveNav('comms');showView('comms');loadCommsTab();});
document.getElementById('nav-sow').addEventListener('click',()=>{setActiveNav('sow');showView('sowresp');loadSOWResp();});
document.getElementById('nav-preinstall').addEventListener('click',()=>{setActiveNav('preinstall');showView('preinstall');loadPreInstall();});
document.getElementById('nav-review').addEventListener('click',()=>{setActiveNav('review');showView('review');loadReview();});
document.getElementById('nav-change').addEventListener('click',()=>{setActiveNav('change');showView('change');loadChangeOrders();});
document.getElementById('nav-roof').addEventListener('click',()=>{setActiveNav('roof');showView('roof');loadRoof();});
document.getElementById('nav-kb').addEventListener('click',()=>{setActiveNav('kb');showView('kb');loadKB();});
```

Remove old nav-sow, nav-action, nav-comm, nav-projects event listeners. Keep nav-projects wiring but change its handler to use the existing projects view:

```javascript
document.getElementById('nav-projects')?.addEventListener('click',()=>{setActiveNav('projects');showView('projects');if(!ALL_ITEMS.length)loadProjects();});
```

Note: nav-projects button is removed from the nav HTML but the projects view still exists and is accessed from Home widgets.

- [ ] **Step 8: Add stub load functions**

Add placeholder functions so the app doesn't error. Each will be replaced in subsequent tasks:

```javascript
// Responsibility tab stubs — replaced in Tasks 2-8
function loadTickets(){ document.getElementById('tickets-list').innerHTML='<div class="resp-row"><div class="resp-row-desc">Loading tickets...</div></div>'; }
function loadCommsTab(){ document.getElementById('comms-list').innerHTML='<div class="resp-row"><div class="resp-row-desc">Loading communications...</div></div>'; }
function loadSOWResp(){ document.getElementById('sowresp-list').innerHTML='<div class="resp-row"><div class="resp-row-desc">Loading SOW...</div></div>'; }
function loadPreInstall(){ document.getElementById('preinstall-list').innerHTML='<div class="resp-row"><div class="resp-row-desc">Loading pre-install...</div></div>'; }
function loadReview(){ document.getElementById('review-list').innerHTML='<div class="resp-row"><div class="resp-row-desc">Loading reviews...</div></div>'; }
function loadChangeOrders(){ document.getElementById('change-list').innerHTML='<div class="resp-row"><div class="resp-row-desc">Loading change orders...</div></div>'; }
function loadRoof(){ document.getElementById('roof-list').innerHTML='<div class="resp-row"><div class="resp-row-desc">Loading roof reviews...</div></div>'; }
```

- [ ] **Step 9: Add badge count updater function**

Add a function that reads cached widget counts and updates badge elements:

```javascript
function updateNavBadges(){
  const badgeMap = [
    {id:'badge-tickets', wi:3},   // Open Support Tickets (widget index 3)
    {id:'badge-comms', wi:17},    // Rep Update Needed (index 18) + Customer Update Needed (index 17)
    {id:'badge-sow', wi:4},      // Total in SOW (index 4)
    {id:'badge-preinstall', wi:14}, // Ready for Pre-Install (index 14)
    {id:'badge-review', wi:2},   // Project Review Needed (index 2)
    {id:'badge-change', wi:16},  // Design Change Orders (index 16)
    {id:'badge-roof', wi:19},    // Roof Review Needed (index 19)
  ];
  badgeMap.forEach(({id, wi})=>{
    const el = document.getElementById(id);
    if(!el) return;
    const [,,appId,viewId,warn,crit] = WIDGETS[wi]||[];
    const v = cGet(appId+'_'+viewId);
    if(v===null || v===0){ el.style.display='none'; return; }
    el.style.display='inline-block';
    el.textContent = v;
    el.className = 'bnav-badge ' + (v>=crit?'crit':v>=warn?'warn':'normal');
  });
}
```

Call `updateNavBadges()` at the end of `loadHome()` after widget counts are fetched.

- [ ] **Step 10: Add shared helper function for timer class**

```javascript
function timerClass(days, reviewMode){
  if(reviewMode) return days>=7?'overdue':'fresh';
  if(days>=14) return 'overdue';
  if(days>=3) return 'moderate';
  return 'fresh';
}
function timerText(dateStr){
  if(!dateStr) return {text:'--', days:0};
  const d = new Date(dateStr);
  const now = new Date();
  const diff = Math.floor((now-d)/(1000*60*60*24));
  const hrs = Math.floor(((now-d)%(1000*60*60*24))/(1000*60*60));
  return {text: diff+'d '+hrs+'h', days: diff};
}
```

- [ ] **Step 11: Version bump**

Update `const VERSION='v112'` to `const VERSION='v113'` in aveyo-dashboard.html.
Update `const VERSION = 'v112'` to `const VERSION = 'v113'` in sw.js.

- [ ] **Step 12: Verify and commit**

Open the app, confirm:
- Bottom nav scrolls horizontally with text-only tabs
- Badge counts appear (may show -- if cache is empty)
- Tapping each tab shows the stub loading text
- Home and KB tabs still work as before

```bash
git add aveyo-dashboard.html sw.js
git commit -m "v113: Scrollable bottom nav with 9 tabs and badge counts"
git push origin main
```

---

### Task 2: Tickets Tab

**Files:**
- Modify: `aveyo-dashboard.html` (JS section, ~after the stub functions)

- [ ] **Step 1: Add state variables**

```javascript
let TICKETS_ITEMS = [];
let TICKETS_FILTER = 'all';
```

- [ ] **Step 2: Implement loadTickets function**

Replace the stub `loadTickets` with:

```javascript
async function loadTickets(){
  if(TICKETS_ITEMS.length){ renderTickets(); return; }
  document.getElementById('tickets-loading').style.display='block';
  document.getElementById('tickets-list').innerHTML='';
  try{
    const raw = await fetchAllItems(29840119, 61747488);
    TICKETS_ITEMS = raw.map(item=>{
      const fields = item.fields||[];
      const fv = (fid)=>{ const f=fields.find(f=>f.field_id===fid); return f?.values?.[0]?.value?.text||f?.values?.[0]?.value||''; };
      const title = item.title||'';
      const status = fv(266494686)||'Open';
      const desc = fv(266494687)||'';
      const created = item.created_on||'';
      const createdBy = item.created_by?.name||'';
      // Parse customer name and address from title
      const parts = title.split(' - ');
      const name = parts[0]?.replace(/^#\S+\s*/,'').trim()||title;
      const address = parts[1]?.trim()||'';
      const tidMatch = title.match(/^#?(\d+)/)||item.item_id;
      const tid = typeof tidMatch==='object'?(tidMatch[1]||item.item_id):tidMatch;
      return {id:item.item_id, tid:'#'+tid, name, address, status: status.trim(), desc: desc.substring(0,200), created, createdBy, raw:item};
    });
    renderTickets();
  }catch(e){
    document.getElementById('tickets-list').innerHTML='<div class="resp-row"><div class="resp-row-desc" style="color:#E88B8B">Error: '+x(e.message)+'</div></div>';
  }
  document.getElementById('tickets-loading').style.display='none';
}
```

- [ ] **Step 3: Implement renderTickets function**

```javascript
function renderTickets(){
  // Filter chips
  const counts = {all:TICKETS_ITEMS.length, open:0, assigned:0};
  TICKETS_ITEMS.forEach(t=>{
    const s=t.status.toLowerCase();
    if(s.includes('assign')) counts.assigned++;
    else if(!s.includes('complet')&&!s.includes('cancel')) counts.open++;
  });
  document.getElementById('tickets-filters').innerHTML=
    ['all','open','assigned'].map(f=>{
      const n = counts[f];
      const cls = f===TICKETS_FILTER?'resp-chip active':(f==='open'&&n>0?'resp-chip urgent':'resp-chip');
      return `<span class="${cls}" data-tfilter="${f}">${f.toUpperCase()} ${n}</span>`;
    }).join('');

  // Filter items
  let items = [...TICKETS_ITEMS];
  if(TICKETS_FILTER==='open') items=items.filter(t=>!t.status.toLowerCase().includes('complet')&&!t.status.toLowerCase().includes('cancel')&&!t.status.toLowerCase().includes('assign'));
  if(TICKETS_FILTER==='assigned') items=items.filter(t=>t.status.toLowerCase().includes('assign'));

  // Sort newest first
  items.sort((a,b)=>new Date(b.created)-new Date(a.created));

  // Render
  document.getElementById('tickets-list').innerHTML = items.length ? items.map(t=>{
    const timer = timerText(t.created);
    const tc = timerClass(timer.days);
    const statusLower = t.status.toLowerCase();
    const badgeCls = statusLower.includes('complet')?'neutral':statusLower.includes('assign')?'neutral':'good';
    return `<div class="resp-row" data-itemid="${t.id}">
      <div class="resp-row-top"><span class="resp-row-id">${x(t.tid)}</span><span class="resp-badge ${badgeCls}">${x(t.status.toUpperCase())}</span></div>
      <div class="resp-row-name">${x(t.name)}</div>
      ${t.address?`<div class="resp-row-meta">${x(t.address)}</div>`:''}
      ${t.desc?`<div class="resp-row-desc">${x(t.desc)}</div>`:''}
      <div class="resp-row-bottom"><span class="resp-row-creator">Created by <b>${x(t.createdBy)}</b></span><span class="resp-timer ${tc}">${timer.text}</span></div>
    </div>`;
  }).join('') : '<div class="resp-row"><div class="resp-row-desc" style="color:rgba(255,255,255,.3)">No tickets found.</div></div>';
}
```

- [ ] **Step 4: Wire filter chip clicks and row clicks**

```javascript
document.addEventListener('click',function(e){
  const chip = e.target.closest('[data-tfilter]');
  if(chip){ TICKETS_FILTER=chip.dataset.tfilter; renderTickets(); return; }
  const row = e.target.closest('#tickets-list .resp-row[data-itemid]');
  if(row){ PREV_VIEW='tickets'; openDetail(parseInt(row.dataset.itemid)); }
});
```

- [ ] **Step 5: Verify and commit**

Open app, tap TICKETS tab. Confirm:
- Loading spinner shows, then ticket list appears
- Each row: bold ticket ID, status badge, name, address, description, creator, age timer
- Filter chips work (All/Open/Assigned)
- Tapping a row opens project detail
- Timer colors: light blue < 3d, white 3-14d, red > 14d

```bash
git add aveyo-dashboard.html
git commit -m "v113: Implement Tickets tab with queue list and filters"
```

---

### Task 3: Comms Tab

**Files:**
- Modify: `aveyo-dashboard.html` (JS section)

- [ ] **Step 1: Add state variables**

```javascript
let COMMS_ITEMS = [];
let COMMS_FILTER = 'all';
```

- [ ] **Step 2: Implement loadCommsTab function**

Replace the stub with:

```javascript
async function loadCommsTab(){
  if(COMMS_ITEMS.length){ renderCommsTab(); return; }
  document.getElementById('comms-loading').style.display='block';
  document.getElementById('comms-list').innerHTML='';
  try{
    // Fetch both views: Customer Update Needed + Rep Update Needed
    const [custRaw, repRaw] = await Promise.all([
      fetchAllItems(29839792, 61743343),
      fetchAllItems(29839792, 61743344)
    ]);
    const seen = new Set();
    const parse = (items, type)=> items.map(item=>{
      if(seen.has(item.item_id)) return null;
      seen.add(item.item_id);
      const parsed = parseItem(item);
      const repName = parseRepName(parsed.repInfo);
      const lastComment = (parsed.comments||'').split('***')[0]?.trim()||'';
      const commentDate = (lastComment.match(/^(\d{4}-\d{2}-\d{2})/)||[])[1]||'';
      return {...parsed, commType:type, repName, lastContactDate:commentDate||parsed.lastReview||''};
    }).filter(Boolean);
    COMMS_ITEMS = [...parse(repRaw,'rep'), ...parse(custRaw,'customer')];
    // Sort by longest since last contact
    COMMS_ITEMS.sort((a,b)=>{
      const da = a.lastContactDate?new Date(a.lastContactDate):new Date(0);
      const db = b.lastContactDate?new Date(b.lastContactDate):new Date(0);
      return da-db; // oldest contact first
    });
    renderCommsTab();
  }catch(e){
    document.getElementById('comms-list').innerHTML='<div class="resp-row"><div class="resp-row-desc" style="color:#E88B8B">Error: '+x(e.message)+'</div></div>';
  }
  document.getElementById('comms-loading').style.display='none';
}
```

- [ ] **Step 3: Implement renderCommsTab function**

```javascript
function renderCommsTab(){
  const counts = {all:COMMS_ITEMS.length, rep:COMMS_ITEMS.filter(c=>c.commType==='rep').length, customer:COMMS_ITEMS.filter(c=>c.commType==='customer').length};
  document.getElementById('comms-filters').innerHTML=
    ['all','rep','customer'].map(f=>{
      const n = counts[f];
      const cls = f===COMMS_FILTER?'resp-chip active':'resp-chip';
      return `<span class="${cls}" data-cfilter="${f}">${f.toUpperCase()} ${n}</span>`;
    }).join('');

  let items = COMMS_FILTER==='all'?COMMS_ITEMS:COMMS_ITEMS.filter(c=>c.commType===COMMS_FILTER);

  document.getElementById('comms-list').innerHTML = items.length ? items.map(c=>{
    const timer = timerText(c.lastContactDate);
    const tc = timerClass(timer.days);
    const badge = c.commType==='rep'?'good':'neutral';
    const label = c.commType==='rep'?'REP UPDATE':'CUSTOMER TEXT';
    return `<div class="resp-row" data-itemid="${c.id}">
      <div class="resp-row-top"><span class="resp-row-name" style="margin:0">${x(c.name)}</span><span class="resp-badge ${badge}">${label}</span></div>
      <div class="resp-row-meta">${x(c.milestone||'')} ${c.repName?'· '+x(c.repName):''}</div>
      <div class="resp-row-desc">${x((c.notes||'').substring(0,150))}</div>
      <div class="resp-row-bottom"><span class="resp-row-creator">Last contact: <b>${timer.days}d ago</b></span><span class="resp-timer ${tc}">${timer.text}</span></div>
    </div>`;
  }).join('') : '<div class="resp-row"><div class="resp-row-desc" style="color:rgba(255,255,255,.3)">No updates needed.</div></div>';
}
```

- [ ] **Step 4: Wire filter and row clicks**

```javascript
document.addEventListener('click',function(e){
  const chip = e.target.closest('[data-cfilter]');
  if(chip){ COMMS_FILTER=chip.dataset.cfilter; renderCommsTab(); return; }
  const row = e.target.closest('#comms-list .resp-row[data-itemid]');
  if(row){ PREV_VIEW='comms'; openDetail(parseInt(row.dataset.itemid)); }
});
```

- [ ] **Step 5: Verify and commit**

```bash
git add aveyo-dashboard.html
git commit -m "v113: Implement Comms tab with rep/customer filter"
```

---

### Task 4: SOW Tab

**Files:**
- Modify: `aveyo-dashboard.html` (JS section)

- [ ] **Step 1: Add state variables**

```javascript
let SOWRESP_ITEMS = [];
let SOWRESP_FILTER = 'all';
```

- [ ] **Step 2: Implement loadSOWResp function**

Replace the stub with:

```javascript
async function loadSOWResp(){
  if(SOWRESP_ITEMS.length){ renderSOWResp(); return; }
  document.getElementById('sowresp-loading').style.display='block';
  document.getElementById('sowresp-list').innerHTML='';
  try{
    const raw = await fetchAllItems(SOW_APP_ID, 61743309); // Total in SOW view
    SOWRESP_ITEMS = raw.map(item=>{
      const fields = item.fields||[];
      const title = item.title||'';
      const name = title.replace(/^#\S+\s+/,'').split(' - ')[0]||title;
      const address = title.split(' - ')[1]||'';
      const systemSize = sowFV(fields, SOW_FIELD.systemSize);
      const contractPrice = sowFV(fields, SOW_FIELD.contractPrice);
      const systemMatches = sowFV(fields, SOW_FIELD.systemSizeMatches);
      const priceMatches = sowFV(fields, SOW_FIELD.contractPriceMatches);
      const designMatches = sowFV(fields, SOW_FIELD.designMatches);
      const roofReview = sowFV(fields, SOW_FIELD.roofReview);
      const electricalWork = sowFV(fields, SOW_FIELD.electricalWork);
      const repScope = sowFV(fields, SOW_FIELD.repScopeApproval);
      const custSOW = sowFV(fields, SOW_FIELD.customerSOWStatus);
      const milestone = sowFV(fields, 269930958)||'';
      // Determine SOW status for filtering
      let sowStatus = 'ready';
      if(custSOW&&custSOW.toLowerCase().includes('reject')) sowStatus='reject';
      else if(repScope&&(repScope.toLowerCase().includes('sent')||repScope.toLowerCase().includes('pending'))) sowStatus='repsow';
      else if(custSOW&&(custSOW.toLowerCase().includes('sent')||custSOW.toLowerCase().includes('approved'))) sowStatus='custsow';
      return {id:item.item_id, name, address, systemSize, contractPrice, systemMatches, priceMatches, designMatches, roofReview, electricalWork, sowStatus, milestone, raw:item};
    });
    renderSOWResp();
  }catch(e){
    document.getElementById('sowresp-list').innerHTML='<div class="resp-row"><div class="resp-row-desc" style="color:#E88B8B">Error: '+x(e.message)+'</div></div>';
  }
  document.getElementById('sowresp-loading').style.display='none';
}
```

- [ ] **Step 3: Implement renderSOWResp function**

```javascript
function renderSOWResp(){
  const counts = {all:SOWRESP_ITEMS.length, ready:0, repsow:0, custsow:0, reject:0};
  SOWRESP_ITEMS.forEach(s=>{ counts[s.sowStatus]=(counts[s.sowStatus]||0)+1; });
  document.getElementById('sowresp-filters').innerHTML=
    ['all','ready','repsow','custsow','reject'].map(f=>{
      const labels = {all:'ALL',ready:'READY',repsow:'REP SOW',custsow:'CUST SOW',reject:'REJECT'};
      const n = counts[f];
      const cls = f===SOWRESP_FILTER?'resp-chip active':(f==='reject'&&n>0?'resp-chip urgent':'resp-chip');
      return `<span class="${cls}" data-sfilter="${f}">${labels[f]} ${n}</span>`;
    }).join('');

  let items = SOWRESP_FILTER==='all'?SOWRESP_ITEMS:SOWRESP_ITEMS.filter(s=>s.sowStatus===SOWRESP_FILTER);

  function checkMark(val){ if(!val) return '<span class="resp-check pending">--</span>'; const v=val.toLowerCase(); if(v==='yes'||v.includes('approved')) return '<span class="resp-check good">&#10003;</span>'; if(v==='no'||v.includes('needed')) return '<span class="resp-check bad">&#10007;</span>'; return '<span class="resp-check pending">--</span>'; }

  document.getElementById('sowresp-list').innerHTML = items.length ? items.map(s=>{
    const statusLabels = {ready:'READY FOR SOW',repsow:'REP SOW SENT',custsow:'CUST SOW SENT',reject:'REJECTED'};
    const badgeCls = s.sowStatus==='reject'?'urgent':s.sowStatus==='ready'?'urgent':'good';
    const price = s.contractPrice?'$'+parseFloat(s.contractPrice).toLocaleString():'';
    return `<div class="resp-row" data-sowid="${s.id}">
      <div class="resp-row-top"><span class="resp-row-name" style="margin:0">${x(s.name)}</span><span class="resp-badge ${badgeCls}">${statusLabels[s.sowStatus]||'SOW'}</span></div>
      <div class="resp-row-meta">${s.systemSize?x(s.systemSize)+' kW':''}${price?' · '+x(price):''}${s.milestone?' · '+x(s.milestone):''}</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:4px">
        <span class="resp-check-label">SIZE ${checkMark(s.systemMatches)}</span>
        <span class="resp-check-label">PRICE ${checkMark(s.priceMatches)}</span>
        <span class="resp-check-label">DESIGN ${checkMark(s.designMatches)}</span>
        <span class="resp-check-label">ROOF ${checkMark(s.roofReview)}</span>
        <span class="resp-check-label">ELEC ${checkMark(s.electricalWork)}</span>
      </div>
    </div>`;
  }).join('') : '<div class="resp-row"><div class="resp-row-desc" style="color:rgba(255,255,255,.3)">No SOW items.</div></div>';
}
```

- [ ] **Step 4: Add CSS for check labels and wire clicks**

```css
.resp-check-label{font-size:7px;letter-spacing:.06em;color:rgba(255,255,255,.4);display:inline-flex;align-items:center;gap:2px}
```

```javascript
document.addEventListener('click',function(e){
  const chip = e.target.closest('[data-sfilter]');
  if(chip){ SOWRESP_FILTER=chip.dataset.sfilter; renderSOWResp(); return; }
  const row = e.target.closest('#sowresp-list .resp-row[data-sowid]');
  if(row){ openSOWDetail(parseInt(row.dataset.sowid)); }
});
```

- [ ] **Step 5: Verify and commit**

```bash
git add aveyo-dashboard.html
git commit -m "v113: Implement SOW tab with verification checklist"
```

---

### Task 5: Pre-Install Tab

**Files:**
- Modify: `aveyo-dashboard.html` (JS section)

- [ ] **Step 1: Add state and implement loadPreInstall**

```javascript
let PREINSTALL_ITEMS = [];
let PREINSTALL_FILTER = 'all';

async function loadPreInstall(){
  if(PREINSTALL_ITEMS.length){ renderPreInstall(); return; }
  document.getElementById('preinstall-loading').style.display='block';
  document.getElementById('preinstall-list').innerHTML='';
  try{
    const [ready, issues] = await Promise.all([
      fetchAllItems(29839773, 61743334),
      fetchAllItems(29839773, 61743335)
    ]);
    const seen = new Set();
    const parse = (items, status)=> items.map(item=>{
      if(seen.has(item.item_id)) return null;
      seen.add(item.item_id);
      const title = item.title||'';
      const name = title.replace(/^#\S+\s+/,'').split(' - ')[0]||title;
      const address = title.split(' - ')[1]||'';
      const milestone = (item.fields||[]).find(f=>f.field_id===269930958);
      const ms = milestone?.values?.[0]?.value||'';
      return {id:item.item_id, name, address, status, milestone:ms, title};
    }).filter(Boolean);
    PREINSTALL_ITEMS = [...parse(ready,'ready'), ...parse(issues,'issue')];
    renderPreInstall();
  }catch(e){
    document.getElementById('preinstall-list').innerHTML='<div class="resp-row"><div class="resp-row-desc" style="color:#E88B8B">Error: '+x(e.message)+'</div></div>';
  }
  document.getElementById('preinstall-loading').style.display='none';
}
```

- [ ] **Step 2: Implement renderPreInstall**

```javascript
function renderPreInstall(){
  const counts = {all:PREINSTALL_ITEMS.length, ready:PREINSTALL_ITEMS.filter(p=>p.status==='ready').length, issue:PREINSTALL_ITEMS.filter(p=>p.status==='issue').length};
  document.getElementById('preinstall-filters').innerHTML=
    ['all','ready','issue'].map(f=>{
      const labels = {all:'ALL',ready:'READY',issue:'ISSUES'};
      const n = counts[f];
      const cls = f===PREINSTALL_FILTER?'resp-chip active':(f==='issue'&&n>0?'resp-chip urgent':'resp-chip');
      return `<span class="${cls}" data-pifilter="${f}">${labels[f]} ${n}</span>`;
    }).join('');

  let items = PREINSTALL_FILTER==='all'?PREINSTALL_ITEMS:PREINSTALL_ITEMS.filter(p=>p.status===PREINSTALL_FILTER);

  document.getElementById('preinstall-list').innerHTML = items.length ? items.map(p=>{
    const badgeCls = p.status==='ready'?'good':'urgent';
    const label = p.status==='ready'?'READY':'ISSUE';
    return `<div class="resp-row" data-itemid="${p.id}">
      <div class="resp-row-top"><span class="resp-row-name" style="margin:0">${x(p.name)}</span><span class="resp-badge ${badgeCls}">${label}</span></div>
      <div class="resp-row-meta">${x(p.milestone)} · ${x(p.address)}</div>
    </div>`;
  }).join('') : '<div class="resp-row"><div class="resp-row-desc" style="color:rgba(255,255,255,.3)">No pre-install items.</div></div>';
}
```

- [ ] **Step 3: Wire clicks**

```javascript
document.addEventListener('click',function(e){
  const chip = e.target.closest('[data-pifilter]');
  if(chip){ PREINSTALL_FILTER=chip.dataset.pifilter; renderPreInstall(); return; }
  const row = e.target.closest('#preinstall-list .resp-row[data-itemid]');
  if(row){ PREV_VIEW='preinstall'; openDetail(parseInt(row.dataset.itemid)); }
});
```

- [ ] **Step 4: Verify and commit**

```bash
git add aveyo-dashboard.html
git commit -m "v113: Implement Pre-Install tab"
```

---

### Task 6: Review Tab

**Files:**
- Modify: `aveyo-dashboard.html` (JS section)

- [ ] **Step 1: Add state and implement loadReview**

```javascript
let REVIEW_FILTER = 'overdue';

async function loadReview(){
  // Uses ALL_ITEMS from Projects — load if needed
  if(!ALL_ITEMS.length) await loadProjects();
  renderReview();
}
```

- [ ] **Step 2: Implement renderReview**

```javascript
function renderReview(){
  const overdue = ALL_ITEMS.filter(i=>i.daysSince!==null&&i.daysSince>=7);
  const notSet = ALL_ITEMS.filter(i=>i.daysSince===null||i.lastReview===null||i.lastReview==='');
  const counts = {overdue:overdue.length, notset:notSet.length, all:ALL_ITEMS.length};

  document.getElementById('review-filters').innerHTML=
    ['overdue','notset','all'].map(f=>{
      const labels = {overdue:'OVERDUE',notset:'NOT SET',all:'ALL'};
      const n = counts[f];
      const cls = f===REVIEW_FILTER?'resp-chip active':(f==='overdue'&&n>0?'resp-chip urgent':'resp-chip');
      return `<span class="${cls}" data-rfilter="${f}">${labels[f]} ${n}</span>`;
    }).join('');

  let items;
  if(REVIEW_FILTER==='overdue') items=[...overdue];
  else if(REVIEW_FILTER==='notset') items=[...notSet];
  else items=[...ALL_ITEMS];

  // Sort by most days since review first
  items.sort((a,b)=>(b.daysSince||999)-(a.daysSince||999));

  document.getElementById('review-list').innerHTML = items.length ? items.map(i=>{
    const days = i.daysSince;
    const tc = days!==null ? timerClass(days, true) : 'overdue';
    const dayText = days!==null ? days+'d' : 'Not set';
    return `<div class="resp-row" data-itemid="${i.id}">
      <div class="resp-row-top"><span class="resp-row-name" style="margin:0">${x(i.name)}</span><span class="resp-timer ${tc}" style="font-size:11px">${dayText}</span></div>
      <div class="resp-row-meta">${x(i.milestone||'')} · ${x(i.address||'')}</div>
      <div style="color:rgba(255,255,255,.4);font-size:9px">${i.lastReview?'Last reviewed: '+x(i.lastReview):'No review date set'}</div>
    </div>`;
  }).join('') : '<div class="resp-row"><div class="resp-row-desc" style="color:rgba(255,255,255,.3)">No items.</div></div>';
}
```

- [ ] **Step 3: Wire clicks**

```javascript
document.addEventListener('click',function(e){
  const chip = e.target.closest('[data-rfilter]');
  if(chip){ REVIEW_FILTER=chip.dataset.rfilter; renderReview(); return; }
  const row = e.target.closest('#review-list .resp-row[data-itemid]');
  if(row){ PREV_VIEW='review'; openDetail(parseInt(row.dataset.itemid)); }
});
```

- [ ] **Step 4: Verify and commit**

```bash
git add aveyo-dashboard.html
git commit -m "v113: Implement Review tab sorted by days since review"
```

---

### Task 7: Change Orders Tab

**Files:**
- Modify: `aveyo-dashboard.html` (JS section)

- [ ] **Step 1: Add state and implement loadChangeOrders**

```javascript
let CHANGE_ITEMS = [];

async function loadChangeOrders(){
  if(CHANGE_ITEMS.length){ renderChangeOrders(); return; }
  document.getElementById('change-loading').style.display='block';
  document.getElementById('change-list').innerHTML='';
  try{
    const raw = await fetchAllItems(29841104, 61743336);
    CHANGE_ITEMS = raw.map(item=>{
      const title = item.title||'';
      const name = title.replace(/^#\S+\s+/,'').split(' - ')[0]||title;
      const address = title.split(' - ')[1]||'';
      const coId = (title.match(/^#?(CO-?\d+|\d+)/i)||[])[1]||item.item_id;
      const created = item.created_on||'';
      const createdBy = item.created_by?.name||'';
      const fields = item.fields||[];
      const descField = fields.find(f=>f.values?.[0]?.value?.text);
      const desc = descField?.values?.[0]?.value?.text||descField?.values?.[0]?.value||'';
      return {id:item.item_id, coId:'#CO-'+coId, name, address, desc:String(desc).substring(0,200), created, createdBy};
    });
    renderChangeOrders();
  }catch(e){
    document.getElementById('change-list').innerHTML='<div class="resp-row"><div class="resp-row-desc" style="color:#E88B8B">Error: '+x(e.message)+'</div></div>';
  }
  document.getElementById('change-loading').style.display='none';
}
```

- [ ] **Step 2: Implement renderChangeOrders**

```javascript
function renderChangeOrders(){
  document.getElementById('change-filters').innerHTML='';
  const items = [...CHANGE_ITEMS].sort((a,b)=>new Date(b.created)-new Date(a.created));

  document.getElementById('change-list').innerHTML = items.length ? items.map(c=>{
    const timer = timerText(c.created);
    const tc = timerClass(timer.days);
    return `<div class="resp-row" data-itemid="${c.id}">
      <div class="resp-row-top"><span class="resp-row-id">${x(c.coId)}</span><span class="resp-badge good">DESIGN CHANGE</span></div>
      <div class="resp-row-name">${x(c.name)}</div>
      ${c.address?`<div class="resp-row-meta">${x(c.address)}</div>`:''}
      ${c.desc?`<div class="resp-row-desc">${x(c.desc)}</div>`:''}
      <div class="resp-row-bottom"><span class="resp-row-creator">Created by <b>${x(c.createdBy)}</b></span><span class="resp-timer ${tc}">${timer.text}</span></div>
    </div>`;
  }).join('') : '<div class="resp-row"><div class="resp-row-desc" style="color:rgba(255,255,255,.3)">No change orders.</div></div>';
}
```

- [ ] **Step 3: Wire row clicks**

```javascript
document.addEventListener('click',function(e){
  const row = e.target.closest('#change-list .resp-row[data-itemid]');
  if(row){ PREV_VIEW='change'; openDetail(parseInt(row.dataset.itemid)); }
});
```

- [ ] **Step 4: Verify and commit**

```bash
git add aveyo-dashboard.html
git commit -m "v113: Implement Change Orders tab"
```

---

### Task 8: Roof Tab

**Files:**
- Modify: `aveyo-dashboard.html` (JS section)

- [ ] **Step 1: Add state and implement loadRoof**

```javascript
let ROOF_ITEMS = [];
let ROOF_FILTER = 'all';

async function loadRoof(){
  if(ROOF_ITEMS.length){ renderRoof(); return; }
  document.getElementById('roof-loading').style.display='block';
  document.getElementById('roof-list').innerHTML='';
  try{
    const raw = await fetchAllItems(29839741, 61743345);
    ROOF_ITEMS = raw.map(item=>{
      const title = item.title||'';
      const name = title.replace(/^#\S+\s+/,'').split(' - ')[0]||title;
      const address = title.split(' - ')[1]||'';
      const created = item.created_on||'';
      const fields = item.fields||[];
      // Determine roof type — look for a field indicating customer/aveyo/not set
      const roofTypeField = fields.find(f=>f.values?.[0]?.value?.text?.toLowerCase().includes('customer')||f.values?.[0]?.value?.text?.toLowerCase().includes('aveyo'));
      const roofTypeVal = roofTypeField?.values?.[0]?.value?.text||roofTypeField?.values?.[0]?.value||'';
      let roofType = 'notset';
      if(typeof roofTypeVal==='string'){
        if(roofTypeVal.toLowerCase().includes('customer')) roofType='customer';
        else if(roofTypeVal.toLowerCase().includes('aveyo')) roofType='aveyo';
      }
      const descField = fields.find(f=>f.values?.[0]?.value?.text&&f!==roofTypeField);
      const desc = descField?.values?.[0]?.value?.text||descField?.values?.[0]?.value||'';
      return {id:item.item_id, name, address, roofType, desc:String(desc).substring(0,200), created};
    });
    renderRoof();
  }catch(e){
    document.getElementById('roof-list').innerHTML='<div class="resp-row"><div class="resp-row-desc" style="color:#E88B8B">Error: '+x(e.message)+'</div></div>';
  }
  document.getElementById('roof-loading').style.display='none';
}
```

- [ ] **Step 2: Implement renderRoof**

```javascript
function renderRoof(){
  const counts = {all:ROOF_ITEMS.length, customer:0, aveyo:0, notset:0};
  ROOF_ITEMS.forEach(r=>{ counts[r.roofType]=(counts[r.roofType]||0)+1; });

  document.getElementById('roof-filters').innerHTML=
    ['all','customer','aveyo','notset'].map(f=>{
      const labels = {all:'ALL',customer:'CUSTOMER',aveyo:'AVEYO',notset:'NOT SET'};
      const n = counts[f];
      const cls = f===ROOF_FILTER?'resp-chip active':(f==='notset'&&n>0?'resp-chip urgent':(f==='customer'?'resp-chip good':'resp-chip'));
      return `<span class="${cls}" data-rffilter="${f}">${labels[f]} ${n}</span>`;
    }).join('');

  let items = ROOF_FILTER==='all'?ROOF_ITEMS:ROOF_ITEMS.filter(r=>r.roofType===ROOF_FILTER);

  document.getElementById('roof-list').innerHTML = items.length ? items.map(r=>{
    const timer = timerText(r.created);
    const tc = timerClass(timer.days);
    const badgeMap = {customer:'good',aveyo:'neutral',notset:'urgent'};
    const labelMap = {customer:'CUSTOMER ROOF',aveyo:'AVEYO ROOF',notset:'NOT SET'};
    return `<div class="resp-row" data-itemid="${r.id}">
      <div class="resp-row-top"><span class="resp-row-name" style="margin:0">${x(r.name)}</span><span class="resp-badge ${badgeMap[r.roofType]}">${labelMap[r.roofType]}</span></div>
      ${r.address?`<div class="resp-row-meta">${x(r.address)}</div>`:''}
      ${r.desc?`<div class="resp-row-desc">${x(r.desc)}</div>`:''}
      <div class="resp-row-bottom"><span class="resp-row-creator">Flagged: <b>${r.created?new Date(r.created).toLocaleDateString():''}</b></span><span class="resp-timer ${tc}">${timer.text}</span></div>
    </div>`;
  }).join('') : '<div class="resp-row"><div class="resp-row-desc" style="color:rgba(255,255,255,.3)">No roof reviews.</div></div>';
}
```

- [ ] **Step 3: Wire clicks**

```javascript
document.addEventListener('click',function(e){
  const chip = e.target.closest('[data-rffilter]');
  if(chip){ ROOF_FILTER=chip.dataset.rffilter; renderRoof(); return; }
  const row = e.target.closest('#roof-list .resp-row[data-itemid]');
  if(row){ PREV_VIEW='roof'; openDetail(parseInt(row.dataset.itemid)); }
});
```

- [ ] **Step 4: Final version bump and cleanup**

Remove old nav-sow, nav-action, nav-comm event listeners and any dead references.
Update doRefresh to handle new tab views.
Final version in title tag.

- [ ] **Step 5: Verify all tabs and commit**

Open the app and verify every tab works:
- HOME: dashboard loads as before
- TICKETS: queue list with bold IDs, status badges, timers
- COMMS: filtered queue with rep/customer chips
- SOW: mini checklists inline
- PRE-INSTALL: ready/issues filter
- REVIEW: sorted by days, 7+ is red
- CHANGE: bold CO IDs, creator names
- ROOF: customer/aveyo/not set filters
- KB: knowledge base loads as before

```bash
git add aveyo-dashboard.html sw.js
git commit -m "v113: Implement Roof tab and complete project-centric restructure"
git push origin main
```

# Ticket Detail View Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a purpose-built ticket detail view that opens when clicking a ticket from the queue, showing ticket info, status controls, inline compose actions, tabbed project context, and project navigation with pipeline stages and Drive folder links.

**Architecture:** Single new view (`#view-ticket-detail`) in `aveyo-dashboard.html` with its own build/render functions. Reuses existing Podio API patterns, parser functions, and compose flow. Desktop splits into left (tabbed content) and right (project navigation sidebar).

**Tech Stack:** Vanilla JS, Podio REST API, existing VPS backend endpoints

**Spec:** `docs/superpowers/specs/2026-04-08-ticket-detail-view-design.md`

---

### Task 1: Add HTML Container and CSS

**Files:**
- Modify: `aveyo-dashboard.html:1513` (after `view-tickets` closing div, add new view container)
- Modify: `aveyo-dashboard.html:~680` (add CSS in the Battlefront theme override section)

- [ ] **Step 1: Add the view container HTML**

Insert after line 1513 (`</div>` closing `view-tickets`):

```html
<!-- TICKET DETAIL VIEW -->
<div id="view-ticket-detail" class="view">
  <div id="td-back-bar"></div>
  <div id="td-header"></div>
  <div id="td-status"></div>
  <div id="td-actions"></div>
  <div id="td-compose"></div>
  <div id="td-tabs-bar"></div>
  <div id="td-tab-content"></div>
  <div id="td-prev-next"></div>
  <!-- Desktop split: right sidebar -->
  <div id="td-sidebar" class="td-sidebar"></div>
</div>
```

- [ ] **Step 2: Add CSS for the ticket detail view**

Insert in the Battlefront theme CSS section (after line ~680, near the other view styles):

```css
/* ── TICKET DETAIL VIEW ─────────────────────────────── */
#view-ticket-detail{background:#000}
#td-back-bar{display:flex;justify-content:space-between;align-items:center;padding:10px 12px;border-bottom:1px solid #1a1a1a}
#td-back-bar .td-back{color:#ADD8E6;font-size:11px;font-weight:700;cursor:pointer}
#td-back-bar .td-pos{color:rgba(255,255,255,.3);font-size:10px}
#td-header{background:#1a1a1a;padding:12px 14px;border-left:3px solid #ADD8E6}
#td-header .td-ticket-num{color:#ADD8E6;font-weight:700;font-size:15px;letter-spacing:.5px}
#td-header .td-customer{color:#fff;font-size:13px;font-weight:600;margin-top:2px}
#td-header .td-address{color:rgba(255,255,255,.4);font-size:10px;margin-top:1px}
#td-header .td-desc{color:#ddd;font-size:11px;line-height:1.5;margin-top:8px}
#td-header .td-meta{display:flex;gap:8px;margin-top:6px;align-items:center;flex-wrap:wrap;color:rgba(255,255,255,.4);font-size:9px}
#td-header .td-context{display:flex;gap:8px;margin-top:6px;padding-top:6px;border-top:1px solid rgba(255,255,255,.08);align-items:center;flex-wrap:wrap}
#td-header .td-age{text-align:right}
#td-header .td-age-num{font-size:14px;font-weight:700}
#td-header .td-age-label{font-size:8px;text-transform:uppercase;letter-spacing:1px;color:rgba(255,255,255,.3)}
#td-status{display:flex;gap:3px;padding:8px 12px;background:#000}
.td-status-pill{flex:1;text-align:center;padding:8px 0;font-size:9px;letter-spacing:.5px;cursor:pointer;transition:opacity .15s;border:none;color:rgba(255,255,255,.4);background:#1a1a1a;font-family:inherit;font-weight:700}
.td-status-pill:active{opacity:.7}
.td-status-pill.active-new{background:#C97850;color:#fff}
.td-status-pill.active-assigned{background:#C9A96E;color:#fff}
.td-status-pill.active-inprogress{background:#ADD8E6;color:#000}
.td-status-pill.active-complete{background:rgba(255,255,255,.35);color:#fff}
#td-actions{display:flex;gap:4px;padding:0 12px 10px;background:#000}
.td-action-btn{flex:1;text-align:center;padding:9px 0;font-size:9px;font-weight:700;letter-spacing:.5px;cursor:pointer;border:1px solid rgba(255,255,255,.2);color:rgba(255,255,255,.5);background:transparent;font-family:inherit;transition:opacity .15s}
.td-action-btn:active{opacity:.7}
.td-action-btn.primary{border-color:#ADD8E6;color:#ADD8E6}
.td-action-btn.active{background:#ADD8E6;color:#000;border-color:#ADD8E6}
#td-compose{display:none;margin:4px 12px 8px;border:1px solid #ADD8E6;padding:12px;background:#0d0d0d}
#td-compose.open{display:block}
#td-compose .td-compose-label{color:rgba(255,255,255,.4);font-size:9px;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px}
#td-compose textarea{width:100%;min-height:60px;border:1px solid #333;padding:10px;color:#ddd;font-size:11px;background:#111;font-family:inherit;resize:vertical;line-height:1.5;box-sizing:border-box}
#td-compose textarea:focus{outline:none;border-color:#ADD8E6}
#td-compose .td-compose-btns{display:flex;gap:4px;margin-top:8px}
#td-compose .td-compose-submit{flex:1;text-align:center;background:#ADD8E6;color:#000;padding:10px 0;font-size:10px;font-weight:700;letter-spacing:.5px;border:none;cursor:pointer;font-family:inherit}
#td-compose .td-compose-cancel{text-align:center;border:1px solid rgba(255,255,255,.2);color:rgba(255,255,255,.4);padding:10px 16px;font-size:10px;background:transparent;cursor:pointer;font-family:inherit}
#td-tabs-bar{display:flex;border-bottom:1px solid #333;background:#000;overflow-x:auto}
.td-tab{padding:8px 14px;font-size:10px;color:rgba(255,255,255,.3);white-space:nowrap;cursor:pointer;border-bottom:2px solid transparent;font-family:inherit;background:transparent;border-top:none;border-left:none;border-right:none}
.td-tab.active{color:#fff;border-bottom-color:#fff;font-weight:700}
.td-tab .td-tab-count{color:#E88B8B}
#td-tab-content{background:#0a0a0a;min-height:200px}
.td-activity-row{padding:10px 14px;border-bottom:1px solid #1a1a1a}
.td-activity-date{display:flex;justify-content:space-between;color:rgba(255,255,255,.5);font-size:10px;font-weight:600}
.td-activity-author{color:#ADD8E6;font-size:10px;font-weight:600;margin-top:2px}
.td-activity-body{color:#ddd;font-size:10px;margin-top:2px;line-height:1.4}
.td-activity-system .td-activity-author{color:rgba(255,255,255,.4)}
.td-activity-system .td-activity-body{color:rgba(255,255,255,.6)}
#td-prev-next{display:flex;justify-content:space-between;align-items:center;padding:12px 14px;background:#000;border-top:1px solid #1a1a1a}
#td-prev-next .td-nav-btn{color:#ADD8E6;font-size:11px;font-weight:700;cursor:pointer;background:transparent;border:none;font-family:inherit}
#td-prev-next .td-nav-pos{color:rgba(255,255,255,.3);font-size:10px}
/* Pipeline stages */
.td-stage{display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid rgba(255,255,255,.04);cursor:pointer;text-decoration:none}
.td-stage:active{opacity:.7}
.td-stage-dot{width:6px;height:6px;flex-shrink:0}
.td-stage-dot.done{background:#ADD8E6}
.td-stage-dot.current{width:8px;height:8px;background:#ADD8E6;box-shadow:0 0 6px rgba(173,216,230,.5)}
.td-stage-dot.future{background:rgba(255,255,255,.12)}
.td-stage-name{font-size:9px;flex:1;letter-spacing:.5px}
.td-stage.done .td-stage-name{color:rgba(255,255,255,.25)}
.td-stage.current .td-stage-name{color:#ADD8E6;font-weight:700;font-size:10px}
.td-stage.future .td-stage-name{color:rgba(255,255,255,.15)}
.td-stage-status{font-size:8px}
.td-stage.done .td-stage-status{color:rgba(255,255,255,.15)}
.td-stage.current .td-stage-status{color:#ADD8E6;font-weight:700;font-size:9px}
.td-stage.future .td-stage-status{color:rgba(255,255,255,.1)}
.td-stage.current{background:rgba(173,216,230,.08);padding:7px 6px;margin:2px -6px}
/* Drive folder buttons */
.td-drive-btn{border:1px solid rgba(255,255,255,.15);color:rgba(255,255,255,.5);padding:6px 12px;font-size:9px;letter-spacing:.5px;text-decoration:none;display:inline-block}
.td-drive-btn:active{opacity:.7}
/* Section labels */
.td-section-label{color:rgba(255,255,255,.4);font-size:9px;text-transform:uppercase;letter-spacing:1px;font-weight:700}
/* Desktop sidebar */
.td-sidebar{display:none}
@media(min-width:768px){
  #view-ticket-detail{display:flex;flex-direction:column}
  .td-sidebar{display:block;flex:0 0 280px;background:#0a0a0a;padding:14px 16px;border-left:1px solid #1a1a1a}
  #view-ticket-detail.active .td-split{display:flex}
  .td-split{display:flex}
  .td-split-left{flex:1}
  .td-tab-project-mobile{display:none!important}
  #td-prev-next{display:none}
  #td-back-bar .td-desktop-nav{display:flex;align-items:center;gap:8px}
  #td-back-bar .td-desktop-nav .td-nav-btn{color:#ADD8E6;font-size:11px;font-weight:700;cursor:pointer;background:transparent;border:none;font-family:inherit}
}
@media(max-width:767px){
  .td-sidebar{display:none!important}
  .td-desktop-nav{display:none!important}
}
```

- [ ] **Step 3: Commit**

```bash
git add aveyo-dashboard.html
git commit -m "feat: add ticket detail view HTML container and CSS"
```

---

### Task 2: Build the Ticket Detail View — Header, Status, and Back Bar

**Files:**
- Modify: `aveyo-dashboard.html` (add JS functions after the `loadRoof` function around line ~2289)

- [ ] **Step 1: Add global state variables**

Insert after line ~1632 (near `let TICKETS_ITEMS = [];`):

```javascript
let TD_TICKET = null;    // current ticket item from TICKETS_ITEMS
let TD_PROJECT = null;   // matched project from ALL_ITEMS
let TD_TAB = 'activity'; // active context tab
let TD_COMPOSE = null;   // active compose type: 'comment','rep','customer' or null
let TD_LIST = [];        // filtered ticket list for prev/next
let TD_INDEX = 0;        // current index in TD_LIST
```

- [ ] **Step 2: Add `openTicketDetail` function**

Insert after `loadRoof` function (~line 2289):

```javascript
// ── TICKET DETAIL VIEW ──────────────────────────────────
function openTicketDetail(ticket, project){
  TD_TICKET = ticket;
  TD_PROJECT = project;
  TD_TAB = 'activity';
  TD_COMPOSE = null;
  SCROLL_POS['tickets_scroll'] = window.scrollY;

  // Build navigation list from current filtered tickets
  let items = [...TICKETS_ITEMS];
  if(TICKETS_FILTER==='new') items=items.filter(t=>t.status.toLowerCase()==='new');
  else if(TICKETS_FILTER==='assigned') items=items.filter(t=>t.status.toLowerCase()==='assigned');
  else if(TICKETS_FILTER==='inprogress') items=items.filter(t=>t.status.toLowerCase()==='in progress');
  items=items.filter(t=>{const s=t.status.toLowerCase();return s!=='complete'&&s!=='cancelled';});
  items.sort((a,b)=>new Date(b.created)-new Date(a.created));
  TD_LIST = items;
  TD_INDEX = items.findIndex(t=>t.id===ticket.id);
  if(TD_INDEX<0) TD_INDEX=0;

  buildTicketDetail();
  showView('ticket-detail');
  setActiveNav('tickets');
  window.scrollTo(0,0);
}
```

- [ ] **Step 3: Add `buildTicketDetail` function — back bar and header**

```javascript
function buildTicketDetail(){
  const t = TD_TICKET;
  const p = TD_PROJECT;
  if(!t) return;

  // Parse project context
  const stage = p ? getDetailedStage(p) : '';
  const repRaw = p ? (p.repInfo||'') : '';
  const repName = (repRaw.match(/Rep Name:[*\s]+([^\n*]+)/i)||[])[1]||'';
  const repPhone = (repRaw.match(/Phone:[*\s]+([^\n*]+)/i)||[])[1]||'';
  const repEmail = (repRaw.match(/Email:[*\s]+([^\n*]+)/i)||[])[1]||'';

  const timer = timerText(t.created);
  const tc = timerClass(timer.days);
  const ageColor = tc==='overdue'?'#E88B8B':tc==='moderate'?'#fff':'#ADD8E6';

  // Back bar
  document.getElementById('td-back-bar').innerHTML =
    '<span class="td-back" id="td-back-btn">< TICKETS</span>'+
    '<span class="td-pos">'+(TD_INDEX+1)+' / '+TD_LIST.length+'</span>'+
    '<span class="td-desktop-nav">'+
      '<button class="td-nav-btn" id="td-desk-prev">< PREV</button>'+
      '<span style="color:rgba(255,255,255,.2);margin:0 4px">|</span>'+
      '<button class="td-nav-btn" id="td-desk-next">NEXT ></button>'+
    '</span>';

  // Header
  const fullDesc = (t.raw && t.raw.title) ? t.raw.title.split(' - ').slice(3).join(' - ') : t.desc;
  const cleanFullDesc = (fullDesc||t.desc||'').replace(/<br\s*\/?>/gi,' ').replace(/<[^>]*>/g,' ').replace(/\s+/g,' ').trim();

  document.getElementById('td-header').innerHTML =
    '<div style="display:flex;justify-content:space-between;align-items:flex-start">'+
      '<div>'+
        '<div class="td-ticket-num">'+x(t.tid)+'</div>'+
        '<div class="td-customer">'+x(t.name)+'</div>'+
        (t.address?'<div class="td-address">'+x(t.address)+'</div>':'')+
      '</div>'+
      '<div class="td-age">'+
        '<div class="td-age-num" style="color:'+ageColor+'">'+timer.text+'</div>'+
        '<div class="td-age-label">AGE</div>'+
      '</div>'+
    '</div>'+
    '<div style="height:1px;background:#333;margin:8px 0"></div>'+
    '<div class="td-desc">'+x(cleanFullDesc)+'</div>'+
    '<div class="td-meta">'+
      (t.ticketType?'<span>'+x(t.ticketType)+'</span><span style="color:rgba(255,255,255,.2)">|</span>':'')+
      (t.creator?'<span>Created by '+x(t.creator)+'</span>':'')+
    '</div>'+
    (p?'<div class="td-context">'+
      '<span style="color:#ADD8E6;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.5px">'+x(stage)+'</span>'+
      (repName?'<span style="color:rgba(255,255,255,.15)">|</span><span style="color:rgba(255,255,255,.4);font-size:9px">Rep: '+x(repName)+'</span>':'')+
      (repPhone?'<span style="color:rgba(255,255,255,.15)">|</span><span style="color:rgba(255,255,255,.4);font-size:9px">'+x(repPhone)+'</span>':'')+
    '</div>':'');

  // Status
  buildTicketStatus();
  // Actions
  buildTicketActions();
  // Tabs
  buildTicketTabs();
  // Tab content
  renderTicketTabContent();
  // Prev/Next
  buildTicketPrevNext();
  // Desktop sidebar
  buildTicketSidebar(stage, repName, repPhone, repEmail);
}
```

- [ ] **Step 4: Add `buildTicketStatus` function**

```javascript
function buildTicketStatus(){
  const current = TD_TICKET.status.toLowerCase().replace(/\s+/g,'');
  const statuses = [
    {key:'new',label:'NEW',mobileLabel:'NEW'},
    {key:'assigned',label:'ASSIGNED',mobileLabel:'ASSIGNED'},
    {key:'inprogress',label:'IN PROGRESS',mobileLabel:'IN PROG'},
    {key:'complete',label:'COMPLETE',mobileLabel:'COMPLETE'}
  ];
  document.getElementById('td-status').innerHTML = statuses.map(s=>{
    const isActive = current===s.key;
    const cls = isActive ? 'td-status-pill active-'+s.key : 'td-status-pill';
    const label = window.innerWidth<768 ? s.mobileLabel : s.label;
    return '<button class="'+cls+'" data-td-status="'+s.key+'">'+label+'</button>';
  }).join('');
}
```

- [ ] **Step 5: Commit**

```bash
git add aveyo-dashboard.html
git commit -m "feat: ticket detail view — header, status bar, back nav"
```

---

### Task 3: Action Buttons and Inline Compose

**Files:**
- Modify: `aveyo-dashboard.html` (continue adding functions after Task 2's code)

- [ ] **Step 1: Add `buildTicketActions` function**

```javascript
function buildTicketActions(){
  const btns = [
    {key:'comment',label:'COMMENT',primary:true},
    {key:'rep',label:'MSG REP',primary:false},
    {key:'customer',label:'MSG CUST',primary:false}
  ];
  document.getElementById('td-actions').innerHTML = btns.map(b=>{
    const cls = TD_COMPOSE===b.key ? 'td-action-btn active' : ('td-action-btn'+(b.primary?' primary':''));
    return '<button class="'+cls+'" data-td-action="'+b.key+'">'+b.label+'</button>';
  }).join('');
}
```

- [ ] **Step 2: Add `openTicketCompose` and `closeTicketCompose` functions**

```javascript
function openTicketCompose(type){
  TD_COMPOSE = type;
  buildTicketActions();
  const t = TD_TICKET;
  const p = TD_PROJECT;
  const repName = p ? ((p.repInfo||'').match(/Rep Name:[*\s]+([^\n*]+)/i)||[])[1]||'' : '';
  const labels = {
    comment:'ADD COMMENT TO TICKET '+t.tid,
    rep:'MESSAGE REP'+(repName?' — '+repName.toUpperCase():''),
    customer:'MESSAGE CUSTOMER — '+t.name.toUpperCase()
  };
  const submitLabels = {comment:'POST COMMENT',rep:'SEND TO REP',customer:'SEND TO CUSTOMER'};
  const el = document.getElementById('td-compose');
  el.innerHTML =
    '<div class="td-compose-label">'+x(labels[type])+'</div>'+
    '<textarea id="td-compose-ta" placeholder="Type your message..."></textarea>'+
    (type!=='comment'?'<div style="margin-top:6px"><button class="td-action-btn primary" id="td-compose-generate" style="width:100%">GENERATE WITH AI</button></div>':'')+
    '<div class="td-compose-btns">'+
      '<button class="td-compose-submit" id="td-compose-send" data-td-compose-type="'+type+'" disabled>'+submitLabels[type]+'</button>'+
      '<button class="td-compose-cancel" id="td-compose-cancel">CANCEL</button>'+
    '</div>';
  el.classList.add('open');
}

function closeTicketCompose(){
  TD_COMPOSE = null;
  buildTicketActions();
  document.getElementById('td-compose').classList.remove('open');
  document.getElementById('td-compose').innerHTML = '';
}
```

- [ ] **Step 3: Commit**

```bash
git add aveyo-dashboard.html
git commit -m "feat: ticket detail view — action buttons and inline compose"
```

---

### Task 4: Context Tabs and Tab Content Rendering

**Files:**
- Modify: `aveyo-dashboard.html` (continue adding functions)

- [ ] **Step 1: Add `buildTicketTabs` function**

```javascript
function buildTicketTabs(){
  const p = TD_PROJECT;
  // Count other tickets for this project
  const otherTickets = TD_TICKET.projectNum ?
    TICKETS_ITEMS.filter(t=>t.projectNum===TD_TICKET.projectNum && t.id!==TD_TICKET.id &&
      !['complete','cancelled'].includes(t.status.toLowerCase())) : [];
  // Count work orders
  const wBlocks = p ? parseBlocks(p.workOrders||'',/\\---|\n---\n/).filter(b=>b.includes('WO-')||b.includes('Type:')) : [];

  let html = '';
  html += '<button class="td-tab'+(TD_TAB==='activity'?' active':'')+'" data-td-tab="activity">ACTIVITY</button>';
  html += '<button class="td-tab'+(TD_TAB==='tickets'?' active':'')+'" data-td-tab="tickets">'+(window.innerWidth<768?'TICKETS':'TICKETS')+
    (otherTickets.length?' <span class="td-tab-count">'+otherTickets.length+'</span>':'')+'</button>';
  html += '<button class="td-tab'+(TD_TAB==='workorders'?' active':'')+'" data-td-tab="workorders">'+(window.innerWidth<768?'WOs':'WORK ORDERS')+
    (wBlocks.length?' <span class="td-tab-count" style="color:rgba(255,255,255,.3)">'+wBlocks.length+'</span>':'')+'</button>';
  // PROJECT tab only on mobile
  html += '<button class="td-tab td-tab-project-mobile'+(TD_TAB==='project'?' active':'')+'" data-td-tab="project">PROJECT</button>';

  document.getElementById('td-tabs-bar').innerHTML = html;
}
```

- [ ] **Step 2: Add `renderTicketTabContent` function**

```javascript
function renderTicketTabContent(){
  const t = TD_TICKET;
  const p = TD_PROJECT;
  const el = document.getElementById('td-tab-content');

  if(TD_TAB==='activity'){
    if(!p || !p.comments){
      el.innerHTML='<div class="td-activity-row"><div class="td-activity-body" style="color:rgba(255,255,255,.3)">No activity found.</div></div>';
      return;
    }
    const blocks = parseBlocks(p.comments, /\*{3}/);
    if(!blocks.length){
      el.innerHTML='<div class="td-activity-row"><div class="td-activity-body" style="color:rgba(255,255,255,.3)">No comments.</div></div>';
      return;
    }
    el.innerHTML = blocks.map(b=>{
      const lines=b.split('\n').map(l=>l.trim()).filter(Boolean);
      const m=lines[0]&&lines[0].match(/^(\d{4}-\d{2}-\d{2})\s+\d{2}:\d{2}:\d{2}\s+(.+)/);
      const date=m?m[1]:'';
      const author=m?m[2]:'';
      const body=lines.slice(m?1:0).join(' ');
      const isSystem=author.toLowerCase().includes('system')||author.toLowerCase().includes('podio');
      const ago=date?timerText(date):{text:''};
      return '<div class="td-activity-row'+(isSystem?' td-activity-system':'')+'">'+
        '<div class="td-activity-date"><span>'+x(date)+(author?' · ':'')+
        '</span><span>'+x(ago.text||'')+'</span></div>'+
        (author?'<div class="td-activity-author">'+x(author)+'</div>':'')+
        '<div class="td-activity-body">'+x(body.substring(0,500))+(body.length>500?'...':'')+'</div>'+
      '</div>';
    }).join('');

  } else if(TD_TAB==='tickets'){
    const others = t.projectNum ?
      TICKETS_ITEMS.filter(ti=>ti.projectNum===t.projectNum && ti.id!==t.id &&
        !['complete','cancelled'].includes(ti.status.toLowerCase())) : [];
    if(!others.length){
      el.innerHTML='<div class="td-activity-row"><div class="td-activity-body" style="color:rgba(255,255,255,.3)">No other open tickets for this project.</div></div>';
      return;
    }
    el.innerHTML = others.map(ti=>{
      const timer=timerText(ti.created);
      const tc2=timerClass(timer.days);
      const sl=ti.status.toLowerCase();
      const badgeCls=sl==='new'?'urgent':sl==='assigned'?'neutral':sl==='in progress'?'good':'neutral';
      return '<div class="td-activity-row" style="cursor:pointer" data-td-switch-ticket="'+ti.id+'">'+
        '<div class="td-activity-date"><span>'+x(ti.tid)+'</span><span class="resp-badge '+badgeCls+'" style="font-size:8px;padding:1px 6px">'+x(ti.status.toUpperCase())+'</span></div>'+
        (ti.desc?'<div class="td-activity-body">'+x(ti.desc)+'</div>':'')+
        '<div style="color:rgba(255,255,255,.3);font-size:9px;margin-top:2px">'+x(timer.text)+'</div>'+
      '</div>';
    }).join('');

  } else if(TD_TAB==='workorders'){
    if(!p){
      el.innerHTML='<div class="td-activity-row"><div class="td-activity-body" style="color:rgba(255,255,255,.3)">No project matched.</div></div>';
      return;
    }
    const wBlocks = parseBlocks(p.workOrders||'',/\\---|\n---\n/).filter(b=>b.includes('WO-')||b.includes('Type:'));
    if(!wBlocks.length){
      el.innerHTML='<div class="td-activity-row"><div class="td-activity-body" style="color:rgba(255,255,255,.3)">No work orders.</div></div>';
      return;
    }
    el.innerHTML = wBlocks.map(b=>{
      const status=(b.match(/Status:\*?\*?\s*([^\n<*]+)/i)||[])[1]||'';
      const type=(b.match(/Type:\*?\*?\s*([^\n<*]+)/i)||[])[1]||'';
      const appt=(b.match(/Appointment:\*?\*?\s*([^\n<*]+)/i)||[])[1]||'';
      const desc=(b.match(/Description:\*?\*?\s*([^\n<*]+)/i)||[])[1]||'';
      const woId=(b.match(/\[WO-(\d+)\]/)||[])[1]||'';
      const woLink=(b.match(/\[WO-\d+\]\(([^)]+)\)/)||[])[1]||'';
      const cls=status.toLowerCase().includes('complet')?'ts-complete':status.toLowerCase().includes('assign')?'ts-assigned':'ts-open';
      return '<div class="td-activity-row">'+
        '<div class="td-activity-date"><span>'+(woId&&woLink?'<a href="'+woLink+'" target="_blank" style="color:#ADD8E6;text-decoration:none">WO-'+woId+'</a>':'')+
        (appt?' · '+x(appt.trim()):'')+'</span></div>'+
        (type?'<div style="font-weight:600;font-size:11px;color:#fff;margin-top:2px">'+x(type.trim())+'</div>':'')+
        (desc?'<div class="td-activity-body">'+x(desc.trim().substring(0,200))+'</div>':'')+
        (status?'<span class="te-status '+cls+'" style="margin-top:4px;display:inline-block">'+x(status.trim())+'</span>':'')+
      '</div>';
    }).join('');

  } else if(TD_TAB==='project'){
    renderTicketProjectTab(el);
  }

  // Wrap in split layout for desktop
  wrapTicketSplit();
}
```

- [ ] **Step 3: Add `renderTicketProjectTab` function**

```javascript
function renderTicketProjectTab(el){
  const t = TD_TICKET;
  const p = TD_PROJECT;
  const currentStage = p ? getDetailedStage(p) : '';
  const projectItemId = p ? p.id : '';

  // Pipeline stages (11 — no Complete)
  const stages = PIPELINE_STAGES.filter(s=>s.key!=='Complete' && s.key!=='On Hold');
  let foundCurrent = false;
  const stageHtml = stages.map(s=>{
    const isCurrent = s.key===currentStage || s.label===currentStage;
    if(isCurrent) foundCurrent = true;
    const state = isCurrent ? 'current' : (foundCurrent ? 'future' : 'done');
    const statusLabel = state==='done'?'DONE':state==='current'?'CURRENT':'--';
    const link = projectItemId ? 'https://podio.com/item/'+projectItemId : '#';
    return '<a href="'+link+'" target="_blank" class="td-stage '+state+'">'+
      '<div class="td-stage-dot '+state+'"></div>'+
      '<span class="td-stage-name">'+x(s.label.toUpperCase())+'</span>'+
      '<span class="td-stage-status">'+statusLabel+'</span>'+
    '</a>';
  }).join('');

  // Drive folders
  const driveDefs = [
    {label:'PARENT',fid:266618729},{label:'SITE SURVEY',fid:266618728},
    {label:'DESIGN',fid:266618723},{label:'APPROVED',fid:268981903},
    {label:'CUSTOMER DOCS',fid:266618731},{label:'PERMIT',fid:266618725}
  ];
  let driveHtml = '';
  if(p && p.raw && p.raw.fields){
    driveHtml = driveDefs.map(d=>{
      const f = p.raw ? (p.raw.fields||[]).find(f=>f.field_id===d.fid) : null;
      const val = f && f.values && f.values[0] ? f.values[0].value : null;
      if(!val) return '';
      return '<a href="https://drive.google.com/drive/folders/'+val+'" target="_blank" class="td-drive-btn">'+d.label+'</a>';
    }).filter(Boolean).join('');
  }

  // Podio links
  const ticketLink = 'https://podio.com/item/'+t.id;
  const projectLink = projectItemId ? 'https://podio.com/item/'+projectItemId : '';

  el.innerHTML =
    '<div style="padding:12px 14px">'+
      '<div class="td-section-label" style="margin-bottom:8px">PIPELINE — TAP STAGE TO OPEN IN PODIO</div>'+
      stageHtml+
      '<div class="td-section-label" style="margin:16px 0 8px;padding-top:10px;border-top:1px solid rgba(255,255,255,.08)">GOOGLE DRIVE</div>'+
      (driveHtml?'<div style="display:flex;flex-wrap:wrap;gap:4px">'+driveHtml+'</div>':'<div style="color:rgba(255,255,255,.3);font-size:10px">No Drive folders linked.</div>')+
      '<div style="margin-top:14px;padding-top:10px;border-top:1px solid rgba(255,255,255,.08)">'+
        '<a href="'+ticketLink+'" target="_blank" style="color:#ADD8E6;font-size:10px;text-decoration:none">Open Ticket in Podio</a>'+
        (projectLink?'<span style="color:rgba(255,255,255,.15);margin:0 8px">|</span>'+
        '<a href="'+projectLink+'" target="_blank" style="color:#ADD8E6;font-size:10px;text-decoration:none">Open Project in Podio</a>':'')+
      '</div>'+
    '</div>';
}
```

- [ ] **Step 4: Commit**

```bash
git add aveyo-dashboard.html
git commit -m "feat: ticket detail view — context tabs with activity, tickets, WOs, project"
```

---

### Task 5: Prev/Next Navigation and Desktop Sidebar

**Files:**
- Modify: `aveyo-dashboard.html` (continue adding functions)

- [ ] **Step 1: Add `buildTicketPrevNext` function**

```javascript
function buildTicketPrevNext(){
  document.getElementById('td-prev-next').innerHTML =
    '<button class="td-nav-btn" id="td-prev-btn">< PREV</button>'+
    '<span class="td-nav-pos">TICKET '+(TD_INDEX+1)+' OF '+TD_LIST.length+'</span>'+
    '<button class="td-nav-btn" id="td-next-btn">NEXT ></button>';
}
```

- [ ] **Step 2: Add `buildTicketSidebar` function**

```javascript
function buildTicketSidebar(stage, repName, repPhone, repEmail){
  if(window.innerWidth<768) return;
  const t = TD_TICKET;
  const p = TD_PROJECT;
  const currentStage = stage;
  const projectItemId = p ? p.id : '';

  const stages = PIPELINE_STAGES.filter(s=>s.key!=='Complete' && s.key!=='On Hold');
  let foundCurrent = false;
  const stageHtml = stages.map(s=>{
    const isCurrent = s.key===currentStage || s.label===currentStage;
    if(isCurrent) foundCurrent = true;
    const state = isCurrent ? 'current' : (foundCurrent ? 'future' : 'done');
    const link = projectItemId ? 'https://podio.com/item/'+projectItemId : '#';
    return '<a href="'+link+'" target="_blank" class="td-stage '+state+'" style="padding:3px 0">'+
      '<div class="td-stage-dot '+state+'" style="width:5px;height:5px'+(state==='current'?';width:7px;height:7px':'')+'"></div>'+
      '<span class="td-stage-name">'+x(s.label.toUpperCase())+'</span>'+
      (state==='current'?'<span class="td-stage-status">CURRENT</span>':'')+
    '</a>';
  }).join('');

  const driveDefs = [
    {label:'PARENT FOLDER',fid:266618729},{label:'SITE SURVEY',fid:266618728},
    {label:'DESIGN',fid:266618723},{label:'APPROVED',fid:268981903},
    {label:'CUSTOMER DOCS',fid:266618731},{label:'PERMIT',fid:266618725}
  ];
  let driveHtml = '';
  if(p && p.raw && p.raw.fields){
    driveHtml = driveDefs.map(d=>{
      const f = (p.raw.fields||[]).find(f=>f.field_id===d.fid);
      const val = f && f.values && f.values[0] ? f.values[0].value : null;
      if(!val) return '';
      return '<a href="https://drive.google.com/drive/folders/'+val+'" target="_blank" class="td-drive-btn" style="display:block;margin-bottom:3px">'+d.label+'</a>';
    }).filter(Boolean).join('');
  }

  const ticketLink = 'https://podio.com/item/'+t.id;
  const projectLink = projectItemId ? 'https://podio.com/item/'+projectItemId : '';

  document.getElementById('td-sidebar').innerHTML =
    '<div class="td-section-label" style="margin-bottom:10px">PROJECT NAVIGATION</div>'+
    stageHtml+
    '<div class="td-section-label" style="margin:12px 0 8px;padding-top:10px;border-top:1px solid rgba(255,255,255,.08)">GOOGLE DRIVE</div>'+
    (driveHtml||'<div style="color:rgba(255,255,255,.3);font-size:10px">No Drive folders linked.</div>')+
    '<div style="margin-top:12px;padding-top:10px;border-top:1px solid rgba(255,255,255,.08);display:flex;flex-direction:column;gap:4px">'+
      '<a href="'+ticketLink+'" target="_blank" style="color:#ADD8E6;font-size:10px;text-decoration:none">Open Ticket in Podio</a>'+
      (projectLink?'<a href="'+projectLink+'" target="_blank" style="color:#ADD8E6;font-size:10px;text-decoration:none">Open Project in Podio</a>':'')+
    '</div>'+
    (repName?'<div class="td-section-label" style="margin:12px 0 6px;padding-top:10px;border-top:1px solid rgba(255,255,255,.08)">REP</div>'+
      '<div style="color:rgba(255,255,255,.6);font-size:10px;font-weight:600">'+x(repName)+'</div>'+
      (repPhone?'<div style="color:rgba(255,255,255,.4);font-size:9px;margin-top:2px">'+x(repPhone)+'</div>':'')+
      (repEmail?'<div style="color:rgba(255,255,255,.4);font-size:9px">'+x(repEmail)+'</div>':''):'');
}

function wrapTicketSplit(){
  // On desktop, wrap tab bar + tab content + sidebar in a flex container
  if(window.innerWidth<768) return;
  const tabsBar = document.getElementById('td-tabs-bar');
  const tabContent = document.getElementById('td-tab-content');
  const sidebar = document.getElementById('td-sidebar');
  // Check if already wrapped
  if(tabsBar.parentElement.classList.contains('td-split-left')) return;
  const splitLeft = document.createElement('div');
  splitLeft.className = 'td-split-left';
  const split = document.createElement('div');
  split.className = 'td-split';
  tabsBar.parentElement.insertBefore(split, tabsBar);
  split.appendChild(splitLeft);
  splitLeft.appendChild(tabsBar);
  splitLeft.appendChild(tabContent);
  split.appendChild(sidebar);
}
```

- [ ] **Step 3: Commit**

```bash
git add aveyo-dashboard.html
git commit -m "feat: ticket detail view — prev/next navigation and desktop sidebar"
```

---

### Task 6: Event Handlers — Clicks, Status Updates, Compose

**Files:**
- Modify: `aveyo-dashboard.html` (add event listener after the existing ticket click handler ~line 5561)

- [ ] **Step 1: Wire up the ticket queue click handler to open ticket detail instead of project detail**

Modify the existing click handler at line ~5547. Change:

```javascript
      if(match){ PREV_VIEW='tickets'; openDetail(match.id); return; }
```

to:

```javascript
      if(match){ openTicketDetail(row.ticketData, match); return; }
```

And change the fallback:

```javascript
      if(match){ PREV_VIEW='tickets'; openDetail(match.id); }
```

to:

```javascript
      if(match){ openTicketDetail(row.ticketData, match); }
```

Also, we need to store the ticket data on the row element. In `renderTickets()` (~line 2272), the row already has `data-ticketid` and `data-projnum`. We need to look up the ticket from `TICKETS_ITEMS` in the click handler. Update the click handler to:

```javascript
  const row = e.target.closest('#tickets-list .resp-row[data-ticketid]');
  if(row){
    const ticketId = parseInt(row.dataset.ticketid);
    const projNum = row.dataset.projnum;
    const ticket = TICKETS_ITEMS.find(t=>t.id===ticketId);
    if(!ticket) return;
    if(projNum && ALL_ITEMS.length){
      const match = ALL_ITEMS.find(p=>p.num&&p.num.replace('#','')===projNum);
      if(match){ openTicketDetail(ticket, match); return; }
    }
    if(projNum && !ALL_ITEMS.length){
      await loadProjects();
      const match = ALL_ITEMS.find(p=>p.num&&p.num.replace('#','')===projNum);
      if(match){ openTicketDetail(ticket, match); return; }
    }
    // No project match — open with null project
    openTicketDetail(ticket, null);
  }
```

- [ ] **Step 2: Add ticket detail event listener**

Add a new event listener after the existing ticket click handler:

```javascript
// Ticket detail view: all click events
document.addEventListener('click', async function(e){
  // Back button
  if(e.target.closest('#td-back-btn')){
    showView('tickets');
    window.scrollTo(0, SCROLL_POS['tickets_scroll']||0);
    return;
  }
  // Status pills
  const pill = e.target.closest('.td-status-pill');
  if(pill && pill.dataset.tdStatus){
    const newStatus = pill.dataset.tdStatus;
    const current = TD_TICKET.status.toLowerCase().replace(/\s+/g,'');
    if(newStatus===current) return;
    // Find status field and option ID from raw item
    const statusMap = {new:'New',assigned:'Assigned',inprogress:'In Progress',complete:'Complete'};
    const newStatusText = statusMap[newStatus];
    // Update UI immediately (optimistic)
    TD_TICKET.status = newStatusText;
    buildTicketStatus();
    // Find the category field
    const fields = TD_TICKET.raw.fields||[];
    let statusFieldId = null;
    let optionId = null;
    for(const f of fields){
      if(!f.values||!f.values.length) continue;
      const v = f.values[0].value;
      if(v && typeof v==='object' && v.text){
        if(['new','assigned','in progress','complete','on hold','cancelled'].includes(v.text.toLowerCase())){
          statusFieldId = f.field_id;
          // Find the option ID for the new status
          if(f.config && f.config.settings && f.config.settings.options){
            const opt = f.config.settings.options.find(o=>o.text.toLowerCase()===newStatusText.toLowerCase());
            if(opt) optionId = opt.id;
          }
          break;
        }
      }
    }
    if(statusFieldId && optionId){
      try{
        await fetch('https://api.podio.com/item/'+TD_TICKET.id+'/value/'+statusFieldId,{
          method:'PUT',
          headers:{'Authorization':'OAuth2 '+TOKEN,'Content-Type':'application/json'},
          body:JSON.stringify({value:optionId})
        });
      }catch(err){ console.error('Status update failed:', err); }
    }
    return;
  }
  // Action buttons
  const actionBtn = e.target.closest('[data-td-action]');
  if(actionBtn){
    const type = actionBtn.dataset.tdAction;
    if(TD_COMPOSE===type){ closeTicketCompose(); }
    else { openTicketCompose(type); }
    return;
  }
  // Compose cancel
  if(e.target.closest('#td-compose-cancel')){
    closeTicketCompose();
    return;
  }
  // Compose send
  const sendBtn = e.target.closest('#td-compose-send');
  if(sendBtn && !sendBtn.disabled){
    const type = sendBtn.dataset.tdComposeType;
    const ta = document.getElementById('td-compose-ta');
    const msg = ta ? ta.value.trim() : '';
    if(!msg) return;
    sendBtn.disabled = true;
    sendBtn.textContent = 'SENDING...';
    try{
      if(type==='comment'){
        await fetch('https://api.podio.com/comment/item/'+TD_TICKET.id+'/',{
          method:'POST',
          headers:{'Authorization':'OAuth2 '+TOKEN,'Content-Type':'application/json'},
          body:JSON.stringify({value:msg})
        });
      } else {
        const fieldId = type==='rep' ? FIELD.notes : FIELD.customerPhone;
        const itemId = TD_PROJECT ? TD_PROJECT.id : TD_TICKET.id;
        await fetch('https://api.podio.com/item/'+itemId+'/value/'+fieldId,{
          method:'PUT',
          headers:{'Authorization':'OAuth2 '+TOKEN,'Content-Type':'application/json'},
          body:JSON.stringify({value:msg})
        });
      }
      closeTicketCompose();
    }catch(err){
      sendBtn.textContent = 'ERROR — TRY AGAIN';
      sendBtn.disabled = false;
    }
    return;
  }
  // Compose generate AI
  if(e.target.closest('#td-compose-generate')){
    const ta = document.getElementById('td-compose-ta');
    const btn = e.target.closest('#td-compose-generate');
    if(!ta||!btn) return;
    btn.textContent = 'GENERATING...';
    btn.disabled = true;
    const itemId = TD_PROJECT ? TD_PROJECT.id : TD_TICKET.id;
    const type = TD_COMPOSE==='rep'?'rep':'customer';
    try{
      const res = await fetch(VPS+'/generate-message',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({item_id:itemId,type})});
      const data = await res.json();
      ta.value = data.message||data.text||'';
      const sendBtn2 = document.getElementById('td-compose-send');
      if(sendBtn2) sendBtn2.disabled = !ta.value.trim();
    }catch(err){ ta.placeholder = 'Generation failed. Type manually.'; }
    btn.textContent = 'GENERATE WITH AI';
    btn.disabled = false;
    return;
  }
  // Tab clicks
  const tab = e.target.closest('.td-tab');
  if(tab && tab.dataset.tdTab){
    TD_TAB = tab.dataset.tdTab;
    buildTicketTabs();
    renderTicketTabContent();
    return;
  }
  // Switch to another ticket from Tickets tab
  const switchTicket = e.target.closest('[data-td-switch-ticket]');
  if(switchTicket){
    const newId = parseInt(switchTicket.dataset.tdSwitchTicket);
    const newTicket = TICKETS_ITEMS.find(t=>t.id===newId);
    if(newTicket){
      const projNum = newTicket.projectNum;
      const match = projNum ? ALL_ITEMS.find(p=>p.num&&p.num.replace('#','')===projNum) : null;
      openTicketDetail(newTicket, match||TD_PROJECT);
    }
    return;
  }
  // Prev/Next
  if(e.target.closest('#td-prev-btn')||e.target.closest('#td-desk-prev')){
    TD_INDEX = (TD_INDEX-1+TD_LIST.length)%TD_LIST.length;
    const prev = TD_LIST[TD_INDEX];
    const match = prev.projectNum ? ALL_ITEMS.find(p=>p.num&&p.num.replace('#','')===prev.projectNum) : null;
    openTicketDetail(prev, match||TD_PROJECT);
    return;
  }
  if(e.target.closest('#td-next-btn')||e.target.closest('#td-desk-next')){
    TD_INDEX = (TD_INDEX+1)%TD_LIST.length;
    const next = TD_LIST[TD_INDEX];
    const match = next.projectNum ? ALL_ITEMS.find(p=>p.num&&p.num.replace('#','')===next.projectNum) : null;
    openTicketDetail(next, match||TD_PROJECT);
    return;
  }
});

// Enable compose send button on input
document.addEventListener('input', function(e){
  if(e.target.id==='td-compose-ta'){
    const sendBtn = document.getElementById('td-compose-send');
    if(sendBtn) sendBtn.disabled = !e.target.value.trim();
  }
});
```

- [ ] **Step 3: Update `showView` function to handle ticket-detail view cleanup**

At line ~1647, update the `showView` function. Add after the existing `if(v !== 'detail'){` block:

```javascript
  if(v !== 'ticket-detail'){
    TD_TICKET = null;
    TD_PROJECT = null;
    TD_COMPOSE = null;
  }
```

- [ ] **Step 4: Commit**

```bash
git add aveyo-dashboard.html
git commit -m "feat: ticket detail view — event handlers, status updates, compose, navigation"
```

---

### Task 7: Integration Testing and Polish

**Files:**
- Modify: `aveyo-dashboard.html` (minor fixes as needed)

- [ ] **Step 1: Test the full flow manually**

Open the app in a browser, navigate to the Tickets tab, click a ticket, and verify:

1. Back bar shows "< TICKETS" and position counter
2. Ticket header shows ticket number, name, address, description, type, creator, age timer
3. Project context line shows milestone and rep info
4. Status pills render with correct active state
5. Action buttons respond to taps — compose area expands inline
6. Activity tab shows project comments
7. Tickets tab shows other tickets for same project
8. Work Orders tab shows project work orders
9. PROJECT tab (mobile) shows pipeline stages and Drive folders
10. Prev/Next navigates through ticket queue
11. Desktop: sidebar shows with project navigation, no PROJECT tab

- [ ] **Step 2: Test status update**

Tap a different status pill, verify it updates visually and check Podio to confirm the API call went through.

- [ ] **Step 3: Test compose flow**

Tap ADD COMMENT, type text, tap POST COMMENT. Verify the comment posts to Podio.

- [ ] **Step 4: Test AI message generation**

Tap MSG REP, tap GENERATE WITH AI, verify message generates. Tap SEND TO REP, verify it sends.

- [ ] **Step 5: Commit any fixes**

```bash
git add aveyo-dashboard.html
git commit -m "fix: ticket detail view polish and integration fixes"
```

---

### Task 8: Update Progress Tracker

**Files:**
- Modify: `/Users/qspencer/.claude/projects/-Users-qspencer-aveyo-dev/memory/progress_tracker.md`

- [ ] **Step 1: Update the progress tracker**

Update the TICKETS row status from "QUEUE DONE, DETAIL VIEW NEEDED" to "DONE" and update the Last Session Work and Last Updated fields.

- [ ] **Step 2: Commit progress tracker is not needed** (memory file, not in git)

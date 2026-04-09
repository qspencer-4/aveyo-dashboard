# SOW Queue Tab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a SOW responsibility queue tab with 10 Podio view filter chips and card-style queue rows showing project info, system size, verification progress, rep name, and age timer.

**Architecture:** Replace the stubbed `loadSOWResp()` function with a full implementation following the exact same pattern as `loadTickets()` / `renderTickets()`. Reuse existing `.resp-row`, `.resp-chip`, `.resp-badge` CSS classes. Add a full-screen loading overlay (same as Tickets). Cache fetched items per Podio view ID.

**Tech Stack:** Vanilla JS, Podio API via `fetchAllItems()`, existing CSS classes

---

### Task 1: Update HTML — Full-screen loading overlay for SOW tab

**Files:**
- Modify: `aveyo-dashboard.html:1626-1631` (view-sowresp HTML)

- [ ] **Step 1: Replace the SOW tab loading div with a full-screen fixed overlay**

Find this block (around line 1626-1631):
```html
<!-- SOW RESPONSIBILITY TAB -->
<div id="view-sowresp" class="view">
  <div class="resp-filter" id="sowresp-filters"></div>
  <div class="loading" id="sowresp-loading" style="display:none"><div class="spinner" style="width:72px;height:72px;...">...</div>Loading...</div>
  <div id="sowresp-list"></div>
</div>
```

Replace with:
```html
<!-- SOW RESPONSIBILITY TAB -->
<div id="view-sowresp" class="view">
  <div class="resp-filter" id="sowresp-filters"></div>
  <div id="sowresp-loading" style="display:none;position:fixed;inset:0;z-index:10;background:#000;flex-direction:column;align-items:center;justify-content:center;text-align:center;color:rgba(255,255,255,.35);font-size:9px;letter-spacing:.2em;text-transform:uppercase"><div style="width:100px;height:100px;margin-bottom:1.5rem;border:none;background:none;animation:spin3d 2.5s ease-in-out infinite;transform-style:preserve-3d"><img src="data:image/jpeg;base64,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" style="width:100%;height:100%;object-fit:contain;display:block" alt=""></div>Loading...</div>
  <div id="sowresp-list"></div>
</div>
```

Note: Use the same Aveyo logo base64 that is already in the other loading divs (the full base64 from `AVEYO_LOGO_SRC` constant).

- [ ] **Step 2: Verify the HTML change is correct by searching for the new sowresp-loading div**

Search for `id="sowresp-loading"` and confirm it has `position:fixed` and `display:none`.

### Task 2: Add SOW queue state variables and view ordering

**Files:**
- Modify: `aveyo-dashboard.html` — near existing `TICKETS_ITEMS` and `TICKETS_FILTER` declarations

- [ ] **Step 1: Find where TICKETS_ITEMS and TICKETS_FILTER are declared**

Search for `TICKETS_ITEMS` and `TICKETS_FILTER` variable declarations (around the top of the script section).

- [ ] **Step 2: Add SOW queue state variables nearby**

Add these declarations near the existing ticket variables:

```javascript
let SOW_RESP_CACHE = {}; // keyed by viewId string
let SOW_RESP_FILTER = '61743309'; // default: Total in SOW
```

- [ ] **Step 3: Define the SOW view chips array**

Add this constant near the existing `SOW_VIEWS` object (around line 4667):

```javascript
const SOW_RESP_CHIPS = [
  ['61743309','TOTAL IN SOW'],
  ['61743307','READY FOR SOW'],
  ['61743308','SOW REJECTIONS'],
  ['61743310','READY TO SEND REP'],
  ['61743311','NO REDLINES'],
  ['61743313','REP SOW PENDING'],
  ['61743314','CUST REJECTIONS'],
  ['61743315','CUST SOW SENT'],
  ['61743332','READY SEND CUST'],
  ['61743312','ROOF REVIEW']
];
```

- [ ] **Step 4: Commit**

```bash
git add aveyo-dashboard.html && git commit -m "feat: add SOW queue state variables and chip definitions"
```

### Task 3: Implement loadSOWResp() function

**Files:**
- Modify: `aveyo-dashboard.html` — replace the stub `loadSOWResp()` (around line 2407)

- [ ] **Step 1: Replace the stubbed loadSOWResp function**

Find:
```javascript
function loadSOWResp(){document.getElementById('sowresp-list').innerHTML='<div class="resp-empty">Loading...</div>';}
```

Replace with:
```javascript
async function loadSOWResp(){
  const viewId = SOW_RESP_FILTER;
  // If cached, render immediately
  if(SOW_RESP_CACHE[viewId]){ renderSOWResp(); return; }
  document.getElementById('sowresp-filters').style.display='none';
  document.getElementById('sowresp-loading').style.display='flex';
  document.getElementById('sowresp-list').innerHTML='';
  try{
    const raw = await fetchAllItems(29839685, parseInt(viewId));
    SOW_RESP_CACHE[viewId] = raw.map(sowItem=>{
      const fields = sowItem.fields||[];
      const title = sowItem.title||'';

      // Parse title for project num, name, address
      let projectNum='', name='', address='';
      const tm = title.match(/^(\d+)\s*-\s*#?(\d+)\s+(.+?)\s*-\s*(.+?)(?:\s*-\s*(.+))?$/);
      if(tm){
        projectNum=tm[2]||tm[1]; name=tm[3].trim(); address=tm[4].trim();
      } else {
        const parts = title.split(' - ');
        projectNum = (parts[0]||'').trim().replace(/^#/,'');
        name = (parts[1]||parts[0]||'').replace(/^#\d+\s*/,'').trim();
        address = parts[2]||'';
      }

      // Read system size
      let systemSize = '';
      const sizeF = fields.find(f=>f.field_id===SOW_FIELD.systemSize);
      if(sizeF && sizeF.values && sizeF.values[0]){
        const sv = sizeF.values[0].value;
        systemSize = (typeof sv==='object'?(sv.text||''):String(sv||'')).trim();
      }

      // Read contract price
      let contractPrice = '';
      const priceF = fields.find(f=>f.field_id===SOW_FIELD.contractPrice);
      if(priceF && priceF.values && priceF.values[0]){
        const pv = priceF.values[0].value;
        contractPrice = (typeof pv==='object'?(pv.text||''):String(pv||'')).trim();
      }

      // Count verification fields (8 checks)
      const verifyIds = [
        SOW_FIELD.systemSizeMatches, SOW_FIELD.contractPriceMatches,
        SOW_FIELD.designMatches, SOW_FIELD.electricalWork,
        SOW_FIELD.structuralUpgrade, SOW_FIELD.roofReview,
        SOW_FIELD.repDesignApproval, SOW_FIELD.permitDesign
      ];
      let verified = 0;
      for(const fid of verifyIds){
        const f = fields.find(ff=>ff.field_id===fid);
        if(f && f.values && f.values.length){
          const v = f.values[0].value;
          const txt = (typeof v==='object'?(v.text||''):String(v||'')).toLowerCase().trim();
          if(txt && txt!=='no' && txt!=='n/a' && txt!=='none' && txt!=='not verified') verified++;
        }
      }

      // Parse rep info from fields (look for contact/member field)
      let repName = '';
      for(const f of fields){
        if(f.values && f.values[0] && f.values[0].value && typeof f.values[0].value==='object'){
          const v = f.values[0].value;
          if(v.name && (f.label||'').toLowerCase().includes('rep')){
            repName = v.name; break;
          }
        }
      }

      return {
        id: sowItem.item_id,
        projectNum: projectNum,
        name: name,
        address: address,
        systemSize: systemSize,
        contractPrice: contractPrice,
        verified: verified,
        repName: repName,
        created: sowItem.created_on||'',
        raw: sowItem
      };
    });
    renderSOWResp();
  }catch(e){
    document.getElementById('sowresp-list').innerHTML='<div class="resp-row"><div class="resp-row-desc" style="color:#E88B8B">Error: '+x(e.message)+'</div></div>';
  }
  document.getElementById('sowresp-loading').style.display='none';
  document.getElementById('sowresp-filters').style.display='';
}
```

- [ ] **Step 2: Verify the function exists by searching for `async function loadSOWResp`**

### Task 4: Implement renderSOWResp() function

**Files:**
- Modify: `aveyo-dashboard.html` — add right after the `loadSOWResp()` function

- [ ] **Step 1: Add the renderSOWResp function immediately after loadSOWResp**

```javascript
function renderSOWResp(){
  const items = SOW_RESP_CACHE[SOW_RESP_FILTER]||[];
  const viewLabel = (SOW_RESP_CHIPS.find(c=>c[0]===SOW_RESP_FILTER)||['','SOW'])[1];

  // Build chips with counts per view (use cached counts or '...' if not fetched)
  document.getElementById('sowresp-filters').innerHTML = SOW_RESP_CHIPS.map(([vid,label])=>{
    const cached = SOW_RESP_CACHE[vid];
    const count = cached ? cached.length : '';
    const cls = vid===SOW_RESP_FILTER?'resp-chip active':'resp-chip';
    return '<span class="'+cls+'" data-sowfilter="'+vid+'">'+label+(count!==''?' '+count:'')+'</span>';
  }).join('');

  // Render rows
  document.getElementById('sowresp-list').innerHTML = items.length ? items.map(s=>{
    const timer = timerText(s.created);
    const tc = timerClass(timer.days);
    const isRejection = viewLabel.includes('REJECTION');
    const badgeCls = isRejection?'urgent':'good';
    const barPct = Math.round((s.verified/8)*100);
    const barColor = (s.verified<=3 && timer.days>10)?'#E88B8B':'#ADD8E6';
    const priceDisplay = s.contractPrice ? '$'+s.contractPrice.replace(/[$,]/g,'').replace(/\B(?=(\d{3})+(?!\d))/g,',') : '';

    return '<div class="resp-row" data-sowid="'+s.id+'">'+
      '<div class="resp-row-top">'+
        '<span class="resp-row-id">#'+x(s.projectNum)+'</span>'+
        '<span class="resp-badge '+badgeCls+'">'+x(viewLabel)+'</span>'+
      '</div>'+
      '<div class="resp-row-name">'+x(s.name)+'</div>'+
      (s.address?'<div class="resp-row-meta">'+x(s.address)+'</div>':'')+
      '<div class="resp-row-desc" style="display:flex;gap:10px">'+
        (s.systemSize?'<span>'+x(s.systemSize)+(s.systemSize.toLowerCase().includes('kw')?'':' kW')+'</span>':'')+
        (s.systemSize&&priceDisplay?'<span style="color:rgba(255,255,255,.12)">|</span>':'')+
        (priceDisplay?'<span>'+priceDisplay+'</span>':'')+
      '</div>'+
      '<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">'+
        '<div style="flex:1;height:2px;background:rgba(255,255,255,.06);overflow:hidden">'+
          '<div style="width:'+barPct+'%;height:100%;background:'+barColor+'"></div>'+
        '</div>'+
        '<span style="font-size:9px;color:rgba(255,255,255,.3);letter-spacing:.5px">'+s.verified+'/8</span>'+
      '</div>'+
      '<div class="resp-row-bottom">'+
        '<span class="resp-row-creator">'+(s.repName?'Rep: <b>'+x(s.repName)+'</b>':'')+'</span>'+
        '<span class="resp-timer '+tc+'">'+timer.text+'</span>'+
      '</div>'+
    '</div>';
  }).join('') : '<div class="resp-empty">No items in this view.</div>';
}
```

- [ ] **Step 2: Commit**

```bash
git add aveyo-dashboard.html && git commit -m "feat: implement loadSOWResp and renderSOWResp functions"
```

### Task 5: Wire up SOW filter chip click handler

**Files:**
- Modify: `aveyo-dashboard.html` — add click handler near existing ticket filter handler (around line 6064-6067)

- [ ] **Step 1: Find the tickets filter chip click handler**

Search for `data-tfilter` click handler (around line 6064):
```javascript
document.addEventListener('click',async function(e){
  const chip = e.target.closest('[data-tfilter]');
  if(chip){ TICKETS_FILTER=chip.dataset.tfilter; renderTickets(); return; }
```

- [ ] **Step 2: Add SOW filter chip click handler right after the tickets block (around line 6085)**

Find a suitable location after the tickets click handlers and add:

```javascript
// SOW Responsibility tab: filter chip clicks
document.addEventListener('click',async function(e){
  const chip = e.target.closest('[data-sowfilter]');
  if(chip){
    SOW_RESP_FILTER = chip.dataset.sowfilter;
    loadSOWResp();
    return;
  }
});
```

- [ ] **Step 3: Commit**

```bash
git add aveyo-dashboard.html && git commit -m "feat: wire SOW filter chip click handler"
```

### Task 6: Bump service worker version and push

**Files:**
- Modify: `aveyo-dashboard.html` — service worker registration version
- Modify: `sw.js` — VERSION constant

- [ ] **Step 1: Bump sw.js VERSION**

Find `const VERSION = 'v117';` in `sw.js` and change to `const VERSION = 'v118';`

- [ ] **Step 2: Bump the registration query param in aveyo-dashboard.html**

Find `navigator.serviceWorker.register('./sw.js?v=117')` and change to `navigator.serviceWorker.register('./sw.js?v=118')`

- [ ] **Step 3: Commit and push**

```bash
git add aveyo-dashboard.html sw.js && git commit -m "feat: SOW responsibility queue tab with 10 Podio view filters

- Full-screen loading overlay with spinning Aveyo logo
- 10 filter chips (one per Podio view) with item counts
- Queue rows: project num, name, address, system size, price,
  verification progress bar (X/8), rep name, age timer
- Per-view caching for fast chip switching" && git push origin main
```

- [ ] **Step 4: Test in browser**

Open the deployed site, tap the SOW nav button. Verify:
1. Full-screen Aveyo logo loading animation appears
2. Filter chips render with "TOTAL IN SOW" active by default
3. Queue rows show project info, system/price, progress bar, rep, timer
4. Tapping a different chip fetches and renders that view
5. Switching back to a previously viewed chip loads instantly from cache

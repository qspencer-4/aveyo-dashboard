# Aveyo Dashboard — Mission Goal

## The Problem

Quentin Spencer is a Project Manager at Aveyo Solar, responsible for shepherding dozens of residential solar installation projects from contract signing through final energization. Every day, he juggles seven distinct responsibilities across disconnected tools:

1. **Support Tickets** — Customers and reps file issues (inverter failures, permit delays, panel damage). These need immediate triage. Every hour a ticket sits unresolved is a customer getting angrier and a project stalling.

2. **Communications** — Reps in the field and customers at home both need regular updates. When a permit gets approved, the rep needs to know. When an install date is set, the customer needs confirmation. Silence breeds distrust and churn.

3. **Scope of Work** — Every project needs a verified SOW before it can proceed to permitting. System size, contract price, design, roof condition, electrical requirements — eight verification items that must all check out. PDF plansets need analysis. Site plans need annotation. Production numbers need comparison. A single mismatch here means rework, change orders, and delays.

4. **Pre-Install** — Projects approaching installation need final readiness checks. Permits approved? Materials ordered? Crew assigned? Roof work complete? One missing item and the install crew shows up to a job that isn't ready.

5. **Project Review** — Every project needs periodic review to ensure nothing has stalled. With 40-60 active projects, it's easy for one to silently fall through the cracks. A project that hasn't been reviewed in 28 days is a project where problems are compounding unseen.

6. **Change Orders** — Design changes trigger cascading updates: new plansets, price adjustments, customer re-approval, lender notification. Each change order is a mini-project within the project.

7. **Roof Reviews** — Before solar panels go up, the roof must be evaluated. Customer roofs (homeowner handles repair), Aveyo roofs (Aveyo handles repair), and unclassified roofs that need triage.

**Today, Quentin manages all of this by:**
- Logging into Podio and clicking through multiple apps (Projects, SOW, Support Tickets, Pre-Install, Change Orders, Roof Work — six separate Podio applications)
- Mentally tracking which projects need what action
- Jumping between browser tabs to check Drive folders, LightReach pricing, and Podio views
- Using widget counts on a dashboard to guess where fires are burning
- Manually sending rep updates and customer texts through a separate compose flow

**The pain:** Context switching kills productivity. Opening a project to check its SOW means leaving the ticket queue. Sending a rep update means navigating away from the review list. Every tab switch is a mental reset. With 40-60 projects and 7 responsibilities, Quentin spends more time navigating than acting.

---

## The Solution

Build a **mobile-first command center** that organizes Quentin's entire workday into a single app, structured around his actual responsibilities in priority order.

### Core Architecture

**One app. Seven responsibility queues. Every project accessible from anywhere.**

The bottom navigation bar is a scrollable row of tabs, ordered by priority:

```
HOME | TICKETS | COMMS | SOW | PRE-INSTALL | REVIEW | CHANGE | ROOF | KB
```

Each tab is a **triage queue** — a sorted list of projects that need attention for that specific responsibility. The queue pattern is identical across all tabs: filter chips at top, sortable list of items, each with a status badge, relevant metadata, and a live age timer showing how long the item has been waiting.

Badge counts on each tab show urgency at a glance. Before tapping a single tab, Quentin can see: 3 tickets open, 5 comms needed, 12 reviews overdue. Priority is visible without any interaction.

### Design Language: Battlefront 2015

The app uses a cinematic dark UI inspired by Star Wars Battlefront 2015:

- **Black backgrounds** (#000 / #0a0a0a) — zero visual noise, content pops
- **PPTelegraf font** — bold, industrial, all-caps for labels with wide letter-spacing
- **#ADD8E6 accent** (light blue) — the only bright color, used for active states and positive indicators
- **Zero border-radius** — sharp edges, military precision
- **No emojis** — ever
- **1px horizontal rules** — minimal separators
- **Three-color status system** applied universally:
  - **#ADD8E6 (light blue)** — good / new / fresh / verified / approved / under threshold
  - **#FFFFFF (white)** — moderate / neutral / in progress / middle range
  - **#E88B8B (light red)** — overdue / urgent / failed / rejected / needs attention

This isn't decoration. The dark theme reduces eye strain during long sessions. The minimal color palette means status is instantly parseable — you never have to read a label to know if something is good, neutral, or urgent. The industrial typography conveys authority and precision.

### Tab-by-Tab Detail

#### HOME — The Command Overview
The dashboard. Pipeline progress bar, key metric widgets with counts for every Podio view that matters, a list of projects needing review, and support ticket alerts. This is the morning briefing — scan it in 10 seconds, know where the fires are, tap the worst one.

#### TICKETS — Triage Queue (Priority 1)
**Why it's #1:** An unresolved ticket is a customer on the phone, a rep in the field stuck, or a system not producing power. Every ticket has a real person waiting.

Shows all open support tickets from Podio app 29840119. Each row:
- Bold ticket number (#105976) for quick reference
- Customer name and address
- Description of the issue
- Who created the ticket (parsed from Podio's Details field)
- Ticket type (Sales Rep Comment, Work Order Issue, etc.)
- Live age timer — light blue under 3 days, white 3-14 days, red over 14 days
- Filter chips: ALL / NEW / ASSIGNED / IN PROGRESS

Tap a ticket → opens the linked project's detail view with full context.

#### COMMS — Communication Queue (Priority 2)
**Why it's #2:** A project where nobody's been contacted in 2 weeks is a project where the customer thinks they've been forgotten.

Shows projects needing rep updates or customer texts (Podio views 61743343, 61743344). Each row:
- Customer name and milestone stage
- Rep name
- Why they need contact
- Days since last communication — same color-coded timer
- Filter chips: ALL / REP / CUSTOMER

Tap → opens project detail with compose form ready.

#### SOW — Scope of Work Pipeline (Priority 3)
**Why it's #3:** SOW is the longest bottleneck in the pipeline. A project stuck in SOW is a project that can't be permitted, which means it can't be installed. SOW verification is meticulous: eight checklist items, each requiring cross-referencing PDFs, Podio data, and sometimes LightReach pricing.

Shows all projects in the SOW flow (Podio app 29839685, multiple views). Each row:
- Customer name and SOW status badge
- System size, contract price, lender
- Mini inline verification checklist: SIZE ✓ | PRICE ✓ | DESIGN ✗ | ROOF -- | ELEC --
- Filter chips: ALL / READY / REP SOW / CUST SOW / REJECT

Tap → opens full SOW detail with verification dropdowns, PDF analysis, site plan editor, production check.

#### PRE-INSTALL — Installation Readiness (Priority 4)
**Why it's #4:** A project that reaches pre-install is close to the finish line. Failing here wastes crew scheduling, truck rolls, and customer goodwill.

Shows projects from Pre-Install app (29839773). Each row:
- Customer name and readiness status (READY / ISSUE)
- Milestone and address
- Description of any blocking issues
- Filter chips: ALL / READY / ISSUES

#### REVIEW — Project Review Tracker (Priority 5)
**Why it's #5:** Review isn't urgent like a ticket, but neglect compounds. A project not reviewed for 7 days may have a small issue. Not reviewed for 28 days — that issue is now a crisis.

Shows all projects sorted by days since last review (worst first). Uses a stricter timer threshold: anything 7+ days is red. Each row:
- Customer name and days since review (large, bold, color-coded)
- Milestone and address
- Last review date
- Filter chips: OVERDUE / NOT SET / ALL

Tap → opens project detail with review date picker.

#### CHANGE ORDERS — Design Changes (Priority 6)
**Why it's #6:** Change orders are disruptive but manageable. Each one needs tracking but they're less time-sensitive than tickets or comms.

Shows change orders from app 29841104. Each row:
- Bold change order ID (#CO-1042)
- Customer name and address
- Description of the change
- Who created it and age timer

#### ROOF — Roof Reviews (Priority 7)
**Why it's #7:** Roof work blocks installation but moves on longer timescales. Classification matters — customer roof vs Aveyo roof determines who pays and who schedules.

Shows items from Roof Work app (29839741). Each row:
- Customer name and roof type badge (CUSTOMER / AVEYO / NOT SET)
- Address and description
- Age timer
- Filter chips: ALL / CUSTOMER / AVEYO / NOT SET

#### KB — Knowledge Base
Reference material. Adder pricing sheets, change order SOPs, process documentation. Not a queue — a reference library. Always available but not time-sensitive.

### The Project Detail View

When you tap any item from any queue, you enter the **project detail view** — a unified, deep-dive interface for a single project. This view is shared across all tabs. It doesn't matter if you entered from Tickets, Comms, or Review — you see the same complete project picture.

The detail view has:
- **Project banner** — name, address, ID, milestone badge, rep info, pipeline progress bar
- **Split panels** (desktop) — left panel for data views, right panel for actions
- **Section tabs** — Milestones, Details, Comments, Work Orders, Tickets, Notes | Rep Update, Customer Text, Project Review
- **Prev/Next navigation** — work through a queue without going back to the list
- **Inline compose** — generate AI-powered rep updates, customer texts, and project reviews without leaving the view

### Data Architecture

**Everything reads from Podio.** The app authenticates via OAuth2 and makes direct API calls to seven Podio applications:

| App | ID | Purpose |
|-----|-----|---------|
| Projects | 29839792 | Master project data — milestones, status, rep info, comments, work orders, tickets |
| SOW | 29839685 | Scope of work verification — checklist items, design review, production |
| Support Tickets | 29840119 | Customer/rep issues requiring resolution |
| Pre-Install | 29839773 | Installation readiness tracking |
| Change Orders | 29841104 | Design change management |
| Roof Work | 29839741 | Roof condition and repair tracking |
| (not yet integrated) | — | LightReach contract pricing (web scraping, no API available) |

**Caching strategy:**
- Widget counts cached for 30 minutes (badge numbers)
- Full item lists cached per session (tab data)
- First tap on a tab triggers lazy fetch; subsequent taps use cache
- Manual refresh button clears cache and re-fetches

**AI-powered features** (via VPS backend at aveyo.aiwhileyousleeping.com):
- `/generate-message` — AI-generated rep updates and customer texts based on project data
- `/generate-review` — AI-generated project review summaries
- `/sow-extract` — PDF extraction from Google Drive plansets, site surveys, and PE letters
- `/sow-render-page` — Planset page rendering for site plan annotation
- `/sow-save-annotated` — Save annotated site plans back to Google Drive and Podio
- `/sow-production-check` — Compare sold vs actual production, auto-create change orders
- `/post-comment` — Post comments to Podio activity stream

### What Success Looks Like

**Before:** Quentin opens his laptop, logs into Podio, clicks through six apps, opens 15 browser tabs, mentally tracks what needs doing, context-switches constantly, and still misses things because there's no unified priority view.

**After:** Quentin opens one app on his phone. Badge counts tell him: 3 tickets, 5 comms, 12 reviews. He starts at Tickets (priority 1), works through the queue top-to-bottom, taps next, next, next. Each ticket opens the full project context. He resolves or escalates. Moves to Comms — generates an AI update, sends it to the rep, next. Each responsibility has its own queue, its own filters, its own sorted view. Nothing falls through the cracks because everything is visible, timed, and color-coded.

**Measurable goals:**
- Time to triage morning tickets: < 10 minutes (from 30+)
- Projects without review in 14+ days: zero (from 10-15)
- Rep/customer communication gaps > 7 days: zero
- Context switches per task: 0 (from 3-5 per task)
- SOW verification time per project: < 5 minutes (from 15+)

### Future Enhancements (Planned)

1. **LightReach Integration** — Web scraper (httrack on VPS) to pull contract prices from LightReach portal and auto-sync to Podio. Eliminates manual price cross-referencing in SOW.

2. **UI Polish Pass** — Layout patterns extracted from Linear (queue flows), Stripe (data density), Jira (multi-view), and Todoist (mobile actions). All reskinned in Battlefront 2015 aesthetic. Mirrored sites stored at /root/mirrors/ on VPS.

3. **Keyboard Navigation** — Desktop users can press arrow keys to move through queues, Enter to open, Escape to go back. Inspired by Linear's keyboard-first design.

4. **Push Notifications** — Alert when a new ticket is created, when a ticket crosses the 7-day threshold, when a SOW rejection comes in.

5. **Offline Support** — Service worker already caches the app shell. Extend to cache project data for offline queue review.

6. **Team View** — If Aveyo adds more PMs, each sees their own filtered queues based on assigned projects.

---

## Technical Constraints

- **Single HTML file** — The entire app is one file (aveyo-dashboard.html) with embedded fonts, CSS, and JavaScript. This is intentional: GitHub Pages deployment, instant loading, no build step, easy to version.
- **No framework** — Vanilla JS. No React, no Vue, no build tools. DOM manipulation and string concatenation. This keeps the app fast and dependency-free.
- **Mobile-first PWA** — Designed for iPhone Safari. Installable to home screen. Works on desktop too (split panel layout on wide screens).
- **Podio rate limits** — API calls are batched and cached. Lazy loading prevents hitting limits on app open.
- **VPS backend** — Flask server at 187.124.240.101 handles AI calls (Anthropic Claude API), Google Drive access, and Podio write operations. The frontend never touches API keys directly.

---

## Current Status

- **v113** — Scrollable bottom nav with 9 tabs and badge counts deployed
- **Tickets tab** — Implemented with queue list, filters, age timers (being refined)
- **Comms tab** — Next to implement
- **SOW tab** — Next after Comms
- **Pre-Install, Review, Change Orders, Roof** — Queued for implementation
- **Home dashboard** — Existing, working
- **Project detail view** — Existing, working (split panels, AI compose, all data sections)
- **Knowledge base** — Existing, working
- **SOW detail** — Existing, working (verification checklist, PDF analysis, site plan editor)

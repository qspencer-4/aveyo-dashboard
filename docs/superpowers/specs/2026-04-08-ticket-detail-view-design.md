# Ticket Detail View — Design Spec

## Overview

When a ticket is clicked from the Tickets queue tab, open a purpose-built ticket detail view instead of the generic project detail view. The view shows the ticket front and center with project context, inline actions, and project navigation — everything needed to fully resolve a ticket without leaving the view.

## Layout: B2 — Ticket Hero + Actions + Tabbed Context

### Mobile (< 768px) — Single Column

From top to bottom:

1. **Back bar** — "< TICKETS" link to return to queue + position counter ("2 / 12")
2. **Ticket header** — ticket details with blue left border accent
3. **Status selector** — tappable status pills
4. **Action buttons** — COMMENT, MSG REP, MSG CUST (inline expand on tap)
5. **Context tabs** — ACTIVITY, TICKETS (count), WOs (count), PROJECT
6. **Tab content** — scrollable content for the active tab
7. **Prev/Next nav** — navigate through ticket queue

### Desktop (>= 768px) — Split Panel

- **Top bar** — "< TICKETS" + position counter + PREV/NEXT (moved up from bottom)
- **Ticket header** — wide layout with description beside ticket ID, stat blocks (milestone, rep, age) on right
- **Status + Actions** — single horizontal row, status pills and action buttons separated by a vertical divider
- **Split panels below:**
  - **Left:** Tabbed content (ACTIVITY, TICKETS, WORK ORDERS) — no PROJECT tab on desktop
  - **Right (280px):** Project Navigation sidebar — always visible (pipeline stages, Drive folders, Podio links, rep info)

---

## Section Details

### 1. Back Bar

- Left: "< TICKETS" — returns to the ticket queue, restores scroll position
- Right: "2 / 12" position counter showing current ticket index in filtered queue
- Sets `PREV_VIEW = 'tickets'` so navigation state is preserved

### 2. Ticket Header

Displays all ticket-specific information:

| Field | Source | Display |
|-------|--------|---------|
| Ticket number | `t.tid` (parsed from title) | `#105976` in #ADD8E6, bold, 15px |
| Customer name | `t.name` (parsed from title) | White, 13px, bold |
| Address | `t.address` (parsed from title) | rgba(255,255,255,.4), 10px |
| Description | `t.desc` (from title or Details field) | #ddd, 11px, full text (not truncated to 200 chars like queue) |
| Ticket type | `t.ticketType` (category field) | rgba(255,255,255,.4), 9px |
| Creator | `t.creator` (parsed from Details "Comment Creator:") | rgba(255,255,255,.4), 9px |
| Age timer | `t.created` → `timerText()` | Color-coded: blue < 3d, white 3-14d, red > 14d. Bold, 14px. |

**Project context line** (below a subtle border):
- Milestone stage from matched project (`getDetailedStage()`) — #ADD8E6, bold, uppercase
- Rep name from project `repInfo` field
- Rep phone from project `repInfo` field

**Styling:** `background: #1a1a1a`, `border-left: 3px solid #ADD8E6`, `padding: 12px 14px`

### 3. Status Selector

A row of 4 tappable pills representing ticket statuses:

| Status | Active Style | Inactive Style |
|--------|-------------|----------------|
| NEW | `background: #C97850; color: #fff` | `background: #1a1a1a; color: rgba(255,255,255,.4)` |
| ASSIGNED | `background: #C9A96E; color: #fff` | same |
| IN PROGRESS | `background: #ADD8E6; color: #000` | same |
| COMPLETE | `background: rgba(255,255,255,.35); color: #fff` | same |

**Behavior:** Tapping a different status updates the ticket's status category field in Podio via API call. The pill immediately updates to reflect the new status (optimistic UI). On mobile, labels are shortened: "IN PROG", "COMPLETE" → "DONE" if space is tight.

**Podio update:** `PUT /item/{ticket_item_id}/value/{status_field_id}` with the selected category option ID. The status field ID must be discovered from `ticket.raw.fields` — find the category field whose values match the known status options (New, Assigned, In Progress, Complete, On Hold, Cancelled).

### 4. Action Buttons

Three buttons in a row:

| Button | Label | Border |
|--------|-------|--------|
| Comment | ADD COMMENT / COMMENT | `1px solid #ADD8E6`, text `#ADD8E6` |
| Rep message | MSG REP | `1px solid rgba(255,255,255,.2)`, text `rgba(255,255,255,.5)` |
| Customer message | MSG CUST | `1px solid rgba(255,255,255,.2)`, text `rgba(255,255,255,.5)` |

**Inline compose behavior (Option A):**
- Tapping a button expands a compose area directly below the action buttons
- The active button fills with `background: #ADD8E6; color: #000`
- Compose area has: label, textarea, POST/SEND button + CANCEL button
- Compose area is bordered with `1px solid #ADD8E6`, `background: #0d0d0d`
- Tabs and content are pushed down (not hidden)
- Submitting collapses the compose area and returns to normal state
- Only one compose can be open at a time

**Compose details by type:**

| Type | Label | Submit button | Backend endpoint |
|------|-------|--------------|-----------------|
| Comment | "ADD COMMENT TO TICKET #XXXXX" | POST COMMENT | `/post-comment` (existing) |
| Rep message | "MESSAGE REP — MIKE JOHNSON" | SEND TO REP | `/generate-message` (existing, type: rep) |
| Customer message | "MESSAGE CUSTOMER — JOHN SMITH" | SEND TO CUSTOMER | `/generate-message` (existing, type: customer) |

Rep and customer message compose forms use the existing AI-powered generation flow from the project detail view.

### 5. Context Tabs

Horizontal tab bar with 4 tabs on mobile, 3 on desktop (PROJECT content moves to sidebar):

| Tab | Label | Badge | Content |
|-----|-------|-------|---------|
| ACTIVITY | ACTIVITY | — | Recent comments/activity for this project |
| TICKETS | TICKETS | Count in #E88B8B if > 0 | Other open tickets for this project |
| WORK ORDERS | WOs (mobile) / WORK ORDERS (desktop) | Count | Open work orders for this project |
| PROJECT | PROJECT (mobile only) | — | Pipeline stages, Drive folders, Podio links |

Active tab: `color: #fff; border-bottom: 2px solid #fff; font-weight: 700`
Inactive tab: `color: rgba(255,255,255,.3)`
Tab bar: `overflow-x: auto` on mobile for horizontal scrolling

### 6. Tab Content

#### ACTIVITY Tab (default)
- Shows comments from the matched project's `item.comments` field
- Parsed using existing `parseBlocks()` with `***` separator
- Each entry: date + relative time, author name in #ADD8E6, comment body
- Sorted newest first
- System-generated entries use `color: rgba(255,255,255,.4)` for author name

#### TICKETS Tab
- Shows other tickets for the same project (from `TICKETS_ITEMS` filtered by `projectNum`)
- Excludes the current ticket
- Each row: date, ticket ID (linked), description, status badge
- Same row styling as the main ticket queue but compact
- Tapping a ticket switches to that ticket's detail view

#### WORK ORDERS Tab
- Shows work orders from the matched project's `item.workOrders` field
- Parsed using existing `parseBlocks()` with `---` separator
- Each entry: WO ID (linked to Podio), appointment date, type, contractor, description, status badge

#### PROJECT Tab (mobile only)
- **Pipeline stages** — 11 stages (Packet Approval through PTO, no Complete)
  - Each stage is a tappable link opening the project item in Podio Projects app (29839792): `https://podio.com/item/{project_item_id}`
  - Completed stages: small blue dot (6px), dimmed text `rgba(255,255,255,.25)`, "DONE" label
  - Current stage: larger glowing blue dot (8px, `box-shadow: 0 0 6px rgba(173,216,230,.5)`), #ADD8E6 text, bold, highlighted row with `background: rgba(173,216,230,.08)`, "CURRENT" label
  - Future stages: dim dot `rgba(255,255,255,.12)`, very faint text `rgba(255,255,255,.15)`, "--" label
  - Current stage determined by `getDetailedStage()` matching against `PIPELINE_STAGES`
- **Google Drive folders** — 6 buttons in a flex-wrap grid
  - Parent (field 266618729), Site Survey (266618728), Design (266618723), Approved (268981903), Customer Docs (266618731), Permit (266618725)
  - Each links to `https://drive.google.com/drive/folders/{folder_id}`
  - Only shown if the field has a value
  - Style: `border: 1px solid rgba(255,255,255,.15); padding: 6px 12px; font-size: 9px`
- **Podio links** — "Open Ticket in Podio" + "Open Project in Podio"
  - Ticket link: `https://podio.com/item/{ticket_item_id}`
  - Project link: `https://podio.com/item/{project_item_id}`

### 7. Prev/Next Navigation

- Mobile: bottom of the view, full width. "< PREV" left, "TICKET 2 OF 12" center, "NEXT >" right
- Desktop: moved into the top bar alongside the back button
- Navigates through the filtered ticket queue (same filter that was active in the queue view)
- Wraps around: NEXT on last ticket goes to first, PREV on first goes to last

---

## Desktop Right Sidebar (280px)

Always visible on desktop, replaces the PROJECT tab. Contains:

1. **PROJECT NAVIGATION** header
2. **Pipeline stages** — same as mobile PROJECT tab but compact (3px padding per row)
3. **Google Drive** — stacked vertically instead of flex-wrap
4. **Podio links** — stacked vertically
5. **Rep info** — name, phone, email from project `repInfo` field

Each section separated by `border-top: 1px solid rgba(255,255,255,.08)` with label headers in `font-size: 9px; text-transform: uppercase; letter-spacing: 1px; color: rgba(255,255,255,.4)`

---

## Data Flow

### Entry point
Current click handler in `document.addEventListener('click', ...)` at line ~5547:
- Currently: finds matching project in `ALL_ITEMS` by `projNum`, calls `openDetail(match.id)`
- New: call `openTicketDetail(ticketItem, matchedProject)` instead

### Data available
- `ticketItem` from `TICKETS_ITEMS` — has `id, tid, projectNum, name, address, status, ticketType, desc, created, creator, raw`
- `matchedProject` from `ALL_ITEMS` — has all project fields (comments, workOrders, repTickets, repInfo, milestones, milestone, etc.)
- `raw` on the ticket item contains the full Podio item response for API updates

### New functions needed
- `openTicketDetail(ticket, project)` — builds and shows the ticket detail view
- `buildTicketDetail(ticket, project)` — generates HTML for the view
- `renderTicketTabs(ticket, project, activeTab)` — renders tab content
- `updateTicketStatus(ticketId, statusOptionId)` — Podio API call to update status

### Existing functions reused
- `timerText()`, `timerClass()` — age timer display
- `parseBlocks()` — parsing comments and work orders
- `getDetailedStage()` — determining current pipeline stage
- `x()` — HTML escaping
- `/post-comment` endpoint — posting comments
- `/generate-message` endpoint — AI-generated rep/customer messages

---

## View Management

- New view ID: `'ticket-detail'`
- `showView('ticket-detail')` shows the ticket detail container, hides all others
- Back button calls `showView('tickets')` and restores scroll position from `SCROLL_POS`
- The view uses a new container div (e.g., `#ticket-detail-view`) separate from the existing `#detail-view`

---

## Styling

All styling follows the existing Battlefront 2015 design system:
- Black backgrounds (#000 / #0a0a0a / #1a1a1a)
- #ADD8E6 accent for active states
- Zero border-radius
- PPTelegraf font for labels (uppercase, letter-spacing)
- No emojis
- Status colors: #C97850 (urgent/new), #C9A96E (warning/assigned), #ADD8E6 (good/in-progress), rgba(255,255,255,.35) (complete/done)
- Age timer colors: #ADD8E6 (< 3d), #fff (3-14d), #E88B8B (> 14d)

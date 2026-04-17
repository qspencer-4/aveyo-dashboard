# Aveyo Dashboard — Project-Centric Restructure Design Spec

## Design Philosophy
Battlefront 2015 aesthetic is **locked** — this spec only changes layout, UX flow, and component structure.
Visual identity stays: #000 bg, #ADD8E6 accent, PPTelegraf, all-caps labels, zero border-radius, no emojis.

## UX Patterns Applied

| Source | Pattern | Where it applies |
|--------|---------|-----------------|
| Linear | Queue triage: sorted list → detail split, prev/next keyboard nav | Support Tickets, Communication |
| Stripe | Data-dense dashboard cards, inline status indicators, sticky context | Home, Project Review |
| Jira | Multi-view on same data (list/kanban/table), filter chips, column grouping | SOW pipeline, Pre-Install |
| Todoist | Priority color-coding (P1-P4), quick-action buttons, mobile-first tap targets | All tabs on mobile |

## Bottom Nav (4 tabs)
```
[ Home ] [ Projects ] [ Action ] [ Knowledge ]
```
- **Home** — dashboard with widgets (unchanged)
- **Projects** — master project list with search/filter (unchanged)
- **Action** — auto-detected items needing attention (unchanged)
- **Knowledge** — adder sheet, SOPs (unchanged)

The 7 PM responsibilities live **inside the project detail view** as tabs when you open a project.

## Project Detail View — Split Layout (Desktop)

### Top: Project Banner (exists, unchanged)
Project ID, name, address, badge, rep info, pipeline progress bar, WO/ticket counts.

### Middle: 7 PM Responsibility Tabs (priority order, left to right)
```
[ Tickets ] [ Comms ] [ SOW ] [ Pre-Install ] [ Review ] [ Change Orders ] [ Roof ]
```
Active tab: white text, 2px bottom border (#fff)
Inactive: rgba(255,255,255,.3), no border

### Bottom: Split Panels (Linear-style)
Left panel: **Tab content** (the selected PM responsibility)
Right panel: **Quick actions** (contextual to the active tab)

Each tab has its own left/right content:

---

## Tab 1: Support Tickets (Priority: Highest)

**Left Panel — Ticket Queue (Linear-style triage)**
- List of open tickets for this project, sorted newest first
- Each ticket row: date, ticket ID (linked), description preview, status badge
- Status badges: `ts-open` = #C97850, `ts-assigned` = #C9A96E, `ts-complete` = rgba(255,255,255,.2)
- Clicking a ticket expands full details inline (no page change)

**Right Panel — Quick Actions**
- "Create Ticket" button (if we add that later)
- Link to open in Podio
- Ticket summary: X open, X assigned, X complete

---

## Tab 2: Communication

**Left Panel — Message Queue (Linear-style)**
- Two sub-sections stacked:
  - **Rep Update** — generate/send rep message (existing inline compose)
  - **Customer Text** — generate/send customer message (existing inline compose)
- Each compose form is open by default (not collapsed)

**Right Panel — Context**
- Rep info: name, phone, email
- Customer phone
- Last comment preview (most recent from Activity)
- Days since last review

---

## Tab 3: Scope of Work

**Left Panel — SOW Checklist (Jira-style verification board)**
- Project Info: system size, contract price, LightReach price (when available)
- Verification Checklist: all 8 items with dropdowns (existing SOW detail)
- Status: permit design, rep design approval, redline analysis
- Distance adder info

**Right Panel — SOW Tools**
- PDF Analysis & Adders: "Run Check" button + results
- Site Plan: "Auto Generate" / "Manual Editor" buttons + results
- Production Check: sold vs new production, change order trigger
- SOW Notes (if any)
- "Open SOW in Podio" link

---

## Tab 4: Pre-Install

**Left Panel — Pre-Install Status**
- Checklist items from pre-install Podio app (29839773)
- Status of each requirement
- Issues flagged

**Right Panel — Actions**
- Resolve issues
- Link to pre-install Podio item

---

## Tab 5: Project Review

**Left Panel — Review Dashboard (Stripe-style data density)**
- Project details: status, milestone, lender, finance type, funding status
- Milestones table (existing, expanded by default)
- Funding milestones (existing)
- Days since review with date picker

**Right Panel — Review Actions**
- Project Review compose (existing inline compose)
- "Save Review" button
- Project notes (existing)

---

## Tab 6: Change Orders

**Left Panel — Change Order History**
- List of design change orders for this project (from app 29841104)
- Each: date, type, status, description

**Right Panel — Actions**
- Create change order (if applicable)
- Link to Podio

---

## Tab 7: Roof Reviews

**Left Panel — Roof Status**
- Roof review status from SOW (roofReview field)
- Roof work items (from app 29839741)

**Right Panel — Actions**
- Update roof review status
- Link to Podio

---

## Mobile Layout
On mobile (< 768px), the split view collapses:
- Tabs become horizontally scrollable
- Single panel view (no left/right split)
- Tab content fills full width
- Quick actions appear below content (not in separate panel)
- Swipe left/right between projects (existing)

## Spacing System (from Linear)
- Tab gap: 4px
- Panel padding: 0.75rem (12px)
- Row gap in lists: 0
- Section spacing: 0.75rem
- Inline item gap: 6-8px

## Status Color System (Battlefront 2015 — closed palette, 4 colors only)
**Hard rule:** the entire dashboard uses exactly these four colors. No other hex values are permitted. Differentiate state via opacity / weight / border, not new hues.

- **Black** — `#000` primary bg, `#0a0a0a` alt bg
- **White** — `#fff` primary text; `rgba(255,255,255,.X)` for all muted / complete / border tiers (`.06`, `.08`, `.25`, `.3`, `.35`, `.5`, `.55`)
- **Silver** — `#C0C0C0` — the single accent for warning / critical / attention / review-overdue / "needs action". Warn and crit collapse to the same silver.
- **Light blue** — `#ADD8E6` — brand accent, active states, hover, links, key highlights

Deprecated (do NOT use): `#C9A96E`, `#C97850`, or any reference-mockup palette color (Linear blue/amber/red/green, etc.).

## Data Flow
All tabs read from the same `item` object (already loaded from Projects).
SOW tab additionally fetches the linked SOW item from Podio (by project number match).
Pre-Install and Change Order tabs fetch from their respective Podio apps when first opened.
Roof Reviews fetches from the Roof Work app when first opened.
Data is cached per session — no redundant fetches.

## Implementation Order
Build and perfect each tab one at a time:
1. Support Tickets
2. Communication
3. SOW
4. Pre-Install
5. Project Review
6. Change Orders
7. Roof Reviews

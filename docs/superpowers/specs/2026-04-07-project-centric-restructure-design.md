# Aveyo Dashboard — Project-Centric Restructure Design Spec

## Overview
Restructure the Aveyo dashboard around PM responsibilities. Each responsibility becomes a top-level tab in a scrollable bottom nav. All tabs follow a consistent queue/list pattern with filter chips. Battlefront 2015 aesthetic is unchanged.

## Bottom Nav — Scrollable with Badge Counts
Text-only tabs (no icons) in a single horizontally scrollable row. Live badge counts show items needing attention. Active tab has white text + 2px bottom border. Inactive tabs are rgba(255,255,255,.3).

**Tab order (priority):**
```
HOME | TICKETS 3 | COMMS 5 | SOW 8 | PRE-INSTALL | REVIEW 12 | CHANGE | ROOF | KB
```

**Badge count colors** use existing widget warning/critical thresholds:
- Normal count: rgba(255,255,255,.15) background, white text
- Warning: #C9A96E background, black text
- Critical: #C97850 background, black text

Badge counts are fetched from existing widget data (Podio view counts already cached).

## Shared Design Patterns

### Queue List Row
All tabs use the same row structure:
- **Line 1:** Bold identifier (left) + status badge (right)
- **Line 2:** Customer name, bold, 12px
- **Line 3:** Address or secondary info, rgba(255,255,255,.35), 9px
- **Line 4:** Description/context, rgba(255,255,255,.55), 10px
- **Line 5:** Creator or metadata (left) + age timer (right)
- Row separated by 1px border: rgba(255,255,255,.04)
- Row padding: 14px 16px

### App-Wide Color System
Three status colors used consistently across the entire app — timers, badges, status indicators, filter chips, checklist items, progress bars, and any element that conveys state.

- **#ADD8E6 (light blue)** — good / new / fresh / under threshold / verified / approved
- **#fff (white)** — moderate / neutral / in progress
- **#E88B8B (light red)** — overdue / urgent / failed / needs attention

These replace the previous mixed color system (#C9A96E amber, #C97850 orange, #3B6D11 green, etc.) for all status-related UI. The only exception is the bottom nav badge counts, which keep #C9A96E / #C97850 to match existing widget thresholds.

**Applied to timers:**
- Under 3 days: #ADD8E6
- 3 to 14 days: #fff
- Over 14 days: #E88B8B
- Exception: Review tab uses #E88B8B for anything 7+ days

**Applied to status badges:**
Small all-caps labels, 6px font, 700 weight, .1em letter-spacing, 2px 8px padding.
- Good state: background rgba(173,216,230,.12), color #ADD8E6, border rgba(173,216,230,.2)
- Neutral state: background rgba(255,255,255,.06), color rgba(255,255,255,.5), border rgba(255,255,255,.1)
- Urgent state: background rgba(232,139,139,.12), color #E88B8B, border rgba(232,139,139,.2)

**Applied to filter chips:**
Horizontal row above the list, scrollable if needed.
- Active chip: white text, 2px bottom border
- Inactive chip: rgba(255,255,255,.3) text, 1px border rgba(255,255,255,.08)
- Urgent chip: #E88B8B text, 1px border rgba(232,139,139,.25)

**Applied to checklist items (SOW tab):**
- Verified: #ADD8E6 with checkmark
- Failed: #E88B8B with X
- Pending: rgba(255,255,255,.2) with --

**Applied to progress indicators:**
- Complete segments: #ADD8E6
- Current segment: #fff
- Incomplete: rgba(255,255,255,.1)

## Tab 1: TICKETS (Support Tickets)
**Data source:** Podio Support Tickets app 29840119, view 61747488

**Filter chips:** ALL | OPEN | ASSIGNED

**Row layout:**
- **Bold ticket ID** (#48291) — top left, 13px, 700 weight
- Status badge (OPEN / ASSIGNED / COMPLETE) — top right
- Customer name — 12px, 600 weight
- Address — 9px, rgba(255,255,255,.35)
- Ticket description — 10px, rgba(255,255,255,.55)
- "Created by [name]" (left) + live age timer (right)

**Sort:** Newest first (most recent ticket date at top).

**Tap action:** Opens the project detail view for that customer.

## Tab 2: COMMS (Communication)
**Data source:** Projects app 29839792, views 61743343 (Customer Update Needed) and 61743344 (Rep Update Needed)

**Filter chips:** ALL | REP | CUSTOMER

**Row layout:**
- Customer name — 12px, 600 weight (left) + type badge REP UPDATE or CUSTOMER TEXT (right)
- Milestone + rep name — 9px, rgba(255,255,255,.35)
- Reason for update — 10px, rgba(255,255,255,.55)
- "Last contact: Xd ago" (left) + age timer (right)

**Sort:** Longest since last contact first.

**Tap action:** Opens project detail with compose form ready.

## Tab 3: SOW (Scope of Work)
**Data source:** SOW app 29839685, multiple views (Ready 61743307, Rejections 61743308, Rep SOW 61743310, No Redlines 61743311, Rep Pending 61743313, Cust Rejections 61743314, Cust Sent 61743315, Ready to Send Cust 61743332, Roof Review 61743312)

**Filter chips:** ALL | READY | REP SOW | CUST SOW | REJECT

**Row layout:**
- Customer name — 12px, 600 weight (left) + SOW status badge (right)
- System size + contract price + lender — 9px, rgba(255,255,255,.35)
- Mini verification checklist inline: SIZE, PRICE, DESIGN, ROOF, ELEC
  - Verified: #ADD8E6 with checkmark
  - Failed: #E88B8B with X
  - Pending: rgba(255,255,255,.2) with --

**Tap action:** Opens full SOW detail (existing buildSOWDetail functionality).

## Tab 4: PRE-INSTALL
**Data source:** Pre-Install app 29839773, views 61743334 (Ready) and 61743335 (Issues)

**Filter chips:** ALL | READY | ISSUES

**Row layout:**
- Customer name — 12px, 600 weight (left) + status badge READY or ISSUE (right)
- Milestone + address — 9px, rgba(255,255,255,.35)
- Status description — 10px, rgba(255,255,255,.55)

**Tap action:** Opens project detail view.

## Tab 5: REVIEW (Project Review)
**Data source:** Projects app 29839792, filtered by daysSince field (276204428). View 61743302 (Review Needed) and 61743306 (Not Set).

**Filter chips:** OVERDUE | NOT SET | ALL

**Row layout:**
- Customer name — 12px, 600 weight (left) + days since review (right, large 11px bold)
- Milestone + address — 9px, rgba(255,255,255,.35)
- "Last reviewed: [date]" — 9px, rgba(255,255,255,.4)

**Timer color (Review-specific):** Anything 7+ days = #E88B8B (red). Under 7 days = #ADD8E6 (light blue).

**Sort:** Most days since review first (worst at top).

**Tap action:** Opens project detail with review date picker ready.

## Tab 6: CHANGE ORDERS
**Data source:** Change Orders app 29841104, view 61743336

**Filter chips:** None needed initially (low volume). Add if count grows.

**Row layout:**
- **Bold change order ID** (#CO-1042) — top left, 13px, 700 weight
- Type badge (DESIGN CHANGE) — top right
- Customer name — 12px, 600 weight
- Address — 9px, rgba(255,255,255,.35)
- Description — 10px, rgba(255,255,255,.55)
- "Created by [name]" (left) + age timer (right)

**Tap action:** Opens change order detail / linked project.

## Tab 7: ROOF (Roof Reviews)
**Data source:** Roof Work app 29839741, view 61743345. Also SOW field roofReview (269989063).

**Filter chips:** ALL | CUSTOMER | AVEYO | NOT SET

**Row layout:**
- Customer name — 12px, 600 weight (left) + roof type badge (right)
  - CUSTOMER ROOF: light blue badge
  - AVEYO ROOF: neutral badge
  - NOT SET: red badge
- Address — 9px, rgba(255,255,255,.35)
- Description — 10px, rgba(255,255,255,.55)
- "Flagged: [date]" (left) + age timer (right)

**Tap action:** Opens project detail / SOW with roof review status.

## What Stays Unchanged
- **Home dashboard** — widgets, pipeline bar, review list (unchanged)
- **Project detail view** — split panels, banner, all existing tabs (Milestones, Details, Comments, Work Orders, Tickets, Notes | Rep Update, Customer Text, Project Review)
- **Knowledge tab** — adder sheet, SOPs (unchanged)
- **Battlefront 2015 aesthetic** — #000 bg, #ADD8E6 accent, PPTelegraf font, all-caps labels, zero border-radius, no emojis, 1px separators

## What Gets Removed
- **SOW as standalone tab** — replaced by SOW responsibility tab (reads from same Podio app)
- **Comms as standalone tab** — replaced by Comms responsibility tab
- **Action tab** — its functionality is distributed across the responsibility tabs (tickets, comms, review all surface action items)

## Data Flow
1. On app load, fetch widget counts for all Podio views (already happening for Home widgets)
2. Badge counts in bottom nav come from these cached widget counts
3. When a tab is tapped, fetch the full item list for that tab's Podio app/view (lazy load)
4. Cache items per session — switching tabs doesn't re-fetch
5. Tapping a project from any tab opens the same detail view, with PREV_VIEW set to the source tab

## Implementation Order
Build each tab one at a time, ship and verify before moving to the next:
1. Scrollable bottom nav with badge counts
2. Tickets tab
3. Comms tab
4. SOW tab
5. Pre-Install tab
6. Review tab
7. Change Orders tab
8. Roof tab

# SOW Queue Tab — Design Spec

## Overview

Build a SOW Responsibility queue tab following the same pattern as the Tickets tab. Replaces the current stubbed `loadSOWResp()` with a fully functional queue view using 10 Podio views as filter chips.

## Scope

Queue list view only. No detail view — tapping a row does nothing for now.

## Data Source

- **Podio App ID:** 29839685 (SOW)
- **Filter chips map to 10 Podio views:**
  - 61743309: Total in SOW (default)
  - 61743307: Ready for SOW
  - 61743308: SOW Rejections
  - 61743310: Ready to Send Rep SOW
  - 61743311: Projects w/ No Redlines
  - 61743313: Rep SOW Pending Approval
  - 61743314: Customer SOW Rejections
  - 61743315: Customer SOW Sent
  - 61743332: Ready to Send Cust SOW
  - 61743312: Roof Review Needed (SOW)

## Loading Screen

Full-screen fixed overlay (#000 background) with centered 100px spinning Aveyo logo (3D Y-axis rotation) and "LOADING..." text. Same pattern as Tickets loading. Filter chips hidden while loading.

## Filter Chips

- Use existing `.resp-chip` / `.resp-filter` CSS classes
- 10 chips, each showing view name + item count after fetch
- Default active chip: Total in SOW
- Tapping a chip fetches that Podio view via `fetchAllItems(29839685, viewId)`
- Cache fetched results per-chip for the session (switching back doesn't re-fetch)
- Chips scroll horizontally on mobile, wrap on desktop

## Queue Row Layout

Reuse existing `.resp-row` CSS classes (same as Tickets). Each row contains:

1. **Top line:** Project number (left, `.resp-row-id`) + status badge (right, `.resp-badge`)
   - Badge text = short view name (e.g. "READY FOR SOW", "SOW REJECTION")
   - Badge color: blue (`.good`) for normal, red (`.urgent`) for rejections
2. **Customer name** (`.resp-row-name`)
3. **Address** (`.resp-row-meta`)
4. **System info line:** System size + contract price, separated by pipe
5. **Verification progress bar:** Thin 2px bar showing X/8 verified items
   - Blue when on track, red when low completion on old items
   - "X/8" label right-aligned
6. **Bottom line:** Rep name (left) + DD:HH:MM:SS age timer (right, `.resp-timer`)
   - Timer colors: blue (<5 days), white (5-10 days), red (>10 days)

## Data Parsing

Parse each SOW item from Podio:
- **Title parsing:** Same regex pattern as Tickets — extract project number, customer name, address from `item.title`
- **System size:** Read from field `SOW_FIELD.systemSize` (267350045)
- **Contract price:** Read from field `SOW_FIELD.contractPrice` (267350044)
- **Verification count:** Count how many of these 8 fields have a non-empty/positive value:
  - systemSizeMatches (271721075)
  - contractPriceMatches (271721078)
  - designMatches (271721079)
  - electricalWork (271721076)
  - structuralUpgrade (271721077)
  - roofReview (269989063)
  - repDesignApproval (266496729)
  - permitDesign (267966500)
- **Rep info:** Parse from item fields (same approach as Projects tab)
- **Age:** Calculate from `item.created_on`

## Nav Wiring

The SOW nav button currently calls `showView('sowresp'); loadSOWResp()`. Keep this — just replace the stubbed `loadSOWResp()` with the real implementation that renders the queue into `#sowresp-list` with filter chips in `#sowresp-filters`.

## Responsive Behavior

- **Mobile:** Card rows stack vertically, chips scroll horizontally
- **Desktop:** Same card layout but wider with more padding, chips wrap to show all 10

## Implementation Notes

- Follow the exact same code pattern as `loadTickets()` / `renderTickets()`
- Store fetched items in a `SOW_ITEMS` object keyed by view ID for caching
- Current active filter stored in `SOW_FILTER` variable (default: '61743309')
- Rows are not tappable — no click handler needed yet

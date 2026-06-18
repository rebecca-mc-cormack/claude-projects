# Portfolio Design Feedback — Session Notes

> **File:** `portfolio_design_feedback.md`
> **Project:** `rebecca_mccormack_portfolio.html`
> **Purpose:** Design decisions and user feedback from the build session, May 2026. Revisit this when updating the portfolio.

---

## Visual style

### Match the Accenture one-pager PPT style
The portfolio should look like the Accenture corporate one-pager document (March 2026), not a web app. Key elements to maintain:

- **White background** throughout — no dark sections except the closing assessment
- **Name in large bold uppercase purple** at the top (`#A100FF`)
- **Accenture `> accenture` logo** top right
- **Purple section bars** (solid `#A100FF` background, white uppercase text) as section headers — matches the "PROFESSIONAL BACKGROUND" / "SELECTED EXPERIENCES" bars from the PPT
- **No decorative elements** — no gradient orbs, no watermarks, no shadows beyond minimal card borders
- **3px purple border** on bottom of page header
- **Purple left border** on priority cards (4px, `#A100FF`)

### Typography
- Font: **Graphik** (Accenture brand font, installed on Accenture devices) with **DM Sans** as fallback
- Do **not** use Inter (too generic)
- Display/serif fonts (Cormorant Garamond) are fine for decorative headings only — avoid for body text
- Body text: minimum **15px**, weight **400** (not light/300), line-height **1.75–1.85**
- Secondary text should use **#555** not `#818180` — the gray was too light to read comfortably

### Readability improvements applied
- Base font size: 17px
- Body text weight: 400 (not 300)
- Context paragraph: 18px, line-height 1.85
- Priority descriptions: 16px, line-height 1.85
- All grays lightened: `#4a4a4a` / `#555` instead of `#818180`
- Section labels: slightly larger and less washed-out

---

## Layout

### Overview / context section
- Must be **full width** — no `max-width` constraint
- No heading needed — the section bar label is sufficient

### Priorities
- **All five priorities must be visible at the same time** — no hidden content on initial load
- Use a **2-column card grid**, not an accordion (accordion hides content)
- Cards are **clickable** — opens a modal with full details (description, impact metrics, feedback, work samples)
- "View feedback →" label at bottom of each card to make clickability clear
- The 5th card (if odd) should span full width

### Download buttons
- **Tab-specific** — each download button is positioned **top right** of its tab
- No persistent download buttons visible at all times
- Label convention: "Download (.png)" / "Download Excel (.xlsx)" / "Download Word (.docx)"

### Section padding
- Keep sections compact — **56px vertical padding** is sufficient
- Hero/header: **min-height 380px** is enough
- Less scrolling is better: avoid excessive whitespace between sections

---

## Interactions

### Priority card modals
- Click card → modal opens with: full description, impact metrics grid, feedback placeholder (dashed purple left border), work samples placeholder
- Press `Escape` or click outside modal to close
- Modal should animate in (translateY + opacity)
- Keep close button visible and accessible

### Process flow map tab
- Layer toggle (left) and Download button (right) both in the same toolbar row above the map
- "Show Activities" toggle stays with the layer controls on the left
- PNG export via html2canvas (2× scale for retina quality); fall back to HTML export if library unavailable

### MBR Requirement Spec tab
- Section 3.1 renders **inline flow maps** (not placeholder text) — one per BasicOperation using `buildL2HTML()`
- Draft label shows `Draft v1.0 — [GMBR description]` top left
- Download Word button is muted purple (`#E6DCFF` background, `#460073` text) — not the full core purple

---

## Content decisions

### What to include
- Stats strip: Promoted to AM, Months at AM, Chargeability, Years at Accenture, Talent Indicator, Overall Rating
- Overview: Full paragraph (no `max-width` limit)
- Delivery highlights: 4 large number callouts (433, 3, 5, >80%)
- FY26 Priorities: 5 cards, all visible, click to expand
- Skills to Grow: 3 cards (Sales/commercial, Agentic AI, Strategy)
- Work Portfolio: 6 placeholder slots
- Overall Assessment: Dark section at bottom

### Skills to Grow section
Added at user's request. Three focus areas with detailed advisory text:
1. **Sales & client-facing commercial work** — hardest to manufacture; get visibility into bid activity, talk to Matt, plug into account planning cycles
2. **Building agentic AI workflows** — EBR tool is the proof of concept; formalize through Amethyst Studio, find one live agentic workflow on AZ
3. **Strategy-focused work** — repositioning how you show up; write up global standardisation approach as a point of view, shift from delivery to strategy framing

---

## Things that didn't work / were changed

| Attempt | Issue | Resolution |
|---|---|---|
| Accordion cards (expandable) | Content hidden by default; user wanted all priorities visible | Replaced with 2-column card grid |
| Table/row layout | Not scannable enough for "all in view" requirement | Replaced with card grid |
| Dark purple hero section | Doesn't match Accenture PPT style | Replaced with clean white header + purple section bars |
| Bottom download buttons | Spec requires top-right placement | Moved to toolbar above each tab |
| Inter font | Too generic per design skill guidelines | Use Graphik (local) + DM Sans (Google Fonts fallback) |
| Decorative background elements (orbs, watermarks) | Clash with corporate document aesthetic | Removed entirely |

---

## File structure

```
claude-projects/
├── rebecca_mccormack_portfolio.html   # Interactive portfolio page
├── rebecca_mccormack_portfolio.md     # Content source / revisit file
└── portfolio_design_feedback.md       # This file — design decisions & feedback
```

---

*Last updated: May 2026*

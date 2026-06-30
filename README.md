# claude-projects — Session Context

This repo contains three separate projects, all worked on with Claude Code. Read this file at the start of each session to orient quickly.

---

## Projects at a glance

| Project | File | Status |
|---------|------|--------|
| EBR Validation Tool | `ebr-validation-tool/PASX_ValidationTool.html` | Active — core features complete, polish remaining |
| AstraZeneca Opportunity Canvas | `az-opportunity-canvas/astrazeneca_opportunity_canvas.html` | Active — 5 slides, 3 canvases |
| Rebecca's Portfolio | `portfolio/rebecca_mccormack_portfolio.html` | Stable |

---

## 1. EBR Validation Tool

**What it is:** A single-file browser app that parses PAS-X GMBR XML exports and generates validation artefacts — an interactive process flow map, a Review by Exception sheet, and an MBR URS preview.

**How to open:**
```bash
py -m http.server 3000
# then open http://localhost:3000/ebr-validation-tool/PASX_ValidationTool.html
```
Or open `ebr-validation-tool/PASX_ValidationTool.html` directly in Chrome.

**Key files:**
- `ebr-validation-tool/PASX_ValidationTool.html` — the entire app (single self-contained file)
- `ebr-validation-tool/` — Python prototype (reference only; superseded by the HTML tool)
- `ebr-validation-tool/EBR_Tool_Master_Reference.md` — master reference spec (source of truth for decisions and design)
- `ebr-validation-tool/EBR_Validation_Tool_Figma_Spec_1.md` — Figma UI spec
- `ebr-validation-tool/SPEC.md` — additional spec notes

**Spec docs (external):**
Located at `C:\Users\rebecca.mc.cormack\OneDrive - Accenture\Documents\AZ\Claude\Tool\`
- `EBR_Validation_Tool_Figma_Spec.md` — UI/visual design spec
- `EBR_Validation_Tool_Requirements_Spec.docx` — formal requirements spec

**Current state (June 2026):**
- Graph-based flow map rendering with directed graph traversal via `ProdStepLinkCollection`
- Parallel branch detection, split/sync node shapes, correct post-convergence rendering
- Review by Exception tab with auto-suggestion logic and cross-referencing
- MBR URS preview tab with inline flow maps and Word export
- Excel export via SheetJS

**Remaining work:**
- [ ] Arrow styling refinement (colours, sizes, positioning)
- [ ] Nested CBFs (CBFs within CBFs) — parser foundation in place, Layer 2 UI needs extending
- [ ] True `.drawio` / Visio export (currently exports standalone HTML)
- [ ] Outputs 4 (Pathways Excel) and 5 (Test Scripts) — business rules TBD
- [ ] PMBR support (Parametrised MBR)
- [ ] Material Input display
- [ ] PNG export via html2canvas

**Design system:** Accenture brand palette — core purple `#A100FF`, dark purple `#7500C0`, background `#F7F5F2`. Font: Graphik / DM Sans / Helvetica Neue.

---

## 2. AstraZeneca Opportunity Canvas

**What it is:** A slide deck (single HTML file, keyboard-navigable) presenting three AI opportunities to AstraZeneca — used in a joint working session with Accenture × Anthropic.

**How to open:** Open `az-opportunity-canvas/astrazeneca_opportunity_canvas.html` directly in a browser. Arrow keys navigate between slides.

**Structure (5 slides):**

| Slide | Content |
|-------|---------|
| 1 | Cover / title |
| 2 | Overview — three opportunities summary |
| 3 | Canvas 01: Clinical Trial Decisioning Platform |
| 4 | Canvas 02: Engineering Digital Twin Agents |
| 5 | Canvas 03: MES Chatbot for GMBR Review |

Each canvas slide covers: Problem → Stakeholders → Anthropic value → Accenture value → Faculty value → Combined impact for AstraZeneca.

**Design system:** Dark theme (`#0e1116`), coral accent (`#CC785C`), Newsreader serif + Inter sans-serif. Progress bar and dot navigation auto-update with slide count.

**Current state:** All 5 slides complete. No outstanding items.

---

## 3. Rebecca's Portfolio

**What it is:** A personal portfolio HTML page (`portfolio/rebecca_mccormack_portfolio.html`) and source markdown (`portfolio/rebecca_mccormack_portfolio.md`).

**Status:** Stable. Design feedback notes in `portfolio/portfolio_design_feedback.md`.

---

## Session notes

- **Update this README at the end of every session** to reflect changes made.
- The AstraZeneca canvas originated as separate per-slide HTML files (`AZ_Canvas00_Cover.html`, `AZ_Canvas01_Three_Opportunities.html`, `AZ_Canvas03_PASX_Chatbot.html`) — these are reference/input files only; the single-file `az-opportunity-canvas/astrazeneca_opportunity_canvas.html` is the live version.
- The EBR tool's design decisions are documented in `EBR_Tool_Master_Reference.md` (Design Decision Log, section 19 onward) — check there before changing established behaviour.

---

*Last updated: 2026-06-30 — Reorganised folder: each project now has its own subfolder (ebr-validation-tool/, az-opportunity-canvas/, portfolio/)*

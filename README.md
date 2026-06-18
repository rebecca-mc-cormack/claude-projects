# EBR Validation Tool

A single-file browser app that parses PAS-X GMBR XML exports and instantly generates validation artefacts — interactive process flow maps, a Review by Exception sheet, and an MBR User Requirements Specification preview.

---

## What It Does

Upload a PAS-X Generic Master Batch Record (GMBR) XML export and the tool automatically:

1. **Parses the XML** — reads the full GMBR hierarchy (Basic Operations → Basic Functions → Activities) using ProdStepLinkCollection to determine correct step ordering
2. **Renders an interactive process flow map** — two-layer drill-down with directed graph traversal, parallel branch detection, and proper rendering of split/sync nodes
3. **Generates a Review by Exception sheet** — auto-populated risk and confirmation defaults per CBF, with dropdown overrides
4. **Generates an MBR URS preview** — document preview with auto/manual field highlighting and inline flow maps per Basic Operation
5. **Exports all outputs** — HTML process map, Excel RbE sheet, Word-compatible URS document

---

## Tabs

### Tab 1 — Process Flow Map

Two layers:

| Layer | Shows | Interaction |
|-------|-------|-------------|
| **Layer 1** | Basic Operations (BO cards) | Click any BO → drills to Layer 2 |
| **Layer 2** | Basic Functions (CBF cards) within selected BO | Per-node expand/collapse + cross-ref to RbE |

**Flow rendering:**
- Nodes are ordered via directed graph traversal using `ProdStepLinkCollection` edges, not XML document order
- Parallel branches are detected automatically when a node has multiple outgoing edges
- Branch nodes are rendered side-by-side in columns with equal width
- Split nodes render as a thick horizontal bar (`#622A8F`)
- Sync nodes render as a V-shape converging to a point (`#622A8F`)
- Post-convergence nodes continue vertically and appear only once, centered below all branches

**Interactions on Layer 2:**
- **Click a node title** — expands/collapses activity rows for that node inline
- **Click a CBF ID** (dotted purple underline) — jumps to the Review by Exception tab and highlights that CBF's row(s)
- **Download (.png)** button top right — exports current layer as a standalone HTML file

**Node styling (per design spec):**
- All nodes: white fill (`#FFFFFF`), colored border (`1.5px`)
- Text: node ID in bold purple (`#3D006B`), description in dark (`#2A1A3E`), type label in muted gray (`#7A7280`)
- Minimum font size: `12pt`

**Border colours by category:**

| Category | Step types | Colour |
|---|---|---|
| Flow control | CommonBFVO / SpecDecisionVO | Darkest purple `#3D006B` |
| Material flow | TakeOutBFVO / IdentityCheckBFVO / YieldDeterminationBFVO / BundleCreationBFVO / StockCreationBFVO | Blue `#185FA5` |
| Equipment | EqmAllocationBFVO / EqmDeallocationBFVO / EqmIdentificationBFVO / StartStepVO / EndStepVO | Dark gray `#818180` |
| Label/context | GenericLabelPrintBfVO / SetCxBfVO | Mid gray `#888780` |
| Control flow | MergeVO / SplittingVO / SynchronisationVO | Muted purple `#622A8F` |

> **Note on future nested CBFs:** Some PAS-X XMLs contain CBFs nested within other CBFs. The current Layer 2 view is designed to accommodate this — do not add a hardcoded Layer 3, instead extend the recursive parser when needed.

---

### Tab 2 — Review by Exception

An 8-column risk assessment table — one row per CBF step in the GMBR.

| # | Column | Source |
|---|--------|--------|
| 1 | Process Map Ref. | CBF ID — clickable link back to flow map |
| 2 | GMBR Path Reference | e.g. `BO1 > CBF17` |
| 3 | Description | CBF description from XML |
| 4 | Process Step Type | Auto-suggested + dropdown override |
| 5 | Confirmation Level Required | Auto-suggested + dropdown override |
| 6 | Can data be QA'd at time of order? | 8-option dropdown |
| 7 | Required at Batch Record Review? | Auto-calculated from column 6 (Yes/No) |
| 8 | Comment | Blank — completed after download |

**Auto-suggestion logic (columns 4 & 5):**
- Columns 4 and 5 are pre-populated based on the activity types present in each CBF
- Auto-suggested values are shown with a **purple border** on the dropdown — border clears when manually overridden
- Column 7 auto-calculates: col6 starts "Yes" or "N/A" → No; starts "No" → Yes; colour-coded green/red

**Cross-reference:** Click a process map ref (column 1) → switches to Process Flow Map tab and highlights that node with a purple border.

**Download Excel (.xlsx)** — exports the full table including any dropdown selections made.

---

### Tab 3 — MBR Requirement Spec

A document preview matching the standard MBR URS format. Fields are colour-coded:
- **White background** — auto-populated from XML (GMBR ID, description, material name, inline flow maps)
- **Amber highlight** ✎ — needs manual input after Word export (document ID, version, dates, site tables, roles, reference documents)

Section 3.1 renders inline Layer 2 flow maps — one per Basic Operation — auto-generated from the XML.

**Download Word (.docx)** — exports a Word-compatible `.doc` file preserving the preview structure.

---

## XML Parsing

- Handles PAS-X full Java class names as XML tag names (e.g. `com.werum.pasx.spec.components.pmbr.global.GenericMasterBatchRecordVO`) — uses `findEl(root, suffix)` with `getElementsByTagName('*')` and suffix-matching to bypass the CSS selector dot-as-class limitation
- **Graph-based traversal:** Extracts `ProdStepLinkCollection` source/target references and builds a directed graph (node_id → [target_ids]); renders nodes following graph edges, not XML document order
- **Parallel branch detection:** Identifies nodes with multiple outgoing edges (split points) and multiple incoming edges from different branches (sync/convergence points); renders branches side-by-side
- **Reference ID mapping:** Converts XML element reference IDs to custom step IDs for consistent graph building and rendering
- Resolves internal formula references to human-readable paths (e.g. `RMCTEST/BO1/CBF17/ACT10`)
- Recognises all PAS-X step types: flow control, material flow, equipment, label/context
- Recognises all specPropCollection activity types: `AttributiveSpecPropVO`, `MeasuredValueSpecPropVO`, `FormulaSpecPropVO`, `TextSpecPropVO`, `DateSpecPropVO`, `ListSpecPropVO`

---

## File Structure

```
claude-projects/
├── PASX_ValidationTool.html   # The entire app — single self-contained file
├── README.md                  # This file
└── portfolio/
    ├── rebecca_mccormack_portfolio.md
    └── portfolio_design_feedback.md
```

---

## How to Use

### Option A — Open directly in browser
Open `PASX_ValidationTool.html` in Chrome (or any modern browser).

### Option B — Run via local server (Claude Code launch.json)
```bash
py -m http.server 3000
# then open http://localhost:3000/PASX_ValidationTool.html
```

### Uploading XML
1. Export your GMBR from PAS-X as XML
2. Drop the `.xml` file onto the upload zone, click **Browse file**, or click **Paste XML**
3. The tool parses instantly and populates all three tabs

---

## Design System

Accenture brand palette:

| Token | Value |
|-------|-------|
| Core purple | `#A100FF` |
| Dark purple | `#7500C0` |
| Darkest purple | `#460073` |
| Light purple | `#C2A3FF` |
| Lightest purple | `#E6DCFF` |
| Pink | `#FF50A0` |
| Blue | `#2248FF` |
| Dark gray | `#818180` |
| Background | `#F7F5F2` |
| Font | Graphik / DM Sans / Helvetica Neue / Arial |

---

## Technical Notes

- **No build step** — pure HTML/CSS/JS, single file
- **SheetJS** (`xlsx.full.min.js`) loaded from CDN for Excel generation
- **DOMParser** used for XML parsing with `text/xml` mode
- Cross-referencing uses `data-bfid` attributes on map nodes and RbE rows — no server needed
- All map styles injected inline so the map is fully portable for export
- Word export generates an HTML blob with `application/msword` MIME type — opens in Word as `.doc`

---

## Spec Documents

Located in `C:\Users\rebecca.mc.cormack\OneDrive - Accenture\Documents\AZ\Claude\Tool\`:

| File | Description |
|------|-------------|
| `EBR_Validation_Tool_Figma_Spec.md` | UI structure, interactions, visual design spec |
| `EBR_Validation_Tool_Requirements_Spec.docx` | Formal requirements specification (outputs 1–3 defined) |

---

## Roadmap / Known Considerations

### Completed (June 2026)
- [x] Graph-based flow map rendering with parallel branch detection
- [x] Directed graph traversal using ProdStepLinkCollection edges
- [x] Split/Sync node shapes and styling
- [x] Responsive node layout for narrow parallel columns
- [x] Reference ID to custom ID mapping

### Remaining
- [ ] Arrow styling refinement (colors, sizes, positioning)
- [ ] Support for nested CBFs (CBFs within CBFs) — parser foundation is in place, Layer 2 UI will need extending
- [ ] True `.drawio` / Visio export — currently exports standalone HTML
- [ ] Outputs 4 (Pathways Excel) and 5 (Test Scripts) — business rules TBD per spec
- [ ] PMBR (Parametrised MBR) support in addition to GMBR
- [ ] Material Input display
- [ ] PNG export via html2canvas (currently exports HTML)

---

*Last updated: 2026-06-18* — Graph-based flow map rendering, parallel branches, split/sync shapes

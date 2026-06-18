# EBR Validation Tool

A single-file browser app that parses PAS-X GMBR XML exports and instantly generates validation artefacts — interactive process flow maps, a Review by Exception sheet, and an MBR User Requirements Specification preview.

---

## What It Does

Upload a PAS-X Generic Master Batch Record (GMBR) XML export and the tool automatically:

1. **Parses the XML** — reads the full GMBR hierarchy (Basic Operations → Basic Functions → Activities) using ProdStepLinkCollection to determine correct step ordering
2. **Renders an interactive process flow map** — two-layer drill-down with per-node activity expand and cross-referencing to the RbE table
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

**Interactions on Layer 2:**
- **Click a node title** — expands/collapses activity rows for that node inline
- **Click a CBF ID** (dotted purple underline) — jumps to the Review by Exception tab and highlights that CBF's row(s)
- **Download (.png)** button top right — exports current layer as a standalone HTML file

**Step type colour coding (Accenture brand palette):**

| Category | Step types | Colour |
|---|---|---|
| Flow control | StartStepVO / EndStepVO | Dark gray `#818180` |
| Flow control | BasicOperationVO | Darkest purple `#460073` |
| Flow control | CommonBFVO | Dark purple `#7500C0` |
| Flow control | SpecDecisionVO | Core purple `#A100FF` |
| Flow control | MergeVO / SplittingVO | Light purple `#C2A3FF` |
| Flow control | SynchronisationVO | Lightest purple `#E6DCFF` |
| Material flow | TakeOutBFVO / IdentityCheckBFVO / YieldDeterminationBFVO / BundleCreationBFVO / StockCreationBFVO | Pink `#FF50A0` |
| Equipment | EqmAllocationBFVO / EqmDeallocationBFVO / EqmIdentificationBFVO | Medium gray `#CFCFCF` |
| Label/context | GenericLabelPrintBfVO / SetCxBfVO | Blue `#2248FF` |

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
- Orders steps using `ProdStepLinkCollection` source/target references; falls back to Y-coordinate sort if no links present
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

- [ ] Support for nested CBFs (CBFs within CBFs) — parser foundation is in place, Layer 2 UI will need extending
- [ ] True `.drawio` / Visio export — currently exports standalone HTML
- [ ] Outputs 4 (Pathways Excel) and 5 (Test Scripts) — business rules TBD per spec
- [ ] PMBR (Parametrised MBR) support in addition to GMBR
- [ ] Material Input display
- [ ] PNG export via html2canvas (currently exports HTML)

---

*Last updated: June 2026*

# PAS-X Validation Export Tool

A single-file browser app that parses PAS-X GMBR XML exports and instantly generates validation artefacts — process flow maps, pathway Excel sheets, and Visio-compatible diagrams.

---

## What It Does

Upload a PAS-X Generic Master Batch Record (GMBR) XML export and the tool automatically:

1. **Parses the XML** — reads the full GMBR hierarchy (Basic Operations → Basic Functions → Activities) using the ProdStepLinkCollection to determine correct ordering
2. **Renders an interactive process flow map** — with drill-down levels and show/hide activity detail
3. **Generates a pathway Excel sheet** — matching the 20-column test options format used for validation
4. **Exports diagrams** — standalone HTML process map and draw.io diagram (convertible to Visio .vsdx)

---

## Features

### XML Parsing
- Handles PAS-X full Java class names as XML tag names (e.g. `com.werum.pasx.spec.components.pmbr.global.GenericMasterBatchRecordVO`)
- Orders steps using `ProdStepLinkCollection` source/target references and Y-coordinates as fallback
- Resolves internal formula references to human-readable paths (e.g. `RMCTEST/BO1/CBF17/ACT10`)
- Supports: `BasicOperationVO`, `CommonBFVO`, `EqmAllocationBFVO`, `AttributiveSpecPropVO`, `MeasuredValueSpecPropVO`, `FormulaSpecPropVO`, `MaterialOutputVO`

### Process Flow Map

Two levels of drill-down:

| Level | Shows | Interaction |
|-------|-------|-------------|
| **Level 1** | Basic Operations (BO cards) | Click any BO → drills to Level 2 |
| **Level 2** | Basic Functions (CBF cards) within selected BO | Toggle activities with Show/Hide button |

- **Show Activities** / **Hide Activities** toggle (gold button) — expands/collapses activity rows within each CBF card
- Activity type colour coding: Attributive (green), Measured Value (amber), Formula (purple), Equipment Allocation (blue), Material Output (orange dashed)
- Verification Signature flag shown on CBF header and activity rows
- Per-level **Export** button in the level navigation bar

> **Note on future nested CBFs:** Some PAS-X XMLs contain CBFs nested within other CBFs (all with their own activities). The current Level 2 view is designed to accommodate this — do not add a hardcoded Level 3, instead extend the recursive parser when needed.

### Excel Export (Pathway Table)
Generates a `.xlsx` file matching the standard test options format with 20 columns:

| Column | Description |
|--------|-------------|
| Relevant Basic Function | e.g. `BO1 > CBF1` |
| Entry Full Path | e.g. `BO1 > CBF1 > ACT10` |
| Entry Full Path Description | Full human-readable path |
| Activity Description | Description of the spec prop |
| Formula | Resolved formula text (FormulaSpecProp) |
| Formula Type | `text` / `numeric` |
| No of References | Count of formula references |
| CXDefinition | (populated if defined) |
| MeasuredValue Tolerance | `maxTolerance-X;minTolerance-Y` |
| Entry Generic Type | `Activity` / `Basic Function` / `Material` |
| Activity Type | `Attributive` / `MeasuredValue` / `Formula` / `EqmAllocation` / `MaterialOutput` |
| User Identification | |
| Verification Signature | `Yes` if required |
| PCS Element | |
| ActiveFlag | e.g. `BO1: NA > CBF1: NA > ACT10: NA` |
| Risk Assessment | `Low` (default) |
| Verification Type | `Static` (default) |
| Input Value | (blank — for test execution) |
| Expect Value | (blank — for test execution) |
| Pass/Fail | (blank — for test execution) |

Header rows include: GMBR ID, Description, Version, and fill-in fields for Manufacturing Order ID, Test Executors, Start Date.

Export respects the current **Show/Hide Activities** state — if activities are hidden, they are also hidden in the exported file.

### Visio / draw.io Export
- Downloads a `.drawio` XML file for the current level view
- Respects Show/Hide Activities state
- Open at **[app.diagrams.net](https://app.diagrams.net)** → File → Export As → VSDX to get a Visio file
- Shape colour coding matches the process map (dark navy for GMBR/Start/End, medium blue for BO/CBF, lighter blue for EqmAllocation, orange dashed for Material Output)

---

## File Structure

```
claude-projects/
├── PASX_ValidationTool.html   # The entire app — single self-contained file
└── README.md                  # This file
```

---

## How to Use

### Option A — Open directly in browser
Open `PASX_ValidationTool.html` in Chrome (or any modern browser).

### Option B — Run via local server
```bash
py -m http.server 3000
# then open http://localhost:3000/PASX_ValidationTool.html
```

### Uploading XML
1. Export your GMBR from PAS-X as XML
2. Drop the `.xml` file onto the upload zone, or click **Browse file**, or click **Paste XML** to paste content directly
3. The tool parses instantly and shows the process map

---

## Design System

Based on the **MBRfactory** design language (AstraZeneca MES CoE):

| Token | Value |
|-------|-------|
| Mulberry (primary) | `#830051` |
| Gold (accent) | `#F0AB00` |
| Navy | `#003865` |
| Background | `#F7F5F2` |
| Font | Helvetica Neue / Helvetica / Inter / Arial |

---

## Technical Notes

- **No build step** — pure HTML/CSS/JS, single file
- **SheetJS** loaded from CDN (`xlsx.full.min.js`) for Excel generation
- **DOMParser** used for XML parsing with `text/xml` mode
- PAS-X dotted Java class names (e.g. `com.werum...GenericMasterBatchRecordVO`) are matched using a `findEl(root, suffix)` helper that uses `getElementsByTagName('*')` and suffix-matches `tagName` — bypasses the CSS selector dot-as-class-selector limitation
- All map styles are injected inline with each render so the map is fully portable for export

---

## Roadmap / Known Considerations

- [ ] Support for nested CBFs (CBFs within CBFs) — parser foundation is in place, UI levels will need extending
- [ ] Support for multiple Basic Operations in Level 2 view (BO selector dropdown already present)
- [ ] Material Input display
- [ ] Direct VSDX generation (currently via draw.io as intermediary)
- [ ] PMBR (Parametrised MBR) support in addition to GMBR

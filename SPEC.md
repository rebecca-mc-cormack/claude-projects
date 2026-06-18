# EBR Validation Tool — SPEC.md

> **Project:** Accenture EBR Validation Tool  
> **Author:** Rebecca McCormack  
> **Source system:** PAS-X MES V3.3.2  
> **Last updated:** 2026-06-18  
> **Status:** Flow map implementation complete with graph-based rendering, parallel branches, and split/sync shapes
> **Purpose:** Developer brief for Claude Code. Defines all business rules, output formats, and logic required to build the tool. UX/visual design is handled separately in Figma.

---

## Tool summary

Takes a PAS-X MES Generic Master Batch Record (GMBR) XML export as input and automatically generates five outputs:

1. Process flow map (PNG)
2. MBR User Requirements Specification (.docx)
3. Pathways Excel sheet (.xlsx)
4. Review by Exception sheet (.xlsx)
5. Test scripts (.xlsx)

Replaces manual EBR review, document preparation, and formal URS authoring work prior to project close.

---

## UI structure

The tool has a tabbed interface. Three tabs are present at this stage — additional tabs (Review by Exception, Test Scripts) will be added in later iterations.

### Header behaviour

| State | Behaviour |
|-------|-----------|
| Before XML upload | Full header — large "EBR Validation Tool" title, upload prompt visible |
| After XML upload | Compact single-line bar — small title left, loaded filename pill right, no description text |

The PAS-X export label is not shown anywhere in the interface.

### Download button rules

- All download buttons are positioned **top right** of their tab, above the content
- Each button is **tab-specific** — only visible when its tab is active
- No persistent download buttons are shown at all times
- Label convention: "Download (.png)", "Download Excel (.xlsx)", "Download Word (.docx)"

### Tab layout

```
[ Process Flow Map ]  [ Review by Exception ]  [ MBR Requirement Spec ]
```

### Tab 1 — Process flow map

| Element | Position | Behaviour |
|---------|----------|-----------|
| Layer toggle | Top left | Switch between Layer 1 (overview) and Layer 2 (BO drilldown) |
| Download button | Top right | "Download (.png)" — downloads current layer view |
| Map area | Main area | Renders process flow map PNG |

### Tab 2 — Review by Exception

| Element | Position | Behaviour |
|---------|----------|-----------|
| Row count label | Top left | e.g. "42 pathways — RMCTEST" |
| Download button | Top right | "Download Excel (.xlsx)" |
| Table | Main area | Risk-assessed pathways table with colour-coded risk column and dropdown override |

### Cross-referencing interactions

| Interaction | Trigger | Result |
|---|---|---|
| Flow map → RbE | Click CBF ID (underlined, dotted) on flow map node | Switches to Review by Exception tab, highlights all rows for that CBF in purple, scrolls to first match |
| RbE → flow map | Click process map ref. link in column 1 of RbE | Switches to Process Flow Map tab, highlights that node with purple border |
| Flow map expand | Click CBF title text on flow map node | Expands activity list inline below the node |
| Flow map collapse | Click CBF title again | Collapses activity list (toggle) |

**Visual indicators:**
- Clickable CBF IDs on flow map: underlined with dotted style, purple colour
- Clickable process map refs in RbE: same dotted underline treatment
- Highlighted row in RbE: purple left border + light purple background `#F3EEF8`
- Highlighted node on flow map: purple border `#3D006B`, 2.5px, light purple background `#F3EEF8`
- Expanded activity list: shown below node title, each activity as a bullet with purple dot

| Element | Position | Behaviour |
|---------|----------|-----------|
| Draft label | Top left | e.g. "Draft v1.0 — PharmaCo Ltd" |
| Download button | Top right | "Download Word (.docx)" — in muted purple to indicate primary action |
| Legend | Below tab bar | Two items: amber = needs manual input after export; white = auto-populated from XML |
| Preview | Main area | White background document preview — matches the look of the exported Word file |
| Auto-populated fields | Inline in preview | White background, plain text — rendered directly from XML |
| Manual input fields | Inline in preview | Amber highlight `#FFF3CD` with amber underline `#F59E0B` and pencil icon — clearly distinguishable from auto fields |
| Section 3.1 | Within preview | Level 2 flow map rendered inline — auto-generated from XML, one per BasicOperation, brand colour coding |

**Manual input fields (amber highlighted):**
- Document ID, version, date
- Manufacturing sites table rows
- Roles and Responsibilities table rows
- Reference Documents table rows
- Version history rows beyond v1.0

---

## Input format

**File type:** XML export from PAS-X MES (`.xml`)  
**Root element:** `ExportImportObjectWrapperVO`  
**Key source element:** `GenericMasterBatchRecordVO`

### Key XML fields used across all outputs

| Field | XML path | Description |
|-------|----------|-------------|
| Batch ID | `GenericMasterBatchRecordVO.customId` | Unique batch record identifier |
| Description | `GenericMasterBatchRecordVO.description` | Human-readable batch name |
| Material name | `GenericMasterBatchRecordVO.materialName` | Target material |
| Version | `GenericMasterBatchRecordVO.versionId` | Record version number |
| Status | `GenericMasterBatchRecordVO.currentStatus` | Numeric status code |
| Step ID | `*.customId` | Unique ID per step (e.g. BO1, CBF17) |
| Step description | `*.description` | Human-readable step name |
| Step type | XML element name | e.g. BasicOperationVO, CommonBFVO |
| Activity ID | `specPropCollection.*.customId` | e.g. ACT10, ACT20 |
| Activity description | `specPropCollection.*.description` | e.g. "Record Waste" |
| Set value | `MeasuredValueSpecPropVO.setValue` | Target numeric value |
| Min tolerance | `MeasuredValueSpecPropVO.minTolerance` | Lower bound |
| Max tolerance | `MeasuredValueSpecPropVO.maxTolerance` | Upper bound |
| Unit | `MeasuredValueSpecPropVO.unit.customId` | Unit of measure (e.g. kg) |
| Formula text | `FormulaSpecPropVO.formulaText` | Calculated value expression |
| Criticality | `specPropCollection.*.criticality` | Numeric criticality code |
| Source step | `ProdStepLinkVO.sourceProdStep` | Reference to origin step |
| Target step | `ProdStepLinkVO.targetProdStep` | Reference to destination step |

### Step types

**Flow control**

| XML element | Role |
|-------------|------|
| `StartStepVO` | Flow start node |
| `EndStepVO` | Flow end node |
| `BasicOperationVO` | Top-level operation — contains all nested collections |
| `CommonBFVO` | Basic function step — primary container for specPropCollection activities |
| `SpecDecisionVO` | Decision/branch node — contains YES/NO SpecConditionVO outcomes |
| `MergeVO` | Merge node — rejoins branched paths |
| `SplittingVO` | Split node — divides into parallel branches |
| `SynchronisationVO` | Sync node — waits for parallel branches to complete |

**Material flow**

| XML element | Role |
|-------------|------|
| `TakeOutBFVO` | Material take-out step |
| `IdentityCheckBFVO` | Material identity verification step |
| `YieldDeterminationBFVO` | Yield calculation step |
| `BundleCreationBFVO` | Bundle/lot creation step |
| `StockCreationBFVO` | Stock creation step |

**Equipment**

| XML element | Role |
|-------------|------|
| `EqmAllocationBFVO` | Equipment allocation step |
| `EqmDeallocationBFVO` | Equipment deallocation step |
| `EqmIdentificationBFVO` | Equipment identification/scan step |

**Label & context**

| XML element | Role |
|-------------|------|
| `GenericLabelPrintBfVO` | Label print step |
| `SetCxBfVO` | Context variable setter step |

**specPropCollection activity types**

| XML element | Role |
|-------------|------|
| `MeasuredValueSpecPropVO` | Numeric measurement — setValue, minTolerance, maxTolerance, unit |
| `FormulaSpecPropVO` | Calculated value — formulaText, unit |
| `TextSpecPropVO` | Free-text entry activity |
| `DateSpecPropVO` | Date/time capture activity |
| `AttributiveSpecPropVO` | Pass/fail attributive result activity |
| `ListSpecPropVO` | Dropdown list selection — contains ListSpecPropElementVO options |

---

## Output 1 — Process flow map

**Current implementation:** Interactive HTML browser tool (single-file PASX_ValidationTool.html)  
**Future:** PNG image file via Python `graphviz`  
**Orientation:** Top to bottom

### Rendering approach

The tool now uses **graph-based traversal** instead of XML document order:

1. **Build directed graph** from `ProdStepLinkCollection` — creates edges from source → target references
2. **Detect parallel branches** — identifies nodes with multiple outgoing edges (splits)
3. **Detect convergence points** — identifies nodes where all branches reconverge (syncs/merges)
4. **Traverse and render** — DFS walk from start node, rendering branches side-by-side when detected
5. **Stop at convergence** — each branch halts at the sync point without continuing past it
6. **Resume main flow** — after all branches render, continues from sync point downward

This ensures correct visual representation of process flow logic, not accidental XML ordering.

### Two-layer structure

The tool generates **two levels** of flow map:

**Layer 1 — Overview map**  
Shows the top-level process: `StartStepVO → BasicOperationVO (one or more) → EndStepVO`  
Connections sourced from the top-level `prodStepLinkCollection` on `GenericMasterBatchRecordVO`.

**Level 2 — Drilldown map (one per BasicOperation)**  
For each `BasicOperationVO`, generates a separate map showing its internal sub-steps:  
`StartStepVO → sub-steps (CommonBFVO, EqmAllocationBFVO, SpecDecisionVO, etc.) → EndStepVO`  
Connections sourced from `prodStepLinkCollection` nested inside each `BasicOperationVO`.

Note: "Layer" terminology replaced with **"Level"** throughout the tool.

### Node appearance (implemented)

| Element | Design |
|---------|--------|
| Canvas background | Light gray `#F5F5F5` |
| Step node shape | Rounded rectangle — white fill `#FFFFFF`, coloured border 1.5px per category |
| Node text — ID | Bold 12pt — `customId` (e.g. `CBF17`), purple `#3D006B`, dotted underline, clickable |
| Node text — description | Regular 12pt, dark `#2A1A3E` |
| Node text — type label | Regular 11pt, muted gray `#7A7280`, right-aligned |
| Node layout | Flexbox row: ID (fixed) \| description (flex) \| type (fixed) |
| Node responsiveness | `width: 100%; max-width: 480px` — shrinks in narrow columns, expands in full width |
| Start node | Filled pill/circle — dark gray `#818180`, white text |
| End node | Filled pill/circle — dark gray `#818180`, white text |
| Merge node (`MergeVO`) | Diamond shape — white fill, `#622A8F` border 2px, label below |
| Sync node (`SynchronisationVO`) | V-shape (SVG polyline) — `#622A8F` stroke 2.5px, converges to center point, label below |
| Split node (`SplittingVO`) | Horizontal bar (SVG line) — `#622A8F` stroke 3px, full width of branch group, label above |
| Parallel branches | Flexbox columns: `display: flex; gap: 24px; justify-content: center` — each column flex:1 |
| Arrows | Purple `#A100FF`, 2px stroke with triangular arrowhead, 18px height in flow, 1.5px in branches |
| Minimum font size | 12pt throughout — designed for accessibility |

### Colour coding by step category (white fill, coloured border)

All nodes use white fill with dark text `#2A1A3E`. Colour is conveyed through border only — never background fill. This ensures accessibility and readability.

| Category | Border colour | Hex |
|----------|---------------|-----|
| Flow control (BO, CBF, SpecDecision) | Darkest purple | `#3D006B` |
| Material flow (TakeOut, IdentityCheck, Yield etc.) | Blue | `#185FA5` |
| Equipment (EqmAllocation, EqmDealloc, EqmIdent) | Dark gray | `#818180` |
| Label / context (LabelPrint, SetCx) | Mid gray | `#888780` |
| Merge / Sync / Split | Muted dark purple | `#622A8F` |
| Start / End | Filled circle, dark gray | `#818180` |

### Material flow nodes — Take-out detail

`TakeOutBFVO` nodes display an additional line below the description:
- Source: `materialName` field from XML
- Displayed as: small italic text in blue `#185FA5` below the node title
- Example: `materialName: Tablet Core API`
- `MaterialOutputCollection` is **not shown** on the process map

### Merges, syncs and splits — shape rules

| Step type | Shape on map | In RbE? |
|-----------|--------------|---------|
| `MergeVO` | Diamond (white fill, `#622A8F` border) | No |
| `SynchronisationVO` | V-shape (two lines to a point) | No |
| `SplittingVO` | Horizontal bar | No |

These three types appear on the process map with their distinct shapes but are excluded from the Review by Exception sheet.

### Activity expand/collapse behaviour

- Click CBF **description text** → expands/collapses activity list inline below the node (toggle)
- Click CBF **ID** → jumps to the Review by Exception tab (separate, independent action)
- Activity list layout: description left-aligned, activity type right-aligned, always in line regardless of description length
- Font size minimum 12pt throughout for accessibility

### Controls — top bar layout

```
[ Level 1 ] [ Level 2 ]  [ Operations ]  [ Basic functions ]          [ Download (.png) ]
←  left-aligned toggles                                                right-aligned  →
```

### Connections

- Sourced from `ProdStepLinkVO` elements (`sourceProdStep` → `targetProdStep`)
- Rendered as directed arrows in core purple `#A100FF` with filled arrowheads
- No label text on any connection
- One arrow per `ProdStepLinkVO` entry

### Output files

| File | Contents |
|------|----------|
| `process_flow_overview.png` | Level 1 — full record overview |
| `process_flow_<customId>.png` | Level 2 — one file per BasicOperation |

---

## Output 2 — MBR User Requirements Specification (.docx)

**Format:** Word document (.docx)  
**Library:** Python `python-docx`  
**Template:** Fixed structure matching formal GxP validation document standard

### Document structure

| Section | No. | Content source | Editable? |
|---------|-----|----------------|-----------|
| Cover / header block | — | Manual (Doc ID, version, date, page) | Manual |
| Title block | — | Auto from XML (GMBR description, client name, production unit) | Read-only |
| Table of contents | — | Fixed structure | Read-only |
| Version history | — | Pre-filled with v1.0 row | Manual |
| Introduction | 1 | Fixed boilerplate + client name + production unit from config | Read-only |
| Scope | 1.1 | Fixed boilerplate + GMBR ID + GMBR description from XML + production unit | Partial |
| Manufacturing sites table | 1.1 | Blank rows — filled manually | Manual |
| Limitations | 2 | Fixed boilerplate — never changes | Read-only |
| Process Overview | 3.1 | Layer 2 flow map PNGs — one per BasicOperation, one page each | Auto-generated |
| Additional Requirements | 3.2 | Fixed boilerplate + production unit from config | Read-only |
| Roles and Responsibilities | 4 | Blank table — filled manually | Manual |
| Definitions & Acronyms | 5 | Fixed table (18 standard terms) | Read-only |
| Reference Documents | 6 | Blank table — variable rows, site-specific | Manual |

### Auto-populated fields (from XML / config)

| Field | Source |
|-------|--------|
| Client name | Config variable (`CLIENT_NAME`) — set once per client rollout |
| Production unit | Config variable (`PRODUCTION_UNIT`) — e.g. Tableting |
| GMBR ID | `GenericMasterBatchRecordVO.customId` |
| GMBR description | `GenericMasterBatchRecordVO.description` |
| Flow map images | Generated PNGs from Output 1 (Layer 2 drilldown, one per BasicOperation) |

### Manual fill fields (completed in Word after export)

- Document ID, version, date, page number
- Manufacturing sites table (one row per site)
- Roles and Responsibilities table (variable rows)
- Reference Documents table (variable rows, site-specific)
- Version history rows beyond v1.0

### Process flow map insertion

- Uses Layer 2 drilldown PNGs generated by Output 1
- One PNG per `BasicOperationVO`, inserted on its own page in Section 3.1
- Caption below each image: `{customId} — {description}`
- Placeholder frame shown if PNG not yet generated

### Client / site configurability

- `CLIENT_NAME` and `PRODUCTION_UNIT` are set once in `config.py` when deploying to a client
- Different clients may have additional site-specific sections — these are added via config flags
- Standard boilerplate (Limitations, Definitions, Additional Requirements) remains constant across all clients

### Output file

| File | Naming convention |
|------|-------------------|
| `MBR_URS_<CLIENT>_<PRODUCTION_UNIT>.docx` | e.g. `MBR_URS_PharmaCo_Tableting.docx` |

### Acceptance criteria

- Given `Test_XML_1.xml`: document must contain correct GMBR ID and description in Scope table
- Section 3.1 must contain one flow map image per `BasicOperationVO` found in the XML
- Each flow map image must be on its own page with correct caption
- All fixed boilerplate sections must render without placeholder text remaining
- Manual fill fields must render as clearly blank/editable cells
- File saved as `.docx` to `/output/`

---

## XML pathway rendering logic

### How connections are read from XML

The tool builds the process flow map by reading `ProdStepLinkVO` elements within `prodStepLinkCollection`. Each link has:
- `sourceProdStep` — `reference` attribute points to the `id` of the source step
- `targetProdStep` — `reference` attribute points to the `id` of the target step

The tool builds a directed graph from all links, then renders it top-to-bottom.

### Level 1 — GMBR overview rendering

Read `prodStepLinkCollection` directly under `GenericMasterBatchRecordVO`.

**From Test_XML_1.xml (RMCTEST):**
```
Start → BO1 (Weigh & Dispense Test) → BO2 (Basic Operation Test) → End
```

Rule: render `StartStepVO → BasicOperationVO nodes → EndStepVO` in link order.

### Level 2 — Per-BO drilldown rendering

Read `prodStepLinkCollection` nested inside each `BasicOperationVO`. Build a directed graph and render top-to-bottom.

**BO1 — Weigh & Dispense Test (simple linear):**
```
Start → 1TO10 (Take-out) → End
```

**BO2 — Basic Operation Test (split/sync/parallel):**
```
Start
  ↓
EQAL1 — Room Allocation        [EqmAllocation]
  ↓
CBF1 — Clearance               [CommonBF]
  ↓
1CBF70 — Setup                 [CommonBF]
  ↓
Split1 ━━━━━━━━━━━━━━━━━━━━━━━ [SplittingVO — horizontal bar]
  ↓              ↓                    ↓
CBF17          1CBF80             1CBF90
Waste          Tare Containers    Consume Granules
[CommonBF]     [CommonBF]         [CommonBF]
  ↓              ↓                    ↓
         Sync1 ◁━━━━━━━━━━━━━━━━━━━━  [SynchronisationVO — V-shape]
  ↓
CBF4 — Other                   [CommonBF]
  ↓
1CBF250 — Stock Creation       [CommonBF]
  ↓
1CBF260 — Reconciliation       [CommonBF]
  ↓
CBF50 — Alarms                 [CommonBF]
  ↓
End
```

### Rendering rules derived from XML structure

**Rule 1 — Detect parallel branches (SplittingVO)**
When a `SplittingVO` node has multiple outgoing links (multiple `targetProdStep` references), render all targets side by side as parallel branches. Draw horizontal bar above them.

**Rule 2 — Detect merge point (SynchronisationVO)**
When a `SynchronisationVO` node has multiple incoming links (multiple sources point to it), it is the sync point. Draw the V-shape converging from all parallel branches into the sync node.

**Rule 3 — Detect decision branches (SpecDecisionVO)**
A `SpecDecisionVO` has multiple outgoing links labelled with `SpecConditionVO` children (YES/NO). Render as a diamond with YES/NO branch labels on the arrows.

**Rule 4 — Detect loops (MergeVO)**
A `MergeVO` with both a forward and a back-edge (one source is downstream) indicates a loop. Render as a diamond. The back-edge arrow loops back up the left side of the map.

**Rule 5 — Linear steps**
Any node with exactly one incoming and one outgoing link renders as a simple step in the vertical chain.

**Rule 6 — TakeOutBFVO**
Render as a standard node with blue border `#185FA5`. Add a second line below the description showing `materialName` from the XML in small italic blue text.

**Rule 7 — Excluded from map**
`materialOutputCollection` elements are not rendered.

**Rule 8 — Excluded from RbE**
`SplittingVO`, `SynchronisationVO`, `MergeVO` appear on the map but are not included as rows in the Review by Exception sheet.

### Graph traversal algorithm (for Claude Code)

```python
# Pseudocode for building the flow map
def build_graph(prod_step_link_collection):
    graph = {}  # node_id -> [target_ids]
    reverse = {}  # node_id -> [source_ids]
    for link in prod_step_link_collection:
        src = link.sourceProdStep.reference
        tgt = link.targetProdStep.reference
        graph.setdefault(src, []).append(tgt)
        reverse.setdefault(tgt, []).append(src)
    return graph, reverse

def render_level(graph, reverse, id_map):
    # Start from StartStepVO
    # Walk graph top-to-bottom
    # When a node has multiple outgoing edges: parallel branch group
    # When a SynchronisationVO has multiple incoming: sync point, close branch group
    # When a SpecDecisionVO has multiple outgoing: decision diamond with YES/NO labels
    # When a MergeVO has a back-edge: loop arrow on left side
    pass
```

**Format:** Excel file (.xlsx)  
**Library:** Python `openpyxl`  
**Tab name:** Review by Exception  
**Purpose:** Assigns a risk level to every pathway/activity in the GMBR, enabling the validation team to determine what level of testing is required per pathway.

### Column specification

| # | Column | Source | Notes |
|---|--------|--------|-------|
| 1 | Process map ref. step | XML `*.customId` | CBF ID — links row to flow map tab e.g. CBF17 |
| 2 | GMBR path reference | XML | Path to CBF level only — e.g. `BO1 > CBF17` |
| 3 | Description | XML `CommonBFVO.description` | CBF-level description |
| 4 | Process step type | Dropdown | CPP/CQA or Critical Step / Functionality or Procedural Step |
| 5 | Confirmation level required | Dropdown | OK / OK with 2nd person verification / OK with block signature / N/A |
| 6 | Can data be QA'd at time of order? | Dropdown | 8 options — see below |
| 7 | Required at batch record review? | Auto from column 6 logic | Yes / No — `=IF(SUM(COUNTIF(col6,{"*Yes*","*N/A*"})),"No","Yes")` |
| 8 | Comment | Manual — blank on export | Completed by reviewer after download |

### Column 4 — Process step type (default logic)

Auto-populated on generation based on the activity types present within the CBF. Human can override via dropdown. Auto-suggested values shown with a purple border indicator.

| Activity type present in CBF | Default |
|---|---|
| `MeasuredValueSpecPropVO` | CPP/CQA or Critical Step |
| `FormulaSpecPropVO` | CPP/CQA or Critical Step |
| `AttributiveSpecPropVO` | CPP/CQA or Critical Step |
| `EqmAllocationBFVO` / `EqmIdentificationBFVO` | Functionality or Procedural Step |
| `TextSpecPropVO` / `DateSpecPropVO` / `ListSpecPropVO` | Functionality or Procedural Step |
| `SpecDecisionVO` | Functionality or Procedural Step |

### Column 5 — Confirmation level required (default logic)

Auto-populated based on activity type severity from the change classification. Human can override via dropdown.

| Activity type | Default |
|---|---|
| `MeasuredValueSpecPropVO` | OK with 2nd person verification |
| `FormulaSpecPropVO` (final quality decision) | OK with block signature |
| `FormulaSpecPropVO` (other) | OK with 2nd person verification |
| `AttributiveSpecPropVO` | OK |
| `EqmAllocationBFVO` | OK with 2nd person verification |
| `TextSpecPropVO` / `DateSpecPropVO` / `ListSpecPropVO` | OK |
| `SpecDecisionVO` | OK |

**Visual indicator:** Auto-suggested defaults shown with a purple border on the dropdown. Border is removed when the human overrides the value.

1. Yes — entry into EBR or equipment verified by second operator
2. Yes — validated calculation/interface transfer
3. Yes — tolerance set/set value check/attributive step
4. Yes — presence of physical sample will be checked during the order
5. No — system cannot verify different individuals performing the task
6. No — presence of physical sample will not be checked during the order
7. No — data not available until after production
8. N/A — not disposition relevant (procedural step or functionality only)

### Column 7 — Required at batch record review? (auto logic)

Derived automatically from column 6. Logic: if column 6 starts with "Yes" or "N/A", result is **No**. If column 6 starts with "No", result is **Yes**.

Excel formula equivalent: `=IF(SUM(COUNTIF(F5,{"*Yes*","*N/A*"})),"No","Yes")`

Colour coding: Yes = red `#FFC7CE`, No = green `#C6EFCE`

### Risk assignment logic

Risk is determined using a two-stage heat map from the Change Classification document (PAS-X MES, Accenture).

**Stage 1 — Severity × Likelihood → Intermediate risk**

| Impact \ Likelihood | 1 (VL) | 2 (L) | 3 (M) | 4 (H) | 5 (VH) |
|---|---|---|---|---|---|
| 5 (VH) | Medium | Medium | Major | Critical | Critical |
| 4 (H) | Low | Medium | Medium | Major | Critical |
| 3 (M) | Low | Medium | Medium | Medium | Major |
| 2 (L) | Low | Low | Medium | Medium | Medium |
| 1 (VL) | Low | Low | Low | Low | Medium |

**Stage 2 — Intermediate risk × Detection → Final risk**

| Risk level \ Detection | 1 (Almost certain) | 2 (High) | 3 (Moderate) | 4 (Low likelihood) | 5 (Absolutely uncertain) |
|---|---|---|---|---|---|
| Critical | Medium | Major | Critical | Critical | Critical |
| Major | Low | Medium | Major | Critical | Critical |
| Medium | Low | Low | Medium | Major | Major |
| Low | Low | Low | Low | Medium | Medium |

### Activity type → risk mapping

| Activity type | Risk | Change classification | Verification type |
|---|---|---|---|
| `AttributiveSpecPropVO` | LOW | MINOR | Static Review in Design Review |
| `DateSpecPropVO` | LOW | MINOR | Static Review in Design Review |
| `TextSpecPropVO` | LOW | MINOR | Static Review in Design Review |
| `ListSpecPropVO` (no set values) | LOW | MINOR | Static Review in Design Review |
| `ListSpecPropVO` (with set values) | LOW | MINOR | Static Review in Design Review |
| `FormulaSpecPropVO` (display only) | LOW | MINOR | Static Review in Design Review |
| `FormulaSpecPropVO` (format/concatenation) | MEDIUM | MAJOR | Simulation in OQ |
| `FormulaSpecPropVO` (input to quality calc) | MEDIUM | MAJOR | Simulation in OQ |
| `FormulaSpecPropVO` (final quality decision) | HIGH | MAJOR | Dynamically Tested in OQ |
| `MeasuredValueSpecPropVO` (independent step) | LOW | MINOR | Static Review in Design Review |
| `MeasuredValueSpecPropVO` (in calculation) | MEDIUM | MAJOR | Simulation in OQ |
| `SpecDecisionVO` (formula driven) | MEDIUM | MAJOR | Simulation in OQ |
| `SpecDecisionVO` (user selection) | LOW | MINOR | Static Review in Design Review |
| `EqmAllocationBFVO` / `EqmIdentificationBFVO` | HIGH | MAJOR | Dynamic Testing in OQ |
| `SplittingVO` / `MergeVO` / `SynchronisationVO` | LOW | MINOR | Static Review in Design Review |

### Risk override dropdown

The Risk column auto-populates based on the logic above. The user can override via a dropdown per row with options: LOW / MEDIUM / HIGH. The original auto-assigned value is preserved as a note/tooltip so reviewers can see what was suggested.

### Risk colour coding

| Risk level | Cell fill |
|---|---|
| LOW | Green `#C6EFCE` |
| MEDIUM | Amber `#FFEB9C` |
| HIGH | Red `#FFC7CE` |

### Acceptance criteria

- Every activity in the XML must appear as a row with its full pathway
- Risk is auto-assigned on generation — no manual input required before export
- Risk dropdown allows override to LOW / MEDIUM / HIGH
- Colour coding updates dynamically with the dropdown selection
- Ver. type updates automatically when risk is overridden
- File saved as `review_by_exception.xlsx` to `/output/`

---

## Output 4 — Review by Exception sheet *(rules TBD)*

*To be defined in next session.*

---

## Output 5 — Test scripts *(rules TBD)*

*To be defined in next session.*

---

## Tech stack

| Component | Choice |
|-----------|--------|
| Language | Python 3 |
| XML parsing | `xml.etree.ElementTree` |
| Excel generation | `openpyxl` |
| Flow map generation | `graphviz` (Python bindings) |
| Word doc generation | `python-docx` |
| Entry point | `main.py` |

## Folder structure

```
ebr-validation-tool/
├── input/
│   └── sample.xml
├── output/
│   ├── process_flow_overview.png
│   ├── process_flow_BO1.png
│   ├── pathways.xlsx
│   ├── review_by_exception.xlsx
│   ├── test_scripts.xlsx
│   └── MBR_URS_PharmaCo_Tableting.docx
├── main.py
├── config.py
├── parsers/
│   └── xml_parser.py
├── generators/
│   ├── flow_map.py
│   ├── pathways_sheet.py
│   ├── rbe_sheet.py
│   ├── test_scripts.py
│   └── urs_document.py
└── SPEC.md
```

---

## Build order

1. `xml_parser.py` — parse XML, extract all steps, links, activities, materials
2. `flow_map.py` — generate overview PNG + one Layer 2 drilldown PNG per BasicOperation
3. `pathways_sheet.py` — generate pathways Excel *(spec TBD)*
4. `rbe_sheet.py` — generate Review by Exception Excel *(spec TBD)*
5. `test_scripts.py` — generate test scripts Excel *(spec TBD)*
6. `urs_document.py` — generate MBR URS Word doc, inserting Layer 2 PNGs from step 2

---

## Acceptance criteria

### Output 1 — Process flow map
- Given `testxml.xml`: overview map must show `Start → BO1 → End`
- Drilldown for `BO1` must show all internal `CommonBFVO` and `EqmAllocationBFVO` nodes
- Each node must display `customId` on line 1 and `description` on line 2
- Arrows connect steps with no labels
- Each step type renders in its assigned colour
- Output saved as PNG to `/output/`

### Output 2 — MBR URS
- Given `Test_XML_1.xml`: GMBR ID and description auto-populated correctly in Scope table
- Section 3.1 contains one flow map image per `BasicOperationVO`
- Each image on its own page with caption `{customId} — {description}`
- All boilerplate sections render with no remaining placeholder text
- Manual fill tables render as blank editable cells
- File named `MBR_URS_PharmaCo_Tableting.docx` and saved to `/output/`

---

*Acceptance criteria for Outputs 3–5 to be added as rules are defined.*

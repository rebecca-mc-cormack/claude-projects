# EBR Validation Tool — Master Reference

> **Project:** Accenture EBR Validation Tool
> **Source system:** PAS-X MES V3.3.2
> **Last updated:** 2026-06-18

---

*Sections 1–18 to be populated. Section 19 below records design decisions made during build.*

---

## 19. Design Decision Log

---

### DDL-001 | Graphviz chosen for process flow map generation | 2026-06-18

**Decision:** Use the Python `graphviz` library (wrapping the Graphviz `dot` engine) to generate process flow map PNG outputs.

**Alternatives considered:**
- `matplotlib` with manual node/edge drawing
- `mermaid` (JS-based diagram renderer)
- `drawio` file generation
- Pure SVG construction in Python

**Rationale:** Graphviz handles automatic layout of directed acyclic graphs natively, including parallel branch positioning and ranking — which would require significant manual effort in alternatives. The Python `graphviz` package provides clean programmatic access. PNGs are the required output format and `dot` renders them reliably. The tool runs fully offline with no browser dependency, ruling out Mermaid. Matplotlib lacks native graph layout and would require a separate layout library (e.g. networkx). DrawIO files are not easily embeddable in downstream Word documents.

**Impact:** Requires Graphviz system binary installed on the user's machine alongside the Python package. Windows PATH workaround added to `main.py` to handle cases where the installer does not update the session PATH. All flow map logic lives in `generators/flow_map.py`.

---

### DDL-002 | Top-to-bottom flow map orientation | 2026-06-18

**Decision:** All process flow maps are rendered top-to-bottom (`rankdir='TB'`) rather than left-to-right.

**Alternatives considered:**
- Left-to-right (`rankdir='LR'`) — the Graphviz default
- Bottom-to-top (`rankdir='BT'`)

**Rationale:** Pharmaceutical process flows are conventionally read top-to-bottom in GxP documentation, matching how batch records are structured and how operators read SOPs. Top-to-bottom orientation also fits better within the portrait page layout of Word documents, where the flow map PNGs are embedded in the URS. Left-to-right would produce very wide images that scale poorly when inserted into A4 or Letter pages.

**Impact:** `rankdir='TB'` set in `_build_graph()` in `flow_map.py`. Affects both Level 1 (overview) and Level 2 (drilldown) maps. Portrait-orientation PNG output fits directly into Word Section 3.1 without rotation.

---

### DDL-003 | Two-level flow map structure (overview vs drilldown) | 2026-06-18

**Decision:** Generate two levels of flow map: a Level 1 overview showing top-level `BasicOperationVO` steps only, and a Level 2 drilldown map per `BasicOperationVO` showing its internal sub-steps.

**Alternatives considered:**
- Single flat map showing all steps at every nesting level simultaneously
- Three levels (adding a CBF-level drilldown)

**Rationale:** PAS-X GMBRs nest steps across multiple levels; a single flat map of all steps would be unreadably large for any non-trivial batch record. Two levels matches the mental model already used by validation engineers: operators think in terms of BasicOperations (major phases) then drill into their constituent functions. A third level (CBF internals) would be activities/data entry — better represented in tabular form (Review by Exception) than as flow nodes. The two-level structure also maps cleanly to the URS: Level 1 belongs in the executive summary, Level 2 per-BO maps belong in Section 3.1.

**Impact:** `generate_flow_maps()` produces one `process_flow_overview.png` plus one `process_flow_<customId>.png` per BasicOperation. Level 2 PNGs are the images embedded into the URS Word document. Layer toggle UI (now labelled "Level") in the frontend reflects this structure.

---

### DDL-004 | Colour coding scheme for node types | 2026-06-18

**Decision:** Each step category is assigned a distinct border colour; non-BO nodes use white fill with the category colour applied to the border only. BasicOperationVO is the exception — it uses a filled dark purple background to make it visually dominant at Level 1.

**Alternatives considered:**
- All nodes using filled background colours (high contrast but harder to read text on coloured backgrounds)
- Single-colour scheme with shape differentiation only
- Greyscale only

**Rationale:** White fill with coloured borders keeps node text readable at all font sizes, which matters for GxP documentation reviewed on screen and in print. Using fill colour only for BasicOperationVO creates a clear visual hierarchy — BO nodes are "container" nodes in the record structure and should look structurally distinct from sub-steps. The colour groupings reflect functional categories already meaningful to validation engineers: flow control (purple), material flow (pink), equipment (grey), label/context (blue), structural nodes (muted purple). Accessibility-informed: colour alone is not the only differentiator — shapes also vary for Merge/Split/Sync nodes.

**Impact:** `STEP_COLORS` dict in `flow_map.py` defines all assignments. `_LIGHT_FILLS` set controls which colours get a darkened border fallback for contrast. Font colour on BasicOperationVO nodes is white; all others are `#000000`. Any new step type added in future must be added to `STEP_COLORS`.

---

### DDL-005 | python-docx chosen for Word document generation | 2026-06-18

**Decision:** Use the `python-docx` library to generate the MBR User Requirements Specification as a `.docx` file.

**Alternatives considered:**
- Generating an HTML file and expecting manual conversion to Word
- Generating a PDF directly (e.g. via `reportlab` or `weasyprint`)
- Using a DOCX template file with placeholder substitution (e.g. `docxtpl`)
- Building a custom XML `.docx` writer

**Rationale:** The output must be a `.docx` file that validation engineers can open, edit, and complete manually after export — a PDF is not editable and a HTML file requires additional conversion steps that would break formatting. `python-docx` provides programmatic control over tables, headings, paragraph styles, and image insertion, all of which are required for the URS structure. A template-based approach (docxtpl) was considered but adds a separate template artefact that must be version-controlled and kept in sync with the spec; `python-docx` keeps all document structure in code. GxP document requirements (fixed structure, controlled boilerplate) suit a code-generated approach over a fill-in template.

**Impact:** All Word output logic lives in `generators/urs_document.py`. The document structure (headings, tables, images) is defined programmatically. Flow map PNGs from Output 1 are inserted directly via `python-docx` image insertion into Section 3.1.

---

### DDL-006 | Amber highlight approach for manual fields in the URS preview | 2026-06-18

**Decision:** Fields requiring manual completion after export are shown with an amber background (`#FFF3CD`) and amber underline (`#F59E0B`) in the URS preview tab of the UI, accompanied by a pencil icon. Auto-populated fields are plain white with no highlight.

**Alternatives considered:**
- Grey-out / disabled styling for manual fields (inverse of the chosen approach)
- Red or blue highlight colours
- Placeholder text only (no colour coding)
- A separate "manual fields" list panel outside the document preview

**Rationale:** Amber is the established convention for "attention required" in document review workflows and is distinct from both error-state red and informational blue. Highlighting the manual fields (rather than the auto fields) draws the reviewer's eye to what still needs doing post-export, which is the action-oriented view needed at handover. The inline approach within the document preview means the reviewer can see exactly where each manual field appears in context, rather than navigating a separate list. The legend (amber = needs manual input; white = auto-populated) makes the system self-documenting for new users. The amber palette also aligns with Accenture brand-adjacent warm tones without using the primary Accenture purple, avoiding confusion between brand colour and status colour.

**Impact:** Amber highlight and pencil icon applied to: Document ID/version/date, manufacturing sites table rows, Roles & Responsibilities table rows, Reference Documents table rows, and version history rows beyond v1.0. Defined in the Figma spec and reflected in `urs_document.py` output styling.

---

### DDL-007 | File-in / file-out architecture (no live API connection) | 2026-06-18

**Decision:** The tool operates as a pure file-in / file-out process: takes a single XML file as input, writes output files to an `/output/` directory, with no live connection to PAS-X, no database, and no network calls.

**Alternatives considered:**
- Direct API integration with PAS-X MES to pull GMBR data live
- Web service / REST API wrapper around the generation logic
- Database-backed approach storing parsed record data

**Rationale:** PAS-X MES environments in pharmaceutical manufacturing are tightly controlled, validated systems. Any live API integration would require formal change control, IT security review, and potentially its own validation lifecycle — a disproportionate overhead for a tooling project. The XML export is a standard, supported PAS-X output that validation teams already produce as part of their normal workflow. A file-in / file-out architecture keeps the tool entirely standalone: no credentials, no network access, no infrastructure dependencies, no GxP impact on the source system. This also makes the tool portable across clients without any environment-specific configuration beyond `config.py`.

**Impact:** Entry point is `main.py` accepting a file path argument. All outputs written to `/output/`. No authentication, session management, or network code anywhere in the tool. `config.py` holds the only client-specific state.

---

### DDL-008 | Review by Exception column logic and default assignment rules | 2026-06-18

**Decision:** Columns 4 (Process step type) and 5 (Confirmation level required) in the Review by Exception sheet are auto-populated based on the activity types present within each CBF, using a rule table derived from the Accenture Change Classification document for PAS-X MES.

**Alternatives considered:**
- Leaving all dropdown columns blank and requiring manual completion
- Assigning a single default value to all rows regardless of activity type
- Using the XML `criticality` field as the sole basis for assignment

**Rationale:** The primary value of the Review by Exception sheet is to accelerate the validation team's review — blank dropdowns would negate this. The activity-type-based rules reflect the established Accenture change classification methodology for PAS-X validation projects, which already exists as a documented standard. Using `criticality` from the XML alone was considered insufficient because criticality is a PAS-X field that may not be consistently populated across client records, whereas activity type is always determinable from the XML element name. Auto-defaults allow the reviewer to focus on exceptions (steps where the default is wrong) rather than populating every row from scratch.

**Impact:** Column 4 defaults: `MeasuredValueSpecPropVO`, `FormulaSpecPropVO`, `AttributiveSpecPropVO` → "CPP/CQA or Critical Step"; all others → "Functionality or Procedural Step". Column 5 defaults: tiered by activity type severity per the change classification table. Auto-suggested defaults are visually indicated with a purple border on the dropdown cell; border is removed when the user overrides. Column 7 (Required at batch record review?) is fully derived from column 6 via Excel formula and requires no user input.

---

### DDL-009 | Auto-default dropdowns rather than leave blank on export | 2026-06-18

**Decision:** All dropdown columns in the Review by Exception sheet export with a pre-populated default value rather than a blank/empty cell.

**Alternatives considered:**
- Export with blank dropdowns and rely on the reviewer to populate all values
- Export with a "TBC" or "Select..." placeholder text that is not a valid option
- Provide defaults only for high-risk rows and leave low-risk rows blank

**Rationale:** A blank dropdown requires the reviewer to actively engage with every single row, even those where the auto-assigned value is clearly correct — this defeats the "review by exception" principle. The tool's purpose is to reduce manual effort; pre-populated defaults mean the reviewer only needs to act on rows they disagree with. Providing defaults consistently across all rows (not just high-risk) maintains the integrity of the sheet — a row left blank could be misread as "not yet reviewed" rather than "low risk / no action needed". "Review by exception" as a validation strategy requires that every row has a documented position, even if that position is the default.

**Impact:** Every row in columns 4, 5, and 6 is populated at generation time. Column 7 is formula-driven. The Comment column (column 8) remains blank — this is intentional as it is the reviewer's own notes field. Purple border indicator distinguishes auto-assigned values from human overrides.

---

### DDL-010 | config.py approach for client-specific variables | 2026-06-18

**Decision:** Client-specific values (`CLIENT_NAME`, `PRODUCTION_UNIT`) are stored in a single `config.py` file at the project root, set once when the tool is deployed to a client engagement.

**Alternatives considered:**
- Command-line arguments for all client variables
- Environment variables
- A `.env` file
- A JSON or YAML config file
- Hard-coding values per client in a separate branch

**Rationale:** The tool is deployed per-client by an Accenture team member who sets it up once and hands it over. A Python file is simpler and more readable than JSON/YAML for a two-variable config, requires no additional parsing library, and is visible and editable without any tooling. Command-line arguments were considered but would require the end user (a validation engineer, not a developer) to pass flags every time they run the tool — an unnecessary friction point. Environment variables and `.env` files add complexity without benefit for a config that changes only at project handover. A branch-per-client approach would fragment version history. `config.py` is imported directly into generators, making values available everywhere without a global state pattern.

**Impact:** `config.py` currently contains `CLIENT_NAME = "PharmaCo"` and `PRODUCTION_UNIT = "Tableting"`. These values propagate into the URS document title, scope section, filename convention (`MBR_URS_<CLIENT>_<PRODUCTION_UNIT>.docx`), and boilerplate text throughout the Word output. When deploying to a new client, only `config.py` needs to change.

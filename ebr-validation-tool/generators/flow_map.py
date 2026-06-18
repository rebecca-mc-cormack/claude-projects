from __future__ import annotations
import html
import os
import textwrap

from graphviz import Digraph

from parsers.xml_parser import GmbrRecord, Step


STEP_COLORS: dict[str, str] = {
    'StartStepVO':           '#818180',
    'EndStepVO':             '#818180',
    'BasicOperationVO':      '#3D006B',
    'CommonBFVO':            '#3D006B',
    'SpecDecisionVO':        '#3D006B',
    'MergeVO':               '#622A8F',
    'SplittingVO':           '#622A8F',
    'SynchronisationVO':     '#622A8F',
    'TakeOutBFVO':           '#185FA5',
    'IdentityCheckBFVO':     '#185FA5',
    'YieldDeterminationBFVO':'#185FA5',
    'BundleCreationBFVO':    '#185FA5',
    'StockCreationBFVO':     '#185FA5',
    'EqmAllocationBFVO':     '#818180',
    'EqmDeallocationBFVO':   '#818180',
    'EqmIdentificationBFVO': '#818180',
    'GenericLabelPrintBfVO': '#888780',
    'SetCxBfVO':             '#888780',
}

_START_END = {'StartStepVO', 'EndStepVO'}
_SPECIAL_SHAPES = {'MergeVO', 'SplittingVO', 'SynchronisationVO', 'SpecDecisionVO'}
_EDGE_COLOR = '#A100FF'
_BG_COLOR = '#F5F5F5'
_NODE_FILL = '#FFFFFF'
_NODE_TEXT_COLOR = '#2A1A3E'
_WRAP_WIDTH = 22


def _node_id(custom_id: str) -> str:
    return ''.join(c if c.isalnum() else '_' for c in custom_id)


def _esc(text: str) -> str:
    return html.escape(text)


def _wrap_esc(text: str, width: int = _WRAP_WIDTH) -> str:
    lines = textwrap.wrap(text, width) or [text]
    return '<BR ALIGN="CENTER"/>'.join(_esc(line) for line in lines)


def _add_node(dot: Digraph, step: Step) -> None:
    color = STEP_COLORS.get(step.step_type, '#000000')
    nid = _node_id(step.custom_id)
    label_text = _esc(step.description or step.step_type)

    if step.step_type in _START_END:
        dot.node(
            nid,
            label=f'<{label_text}>',
            shape='oval',
            style='filled',
            fillcolor=color,
            fontcolor='white',
            fontname='Arial',
            fontsize='12',
        )
        return

    # Special shapes for control flow
    shape = 'box'
    if step.step_type == 'SpecDecisionVO':
        shape = 'diamond'
    elif step.step_type == 'MergeVO':
        shape = 'diamond'
    elif step.step_type == 'SplittingVO':
        shape = 'box'  # Graphviz doesn't have native horizontal bar; use box with special label
    elif step.step_type == 'SynchronisationVO':
        shape = 'box'  # Similar limitation

    label = (
        f'<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="6">'
        f'<TR><TD ALIGN="CENTER"><B>'
        f'<FONT POINT-SIZE="12" COLOR="#3D006B">{_esc(step.custom_id)}</FONT>'
        f'</B></TD></TR>'
        f'<TR><TD ALIGN="CENTER">'
        f'<FONT POINT-SIZE="12" COLOR="{_NODE_TEXT_COLOR}">'
        f'{_wrap_esc(step.description)}'
        f'</FONT></TD></TR>'
        f'</TABLE>>'
    )

    dot.node(
        nid,
        label=label,
        shape=shape,
        style='rounded,filled',
        fillcolor=_NODE_FILL,
        color=color,
        penwidth='1.5',
        fontname='Arial',
    )


def _build_graph(name: str, title: str, steps: list[Step], links: list[tuple]) -> Digraph:
    dot = Digraph(name=name, comment=title)
    dot.attr(
        rankdir='TB',
        bgcolor=_BG_COLOR,
        pad='0.6',
        nodesep='0.55',
        ranksep='0.7',
        fontname='Arial',
    )
    dot.attr('edge', color=_EDGE_COLOR, arrowhead='normal', penwidth='1.5')

    step_ids = {s.custom_id for s in steps}
    id_map = {s.custom_id: _node_id(s.custom_id) for s in steps}

    for step in steps:
        _add_node(dot, step)

    for source, target in links:
        src = id_map.get(source)
        tgt = id_map.get(target)
        if src and tgt:
            dot.edge(src, tgt)
        else:
            # Fallback: partial suffix match for path-style references
            src_key = next((k for k in step_ids if source.endswith(k) or k.endswith(source)), None)
            tgt_key = next((k for k in step_ids if target.endswith(k) or k.endswith(target)), None)
            if src_key and tgt_key:
                dot.edge(id_map[src_key], id_map[tgt_key])

    return dot


def generate_flow_maps(record: GmbrRecord, output_dir: str = 'output') -> None:
    os.makedirs(output_dir, exist_ok=True)

    overview = _build_graph(
        name='overview',
        title=f'{record.custom_id} – {record.description}',
        steps=record.top_level_steps,
        links=record.top_level_links,
    )
    out = os.path.join(output_dir, 'process_flow_overview')
    overview.render(out, format='png', cleanup=True)
    print(f'  [OK] {out}.png')

    for step in record.top_level_steps:
        if step.step_type != 'BasicOperationVO':
            continue
        if not step.sub_steps:
            print(f'  [SKIP] {step.custom_id} – no sub-steps found')
            continue
        drilldown = _build_graph(
            name=step.custom_id,
            title=f'{step.custom_id} – {step.description}',
            steps=step.sub_steps,
            links=step.sub_links,
        )
        out = os.path.join(output_dir, f'process_flow_{step.custom_id}')
        drilldown.render(out, format='png', cleanup=True)
        print(f'  [OK] {out}.png')
